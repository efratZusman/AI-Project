# -*- coding: utf-8 -*-

import logging
from typing import Optional, List, Tuple
from backend.ai.lexicon import LEXICON
from backend.ai.ai import generate_structured_json
from backend.ai.prompts import BEFORE_SEND_SCHEMA, build_before_send_prompt
from backend.models import ThreadMessage

logger = logging.getLogger("analyzer")

def detect_lang(text: str, language: str) -> str:
    if language in ("he", "en"):
        return language
    return "he" if any("\u0590" <= ch <= "\u05EA" for ch in (text or "")) else "en"

def risk_bucket(score: int) -> str:
    if score <= 1:
        return "low"
    if score <= 6:
        return "medium"
    return "high"

def base_response(body: str, lang: str) -> dict:
    return {
        "intent": "העברת מסר מקצועי" if lang == "he" else "Professional message",
        "risk_level": "low",
        "risk_factors": [],
        "recipient_interpretation": "ההודעה תיתפס כעניינית." if lang == "he" else "The message will be perceived as professional.",
        "send_decision": "send_as_is",
        "follow_up_needed": False,
        "follow_up_reason": "",
        "safer_subject": None,
        "safer_body": body,  # תמיד גוף קיים (כדי שה-UI לא יישבר)
        "notes_for_sender": [],
        # סטטוס AI – תמיד קיים (הפרדה מוחלטת!)
        "ai_ok": True,
        "ai_error_code": None,
        "ai_error_message": None,
        "analysis_layer": "lexicon",
    }

def quick_risk_score(text: str, lang: str, is_reply: bool) -> Tuple[int, List[str]]:
    if not (text or "").strip():
        return 0, []

    lex = LEXICON.get(lang, LEXICON["he"])
    t = text.lower()
    score = 0
    reasons: List[str] = []

    if any(m in text for m in lex["escalation_signs"]):
        score += 2
        reasons.append("סימני הסלמה" if lang == "he" else "Escalation signs")

    for p in lex["insult_phrases"]:
        if p.lower() in t:
            score += 8
            reasons.append("שפה פוגענית" if lang == "he" else "Insulting language")

    for w in lex["pressure_phrases"]:
        if w.lower() in t:
            score += 3
            reasons.append("לחץ" if lang == "he" else "Pressure")

    for w in lex["accusation_phrases"]:
        if w.lower() in t:
            score += 3
            reasons.append("האשמה" if lang == "he" else "Accusation")

    # reply = יותר “טעון” בהקשר
    if is_reply:
        score += 2
        reasons.append("תגובה בשרשור" if lang == "he" else "Reply in thread")

    # להסיר כפילויות
    reasons = list(dict.fromkeys(reasons))
    return score, reasons

def analyze_before_send(
    subject: Optional[str],
    body: str,
    language: str = "auto",
    is_reply: bool = False,
    thread_context: Optional[List[ThreadMessage]] = None,
):
    lang = detect_lang(body, language)
    res = base_response(body, lang)

    # -------- Layer A: Lexicon Gate --------
    score, reasons = quick_risk_score(body, lang, is_reply)
    res["risk_level"] = risk_bucket(score)
    res["risk_factors"] = reasons

    # כלל חכם: אם אין סימנים בכלל וגם לא reply → לא שולחים לג׳מיני
    must_check = (score >= 2) or bool(is_reply and thread_context)

    logger.info(
        "Gate decision: lang=%s score=%s is_reply=%s must_check=%s",
        lang, score, is_reply, must_check
    )

    if not must_check:
        res["analysis_layer"] = "lexicon_only"
        res["send_decision"] = "send_as_is"
        return res

    # אם יש רמזים – לפחות להזהיר מקומית (גם אם אין Gemini)
    res["send_decision"] = "send_with_caution" if score < 7 else "rewrite_recommended"
    res["analysis_layer"] = "lexicon_gate"

    # -------- Layer B: Gemini Deep --------
    prompt = build_before_send_prompt(
        body=body,
        subject=subject,
        language=lang,
        is_reply=is_reply,
        thread_context=thread_context,
    )

    gem = generate_structured_json(prompt, BEFORE_SEND_SCHEMA)

    if gem.get("error"):
        # הפרדה מוחלטת: אין ניסוח “חירום” שממציא טקסט
        res["ai_ok"] = False
        res["ai_error_code"] = gem.get("error")
        res["ai_error_message"] = gem.get("message") or ""
        res["notes_for_sender"] = res.get("notes_for_sender", []) + [
            ("אין חיבור ל‑Gemini כרגע. מוצגת אזהרה מקומית בלבד — ללא ניסוח מחדש."
             if lang == "he" else
             "Gemini is not available right now. Showing local warnings only — no rewrite.")
        ]
        # safer_body נשאר המקורי, וה-UI צריך לחסום Apply
        return res

    # Gemini תקין → מחזירים “אמיתי” + סטטוס ai_ok
    gem["ai_ok"] = True
    gem["ai_error_code"] = None
    gem["ai_error_message"] = None
    gem["analysis_layer"] = "gemini"
    return gem
