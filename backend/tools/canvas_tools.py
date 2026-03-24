import uuid

def add_text_to_board(text: str, x: int, y: int) -> dict:
    """
    Writes raw text at a specific coordinate on the educational graphical board.
    
    Args:
        text: The string content to render.
        x: The absolute X coordinate.
        y: The absolute Y coordinate.

    Returns:
        dict: The Excalidraw action command to upsert the component.
    """
    text_id = str(uuid.uuid4())
    return {
        "action": "upsert",
        "elements": [{
            "id": text_id,
            "type": "text",
            "x": x,
            "y": y,
            "width": max(100, len(text) * 12),
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
            "text": text,
            "fontSize": 24,
            "fontFamily": 1,
            "textAlign": "center",
            "verticalAlign": "middle",
            "baseline": 22,
            "originalText": text,
            "lineHeight": 1.25
        }],
        "reason": f"Wrote text '{text}' to board."
    }

def clear_board() -> dict:
    """
    Wipes the educational board completely clean of all past drawings and elements.

    Returns:
        dict: The Excalidraw action command to clear the board.
    """
    # Excalidraw natively clears the board when receiving exactly this from updateScene
    return {
        "action": "upsert",
        "elements": [],
        "reason": "Cleared the entire board."
    }

def highlight_area(x: int, y: int) -> dict:
    """
    Draws a yellow translucent highlight box at specific coordinates to emphasize something on the board.
    
    Args:
        x: The absolute X coordinate to center the highlight.
        y: The absolute Y coordinate to center the highlight.

    Returns:
        dict: The Excalidraw action command to upsert the component.
    """
    highlight_element = {
        "id": str(uuid.uuid4()),
        "type": "rectangle",
        "x": x - 10,
        "y": y - 10,
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
        "reason": "Highlighting target for emphasis."
    }
