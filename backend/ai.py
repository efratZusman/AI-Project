import google.generativeai as genai
import json
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import ssl
import certifi

os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = certifi.where()

load_dotenv() 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# פונקציית קריאה למודל
def analyze_email_with_ai(subject: str | None, body: str):
    prompt = f"""
אתה מנתח מיילים חכם. קח את הנושא והתוכן, ותחזיר ניתוח בפורמט JSON.
חובה להחזיר JSON תקין בלבד ללא טקסט מסביב.

הפורמט:
{{
  "summary": "סיכום קצר של המייל",
  "category": "finance / kids_school / health / study_work / urgent / general",
  "priority": "low / medium / high",
  "tasks": ["רשימת משימות שנגזרות מהטקסט"],
  "suggested_reply": "טיוטת תשובה מנומסת"
}}

כאן הנתונים:
Subject: {subject}
Body: {body}

תחזיר רק JSON תקין.
"""

    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(prompt)

    try:
        # ניסיון להמיר לפורמט JSON
        data = json.loads(response.text)
        return data
    except Exception:
        # טיפול במקרה שהמודל החזיר משהו לא חוקי
        return {
            "summary": "לא ניתן היה לנתח את המייל",
            "category": "general",
            "priority": "medium",
            "tasks": ["קריאה ידנית נדרשת"],
            "suggested_reply": "היי, קיבלתי את המייל. אבדוק ואחזור אליך."
        }
