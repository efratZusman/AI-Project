import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "category": {"type": "string"},
        "priority": {"type": "string"},
        "tasks": {
            "type": "array",
            "items": {"type": "string"}
        },
        "suggested_reply": {"type": "string"}
    },
    "required": ["summary", "category", "priority", "tasks", "suggested_reply"]
}


def analyze_email_with_ai(subject: str, body: str):
    prompt = f"""
    נתח את המייל הבא:
    נושא: {subject}
    תוכן: {body}

    החזר JSON בלבד בהתאם לסכמה.
    """

    try:
        model = genai.GenerativeModel(MODEL_NAME)

        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": ANALYSIS_SCHEMA
            }
        )

        return json.loads(response.text)

    except Exception as e:
        print("AI ERROR:", e)
        return {
            "summary": "שגיאה בניתוח המייל",
            "category": "technical_error",
            "priority": "medium",
            "tasks": ["AI error occurred"],
            "suggested_reply": "הייתה תקלה בעיבוד המייל."
        }
