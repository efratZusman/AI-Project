# backend/ai/analyzer.py

from .ai import generate_structured_json
from .prompts import (
    BEFORE_SEND_SCHEMA,
    FOLLOW_UP_SCHEMA,
    build_before_send_prompt,
    build_follow_up_prompt,
)


def analyze_before_send(draft: str) -> dict:
    """
    נקודת הכניסה הגבוהה ל-Backend:
    מקבל טקסט של הודעה לפני שליחה,
    מחזיר ניתוח + ניסוח בטוח יותר.
    """
    prompt = build_before_send_prompt(draft)
    result = generate_structured_json(prompt, BEFORE_SEND_SCHEMA)

    # במקרה של שגיאת AI – להחזיר מבנה סביר שלא יפיל את הפרונט
    if "error" in result:
        return {
            "intent": "unknown",
            "risk_level": "medium",
            "risk_factors": ["שגיאה טכנית בניתוח ה-AI"],
            "recipient_interpretation": "",
            "send_decision": "edit_before_send",
            "follow_up_needed": False,
            "follow_up_reason": "",
            "safer_subject": "",
            "safer_body": "אירעה תקלה בניתוח. מומלץ לקרוא שוב את ההודעה לפני שליחה.",
            "notes_for_sender": ["בדקי את הניסוח ידנית לפני שליחה."],
        }

    return result


def analyze_follow_up(email_body: str, days_passed: int) -> dict:
    """
    ניתוח האם כדאי לעשות Follow-Up על מייל שכבר נשלח.
    """
    prompt = build_follow_up_prompt(email_body, days_passed)
    result = generate_structured_json(prompt, FOLLOW_UP_SCHEMA)

    if "error" in result:
        return {
            "needs_follow_up": False,
            "follow_up_reason": "שגיאה טכנית בניתוח ה-AI",
            "urgency": "low",
            "suggested_follow_up": "",
            "channel": "none",
            "tone_recommendation": "",
            "notes_for_sender": [
                "אם חשוב לך המייל – שקלי לבדוק ידנית אם מתאים לשלוח תזכורת."
            ],
        }

    return result
