import random
from typing import Dict, Any, List

class ReinforcementAgent:
    """
    The Reinforcement Agent generates tailored practice problems to solidify learning.
    """
    
    def __init__(self):
        self.mastered_templates = [
            "ax + b = c",
            "x/a - b = c",
            "a(x + b) = c"
        ]

    def generate_practice_problems(self, mastered_concepts: List[str], count: int = 3) -> List[Dict[str, Any]]:
        """
        Mocks the generation of similar problems. 
        In production, Gemini generates these based on the student's specific struggle points.
        """
        problems = []
        for i in range(count):
            # Simulation of problem generation
            a = random.randint(2, 10)
            b = random.randint(1, 15)
            c = random.randint(20, 50)
            problems.append({
                "problem_type": "Algebraic Equation",
                "text": f"{a}x + {b} = {c}",
                "difficulty": "Moderate",
                "hint": f"Remember to isolate the x term first by {mastered_concepts[0] if mastered_concepts else 'subtracting'}"
            })
        return problems

if __name__ == "__main__":
    reinforcement = ReinforcementAgent()
    print("--- Testing Reinforcement Agent Practice Generation ---")
    problems = reinforcement.generate_practice_problems(["subtraction"], 2)
    for i, p in enumerate(problems):
        print(f"Problem {i+1}: {p['text']} (Hint: {p['hint']})")
