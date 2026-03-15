---
stepsCompleted: [step-01-architectural-design]
inputDocuments: [brainstorming-session-20260309-200920, prd.md]
workflowType: 'architecture'
project_name: 'Live Homework Tutor Agent'
user_name: 'Harishkanuri'
date: '2026-03-09T22:31:41-04:00'
---

# Architecture Solution Design - Live Homework Tutor Agent

## 🏗️ 7. Canvas Interaction Architecture

This section defines the precise relationship between the pedagogical logic and the visual reasoning interface.

### 7.1 Overview
The **Canvas Agent** acts as a "Graphics Driver" for the **Tutor Agent**. The Tutor Agent determines *what* needs to be explained pedagogically, and the Canvas Agent determines *how* to represent that in Excalidraw.

### 7.2 Component Interaction Model

| Component | Responsibility | Interface |
| :--- | :--- | :--- |
| **Tutor Agent** | Pedagogical reasoning & Socratic strategy | High-level Intent (e.g., "Highlight the variable") |
| **Canvas Agent** | State management & Excalidraw Command generation | JSON Command Stream (Excalidraw API) |
| **Excalidraw (FE)** | Rendering & User Interaction | Snapshot API / Live Hooks |
| **Gemini Live API** | Real-time multimodal context (Voice/Vision) | Multimodal Stream (ADK) |

---

## 🏗️ 8. System Architecture & Event Flows

### 8.1 Real-Time Sequence Diagram (Conceptual)

1. **Student Voice Input**: "I'm stuck on the first step."
2. **Gemini Live (ADK)**: Transcribes voice + captures camera snapshot.
3. **Tutor Agent**: 
    - Analyzes current problem text.
    - Observes current whiteboard state (via Canvas Agent state check).
    - Decides: "Highlight the constant term to prompt subtraction."
4. **Tutor Agent → Canvas Agent**: 
    - `intent: "HIGHLIGHT_TARGET"`, `payload: { term: "+5", color: "remedial-yellow" }`
5. **Canvas Agent**:
    - Scans Excalidraw element tree for text matching "+5".
    - Generates update instruction for the specific element ID.
6. **Canvas Agent → Frontend (Socket)**: 
    - `type: "UPDATE_ELEMENT"`, `id: "elem_xyz"`, `styles: { strokeColor: "#FFD700", strokeWidth: 4 }`
7. **Excalidraw**: Renders the highlight instantly.

### 8.2 Data Contracts

#### Tutor → Canvas (High-Level Intent)
```json
{
  "sequence_id": "uuid",
  "command": "ANNOTATE | HIGHLIGHT | DRAW_ARROW | CLEAR_AREA",
  "parameters": {
    "text_target": "3x", 
    "context": "simplification",
    "style": "focus"
  }
}
```

#### Canvas → Excalidraw (Low-Level Action)
```json
{
  "action": "upsert",
  "elements": [
    {
      "type": "arrow",
      "x": 100,
      "y": 200,
      "points": [[0,0], [50,50]],
      "strokeColor": "#4a90e2"
    }
  ],
  "appState": {
    "currentItemFontFamily": 1
  }
}
```

### 8.3 State Management
- **Primary Source of Truth**: The Frontend Excalidraw instance holds the current scene.
- **Sync Model**: The Frontend emits a scene snapshot (JSON) to the **Canvas Agent** whenever an operation is completed.
- **Agent Memory**: The Canvas Agent maintains a simplified "Abstract Visual Map" (e.g., "3x is at top-left") to provide spatial context to the Tutor Agent.

---

## 🏗️ 10. Development Epics

### Epic 1: Multimodal Interface & RTC
Establish the real-time foundation using Gemini Live.
- **Story 1.1**: Integrate Gemini Live API into the React frontend.
- **Story 1.2**: Implement Camera snapshot and Microphone streaming logic.
- **Story 1.3**: Handle interruptible audio dialogue flows.

### Epic 2: Socratic Agent Orchestration (ADK)
Build the "brains" of the system using Google ADK.
- **Story 2.1**: Implement the **Tutor Agent** with Socratic prompting strategies.
- **Story 2.2**: Build the **Vision Agent** for OCR and logic extraction from snapshots.
- **Story 2.3**: Orchestrate handoffs between Tutor, Vision, and Canvas agents via ADK.

### Epic 3: Interactive Visual Reasoning (Canvas)
Connect the AI's logic to the Excalidraw whiteboard.
- **Story 3.1**: Implement the **Canvas Agent** (the intent-to-drawing translator).
- **Story 3.2**: Establish real-time JSON sync between Backend and Excalidraw FE.
- **Story 3.3**: Create visual templates for Math (Equations) and Science (Diagrams).

