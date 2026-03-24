# Copilot Instructions — Live AI Tutor

## Quick Start

### Run locally
```bash
./run-local.sh
# Backend: http://localhost:8000 (docs at /docs)
# Frontend: http://localhost:5173
```

### Backend commands
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend commands
```bash
cd frontend
npm install
npm run dev                    # Start dev server
npm run build                  # Build production
npm run lint                   # ESLint check
```

### Environment setup
- `backend/.env` — Add `GOOGLE_API_KEY` (Gemini API key)
- `frontend/.env.local` — Add `VITE_GEMINI_API_KEY` (same key, used in browser for voice)

---

## Architecture Overview

### Two-channel design
The system separates **real-time voice** (direct WebSocket) from **vision + multi-agent orchestration** (HTTP):

1. **Channel 1 — Voice (WebSocket, <200ms latency)**
   - Frontend `useGeminiLive.js` connects directly to `wss://generativelanguage.googleapis.com`
   - Bidirectional audio streaming (16kHz PCM in, 24kHz PCM out)
   - Tool calls trigger backend vision/orchestration via HTTP

2. **Channel 2 — Vision + Orchestration (HTTP POST /interact)**
   - Frontend sends snapshot + message to backend
   - Backend runs: VisionAgent → ADKOrchestrator → diagram/canvas agents
   - Returns Excalidraw-compatible JSON for canvas updates
   - Result fed back to Gemini Live as tool response

### Tech stack
- **Frontend:** React 18 + Vite, Excalidraw (canvas), react-webcam
- **Backend:** FastAPI, Google ADK (multi-agent), Gemini 2.5 Flash + 1.5 Flash
- **Deployment:** Google Cloud Run (single container, frontend + backend)

---

## Key Files & Patterns

### Frontend
- **`src/hooks/useGeminiLive.js`** — Core WebSocket hook
  - Opens connection with `responseModalities: ["AUDIO"]`
  - Manages playback queue, mic capture (ScriptProcessorNode → PCM), tool calls
  - Exposes: `connect()`, `disconnect()`, `sendContext(image)`, `sendToolResponse()`, `toolCall` state
  - **Pattern:** Persona injected via fake model turn (workaround for native audio limitation)

- **`src/App.jsx`** — Main orchestrator
  - Wires webcam → canvas → Gemini Live hook
  - When `toolCall` fires (e.g., `generate_diagram`), POSTs to backend `/interact`
  - Passes backend canvas action to `CanvasBoard` via `externalCanvasActions`
  - Sends `toolResponse` back to Gemini
  - **Key:** Tool call → backend → canvas render → resume conversation

- **`src/components/CanvasBoard.jsx`** — Excalidraw wrapper
  - Listens for `externalCanvasActions` changes
  - Calls `excalidrawAPI.updateScene()` to render backend-generated elements
  - Contract: `{action: "upsert", elements: [...], reason: "..."}`

### Backend
- **`main.py`** — FastAPI + lifespan startup
  - Initializes all 6 agents + ADK orchestrator on startup
  - `POST /interact` — Main endpoint: VisionAgent → ADKOrchestrator → returns tutor text + canvas action
  - `GET /{path}` — SPA fallback, serves React from `static/`

- **`orchestrator.py`** — Google ADK multi-agent router
  - Creates 3 agents (canvas_agent, diagram_agent, hw_tutor_orchestrator)
  - Uses `InMemoryRunner` to execute agent loop
  - `process_interaction()` method sends message, captures events, returns final response + canvas actions

- **`agents/tutor_agent.py`** — Grade-adaptive personas (Sophie, Leo, Maya, Sam)
  - Each has unique teaching style tied to system prompt
  - Default: "Coach Leo" (grades 3-5)

- **`agents/vision_agent.py`** — Image → text description
  - Calls Gemini 1.5 Flash (higher free-tier quota than 2.0)
  - Returns: `{text, topic, detected_elements}`
  - Handles 429 quota errors gracefully

- **`tools/canvas_tools.py`** — Excalidraw element generators
  - `add_text_to_board(text, x, y)`, `clear_board()`, `highlight_area(x, y)`
  - All return `{action: "upsert", elements: [...]}`

