import json
from enum import Enum
from typing import Dict, Any

class GradeLevel(Enum):
    SOPHIE = "K-2"
    LEO = "3-5"
    MAYA = "6-8"
    SAM = "9-12"

class TutorAgent:
    """
    The Socratic Tutor Agent responsible for pedagogical reasoning.
    It guides students through problems without giving direct answers.
    """
    
    PERSONAS = {
        GradeLevel.SOPHIE: {
            "name": "Sophie Helper",
            "style": "playful, encouraging, simple 3-5 word sentences",
            "technique": "Narrative scaffolding (using stories/animals)",
            "system_prompt": "You are Sophie's playful helper. Use emojis and simple metaphors. Always ask 'What do you see?' or 'Can you count these?'"
        },
        GradeLevel.LEO: {
            "name": "Coach Leo",
            "style": "supportive, visual-focused, clear instructions",
            "technique": "Visual prompting (referencing shapes/colors)",
            "system_prompt": "You are Coach Leo. Help the student by pointing out patterns. Ask 'What do you notice about this part?'"
        },
        GradeLevel.MAYA: {
            "name": "Mentor Maya",
            "style": "logical, structured, step-oriented",
            "technique": "Step-by-step discovery",
            "system_prompt": "You are Mentor Maya. Guide the student through the logical sequence. Ask 'What would be the next logical step?'"
        },
        GradeLevel.SAM: {
            "name": "Strategist Sam",
            "style": "analytical, challenging, high-level",
            "technique": "First principles reasoning",
            "system_prompt": "You are Strategist Sam. Challenge the student's assumptions. Ask 'Why does this theorem apply here?'"
        }
    }

    def __init__(self, grade_level: GradeLevel = GradeLevel.LEO):
        self.grade_level = grade_level
        self.persona = self.PERSONAS[grade_level]
        self.session_state = {"steps_completed": 0, "hints_given": 0}

    def get_socratic_prompt(self, student_input: str, current_context: str) -> str:
        """
        Generates a Socratic response based on student input and persona.
        """
        # In a real implementation, this would call Gemini with the system_prompt
        # For the POC foundation, we define the logic flow
        prompt = f"""
        [SYSTEM]: {self.persona['system_prompt']}
        [TECHNIQUE]: {self.persona['technique']}
        [CONTEXT]: {current_context}
        [STUDENT]: {student_input}
        [ADVICE]: Do NOT give the answer. Provide a small nudge or ask a leading question.
        """
        return prompt

    def generate_intent(self, feedback: str) -> Dict[str, Any]:
        """
        Generates a high-level intent for the Canvas Agent.
        """
        # Example of determining a visual action based on text feedback
        if "highlight" in feedback.lower() or "notice" in feedback.lower():
            return {"command": "HIGHLIGHT", "parameters": {"target": "focus_area"}}
        return {"command": "IDLE"}

if __name__ == "__main__":
    # Test session for Leo (3-5)
    tutor = TutorAgent(GradeLevel.LEO)
    print(f"--- Initializing {tutor.persona['name']} for Grade {tutor.grade_level.value} ---")
    
    test_input = "I don't know what to do with the +5 in 3x + 5 = 20"
    context = "Algebra basics: Solving for x"
    
    response_prompt = tutor.get_socratic_prompt(test_input, context)
    print(response_prompt)
    
    visual_intent = tutor.generate_intent("Look at the +5, what is the opposite of adding?")
    print(f"Canvas Intent: {visual_intent}")
