import os
import base64
from typing import Dict, Any
from google import genai
from google.genai import types


class VisionAgent:
    """
    The Vision Agent handles the 'See' part of the multimodal interaction.
    It extracts problem text and visual context from student snapshots using Gemini.
    """

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=api_key)
        # gemini-1.5-flash has much higher free-tier quotas than 2.0-flash
        self.model = "gemini-1.5-flash"
        self.last_extraction: Dict[str, Any] = {}

    def extract_problem_context(self, image_data: str) -> Dict[str, Any]:
        """
        Calls Gemini Vision to describe what is in the student's image.
        Returns structured dict with `text` (description), `topic`, and `detected_elements`.
        """
        try:
            image_bytes = base64.b64decode(image_data)

            prompt = (
                "You are analyzing a student's homework image. "
                "In 2-3 sentences, describe: (1) the subject/topic shown, "
                "(2) the key visual elements or problem you see, and "
                "(3) what kind of homework this appears to be. "
                "Be specific and accurate. Do not solve the problem — just describe what you see."
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt,
                ],
            )

            description = response.text.strip()

            # Extract a short topic label from the first sentence
            first_sentence = description.split(".")[0]
            topic = first_sentence[:80] if first_sentence else "Homework problem"

            extraction: Dict[str, Any] = {
                "text": description,
                "topic": topic,
                "detected_elements": ["image_analyzed"],
            }
            self.last_extraction = extraction
            return extraction

        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                print(f"[VisionAgent] Quota exhausted — try again shortly")
                return {
                    "text": "I can see you've shared an image, but I'm getting a lot of requests right now. Please describe the problem verbally!",
                    "topic": "Image shared",
                    "detected_elements": [],
                }
            print(f"[VisionAgent] Error analyzing image: {e}")
            return {
                "text": "A homework problem (image could not be analyzed in detail).",
                "topic": "Homework problem",
                "detected_elements": [],
            }

    def get_canvas_alignment(self) -> Dict[str, Any]:
        return {}
