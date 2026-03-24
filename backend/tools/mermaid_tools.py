def display_mermaid_diagram(mermaid_code: str, title: str) -> dict:
    """
    Displays a Mermaid DSL diagram to the student.
    
    Args:
        mermaid_code: The raw Mermaid DSL string (e.g. 'graph TD\n  A-->B').
        title: A short, descriptive title for the diagram.
    """
    # This is a dummy tool. The orchestrator captures the call and its arguments.
    return {
        "mermaid": mermaid_code,
        "title": title
    }
