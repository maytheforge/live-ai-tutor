# Live AI Tutor — Architecture & Design Walkthrough

## 1. What It Is

A **real-time, multimodal AI tutor** that uses the Socratic method — it never gives answers, only asks guiding questions. A student can speak, show their homework via camera/upload, and get voice responses + visual drawings on a shared whiteboard. Think of it as a 1:1 tutor that can see, hear, and draw.

---

## 2. High-Level Architecture

There are **two communication channels** running simultaneously:

```
                          ┌──────────────────────┐
                     WSS  │  Gemini Live API      │
              ┌──────────►│  (Voice + Vision)     │◄─────────┐
              │           │  gemini-2.5-flash      │          │
              │           │  native-audio          │          │
              │           └──────────────────────┘          │
              │  Audio in (16kHz PCM)        Audio out (24kHz PCM)
              │  + Image snapshots           + Tool calls
              │                                             │
     ┌────────┴─────────────────────────────────────────────┴──────┐
     │                    React Frontend (Vite)                     │
     │                                                              │
     │  useGeminiLive.js ←→ WebSocket (real-time voice)            │
     │  App.jsx          ←→ POST /interact (snapshots + text)      │
     │  CanvasBoard.jsx  ←→ Excalidraw (shared whiteboard)        │
     └────────────────────────────┬────────────────────────────────┘
                                  │ HTTP POST /interact
                                  │ { image_data, message }
                                  ▼
     ┌────────────────────────────────────────────────────────────┐
     │                  FastAPI Backend (Cloud Run)                │
     │                                                            │
     │  1. VisionAgent (Gemini 1.5 Flash) — image analysis        │
     │  2. ADK Orchestrator (InMemoryRunner)                      │
     │     ├── Root: Tutor Agent — Socratic logic                 │
     │     ├── Sub: Canvas Agent — board drawing tools            │
     │     └── Sub: Diagram Agent — math/science visuals          │
     │  3. ReviewAgent — session recording                        │
     │  4. ReinforcementAgent — practice problems                 │
     └────────────────────────────────────────────────────────────┘
```

**Channel 1 — Voice (frontend-only):** `useGeminiLive.js` opens a WebSocket directly to `wss://generativelanguage.googleapis.com`. Mic audio streams in at 16kHz PCM, Gemini responds with 24kHz PCM audio. This is the live conversation. The frontend also sends camera snapshots over this same WebSocket as image chunks.

**Channel 2 — Vision + Orchestration (frontend → backend):** When a snapshot is taken or an image uploaded, the frontend POSTs to `/interact`. The backend runs it through the VisionAgent, then the ADK orchestrator (which routes to `diagram_agent` or `canvas_agent`), and returns Socratic text + diagram/canvas data:
- **Mermaid diagrams** — DSL string rendered as SVG in `MermaidPanel`
- **Excalidraw canvas updates** — JSON elements rendered in `CanvasBoard`

---

## 3. Frontend Deep Dive

### `frontend/src/hooks/useGeminiLive.js` — The core real-time hook

