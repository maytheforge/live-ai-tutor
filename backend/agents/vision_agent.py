import os
import base64
from typing import Dict, Any
import google.generativeai as genai


class VisionAgent:
    """
    The Vision Agent handles the 'See' part of the multimodal interaction.
    It extracts problem text and visual context from student snapshots using Gemini.
    """

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.last_extraction = {}

    def extract_problem_context(self, image_data: str) -> Dict[str, Any]:
        """
        Calls Gemini Vision to describe what is in the student's image.
        Returns structured dict with `text` (description), `topic`, and `detected_elements`.
        """
        try:
            # Decode base64 → bytes
            image_bytes = base64.b64decode(image_data)

            prompt = (
                "You are analyzing a student's homework image. "
                "In 2-3 sentences, describe: (1) the subject/topic shown, "
                "(2) the key visual elements or problem you see, and "
                "(3) what kind of homework this appears to be. "
                "Be specific and accurate. Do not solve the problem — just describe what you see."
            )

            response = self.model.generate_content([
                {"mime_type": "image/jpeg", "data": image_bytes},
                prompt
            ])

            description = response.text.strip()

            # Extract a short topic label from the first sentence
            first_sentence = description.split(".")[0]
            topic = first_sentence[:80] if first_sentence else "Homework problem"

            extraction = {
                "text": description,
                "topic": topic,
                "detected_elements": ["image_analyzed"],
            }
            self.last_extraction = extraction
            return extraction

        except Exception as e:
            print(f"[VisionAgent] Error analyzing image: {e}")
            # Graceful fallback — don't block the orchestrator
            return {
                "text": "A homework problem (image could not be analyzed in detail).",
                "topic": "Homework problem",
                "detected_elements": [],
            }

    def get_canvas_alignment(self) -> Dict[str, Any]:
        return self.last_extraction.get("detected_elements", {})
