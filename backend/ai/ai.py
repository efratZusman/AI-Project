# backend/ai/ai.py
import os
import json
os.environ["REQUESTS_CA_BUNDLE"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"
os.environ["SSL_CERT_FILE"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"
os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"

import logging
import google.generativeai as genai
from dotenv import load_dotenv

# -----------------------
# Logging
# -----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gemini")

# -----------------------
# Env / Config
# -----------------------
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

def get_model():
    if not API_KEY:
        return None

    genai.configure(api_key=API_KEY, transport="rest")
    return genai.GenerativeModel(MODEL_NAME)


def generate_structured_json(prompt: str, schema: dict) -> dict:
    try:
        model = get_model()
        if model is None:
            return {"error": "NO_API_KEY"}
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.35,
                "top_p": 0.9,
            },
            request_options={"timeout": 60},
        )

        raw_text = (response.text or "").strip()

        # 🔍 לוג גולמי – זה מה שיאיר לך את העיניים
        logger.warning("=== GEMINI RAW RESPONSE START ===")
        logger.warning(raw_text)
        logger.warning("=== GEMINI RAW RESPONSE END ===")

        if not raw_text:
            return {"error": "EMPTY_RESPONSE"}

        start = raw_text.find("{")
        end = raw_text.rfind("}")

        if start == -1 or end == -1:
            return {
                "error": "NO_JSON",
                "raw": raw_text,
            }

        json_text = raw_text[start:end + 1]
        return json.loads(json_text)

    except Exception as e:
        logger.exception("Gemini exception")
        return {
            "error": "AI_EXCEPTION",
            "message": str(e),
        }
