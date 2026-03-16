import os
from typing import Optional
from google import genai
from google.genai import types

# Initialise once at module level
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    return _client


MERMAID_SYSTEM = """You are an expert educational diagram designer.
Your only job is to produce a valid Mermaid DSL diagram string.
Rules:
- Output ONLY the raw Mermaid code — no markdown fences, no explanation, no preamble.
- Make the diagram educational and appropriate for a student.
- Keep labels short (under 40 chars each).
- Use clean, readable layout directions (TD for flowcharts, LR for timelines).
- Do NOT include any colors, styles, or theme overrides unless essential.
"""


def generate_mermaid_diagram(topic: str, diagram_type: str = "flowchart") -> dict:
    """
    Generates a Mermaid DSL diagram to visually explain an educational topic.

    Args:
        topic: The educational topic or concept to visualise (e.g. 'Water Cycle', 'Photosynthesis').
        diagram_type: One of 'flowchart', 'sequence', 'mindmap', 'stateDiagram'.
                      Defaults to 'flowchart' which suits most science/process topics.

    Returns:
        dict: Contains 'mermaid' (the DSL string) and 'title' (a short display title).
    """
    type_hints = {
        "flowchart":    "Use `graph TD` with labeled nodes and arrows to show process steps.",
        "sequence":     "Use `sequenceDiagram` to show interactions between actors/components step by step.",
        "mindmap":      "Use `mindmap` to show the central concept and its sub-topics.",
        "stateDiagram": "Use `stateDiagram-v2` to show states and transitions.",
    }

    hint = type_hints.get(diagram_type, type_hints["flowchart"])

    user_prompt = (
        f"Create a {diagram_type} diagram that clearly explains: '{topic}'.\n"
        f"Diagram style guidance: {hint}\n"
        "Output only the raw Mermaid code."
    )

    try:
        client = _get_client()
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=MERMAID_SYSTEM,
                temperature=0.3,
            ),
        )

        mermaid_code = response.text.strip()

        # Strip accidental markdown fences if model included them
        if mermaid_code.startswith("```"):
            lines = mermaid_code.splitlines()
            mermaid_code = "\n".join(
                line for line in lines
                if not line.startswith("```")
            ).strip()

        return {
            "mermaid": mermaid_code,
            "title": topic,
        }

    except Exception as e:
        print(f"[MermaidTool] Error generating diagram: {e}")
        # Minimal fallback so the frontend still receives something renderable
        return {
            "mermaid": f'graph TD\n    A["{topic}"]\n    A --> B["Could not generate diagram\\nPlease try again"]',
            "title": topic,
        }
