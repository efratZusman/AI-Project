import os
os.environ["REQUESTS_CA_BUNDLE"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"
os.environ["SSL_CERT_FILE"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"
os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"

import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(
#     api_key=API_KEY,
#     transport="rest" 
# )

MODEL_NAME = "gemini-2.5-flash"

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "category": {"type": "string"},
        "priority": {"type": "string"},
        "tone": {"type": "string"},
        "emotions": {"type": "array", "items": {"type": "string"}},
        "intent": {"type": "string"},
        "tasks": {"type": "array", "items": {"type": "string"}},
        "deadline": {"type": "string"},
        "missing_information": {"type": "array", "items": {"type": "string"}},
        "risk_level": {"type": "string"},
        "suggested_reply": {"type": "string"}
    },
    "required": [
        "summary",
        "category",
        "priority",
        "tone",
        "emotions",
        "intent",
        "tasks",
        "suggested_reply"
    ]
}

def analyze_email_with_ai(subject: str, body: str):
    prompt = f"""
    אתה מודול ניתוח מיילים מתקדם מסוג Enterprise.
    עליך לבצע ניתוח עמוק ורב־שכבתי לפי כללים מחמירים. 
    אסור לך להחזיר שום דבר שאיננו JSON תקין לפי הסכמה שסופקה.

    ==============================
    ### כללי יסוד (חייבים להתקיים)
    1. אל תוסיף טקסט לפני או אחרי ה‑JSON.
    2. אל תוסיף הערות, הסברים או טקסט חופשי.
    3. אם המייל לא ברור — עליך להסיק מסקנות מושכלות, לא להחזיר ערכים ריקים.
    4. כל משימה חייבת להיות אקטיבית וברורה (SMART).
    5. עליך להשתמש בעברית תקינה בלבד.

    ==============================
    ### חמשת שלבי העומק (Strict Reasoning Layers)
    אתה מחויב לעבור דרך כל השכבות הפנימיות האלו —  
    אך לא להציג אותן בתשובה, אלא להשתמש בהן כדי לייצר JSON איכותי:

    #### שכבה 1 — Logical Decomposition (P1)
    • נתח את המבנה הלוגי של המייל.  
    • מה מבוקש? האם יש רמזים סמויים? האם יש ניגוד בין הנושא לתוכן?

    #### שכבה 2 — Emotional & Tone Analysis (P2)
    • זהה טון רגשי עיקרי + משני.  
    • זהה רמזים ללחץ, כעס, בלבול, דחיפות, חוסר שביעות רצון.  
    • הפק רשימת רגשות.

    #### שכבה 3 — Intent Extraction (P3)
    • מה המטרה המפורשת של השולח?  
    • מה המטרה המרומזת?  
    • אם יש מספר מטרות — בחר מרכזית אחת והגדר אותה.

    #### שכבה 4 — Task Derivation (P4)
    • גזור משימות אקטיביות.  
    • משימות נסתרות — חובה לזהות.  
    • כל משימה בפורמט פעולה (פועל ראשון):  
    למשל: "לשלוח עדכון", "לבדוק מסמך", "לקבוע פגישה".

    #### שכבה 5 — Risk & Priority Modeling (P5)
    • הערכת סיכונים לפי תוכן המייל.  
    • הגב רמת עדיפות לפי דחיפות אמיתית, לא לפי ניסוח בלבד.  
    • אם ניתן להסיק דדליין — ציין אותו.

    ==============================
    ### הפלט הסופי (מותר להחזיר רק את ה‑JSON):
    המייל לניתוח:
    נושא: {subject}
    תוכן:
    {body}

    החזר JSON תקין לפי הסכמה:
    {json.dumps(ANALYSIS_SCHEMA, ensure_ascii=False)}

    אסור להחזיר שום מידע נוסף מעבר ל‑JSON.
    """


    try:
        genai.configure(
            api_key=API_KEY,
            transport="rest" 
        )
        model = genai.GenerativeModel(MODEL_NAME)

        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": ANALYSIS_SCHEMA,
                "temperature": 0.4,   # יותר יציב, פחות הזיות
                "top_p": 0.8,
                "top_k": 40,
            },
            request_options={"timeout": 30}
        )

        print("RAW AI RESPONSE:", response)
        return json.loads(response.text)

    except Exception as e:
        print("AI ERROR:", e)
        return {
            "summary": "שגיאה בניתוח המייל",
            "category": "technical_error",
            "priority": "medium",
            "tone": "neutral",
            "emotions": [],
            "intent": "unknown",
            "tasks": [],
            "deadline": "",
            "missing_information": [],
            "risk_level": "low",
            "suggested_reply": "לא ניתן לנתח את המייל עקב תקלה טכנית."
        }
