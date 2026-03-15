import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
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

app = FastAPI(title="Live Homework Tutor API", lifespan=lifespan)

# Add CORS Middleware to allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend domain
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

@app.get("/")
def read_root():
    return {"status": "online", "agents_loaded": True}

@app.post("/interact")
async def interact(request: InteractionRequest):
    """
    Main orchestration endpoint using Google ADK.
    """
    response = {}
    
    # 1. Vision Processing (legacy extraction)
    context = "General homework help"
    if request.image_data:
        vision_result = vision_agent.extract_problem_context(request.image_data)
        context = f"Detected Problem: {vision_result['text']}"
        response["vision_context"] = vision_result

    # 2. ADK Orchestrator
    # Pass student intent & image context to the Vertex AI Reasoning Engine
    msg = request.message
    if not msg and request.request_diagram:
        msg = f"Please draw a {request.request_diagram} for me."

    adk_result = await adk_orchestrator.process_interaction(
        user_message=msg or "Help me!",
        image_context=context if request.image_data else None
    )
    
    response["tutor_response"] = adk_result.get("tutor_response", "I'm thinking about that...")
    response["canvas_action"] = adk_result.get("canvas_action", {"action": "noop"})
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
