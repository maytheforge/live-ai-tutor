import os
from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

# Import agents
from agents.tutor_agent import TutorAgent, GradeLevel
from agents.vision_agent import VisionAgent
from agents.canvas_agent import CanvasAgent
from agents.diagram_agent import DiagramAgent, DiagramType
from agents.review_agent import ReviewAgent
from agents.reinforcement_agent import ReinforcementAgent
from orchestrator import ADKOrchestrator
from tools.mermaid_tools import generate_mermaid_diagram

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Global agent instances
tutor_agent = None
vision_agent = None
canvas_agent = None
diagram_agent = None
review_agent = None
reinforcement_agent = None
adk_orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles bot startup and shutdown routines."""
    global tutor_agent, vision_agent, canvas_agent, diagram_agent, review_agent, reinforcement_agent, adk_orchestrator
    # Initialize all agents on startup
    tutor_agent = TutorAgent(GradeLevel.LEO)
    vision_agent = VisionAgent()
    canvas_agent = CanvasAgent()
    diagram_agent = DiagramAgent()
    review_agent = ReviewAgent()
    reinforcement_agent = ReinforcementAgent()
    adk_orchestrator = ADKOrchestrator()
    await adk_orchestrator.initialize()
    print("All agents and ADK orchestrator ready!")
    yield  # App runs here
    # Shutdown cleanup (if needed)

app = FastAPI(title="Live AI Tutor API", lifespan=lifespan)

# CORS: use ALLOWED_ORIGINS env var in production, fallback to permissive for local dev
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InteractionRequest(BaseModel):
    student_id: str
    message: Optional[str] = None
    image_data: Optional[str] = None # Base64 snapshot
    grade_level: Optional[str] = "3-5"
    request_diagram: Optional[str] = None # e.g. "number_line"

@app.get("/health")
def health_check():
    return {"status": "online", "agents_loaded": True}

@app.post("/interact")
async def interact(request: InteractionRequest):
    """
    Main orchestration endpoint using Google ADK.
    """
    response = {}
    
    # 1. Vision Processing — analyze the real image with Gemini
    context = None
    if request.image_data:
        vision_result = vision_agent.extract_problem_context(request.image_data)
        context = vision_result['text']
        response["vision_context"] = vision_result
        response["vision_topic"] = vision_result.get("topic", "Homework problem")

    # 2. ADK Orchestrator
    msg = request.message
    if not msg and request.request_diagram:
        msg = f"Please draw a {request.request_diagram} for me."

    # Enrich the message with vision context so the orchestrator knows what it's looking at
    if context and msg:
        orchestrator_message = f"{msg}\n\n[Image context: {context}]"
    elif context:
        orchestrator_message = f"I can see: {context}. Can you help me understand this?"
    else:
        orchestrator_message = msg or "Help me!"

    adk_result = await adk_orchestrator.process_interaction(
        user_message=orchestrator_message,
        image_context=context
    )
    
    response["tutor_response"] = adk_result.get("tutor_response", "I'm thinking about that...")
    response["canvas_action"] = adk_result.get("canvas_action", {"action": "noop"})

    # --- Direct Mermaid diagram generation (independent of ADK) ---
    # Case 1: Explicit diagram request from the voice agent (request_diagram set)
    # Case 2: Image analyzed — auto-generate a diagram for the detected homework topic
    mermaid_result = None
    topic_for_diagram = None
    diagram_type = "flowchart"

    if request.request_diagram:
        # request_diagram contains the topic or type hint from the voice call
        topic_for_diagram = request.request_diagram
        # Pick diagram type based on the hint
        if "flow" in request.request_diagram.lower() or "cycle" in request.request_diagram.lower() or "process" in request.request_diagram.lower():
            diagram_type = "flowchart"
        elif "sequence" in request.request_diagram.lower() or "step" in request.request_diagram.lower():
            diagram_type = "sequence"
        elif "mind" in request.request_diagram.lower():
            diagram_type = "mindmap"
    elif response.get("vision_topic") and response["vision_topic"] != "Homework problem":
        # Use the vision-detected topic to generate a relevant contextual diagram
        topic_for_diagram = response["vision_topic"]
        # Try to pick an appropriate type based on the topic
        topic_lower = topic_for_diagram.lower()
        if any(w in topic_lower for w in ["cycle", "flow", "process", "phase", "stage", "step"]):
            diagram_type = "flowchart"
        elif any(w in topic_lower for w in ["equation", "math", "algebra", "solve", "formula"]):
            diagram_type = "flowchart"  # step-by-step solving flow
        else:
            diagram_type = "flowchart"

    if topic_for_diagram:
        mermaid_result = generate_mermaid_diagram(
            topic=topic_for_diagram,
            diagram_type=diagram_type
        )

    response["mermaid_diagram"] = mermaid_result  # None if no diagram needed

    # 3. Logic to record for review later
    review_agent.record_interaction(response["tutor_response"], request.message or "")

    return response


@app.get("/session/summary")
def get_summary():
    return review_agent.generate_summary()

@app.get("/session/practice")
def get_practice():
    summary = review_agent.generate_summary()
    return reinforcement_agent.generate_practice_problems(summary["concepts_covered"])

# Serve the built React frontend in production (static/ directory created by Docker build)
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.is_dir():
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve frontend static files; fall back to index.html for SPA routing."""
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
