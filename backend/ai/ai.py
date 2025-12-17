import os
import json
# NetFree certs
os.environ["REQUESTS_CA_BUNDLE"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"
os.environ["SSL_CERT_FILE"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"
os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"


def get_model():
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY missing")

    genai.configure(api_key=API_KEY, transport="rest")
    return genai.GenerativeModel(MODEL_NAME)


def generate_structured_json(prompt: str, schema: dict) -> dict:
    try:
        model = get_model()
        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": schema,
                "temperature": 0.4,
                "top_p": 0.8,
            },
            request_options={"timeout": 60},
        )

        return json.loads(response.text)

    except Exception as e:
        msg = str(e)

        if "429" in msg or "quota" in msg.lower():
            return {"error": "RATE_LIMIT"}

        return {"error": "AI_ERROR", "message": msg}
