# backend/ai/prompts.py

import json

# ====== BEFORE YOU SEND ======

BEFORE_SEND_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string"},
        "risk_level": {"type": "string"},  # low / medium / high
        "risk_factors": {
            "type": "array",
            "items": {"type": "string"},
        },
        "recipient_interpretation": {"type": "string"},
        "send_decision": {  # send_as_is / edit_before_send / do_not_send
            "type": "string"
        },
        "follow_up_needed": {"type": "boolean"},
        "follow_up_reason": {"type": "string"},
        "safer_subject": {"type": "string"},
        "safer_body": {"type": "string"},
        "notes_for_sender": {
            "type": "array",
            "items": {"type": "string"},
        },
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


def build_before_send_prompt(draft: str) -> str:
    """
    פרומפט לניתוח הודעה לפני שליחה.
    שם דגש על:
    - Intent analysis
    - Risk assessment
    - Recipient simulation
    - Decision modeling
    - Safer rewrite
    """
    prompt = f"""
אתה מודול ניתוח תקשורת כתובה לפני שליחה ("Before You Send") עבור אימיילים.

המטרה שלך:
1. להבין מה השולח באמת מנסה לעשות (Intent analysis).
2. לזהות סיכוני תקשורת:
   - טון פוגעני / תוקפני / פסיבי־אגרסיבי.
   - עמימות, חוסר הקשר, משפטים שניתן לפרש בשתי צורות.
   - עומס רגשי או דרמטי מדי.
3. לדמיין איך הנמען עלול לפרש את ההודעה (Recipient simulation).
4. להחליט האם כדאי:
   - לשלוח כמו שזה.
   - לערוך לפני שליחה.
   - לא לשלוח בכלל.
5. להציע ניסוח בטוח יותר שמכבד את הכוונה המקורית של השולח,
   אבל מפחית סיכון למתח, ריב, פגיעה או חוסר מקצועיות.

כללי עבודה:
- אתה לא שופט את השולח, רק מייעץ מקצועית.
- אל תחזיר טקסט חופשי, רק JSON לפי הסכמה.
- אם ההודעה נייטרלית ולא מסוכנת – תגיד זאת בבירור ותשאיר את הניסוח קרוב למקור.
- אם יש סיכון גבוה – אל תפחד להגיד זאת במפורש ולהציע ניסוח אחר לגמרי.

ההודעה לניתוח (הטקסט הגולמי שהמשתמש עומד לשלוח):

\"\"\"{draft}\"\"\"


החזר אך ורק JSON תקין לפי הסכמה הבאה:

{json.dumps(BEFORE_SEND_SCHEMA, ensure_ascii=False)}

אסור להחזיר שום טקסט לפני או אחרי ה-JSON.
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


def build_follow_up_prompt(email_body: str, days_passed: int) -> str:
    """
    פרומפט לבדיקת האם נדרש Follow-Up + ניסוח.
    """
    prompt = f"""
אתה מודול "Follow-Up Guardian" שמסייע למשתמש להחליט
האם צריך לעשות פולואפ על אימייל שכבר נשלח.

המטרה שלך:
1. להבין מה הייתה מטרת המייל המקורי.
2. לחשוב אם סביר לצפות לתגובה.
3. לשקלל כמה זמן עבר מאז שנשלח המייל.
4. להחליט אם כדאי לשלוח Follow-Up או דווקא לשחרר.
5. אם כן – לנסח Follow-Up:
   - מנומס, לא לוחץ מדי.
   - ברור, קצר, מכבד.
   - מותאם למטרה המקורית.

מידע חשוב:
- המשתמש נותן לך רק את גוף המייל המקורי וכמה ימים עברו.
- אין לך גישה לתיבת המייל האמיתית או לתשובות.
- אתה צריך לתת המלצה אנושית, שקולה, לא אוטומטית מדי.

הנתונים:
- מספר הימים שעברו מאז שנשלח המייל: {days_passed}
- גוף האימייל שנשלח:

\"\"\"{email_body}\"\"\"


החזר אך ורק JSON תקין לפי הסכמה הבאה:

{json.dumps(FOLLOW_UP_SCHEMA, ensure_ascii=False)}

אסור להחזיר שום טקסט לפני או אחרי ה-JSON.
"""
    return prompt
