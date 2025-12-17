# backend/ai/analyzer.py
from typing import Optional, List
from backend.ai.ai import generate_structured_json
from backend.ai.prompts import (
    EMOTION_SCHEMA,
    BEFORE_SEND_SCHEMA,
    build_emotion_prompt,
    build_before_send_prompt,
)
from backend.models import ThreadMessage


# ========= RESPONSES =========


def base_response(body: str) -> dict:
    """
    תשובת בסיס "אין סיכון מיוחד" – משמשת גם כ‑fallback בשגיאות.
    """
    return {
        "intent": "הודעה עניינית / יומיומית",
        "risk_level": "low",
        "risk_factors": [],
        "recipient_interpretation": "ההודעה תיתפס כרגילה ומקצועית.",
        "send_decision": "send_as_is",
        "follow_up_needed": False,
        "follow_up_reason": "",
        "safer_subject": None,
        "safer_body": body,
        "notes_for_sender": [],
    }


# ========= LAYER 1 – HEURISTICS =========


def quick_risk_score(text: str) -> int:
    """
    שכבה 1 – הערכת סיכון מהירה, בלי AI.

    מספרים חיוביים = יותר סיכון.
    מספרים שליליים = טיפה "קטן מדי" או יבש, אבל לא בהכרח מסוכן.
    """
    score = 0
    t = (text or "").strip()

    if len(t) < 20:
        # הודעות קצרות מאוד – לרוב לא מסוכנות, רק פחות מידע
        score -= 1

    triggers = [
        "שוב",
        "בעיה",
        "בעייתי",
        "עדיין לא",
        "לא קיבלתי תשובה",
        "כמה הודעות",
        "כבר אמרתי",
    ]
    for w in triggers:
        if w in t:
            score += 2

    if "כבר" in t and "לא" in t:
        score += 1

    return score


# ========= MAIN ANALYSIS (3 LAYERS) =========


def analyze_before_send(
    subject: Optional[str],
    body: str,
    language: str = "auto",
    is_reply: bool = False,
    thread_context: Optional[List[ThreadMessage]] = None,
) -> dict:
    text = body or ""
    risk = quick_risk_score(text)

    # ===== Layer 1 – heuristics בלבד =====
    if risk <= 0 and not is_reply:
        # מייל לא חריג + לא reply → חוסכים AI
        res = base_response(text)
        res["analysis_layer"] = 1
        return res

    # ===== Layer 2 – ניתוח רגשי קל =====
    emotion_result = generate_structured_json(
        build_emotion_prompt(text, language),
        EMOTION_SCHEMA,
    )

    if emotion_result.get("error"):
        # לא נכשיל את המשתמש בגלל כשל AI
        res = base_response(text)
        res["risk_level"] = "unknown"
        res["notes_for_sender"] = [
            "חלה שגיאה בניתוח הרגשי, נעשה שימוש בהערכה שמרנית."
        ]
        res["analysis_layer"] = 2
        return res

    emotion = emotion_result.get("emotion", "neutral")
    confidence = float(emotion_result.get("confidence", 0) or 0.0)

    # האם צריך לעלות לשכבה 3?
    escalate = False

    # 1) reply עם הקשר – תמיד רוצים להבין את השירשור לעומק
    if is_reply and thread_context:
        escalate = True

    # 2) סיכון טקסטואלי גבוה יותר
    if risk >= 2:
        escalate = True

    # 3) רגש רגיש – גם אם הסיכון הטקסטואלי לא מאוד גבוה
    if emotion in {"tense", "frustrated", "sensitive"} and confidence >= 0.4:
        escalate = True

    # 4) אם הכול נראה רגוע → נעצור בשכבה 2
    if not escalate:
        res = base_response(text)
        # נרים קצת את הרגישות אם יש לפחות טריגר אחד
        if risk == 1 or (emotion in {"tense", "sensitive"} and confidence < 0.4):
            res["risk_level"] = "medium"
            res["send_decision"] = "send_as_is"
            res["risk_factors"] = ["ייתכן שהניסוח מעט יבש או לחוץ, אבל לא חריג."]
        res["analysis_layer"] = 2
        return res

    # ===== Layer 3 – ניתוח מלא עם הקשר =====
    prompt = build_before_send_prompt(
        body=text,
        subject=subject,
        language=language,
        is_reply=is_reply,
        thread_context=thread_context,
    )

    result = generate_structured_json(prompt, BEFORE_SEND_SCHEMA)

    if result.get("error"):
        res = base_response(text)
        res["risk_level"] = "unknown"
        res["notes_for_sender"] = [
            "חלה שגיאה בניתוח העמוק, נעשה שימוש בהערכה בסיסית."
        ]
        res["analysis_layer"] = 3
        return res

    result["analysis_layer"] = 3
    return result


def analyze_follow_up(email_body: str, days_passed: int) -> dict:
    """
    כרגע Stub – אם תרצי, נבנה מנוע follow-up שכבות דומה.
    """
    return {
        "needs_follow_up": False,
        "urgency": "low",
        "suggested_follow_up": "",
    }
