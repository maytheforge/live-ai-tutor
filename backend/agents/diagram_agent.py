import json
import os
from enum import Enum
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

class DiagramType(Enum):
    GRAPH = "math_graph"
    NUMBER_LINE = "math_number_line"
    FRACTION = "math_fraction"
    GEOMETRY = "math_geometry"
    PROCESS_FLOW = "science_flow"
    CYCLE = "science_cycle"
    LABELED_DIAGRAM = "science_labeled"
    GRAMMAR_TREE = "english_tree"
    SENTENCE_STRUCTURE = "english_structure"
    MATH_EQUATION = "math_equation_steps"

class DiagramAgent:
    """
    The Diagram Agent produces semantic JSON instructions for educational visualizations.
    These are consumed by the Canvas Agent to be rendered on Excalidraw.
    """
    
    def __init__(self):
        try:
            self.client = genai.Client()
        except Exception as e:
            print(f"Warning: Could not initialize Gemini Client: {e}")
            self.client = None

    def generate_diagram_spec(self, diagram_type: DiagramType, context: str) -> Dict[str, Any]:
        """
        Generates a semantic specification for a diagram based on type and input data.
        """
        data = self._fetch_dynamic_data(diagram_type, context)
        
        spec: Dict[str, Any] = {
            "type": diagram_type.value,
            "data": data,
            "metadata": {
                "agent": "DiagramAgent",
                "version": "1.0",
                "dynamic": True
            }
        }
        
        # Example specific logic for Math Number Line
        if diagram_type == DiagramType.NUMBER_LINE:
            spec["elements"] = self._build_number_line(data)
        elif diagram_type == DiagramType.PROCESS_FLOW:
            spec["elements"] = self._build_process_flow(data)
        elif diagram_type == DiagramType.MATH_EQUATION:
            spec["elements"] = self._build_math_equation(data)
        elif diagram_type == DiagramType.GRAMMAR_TREE:
            spec["elements"] = self._build_grammar_tree(data)
            
        return spec

    def _fetch_dynamic_data(self, diagram_type: DiagramType, context: str) -> Dict[str, Any]:
        if not self.client:
            print("Gemini client not available. Falling back to mock data.")
            return self._fallback_mock_data(diagram_type)
            
        system_prompt = f"You are an expert educational content creator, visual architect and diagram designer API. Create a detailed Excalidraw JSON schema to visually explain the concept of type {diagram_type.name} to explain the following concept: '{context}'. "
        
        if diagram_type == DiagramType.PROCESS_FLOW:
            system_prompt += "Return a strictly valid JSON object with a single key 'steps' containing a list of strings representing the consecutive sequence of events. For example: {\"steps\": [\"Step 1\", \"Step 2\", \"Step 3\"]}."
        elif diagram_type == DiagramType.MATH_EQUATION:
            system_prompt += "Return a strictly valid JSON object with a single key 'steps' containing a list of strings representing the step-by-step algebraic solving process. Each string should contain the equation step and an explanation. For example: {\"steps\": [\"2x + 5 = 15 (Given)\", \"2x = 10 (Subtract 5)\", \"x = 5 (Divide by 2)\"]}."
        elif diagram_type == DiagramType.NUMBER_LINE:
            system_prompt += "Return a strictly valid JSON object with keys 'start' (integer), 'end' (integer), and 'highlight_points' (list of integers). For example: {\"start\": 0, \"end\": 10, \"highlight_points\": [2, 5]}."
        else:
            system_prompt += "Return a strictly valid JSON object with the data necessary to draw this diagram."
            
        try:
            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=system_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error fetching dynamic data from Gemini: {e}")
            return self._fallback_mock_data(diagram_type)

    def _fallback_mock_data(self, diagram_type: DiagramType) -> Dict[str, Any]:
        if diagram_type == DiagramType.PROCESS_FLOW:
            return {"steps": ["Phase 1 (Mock)", "Phase 2 (Mock)", "Phase 3 (Mock)"]}
        elif diagram_type == DiagramType.MATH_EQUATION:
            return {"steps": ["2x + 5 = 15 (Given)", "2x = 10 (Subtract 5)", "x = 5 (Divide by 2)"]}
        elif diagram_type == DiagramType.NUMBER_LINE:
            return {"start": 0, "end": 10, "highlight_points": [5]}
        return {}

    def _build_number_line(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        start = data.get("start", 0)
        end = data.get("end", 10)
        points = data.get("highlight_points", [])
        return [
            {"type": "axis", "from": start, "to": end},
            {"type": "ticks", "interval": 1},
            {"type": "highlights", "points": points}
        ]

    def _build_process_flow(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = data.get("steps", [])
        return [
            {"type": "nodes", "items": steps},
            {"type": "connectors", "style": "arrow"}
        ]

    def _build_math_equation(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = data.get("steps", [])
        return [
            {"type": "equation_steps", "items": steps}
        ]

    def _build_grammar_tree(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        sentence = data.get("sentence", "")
        parsed = data.get("structure", {})
        return [
            {"type": "text_base", "content": sentence},
            {"type": "tree_nodes", "data": parsed}
        ]

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = DiagramAgent()
    
    print("--- Math: Number Line Spec ---")
    math_spec = agent.generate_diagram_spec(
        DiagramType.NUMBER_LINE, 
        "Show a number line pointing to negative numbers like -5 and -2."
    )
    print(json.dumps(math_spec, indent=2))
    
    print("\n--- Science: Process Flow Spec ---")
    science_spec = agent.generate_diagram_spec(
        DiagramType.PROCESS_FLOW, 
        "The Water Cycle"
    )
    print(json.dumps(science_spec, indent=2))
