import uuid
import textwrap

def draw_science_flow(steps: list[str]) -> dict:
    """
    Draws a scientific process flow flowchart on the educational board.
    
    Args:
        steps: A list of short strings representing the consecutive sequence of events in the process.

    Returns:
        dict: The Excalidraw action command to upsert the diagram.
    """
    elements = []
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
                "x": rect_x + 200,
                "y": rect_y + 50,
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

    return {
        "action": "upsert",
        "elements": elements,
        "reason": "Generated science_flow diagram."
    }

def draw_math_equation_steps(steps: list[str]) -> dict:
    """
    Draws a vertical step-by-step unrolling of a mathematical equation on the board.
    
    Args:
        steps: A list of strings representing the algebraic solving process, e.g., ["2x + 5 = 15", "2x = 10", "x = 5"]

    Returns:
        dict: The Excalidraw action command to upsert the diagram.
    """
    elements = []
    for i, step in enumerate(steps):
        text_id = str(uuid.uuid4())
        y_pos = 100 + (i * 100)
        
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
        
        if i < len(steps) - 1:
            elements.append({
                "id": str(uuid.uuid4()),
                "type": "arrow",
                "x": 500,
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
        "reason": "Generated math_equation_steps diagram."
    }

def draw_math_number_line(start: int, end: int, highlight_points: list[int]) -> dict:
    """
    Draws a horizontal number line on the educational board.
    
    Args:
        start: The starting integer of the number line.
        end: The ending integer of the number line.
        highlight_points: A list of integers to visually emphasize on the line.

    Returns:
        dict: The Excalidraw action command to upsert the diagram.
    """
    elements = []
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
    
    # Add ticks (simplified logic)
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
        
    return {
        "action": "upsert",
        "elements": elements,
        "reason": "Generated math_number_line diagram."
    }