- Opens a WebSocket to `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent`
- Sends a `setup` message configuring the model (`gemini-2.5-flash-native-audio-latest`) with `responseModalities: ["AUDIO"]` and a `generate_diagram` tool declaration
- Injects the Socratic persona via a fake model turn (workaround because native audio models don't support `systemInstruction`)
- Captures mic audio via `ScriptProcessorNode`, converts to 16-bit PCM, base64-encodes it, and streams it as `realtimeInput.mediaChunks`
- Receives responses: audio chunks go to a playback queue (`playNextAudio`), tool calls go to React state (`setToolCall`)
- Exposes: `connect`, `disconnect`, `sendContext` (image), `sendToolResponse`, `toolCall`, `isConnected`

### `frontend/src/App.jsx` — The glue

- Wires the webcam (react-webcam), the canvas (Excalidraw), and the Gemini Live hook together
- When `toolCall` fires (e.g. `generate_diagram`), it POSTs to the backend `/interact` endpoint with the diagram type
- The backend returns an Excalidraw-compatible JSON action, which App.jsx passes to `CanvasBoard` as `externalCanvasActions`
- Then sends a `toolResponse` back to Gemini so the voice conversation continues

### `frontend/src/components/MermaidPanel.jsx` — Mermaid diagram renderer

- Renders Mermaid DSL diagrams as interactive SVG
- Uses library: `mermaid@11.13.0`
- Process:
  1. Receives Mermaid code string from backend
  2. Calls `mermaid.render()` → converts DSL to SVG
  3. Displays as read-only conceptual visualization
- Status: **Read-only display** (for explaining processes and concepts)

### `frontend/src/components/CanvasBoard.jsx` — Excalidraw wrapper

- Renders an interactive, editable Excalidraw canvas
- Uses library: `@excalidraw/excalidraw@0.18.0`
- Listens for `externalCanvasActions` prop changes
- When a canvas action arrives (e.g. `{action: "upsert", elements: [...]}`) it calls `excalidrawAPI.updateScene()` to draw the elements
- Status: **Fully editable** (for Socratic visual aids, student annotations, highlighting)

### `frontend/src/pages/HomePage.jsx` — Landing page

Landing page with feature cards and "Start Tutoring Session" button.

### `frontend/src/pages/TutorPage.jsx` — Session interface

The main tutoring interface with webcam + canvas + controls.

---

## 4. Backend Deep Dive

### `backend/main.py` — FastAPI entry point

- Uses `lifespan` async context to initialize all 6 agents + the ADK orchestrator on startup
- **`POST /interact`** — The main endpoint:
  1. If `image_data` present → `VisionAgent.extract_problem_context()` (calls Gemini 1.5 Flash)
  2. Enriches the message with vision context
  3. Passes to `ADKOrchestrator.process_interaction()` → returns tutor text + canvas action
  4. Records the interaction via `ReviewAgent`
- **`GET /session/summary`** — Returns session review
- **`GET /session/practice`** — Generates practice problems
- **`GET /{path}`** — SPA fallback serving the built React app from `static/`

### `backend/orchestrator.py` — Google ADK multi-agent system

- Creates 3 agents using `google.adk.agents.llm_agent.Agent`:
  - **`canvas_agent`** (Gemini 2.5 Flash) — **Excalidraw tools:** `add_text_to_board`, `clear_board`, `highlight_area`
  - **`diagram_agent`** (Gemini 2.5 Flash) — **Mermaid tools:** `display_mermaid_diagram`
  - **`hw_tutor_orchestrator`** (root, Gemini 2.5 Flash) — has canvas + diagram as `sub_agents`, uses Socratic system prompt
- Uses `InMemoryRunner` to execute the agent loop
- `process_interaction()` sends a message, iterates over events, captures the final text response and both diagram + canvas results

### `backend/agents/tutor_agent.py` — Grade-adaptive persona definitions

- 4 personas mapped to grade levels: Sophie (K-2), Leo (3-5), Maya (6-8), Sam (9-12)
- Each has a unique teaching style, technique, and system prompt
- Default is "Coach Leo" — supportive, visual-focused

### `backend/agents/vision_agent.py` — Image understanding

- Takes base64 image data, calls `genai.Client.models.generate_content()` with Gemini 1.5 Flash
- Prompt instructs it to describe the homework without solving it
- Returns `{text, topic, detected_elements}`
- Handles 429 quota errors gracefully

### `backend/tools/canvas_tools.py` — Excalidraw element generators

- **Excalidraw JSON format** — returns interactive drawing elements
- `add_text_to_board(text, x, y)` → text element
- `clear_board()` → empty canvas
- `highlight_area(x, y)` → yellow highlight rectangle
- Used by canvas_agent for Socratic visual aids

### `backend/tools/mermaid_tools.py` — Mermaid diagram generator

- **Mermaid DSL format** — returns conceptual diagrams
- `display_mermaid_diagram(mermaid_code: str, title: str)` → Mermaid DSL string
- Converts to SVG at frontend (MermaidPanel)
- Used by diagram_agent for flowcharts, sequences, mindmaps

---

## 5. The Tool Call Flow (Most Important Pattern)

This is the most architecturally interesting part — how voice, vision, and canvas connect:

```
Student says: "Can you draw a number line for this?"
        │
        ▼
[Gemini Live API] recognizes generate_diagram tool call
        │
        ▼
[useGeminiLive.js] receives toolCall:
  {name: "generate_diagram", args: {diagram_type: "math_number_line", topic: "..."}}
        │
        ▼
[App.jsx] POSTs to backend: /interact {request_diagram: "math_number_line"}
        │
        ▼
[Backend ADK Orchestrator] routes to diagram_agent → calls display_mermaid_diagram()
        │
        ▼
[Backend] returns: {mermaid_diagram: {mermaid: "graph...", title: "..."}}
        │
        ▼
[App.jsx] renders in MermaidPanel → Mermaid DSL converts to SVG
        │
        ▼
[App.jsx] sends toolResponse back to Gemini Live → voice conversation resumes
```

**Alternative flow** — if the tutor uses **Excalidraw** (for highlighted steps, annotations):
```
[Backend ADK Orchestrator] routes to canvas_agent → calls add_text_to_board()
        │
        ▼
[Backend] returns: {canvas_action: {action: "upsert", elements: [text elements...]}}
        │
        ▼
[App.jsx] passes canvas_action to CanvasBoard → Excalidraw renders + allows student interaction
```

---

## 6. Deployment

### Dockerfile — Multi-stage build

- **Stage 1:** `node:22-slim` builds the React app (`npm run build`), reads `VITE_GEMINI_API_KEY` from `.env.production`
- **Stage 2:** `python:3.11-slim` installs backend deps, copies backend code + built frontend into `static/`
- Runs: `uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}`

### deploy.sh

- Writes `frontend/.env.production` with the API key (so Vite embeds it at build time)
- Runs `gcloud run deploy --source .` which uploads source → Cloud Build → Docker build → Cloud Run
- Sets runtime env vars: `GOOGLE_API_KEY`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`
- Cleans up the `.env.production` file after deploy

### Production serving

The FastAPI backend serves the React SPA from `static/` via the catch-all `/{path}` route. Everything runs on a single Cloud Run container.

---

## 7. Key Design Decisions

| Decision | Why |
|----------|-----|
| **Two-channel architecture** (WebSocket + HTTP) | Voice must be real-time (<200ms), but vision/orchestration can tolerate ~1-2s latency |
| **Gemini native audio model for voice** | Supports bidirectional streaming, interruptions, natural conversation — can't do this with REST |
| **ADK with sub-agents** (not a single monolithic prompt) | Separation of concerns — tutor logic, canvas commands, and diagram generation are independent skills |
| **Tool calls bridge voice → visuals** | Gemini decides when a visual helps, triggers `generate_diagram`, backend routes to diagram_agent (Mermaid) or canvas_agent (Excalidraw) |
| **Dual-path diagram system** | Mermaid (conceptual, read-only SVG) for flowcharts + sequences; Excalidraw (interactive JSON) for Socratic visual aids + student annotation |
| **Socratic persona injected as model turn** | Native audio models don't support `systemInstruction`, so the persona is faked as a prior model response |
| **VisionAgent on 1.5 Flash (not 2.0)** | Higher free-tier quotas for image analysis |
| **Mermaid DSL + Excalidraw JSON contracts** | Diagram_agent returns DSL string (rendered frontend), canvas_agent returns JSON — no translation layer, frontend calls respective render methods directly |
| **Single container for frontend + backend** | Simplifies deployment — one Cloud Run service, no CORS in production |