### Epic 4: Post-Session Reinforcement
Add the "learning loop" features.
- **Story 4.1**: Build the **Review Agent** to summarize the session's progress.
- **Story 4.2**: Implement the **Reinforcement Agent** to generate similar practice problems.
- **Story 4.3**: Persist session highlights to Firestore for student review.

---

## 🏗️ 11. Project Repository Structure

```text
/homework-helper
  /frontend            # React + Vite + Excalidraw
    /src
      /components
        /CameraPreview
        /CanvasBoard    # Excalidraw wrapper
        /VoiceUI        # Gemini Live indicators
      /hooks            # useGeminiLive, useCanvasSync
  /backend             # FastAPI / Node.js
    /agents            # Google ADK agent definitions
      tutor_agent.py
      vision_agent.py
      canvas_agent.py
      diagram_agent.py
      review_agent.py

      reinforcement_agent.py
    /services          # Gemini model client, persistence
      gemini_service.py
      state_service.py
  /contracts           # Shared JSON schemas for agent comms
  /infrastructure      # Terraform / GCloud deployment scripts
  package.json
  docker-compose.yml
```

---

## 🏗️ 12. Technology Stack (Google Cloud Focus)

To ensure hackathon compliance and maximum scalability, we are leveraging the full Google Cloud ecosystem:

- **AI Orchestration**: **Google Agent Development Kit (ADK)** for multi-agent coordination.
- **Model Layer**: **Vertex AI** for Gemini 1.5 Pro/Flash integration via the Multimodal Live API.
- **Backend Execution**: **Google Cloud Run** for serverless, auto-scaling backend services (Python/FastAPI).
- **State & Persistence**: **Google Cloud Firestore** for real-time student session and canvas state syncing.
- **Media Storage**: **Google Cloud Storage** for persisting student camera snapshots and review artifacts.
- **Authentication**: **Google Cloud Identity Platform** (Firebase Auth) for secure student login.
- **CI/CD & Deployment**: **Google Cloud Build** and **Artifact Registry** for automated container deployment.
- **Frontend**: React (Vite) + Excalidraw SDK, hosted on **Firebase Hosting**.


---

## 🏗️ 13. Hackathon Demo Script (4 Minutes)

1. **0:00 - 0:45**: **The Hook**. Present the problem: "Students are stuck, AI tools just give them the answer." Start the "Sophie" (K-2) or "Leo" (Upper Elem) demo.
2. **0:45 - 2:00**: **Multimodal Interaction**. Show the camera feed. Student says: "I can't solve this." Gemini responds: "No worries! Let's look at it together."
3. **2:00 - 3:15**: **The Shared Canvas**. The AI draws an arrow on the whiteboard pointing to a specific part of the student's work. "I noticed you added here, what if we tried subtracting?"
4. **3:15 - 4:00**: **Reinforcement & Closure**. Student solves the problem. Gemini celebrates and generates a 'Challenge Question' for later. End with the prompt: "Built with Gemini Live and Google Cloud."

---

## 🏗️ 14. Local Development & Testing Plan

Yes, local testing is highly feasible and recommended for rapid iteration during the hackathon.

### 14.1 Local Mocking & Emulation
- **Firestore**: Use the **Firebase Emulator Suite** to run a local instance of Firestore. This allows for real-time state syncing on your machine.
- **Backend (Cloud Run)**: Run the FastAPI backend locally using `uvicorn`. It can connect to the local Firestore emulator via environment variables.
- **Gemini Live API**: While the model itself runs in the cloud, you can call the Vertex AI APIs directly from your local environment using a Service Account Key or `gcloud auth application-default login`.
- **Cloud Storage**: Use the local filesystem or the Firebase Storage emulator to mock snapshot uploads.

### 14.2 Testing Workflow
1.  **Frontend**: Run `npm run dev`. It will point to your local backend.
2.  **Backend**: Run the Python server. It will coordinate the ADK agents locally.
3.  **Agents**: ADK agents are just Python/Node logic. They can be tested with unit tests or by triggering them through the local API endpoints.
4.  **Hardware**: Since it's a Web App, the camera and microphone will work directly in your local browser (localhost).

### 14.3 Pre-Deployment Validation
Before pushing to Google Cloud, we will use **Docker Compose** to run the frontend and backend together in a production-like containerized environment to ensure all environment variables and internal network calls are correct.


