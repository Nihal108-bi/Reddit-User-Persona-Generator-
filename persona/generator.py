
import os
import logging
from typing import List, Dict
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PersonaGenerator:
    """
    Uses a generative AI model to create a user persona based on Reddit activity.
    """

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Google API key is missing. Please set it in the .env file.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-pro')
        logging.info("✅ PersonaGenerator initialized with gemini-2.5-Pro.")

    def generate(self, username: str, activity: List[Dict[str, str]]) -> str:
        activity_str = "\n".join([f"- {item['type']}: {item['content']}" for item in activity])
        
        
        prompt = f"""
        Analyze the following Reddit activity for the user "{username}" to create a detailed user persona.
        Format the output exactly as specified below.

        ---
        **Reddit Activity for u/{username}:**
        {activity_str}
        ---

        **Required Output Format:**

        "A concise, one-sentence summary of the user's core identity, written in quotes."

        BASIC INFORMATION
        -----------------
        - Age: (Estimate, e.g., 25-35)
        - Gender: (Estimate if possible, otherwise "Not specified")
        - Location: (Estimate if possible, otherwise "Not specified")
        - Occupation/Field: (Estimate based on comments, otherwise "Not specified")
        - Tech Savviness: (e.g., High, Medium, Low)

        MOTIVATIONS
        -----------
        - Convenience: (Score from 0-100)
        - Wellness: (Score from 0-100)
        - Speed: (Score from 0-100)
        - Comfort: (Score from 0-100)
        - Dietary Needs: (Score from 0-100)

        PERSONALITY (Myers-Briggs Style Scoring)
        ----------------------------------------
        - Introvert/Extrovert: (Score from 0-100, where 0 is Introvert, 100 is Extrovert)
        - Intuition/Sensing: (Score from 0-100, where 0 is Intuitive, 100 is Sensing)
        - Feeling/Thinking: (Score from 0-100, where 0 is Feeling, 100 is Thinking)
        - Perceiving/Judging: (Score from 0-100, where 0 is Perceiving, 100 is Judging)

        BEHAVIOUR & HABITS
        ------------------
        - **Bold Title Without Colon**
          Description text on a new line.
        - **Another Bold Title**
          Another description on a new line.

        FRUSTRATIONS
        ------------
        - **Bold Title Without Colon**
          Description text on a new line.

        GOALS & NEEDS
        -------------
        - **Bold Title Without Colon**
          Description text on a new line.

        CITED SOURCES
        -------------
        (This section will be populated by the application later, do not add anything here.)
        """

        try:
            logging.info(f"Sending request to Gemini for user u/{username}...")
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logging.error(f"❌ An error occurred while generating the persona: {e}")
            return "Error: Could not generate the persona."