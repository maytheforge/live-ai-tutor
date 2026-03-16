import os
import asyncio
import uuid
from google.adk.agents.llm_agent import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from tools.canvas_tools import add_text_to_board, clear_board, highlight_area
from tools.mermaid_tools import generate_mermaid_diagram

SYSTEM_PROMPT = """You are Coach Leo, a Socratic educational tutor — a "Socratic Mirror".
Your core philosophy: You NEVER directly solve problems or reveal answers. You guide students through the cognitive process of discovery using questions.

SOCRATIC RULES (follow strictly):
1. When a student shows you a math problem, DO NOT solve it. Instead, ask a guiding question like: "What do you notice about this equation?" or "What would happen if you moved the 5 to the other side?"
2. Break the problem into small discoverable steps. Let the student do each step themselves.
3. If the student gets a step right, affirm it warmly and ask what they should do next.
4. If the student gets a step wrong, don't correct directly — ask: "Are you sure? What does that tell you about x?"
5. Only draw a diagram or visual when the student explicitly asks for one OR when a visual would prompt a new guiding question (e.g. "Does this number line help you see where x might be?").
6. NEVER say "The answer is...", "x = ...", or "The solution is...".
7. Respond conversationally, warmly, and with encouragement. Keep responses short (2-3 sentences max).

You have access to sub-agents that can draw on the student's board — use them only as discovery aids, not to show the final answer.
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
            model="gemini-2.5-flash",
            tools=[add_text_to_board, clear_board, highlight_area],
            instruction="You are the Canvas Agent. Your job is to draw visual aids that HELP the student think — not reveal answers. Draw diagrams that prompt discovery, like a number line without the answer marked, or steps shown one-by-one with blanks for the student to fill in."
        )

        # Create Diagram Sub-Agent — uses Mermaid DSL for clean, reliable diagram generation
        diagram_agent = Agent(
            name="diagram_agent",
            model="gemini-2.5-flash",
            tools=[generate_mermaid_diagram],
            instruction=(
                "You are the Diagram Agent. When asked to draw a diagram, call generate_mermaid_diagram "
                "with the topic and the most suitable diagram_type: "
                "'flowchart' for processes/cycles (default), "
                "'sequence' for step-by-step interactions, "
                "'mindmap' for concept maps, "
                "'stateDiagram' for state/logic flows. "
                "Always use the diagram as a discovery aid — show the structure of a concept, not its answer."
            )
        )

        # Initialize Top-Level Google ADK Orchestrator Agent
        self.root_agent = Agent(
            name="hw_tutor_orchestrator",
            model="gemini-2.5-flash",
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
