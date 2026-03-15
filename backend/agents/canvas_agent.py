import json
import uuid
import textwrap
from typing import Dict, Any, List

class CanvasAgent:
    """
    The Canvas Agent translates pedagogical intents into visual actions on Excalidraw.
    """
    
    def __init__(self):
        self.current_scene_elements = []

    def generate_excalidraw_action(self, intent: Dict[str, Any], spatial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translates a Tutor Agent intent or Diagram Spec into a low-level Excalidraw update.
        """
        # Handle Structured Diagrams
        intent_type = intent.get("type")
        if intent_type and isinstance(intent_type, str) and intent_type.startswith(("math_", "science_", "english_")):
            return self.handle_diagram(intent)

        command = intent.get("command")
        params = intent.get("parameters", {})
        # ... (rest of old logic)
        if command == "HIGHLIGHT":
            target = params.get("target")
            coords = spatial_context.get(target, {"x": 100, "y": 100})
            
            highlight_element = {
                "id": str(uuid.uuid4()),
                "type": "rectangle",
                "x": coords["x"] - 10,
                "y": coords["y"] - 10,
                "width": 50,
                "height": 50,
                "angle": 0,
                "strokeColor": "#FFD700",
                "backgroundColor": "rgba(255, 215, 0, 0.2)",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "strokeStyle": "solid",
                "roughness": 1,
                "opacity": 100,
                "groupIds": [],
                "strokeSharpness": "sharp",
                "boundElements": [],
                "isDeleted": False,
                "version": 1,
                "versionNonce": 12345,
            }
            return {
                "action": "upsert",
                "elements": [highlight_element],
                "reason": f"Highlighting {target} for emphasis."
            }
            
        return {"action": "noop"}

    def handle_diagram(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts semantic diagram specs into Excalidraw elements.
        """
        diag_type = spec.get("type")
        elements = []
        
        if diag_type == "math_number_line":
            # Simplified number line: a main horizontal line and small vertical ticks
            base_y = 300
            start_x = 100
            length = 400
            elements.append({
                "id": str(uuid.uuid4()),
                "type": "line",
                "x": start_x,
                "y": base_y,
                "width": length,
                "height": 0,
                "angle": 0,
                "strokeColor": "#000000",
                "backgroundColor": "transparent",
                "fillStyle": "hachure",
                "strokeWidth": 2,
                "strokeStyle": "solid",
                "roughness": 1,
                "opacity": 100,
                "groupIds": [],
                "strokeSharpness": "round",
                "boundElements": [],
                "points": [[0,0], [length, 0]],
                "isDeleted": False,
                "version": 1,
                "versionNonce": 12345,
            })
            # Add ticks
            for i in range(11):
                tick_x = start_x + (i * (length // 10))
                elements.append({
                    "id": str(uuid.uuid4()),
                    "type": "line",
                    "x": tick_x,
                    "y": base_y - 5,
                    "width": 0,
                    "height": 10,
                    "angle": 0,
                    "strokeColor": "#000000",
                    "backgroundColor": "transparent",
                    "fillStyle": "hachure",
                    "strokeWidth": 2,
                    "strokeStyle": "solid",
                    "roughness": 1,
                    "opacity": 100,
                    "groupIds": [],
                    "strokeSharpness": "round",
                    "boundElements": [],
                    "points": [[0,0], [0, 10]],
                    "isDeleted": False,
                    "version": 1,
                    "versionNonce": 12345,
                })
        
        elif diag_type == "science_flow":
            # Simplified flow: boxes with text
            steps = spec.get("data", {}).get("steps", [])
            for i, step in enumerate(steps):
                rect_id = str(uuid.uuid4())
                text_id = str(uuid.uuid4())
                rect_x = 100 + (i * 250)
                rect_y = 200
                
                # Rectangle
                elements.append({
                    "id": rect_id,
                    "type": "rectangle",
                    "x": rect_x,
                    "y": rect_y,
                    "width": 200,
                    "height": 100,
                    "angle": 0,
                    "strokeColor": "#000000",
                    "backgroundColor": "#e7f3ff",
                    "fillStyle": "solid",
                    "strokeWidth": 2,
                    "strokeStyle": "solid",
                    "roughness": 1,
                    "opacity": 100,
                    "groupIds": [],
                    "strokeSharpness": "round",
                    "boundElements": [],
                    "isDeleted": False,
                    "version": 1,
                    "versionNonce": 12345,
                })
                
                # Text inside
                elements.append({
                    "id": text_id,
                    "type": "text",
                    "x": rect_x + 10,
                    "y": rect_y + 10,
                    "width": 180,
                    "height": 80,
                    "angle": 0,
                    "strokeColor": "#000000",
                    "backgroundColor": "transparent",
                    "fillStyle": "hachure",
                    "strokeWidth": 1,
                    "strokeStyle": "solid",
                    "roughness": 1,
                    "opacity": 100,
                    "groupIds": [],
                    "strokeSharpness": "sharp",
                    "isDeleted": False,
                    "version": 1,
                    "versionNonce": 12345,
                    "text": "\n".join(textwrap.wrap(step, width=22)),
                    "fontSize": 16,
                    "fontFamily": 1,
                    "textAlign": "center",
                    "verticalAlign": "middle",
                    "baseline": 18,
                    "originalText": step,
                    "lineHeight": 1.25
                })
                
                # Draw connector arrow to the next box (if not last)
                if i < len(steps) - 1:
                    elements.append({
                        "id": str(uuid.uuid4()),
                        "type": "arrow",
                        "x": rect_x + 200, # end of this rect
                        "y": rect_y + 50, # middle height
                        "width": 50,
                        "height": 0,
                        "angle": 0,
                        "strokeColor": "#000000",
                        "backgroundColor": "transparent",
                        "fillStyle": "solid",
                        "strokeWidth": 2,
                        "strokeStyle": "solid",
                        "roughness": 1,
                        "opacity": 100,
                        "groupIds": [],
                        "strokeSharpness": "round",
                        "points": [[0,0], [50, 0]],
                        "isDeleted": False,
                        "version": 1,
                        "versionNonce": 12345,
                    })

        elif diag_type == "math_equation_steps":
            # Vertical step-by-step equation list
            steps = spec.get("data", {}).get("steps", [])
            for i, step in enumerate(steps):
                text_id = str(uuid.uuid4())
                y_pos = 100 + (i * 100)
                
                # Naked text for equation
                elements.append({
                    "id": text_id,
                    "type": "text",
                    "x": 300,
                    "y": y_pos,
                    "width": 400,
                    "height": 40,
                    "angle": 0,
                    "strokeColor": "#000000",
                    "backgroundColor": "transparent",
                    "fillStyle": "hachure",
                    "strokeWidth": 1,
                    "strokeStyle": "solid",
                    "roughness": 1,
                    "opacity": 100,
                    "groupIds": [],
                    "strokeSharpness": "sharp",
                    "isDeleted": False,
                    "version": 1,
                    "versionNonce": 12345,
                    "text": step,
                    "fontSize": 24,
                    "fontFamily": 1,
                    "textAlign": "center",
                    "verticalAlign": "middle",
                    "baseline": 22,
                    "originalText": step,
                    "lineHeight": 1.25
                })
                
                # Draw vertical connector arrow to the next step (if not last)
                if i < len(steps) - 1:
                    elements.append({
                        "id": str(uuid.uuid4()),
                        "type": "arrow",
                        "x": 500, # middle of text width
                        "y": y_pos + 40, 
                        "width": 0,
                        "height": 40,
                        "angle": 0,
                        "strokeColor": "#aaaaaa",
                        "backgroundColor": "transparent",
                        "fillStyle": "solid",
                        "strokeWidth": 2,
                        "strokeStyle": "dashed",
                        "roughness": 1,
                        "opacity": 100,
                        "groupIds": [],
                        "strokeSharpness": "round",
                        "points": [[0,0], [0, 40]],
                        "isDeleted": False,
                        "version": 1,
                        "versionNonce": 12345,
                    })

        return {
            "action": "upsert",
            "elements": elements,
            "reason": f"Generated {diag_type} diagram."
        }


if __name__ == "__main__":
    canvas = CanvasAgent()
    print("--- Testing Canvas Agent command generation ---")
    
    # Mock data from Tutor and Vision agents
    mock_intent = {"command": "HIGHLIGHT", "parameters": {"target": "constant_5"}}
    mock_spatial = {"constant_5": {"x": 180, "y": 250}}
    
    action = canvas.generate_excalidraw_action(mock_intent, mock_spatial)
    print(f"Generated Excalidraw Action: {json.dumps(action, indent=2)}")
