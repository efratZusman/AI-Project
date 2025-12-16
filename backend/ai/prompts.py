# backend/ai/prompts.py

import json
from typing import List, Optional
from backend.models import ThreadMessage

# ====== BEFORE YOU SEND ======

BEFORE_SEND_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string"},
        "risk_level": {"type": "string"},
        "risk_factors": {"type": "array", "items": {"type": "string"}},
        "recipient_interpretation": {"type": "string"},
        "send_decision": {"type": "string"},
        "follow_up_needed": {"type": "boolean"},
        "follow_up_reason": {"type": "string"},
        "safer_subject": {"type": "string"},
        "safer_body": {"type": "string"},
        "notes_for_sender": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "intent",
        "risk_level",
        "risk_factors",
        "recipient_interpretation",
        "send_decision",
        "follow_up_needed",
        "safer_body",
    ],
}


def render_thread(thread: Optional[List[ThreadMessage]]) -> str:
    if not thread:
        return ""

    out = "### Conversation Thread (Newest first):\n\n"
    for msg in reversed(thread):  # newest first
        who = "Sender" if msg.author == "me" else "Recipient"
        out += f"{who} said:\n{msg.text.strip()}\n\n"

    return out

def build_before_send_prompt(
    body: str,
    subject: Optional[str] = None,
    language: str = "auto",
    is_reply: bool = False,
    thread_context: Optional[List[ThreadMessage]] = None
) -> str:

    # זיהוי אוטומטי של שפה (עברית → עונה בעברית)
    is_hebrew = any("\u0590" <= ch <= "\u05EA" for ch in body)
    reply_language = "עברית" if language == "he" or is_hebrew else "English"

    thread_block = render_thread(thread_context) if is_reply else ""

    prompt = f"""
אתה מערכת Advanced Communication Safety Engine — מנוע ניתוח תקשורת מקצועי.

🟦 חשוב מאוד:  
עליך להחזיר את **כל התוכן בתוך ה‑JSON בלבד** ובשפה: **{reply_language}**.  
כל השדות, כל הטקסטים, כל ההסברים — אך ורק בשפה זו.  
אין לחרוג מהסכמה ואין להוסיף מלל חופשי מחוץ ל‑JSON.

============================================================
## 0. הקשר וניתוח שירשור (אם קיים)
אם קיים שירשור, עליך:
- לזהות מתחים, אי‑הבנות, תסכול, פערי ציפיות
- להבין את מצב הרוח של הצד השני
- לזהות האם התשובה הנוכחית עשויה להחמיר מצב

{thread_block}

============================================================
## 1. Intent Analysis — מה השולח מנסה להשיג?
דוגמאות לכוונות:
- בקשה לקבל מידע / קבלת אישור / העברת מסר
- תזכורת עדינה / ניסיון לתקן אי‑הבנה / הצבת גבולות
- הבאת תסכול או אכזבה
יש לנסח זאת בצורה ברורה ולא כללית.

============================================================
## 2. Risk Assessment — ניתוח סיכונים אמיתי (לא גנרי!)
עליך לזהות לפחות 2–5 סיכונים אם קיימים:
- טון שעלול להישמע תוקפני / פסיבי‑אגרסיבי / לוחץ
- עמימות שעלולה לגרום לפרשנות שלילית
- חוסר הקשר (context gaps)
- נקודות שעלולות להצטייר כלא מקצועיות
- פער בין כוונת השולח למה שהנמען עשוי לפרש

הסברים חייבים להיות קונקרטיים, לא משפטים כלליים.

============================================================
## 3. Recipient Simulation — איך הנמען יפרש זאת?
עליך לסמלץ תגובה אנושית:
- האם הוא עשוי להרגיש מותקף?
- האם זה עלול להישמע דרשני מדי?
- האם זה עלול לייצר ריחוק או בלבול?
להציג פרשנות אמיתית — לא גנרית.

============================================================
## 4. Decision Modeling — החלטה אופרטיבית
יש לבחור אחת:
- send_as_is — אפשר לשלוח כפי שזה
- edit_before_send — דרוש תיקון
- do_not_send — לא מומלץ לשלוח

ההחלטה חייבת להיות מנומקת בהתבסס על הניתוח.

אם נדרש follow‑up → להסביר למה.

============================================================
## 5. Safer Rewrite — ניסוח בטוח, מקצועי ומדויק
יש לספק ניסוח אלטרנטיבי:
- ברור, מנומס, מאוזן
- משמר את הכוונה המקורית
- מתאים להקשר שנלמד מהשירשור
- ללא שיפוטיות
- ללא ניסוחים בוטים

הניסוח חייב להיות בשפה {reply_language} בלבד.

============================================================

Email subject:
{subject or "No subject"}

Email body:
\"\"\"{body}\"\"\"

החזר אך ורק JSON תקין לפי הסכמה הבאה:
{json.dumps(BEFORE_SEND_SCHEMA, ensure_ascii=False)}
"""
    return prompt



# ====== FOLLOW-UP GUARDIAN ======

FOLLOW_UP_SCHEMA = {
    "type": "object",
    "properties": {
        "needs_follow_up": {"type": "boolean"},
        "follow_up_reason": {"type": "string"},
        "urgency": {"type": "string"},  # low / medium / high
        "suggested_follow_up": {"type": "string"},
        "channel": {"type": "string"},  # email / phone / chat / none
        "tone_recommendation": {"type": "string"},
        "notes_for_sender": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "needs_follow_up",
        "urgency",
        "suggested_follow_up",
    ],
}

def build_follow_up_prompt(email_body: str, days_passed: int, language: str = "auto") -> str:
    """
    פרומפט מתקדם לבדיקת Follow-Up + ניסוח מקצועי מותאם‑מצב.
    """

    # זיהוי שפה אוטומטי — אם יש עברית בגוף המייל → תשובה בעברית
    reply_language = "עברית" if language == "he" or any("\u0590" <= ch <= "\u05EA" for ch in email_body) else "English"

    prompt = f"""
You are the module **Follow-Up Guardian**.
Your task: determine **whether a follow‑up is needed**, why, how urgent it is, and write a **professionally phrased follow‑up message**.

⚠️ IMPORTANT:
You must return the JSON **only in: {reply_language}**.
All explanations, fields and generated texts must be in this language.

============================================================
### Step 1 — Expectation Analysis
Evaluate whether a reply is normally expected in such a situation:
- Is this a request?
- Is there a deliverable?
- Is the sender waiting for approval / clarification?
- Is the message likely to have been overlooked?

### Step 2 — Risk of Not Following Up
Consider risks such as:
- delays in workflow
- missed opportunity
- harm to professional relationship
- miscommunication
- appearing unprofessional or passive

### Step 3 — Action Decision
Decide:
- Is follow‑up needed?
- What is the urgency level? (low / medium / high)
- What is the justification?

### Step 4 — Follow‑Up Message Draft
Generate a **short, polite, non‑pressuring** follow‑up message:
- friendly tone
- invites a response
- avoids guilt-tripping
- clearly references the original message

============================================================
### Input Data:
Days since original email: {days_passed}

Original email body:
\"\"\"{email_body}\"\"\"

Return **ONLY valid JSON** according to the following schema:
{json.dumps(FOLLOW_UP_SCHEMA, ensure_ascii=False)}

Do NOT return any text before or after the JSON.
"""
    return prompt