- **`tools/diagram_tools.py`** — Mermaid/flowchart generators
  - `draw_science_flow(steps)`, `draw_math_equation_steps(steps)`, `draw_math_number_line(start, end, highlight_points)`
  - Generates Excalidraw elements directly (no Mermaid DSL rendering)

---

## Critical Design Decisions

| What | Why |
|------|-----|
| WebSocket + HTTP split | Voice needs real-time (<200ms), vision/orchestration tolerates ~1-2s latency |
| Gemini native audio for voice | Supports bidirectional streaming, interruptions, natural pauses — REST can't do this |
| ADK with sub-agents | Separate concerns: tutor logic, canvas commands, diagram generation are independent skills |
| Tool calls bridge voice → canvas | Gemini decides when visual helps, triggers `generate_diagram`, backend generates JSON |
| Socratic persona as fake model turn | Native audio models don't support `systemInstruction`, workaround: inject persona as prior response |
| Excalidraw JSON as contract | Tools return raw Excalidraw JSON → frontend calls `updateScene()` directly, no translation layer |
| Single container deploy | Frontend + backend in one Cloud Run service, no CORS in production |

---

## Socratic Philosophy (Core Behavior)

Coach Leo follows strict rules:
1. **Never reveals answers** — always responds with guiding questions
2. **One question at a time** — keeps cognitive load manageable
3. **Affirms correct steps** — reinforces learning when student progresses
4. **Mermaid wrap-up** — provides final step-by-step visual summary once logic is discovered
5. **Confirmation step** — summarizes problem before starting: "I've got [description]. Does that look right?"

---

## Common Workflow: Adding a Canvas Tool

1. **Define the tool** in `backend/tools/canvas_tools.py`
   - Must return `{action: "upsert", elements: [...], reason: "..."}`
   - Use Excalidraw element schema for shapes, text, groups

2. **Register in orchestrator.py**
   - Add to `canvas_agent` tool list in `create_adk_orchestrator()`

3. **Trigger from frontend** (optional)
   - If user should trigger directly: add button in `App.jsx` → `POST /interact` with `request_tool: "tool_name"`

4. **Test**
   - Call backend endpoint directly with curl: `curl -X POST http://localhost:8000/interact -H "Content-Type: application/json" -d '{"message": "test", "request_tool": "tool_name"}'`
   - Verify Excalidraw renders the canvas action in frontend

---

## Common Workflow: Adding a Diagram Type

1. **Define the diagram generator** in `backend/tools/diagram_tools.py`
   - Function signature: `def draw_<type>(params) -> dict`
   - Must return `{action: "upsert", elements: [...], reason: "..."}`

2. **Register in orchestrator.py**
   - Add to `diagram_agent` tool list

3. **Update system prompt** in `orchestrator.py`
   - Add example of when to use this diagram type (helps ADK agent decide)

4. **Test**
   - Trigger via voice: "Can you draw a [diagram type] for this?"
   - Or POST directly: `{"message": "draw", "request_diagram": "diagram_type"}`

---

## Deployment

### Local testing
```bash
./run-local.sh
```

### Deploy to Google Cloud Run
```bash
cd backend
chmod +x deploy.sh
./deploy.sh YOUR_PROJECT_ID
```

The script:
1. Builds Docker image (multi-stage: Node builds frontend, Python builds backend)
2. Pushes to Artifact Registry
3. Deploys to Cloud Run with `GOOGLE_API_KEY` env var
4. Cleans up temporary `.env.production` file

### Environment variables
- `GOOGLE_API_KEY` — Gemini API key (both frontend build + backend runtime)
- `VITE_GEMINI_API_KEY` — Same key (used in browser for voice streaming)

---

## Debugging Tips

- **Frontend won't connect to backend:** Check `VITE_BACKEND_URL` env var or `window.location.hostname` logic in `App.jsx`
- **Voice not working:** Verify API key has access to `gemini-2.5-flash-native-audio-latest` model; check browser console for WebSocket errors
- **Canvas actions not rendering:** Check backend response format matches `{action: "upsert", elements: [...]}` contract; verify Excalidraw element schema
- **ADK agent stuck:** Set `max_steps` in `InMemoryRunner` to avoid infinite loops; check system prompt for clarity
- **Image quota hit (429):** VisionAgent uses Gemini 1.5 Flash for higher free tier; wait or upgrade API tier
