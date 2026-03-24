# 🎓 Live AI Tutor — Socratic Mirror

A real-time, multimodal AI homework tutor powered by Google Gemini Live API and Google ADK (Agent Development Kit). Coach Leo acts as a **Socratic Mirror** — guiding students through the cognitive process of discovery rather than simply providing answers.

---

## ✨ What It Does

| Feature | Description |
|---|---|
| 🎤 **Live Voice Tutoring** | Students talk to Coach Leo in real-time using the Gemini Live API (WebSocket-based audio) |
| 📷 **Homework Vision** | Students hold homework up to their camera — the tutor "sees" it via snapshot analysis |
| 📊 **Mermaid Diagrams** | High-quality AI-generated flowcharts, sequences, and mindmaps render natively in the **Diagram** tab |
| 📐 **Shared Whiteboard** | An Excalidraw canvas for student free-hand annotation and manual highlighting |
| 🤔 **Socratic Method** | The tutor never gives answers directly — it asks guiding questions to promote discovery |
| 🤖 **Multi-Agent Orchestration** | A Google ADK parent orchestrator delegates to specialized sub-agents |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                      │
│  Gemini Live API ──► useGeminiLive.js ──► Tool Call Handler   │
│  ┌───────────────────────────┬──────────────────────────────┐  │
│  │    Mermaid Diagram Tab    │      Excalidraw Whiteboard    │  │
│  └───────────────────────────┴──────────────────────────────┘  │
└─────────────────────────────┬────────────────────────────────┘
                               │ HTTP POST /interact
┌─────────────────────────────▼────────────────────────────────┐
│                  FastAPI Backend (Python)                       │
│                                                                │
│  ADKOrchestrator (hw_tutor_orchestrator)                       │
│    ├── diagram_agent ──► Generates Mermaid DSL (Solution/Flow)   │
│    └── canvas_agent  ──► Dynamic highlights and annotation      │
└──────────────────────────────────────────────────────────────┘
```

**Key technologies:**
- **Frontend:** React + Vite, `mermaid.js`, Excalidraw, Gemini Live WebSocket API
- **Backend:** FastAPI (Python), Google ADK (`google-adk`), `google-genai`
- **Deployment:** Google Cloud Run + Docker

---

## 🚀 Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- A [Gemini API Key](https://ai.google.dev/gemini-api/docs/api-key)

### 1. Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Start the server
uvicorn main:app --reload --port 8000
```

The backend runs at `http://localhost:8000`.

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create frontend environment file
echo "VITE_GEMINI_API_KEY=your_api_key_here" > .env.local

# Start the dev server
npm run dev
```

The frontend runs at `http://localhost:5173`. Open it in your browser.

---

## ☁️ Deploy to Google Cloud Run

### Prerequisites
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and authenticated
- A GCP project with Cloud Run and Artifact Registry APIs enabled

### 1. Set your project

```bash
gcloud config set project YOUR_PROJECT_ID
```

### 2. Deploy the backend

```bash
cd backend

# Make the deploy script executable (first time only)
chmod +x deploy.sh

# Deploy to Cloud Run
./deploy.sh YOUR_PROJECT_ID
```

The script will:
1. Build the Docker image using Cloud Build
2. Push it to Google Artifact Registry
3. Deploy to Cloud Run with your `GOOGLE_API_KEY` env var

### 3. Set environment variables on the deployed service

```bash
gcloud run services update live-ai-tutor \
  --region us-central1 \
  --set-env-vars="GOOGLE_API_KEY=your_key_here"
```

### 4. Update the frontend API URL

After deployment, update your frontend to point to the Cloud Run URL instead of `localhost:8000`. The frontend uses `window.location.hostname` dynamically, so if you deploy the frontend on the same domain, no changes are needed.

### 5. Required IAM permissions

The Cloud Run service account needs the **Vertex AI User** role:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

---

## 📁 Project Structure

```
live-ai-tutor/
├── backend/
│   ├── main.py              # FastAPI app with lifespan startup
│   ├── orchestrator.py      # Google ADK multi-agent orchestrator
│   ├── agents/              # Legacy single-agent implementations
│   ├── tools/
│   │   ├── canvas_tools.py  # Dynamic highlights tool
│   │   └── mermaid_tools.py # Mermaid diagram tool
│   ├── Dockerfile
│   ├── deploy.sh
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx              # Main app + tool call handler
    │   ├── hooks/
    │   │   └── useGeminiLive.js # Gemini Live WebSocket hook
    │   └── components/
    │       └── CanvasBoard.jsx  # Excalidraw canvas component
    └── package.json
```

---

## 🔑 Environment Variables

| Variable | Where | Description |
|---|---|---|
| `GOOGLE_API_KEY` | `backend/.env` | Gemini API key for ADK backend |
| `VITE_GEMINI_API_KEY` | `frontend/.env.local` | Gemini API key for Live audio in browser |

---

## 🧠 Socratic Philosophy

Coach Leo follows strict Socratic rules:
- **Never reveals answers** — always responds with guiding questions
- **One question at a time** — keeps the student's cognitive load manageable  
- **Affirms correct steps** — reinforces learning when the student progresses
- **Mermaid Solution Wrap-up** — provides a final step-by-step visual summary once the logic is discovered

---

## 📄 License

MIT
