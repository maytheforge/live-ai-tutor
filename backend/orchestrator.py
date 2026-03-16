import os
import asyncio
import uuid
from google.adk.agents.llm_agent import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from tools.canvas_tools import add_text_to_board, clear_board, highlight_area
from tools.mermaid_tools import display_mermaid_diagram

SYSTEM_PROMPT = """You are Coach Leo, a Socratic educational tutor. Your core philosophy: NEVER reveal answers. You guide discovery using questions.

TRIAGE & INGESTION (Start of Session):
1. Greet the student and ask: "Are you here for Homework help or to Learn a new topic?"
2. If HOMEWORK: Suggest they share the problem by saying it, taking a snapshot, or uploading a file.
3. CONFIRMATION: Once a problem is shared (via voice or image), you MUST summarize it and ask: "I've got [problem description]. Does that look right?" before starting the discussion.

SOCRATIC DIALOGUE RULES:
1. Break problems into small discoverable steps. Ask ONE guiding question at a time.
2. If the student is right, affirm and ask "What's next?". If wrong, ask a guiding question about their reasoning.

DIAGRAM LOGIC (via diagram_agent):
1. MERMAID FIRST: Mermaid is your PREFERRED tool for all visual explanations. Use `diagram_agent` to create flowcharts, sequences, or mindmaps.
2. HOMEWORK MODE: Delay diagrams until the conceptual solution is reached or a breakthrough is needed.
3. SOLUTION WRAP-UP (MANDATORY): As soon as the student reaches the final answer, or if they explicitly ask for the solution/final steps, you MUST IMMEDIATELY delegate to `diagram_agent` to show a visual step-by-step summary of the path to the solution. This is the official way to conclude a math or science problem session.
4. LEARNING MODE: Generate the Mermaid diagram UPFRONT as a conceptual framework.

RESPONSE STYLE: Conversational, warm, and brief (1-2 sentences).
"""


class ADKOrchestrator:
    """
    The main Multi-Agent Orchestrator powered by Google ADK.
    Uses InMemoryRunner with a parent Orchestrator agent that delegates to sub-agents.
    """

    def __init__(self):
        # Create Canvas Sub-Agent
        canvas_agent = Agent(
            name="canvas_agent",
            model="gemini-flash-latest",
            tools=[add_text_to_board, clear_board, highlight_area],
            instruction="You are the Canvas Agent. Your job is to draw visual aids that HELP the student think — not reveal answers. Draw diagrams that prompt discovery, like a number line without the answer marked, or steps shown one-by-one with blanks for the student to fill in."
        )

        # Create Diagram Sub-Agent — uses the model to produce Mermaid DSL
        diagram_agent = Agent(
            name="diagram_agent",
            model="gemini-flash-latest",
            tools=[display_mermaid_diagram],
            instruction=(
                "You are the Diagram Agent. Your goal is to create a visual Mermaid DSL diagram to help the student. "
                "Steps:\n"
                "1. Think of the best diagram type: flowchart, sequence, mindmap, or stateDiagram.\n"
                "2. Generate the valid Mermaid code.\n"
                "3. Call display_mermaid_diagram(mermaid_code=..., title=...) with your result.\n\n"
                "Rules:\n"
                "- Normally, visualize the STRUCTURE or PROCESS, not the final answer.\n"
                "- EXCEPTION (Solution Wrap-up): If tasked with a 'solution wrap-up' or 'final summary', you SHOULD include the complete step-by-step process including the final answer to consolidate the student's learning.\n"
                "- Keep labels short and readable."
            )
        )

        # Initialize Top-Level Google ADK Orchestrator Agent
        self.root_agent = Agent(
            name="hw_tutor_orchestrator",
            model="gemini-flash-latest",
            sub_agents=[canvas_agent, diagram_agent],
            instruction=SYSTEM_PROMPT
        )

        # InMemoryRunner is the proper execution engine in google.adk
        self.runner = InMemoryRunner(agent=self.root_agent)
        self.user_id = "hw_student"
        self.session_id = None  # Set during async startup via initialize()

    async def initialize(self):
        """Creates the shared session. Must be called once inside an async context (e.g. FastAPI startup)."""
        session = await self.runner.session_service.create_session(
            app_name=self.runner.app_name,
            user_id=self.user_id
        )
        self.session_id = session.id
        print(f"ADK session created: {self.session_id}")

    async def process_interaction(self, user_message: str, image_context: str = None) -> dict:
        """
        Takes the user message, runs it through the Google ADK multi-agent loop,
        and returns the tool payloads to send to the Excalidraw frontend.
        This is an async method — call with `await` from an async FastAPI endpoint.
        """
        return await self._process_async(user_message, image_context)

    async def _process_async(self, user_message: str, image_context: str = None) -> dict:
        """Async implementation of the agent interaction."""
        prompt = f"Student says: {user_message}"
        if image_context:
            prompt += f"\n\nContext from student's board: {image_context}"

        try:
            new_message = types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )

            final_text = ""
            canvas_action = {"action": "noop"}
            mermaid_diagram = None

            # Collect all events from the ADK runner
            async for event in self.runner.run_async(
                user_id=self.user_id,
                session_id=self.session_id,
                new_message=new_message
            ):
                # Capture the final text response
                if event.is_final_response() and event.content:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            final_text = part.text

                # Capture tool execution results from sub-agents
                if (
                    event.content
                    and event.content.parts
                    and hasattr(event.content.parts[0], "function_response")
                    and event.content.parts[0].function_response
                ):
                    tool_result = event.content.parts[0].function_response.response
                    if isinstance(tool_result, dict):
                        if "mermaid" in tool_result:
                            # New Mermaid diagram tool result
                            mermaid_diagram = tool_result
                        elif "action" in tool_result:
                            # Legacy canvas tool result
                            canvas_action = tool_result

            return {
                "tutor_response": final_text or "Let me think about that...",
                "canvas_action": canvas_action,
                "mermaid_diagram": mermaid_diagram,
                "dynamic_adk": True
            }

        except Exception as e:
            print(f"ADK Orchestrator Exception: {e}")
            return {
                "tutor_response": f"I had trouble thinking about that... (Error: {e})",
                "canvas_action": {"action": "noop"},
                "dynamic_adk": False
            }
