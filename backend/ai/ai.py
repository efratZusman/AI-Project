# backend/ai/ai.py

import os
import json

# הגדרות תעודות ל-NetFree (כמו שהיה לך)
os.environ["REQUESTS_CA_BUNDLE"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"
os.environ["SSL_CERT_FILE"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"
os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"


def get_model():
    """
    מחזיר אובייקט מודל מוכן לשימוש.
    אם יש בעיה במפתח – זורק Exception (שנתפוס בקוד שקורא).
    """
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY לא מוגדר בקובץ .env")

    genai.configure(
        api_key=API_KEY,
        transport="rest",
    )
    return genai.GenerativeModel(MODEL_NAME)


def generate_structured_json(prompt: str, schema: dict) -> dict:
    """
    פונקציית עזר כללית:
    מקבלת פרומפט + סכמת JSON,
    קוראת למודל ומחזירה dict מוכן לשימוש.
    במקרה של תקלה – מחזירה מבנה שגיאה בסיסי.
    """
    try:
        model = get_model()
        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": schema,
                "temperature": 0.4,
                "top_p": 0.8,
                "top_k": 40,
            },
            request_options={"timeout": 60},
        )
        print("Gemini response received successfully")

        return json.loads(response.text)

    except Exception as e:
        print("AI ERROR:", e)
        # חשוב: נחזיר שדות בסיסיים כדי שהפרונט לא יישבר
        return {
            "error": "AI_ERROR",
            "message": str(e),
        }
