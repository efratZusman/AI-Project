# backend/ai/analyzer.py
from backend.ai.ai import generate_structured_json
from backend.ai.prompts import (
    BEFORE_SEND_SCHEMA,
    FOLLOW_UP_SCHEMA,
    build_before_send_prompt,
    build_follow_up_prompt,
)
from backend.models import ThreadMessage



def analyze_before_send(
    subject: str,
    body: str,
    language: str = "auto",
    is_reply: bool = False,
    thread_context: list[ThreadMessage] | None = None
):

    prompt = build_before_send_prompt(
        body=body,
        subject=subject,
        is_reply=is_reply,
        thread_context=thread_context
    )
    return generate_structured_json(prompt, BEFORE_SEND_SCHEMA)
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
