import os
import json
import logging
from typing import Optional

# NetFree certs (כמו אצלכן)
os.environ["REQUESTS_CA_BUNDLE"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"
os.environ["SSL_CERT_FILE"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"
os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(dotenv_path="C:/Users/This User/Desktop/AI_Project/backend/.env")

logger = logging.getLogger("gemini")
# שימי לב: אפשר לשלוט ברמת הלוג דרך uvicorn --log-level / או logging.basicConfig בפרויקט

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

_model = None

def _get_model() -> Optional[object]:
    global _model
    if _model is not None:
        return _model

    if not API_KEY:
        return None

    genai.configure(api_key=API_KEY, transport="rest")
    _model = genai.GenerativeModel(MODEL_NAME)
    return _model

def _extract_json(raw_text: str) -> dict:
    raw_text = (raw_text or "").strip()
    if not raw_text:
        return {"error": "EMPTY_RESPONSE"}

    # ניסיון 1: JSON נקי
    try:
        return json.loads(raw_text)
    except Exception:
        pass

    # ניסיון 2: חילוץ “הבלוק” הראשון
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {"error": "NO_JSON", "raw": raw_text[:1500]}

    json_text = raw_text[start:end + 1]
    try:
        return json.loads(json_text)
    except Exception:
        return {"error": "JSON_PARSE_FAILED", "raw": raw_text[:1500]}

def generate_structured_json(prompt: str, schema: dict) -> dict:
    """
    מחזירה:
      - dict תקין לפי schema, או
      - {"error": "<CODE>", "message": "...", "raw": "..."} במקרי כשל
    """
    model = _get_model()
    if model is None:
        return {"error": "NO_API_KEY", "message": "GEMINI_API_KEY missing or not loaded"}

    try:
        # ניסיון עדין (2 נסיונות) כדי להקטין “לא JSON”
        for attempt in (1, 2):
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.25 if attempt == 1 else 0.10,
                    "top_p": 0.9,
                },
                request_options={"timeout": 60},
            )

            raw_text = (getattr(response, "text", "") or "").strip()

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Gemini raw response (attempt %s): %s", attempt, raw_text)

            parsed = _extract_json(raw_text)

            # הצליח
            if not parsed.get("error"):
                return parsed

            # אם זה לא JSON – ננסה שוב פעם אחת
            if parsed.get("error") in ("NO_JSON", "JSON_PARSE_FAILED", "EMPTY_RESPONSE") and attempt == 1:
                continue

            return parsed

        return {"error": "UNKNOWN", "message": "Unexpected loop end"}

    except Exception as e:
        logger.exception("Gemini exception")
        return {"error": "AI_EXCEPTION", "message": str(e)}
