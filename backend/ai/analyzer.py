from backend.ai.ai import generate_structured_json
from backend.ai.prompts import (
    EMOTION_SCHEMA,
    BEFORE_SEND_SCHEMA,
    build_emotion_prompt,
    build_before_send_prompt,
)
from backend.models import ThreadMessage


def base_response(body: str):
    return {
        "intent": "הודעה עניינית",
        "risk_level": "low",
        "risk_factors": [],
        "recipient_interpretation": "ההודעה תיתפס כרגילה",
        "send_decision": "send_as_is",
        "follow_up_needed": False,
        "follow_up_reason": "",
        "safer_subject": None,
        "safer_body": body,
        "notes_for_sender": [],
    }


def quick_risk_score(text: str) -> int:
    score = 0
    t = text.strip()

    if len(t) < 20:
        score -= 2

    triggers = [
        "שוב",
        "בעיה",
        "בעייתי",
        "עדיין לא",
        "לא קיבלתי תשובה",
        "כמה הודעות",
    ]

    for w in triggers:
        if w in t:
            score += 2

    if "כבר" in t and "לא" in t:
        score += 1

    return score


def analyze_before_send(
    subject: str | None,
    body: str,
    language: str = "auto",
    is_reply: bool = False,
    thread_context: list[ThreadMessage] | None = None,
):
    risk = quick_risk_score(body)

    # ===== Layer 1 =====
    if risk <= 0:
        res = base_response(body)
        res["analysis_layer"] = 1
        return res

    # ===== Layer 2 =====
    emotion_result = generate_structured_json(
        build_emotion_prompt(body, language),
        EMOTION_SCHEMA,
    )

    if emotion_result.get("error"):
        res = base_response(body)
        res["risk_level"] = "unknown"
        res["analysis_layer"] = 2
        return res

    emotion = emotion_result.get("emotion", "neutral")
    confidence = float(emotion_result.get("confidence", 0))

    if emotion in ["neutral", "positive"] and confidence < 0.6 and risk < 2:
        res = base_response(body)
        res["analysis_layer"] = 2
        return res

    # ===== Layer 3 =====
    prompt = build_before_send_prompt(
        body=body,
        subject=subject,
        language=language,
        is_reply=is_reply,
        thread_context=thread_context,
    )

    result = generate_structured_json(prompt, BEFORE_SEND_SCHEMA)

    if result.get("error"):
        res = base_response(body)
        res["risk_level"] = "unknown"
        res["analysis_layer"] = 3
        return res

    result["analysis_layer"] = 3
    return result


def analyze_follow_up(email_body: str, days_passed: int):
    return {
        "needs_follow_up": False,
        "urgency": "low",
        "suggested_follow_up": "",
    }
