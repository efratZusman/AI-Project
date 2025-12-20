# backend/ai/analyzer.py
# -*- coding: utf-8 -*-

import logging
from typing import Optional, List, Tuple
from .lexicon import LEXICON
from .ai import generate_structured_json
from .prompts import BEFORE_SEND_SCHEMA, build_before_send_prompt
from ..models import ThreadMessage

logger = logging.getLogger("analyzer")

# --------------------------------------------------
# Utils
# --------------------------------------------------

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
        "recipient_interpretation": (
            "ההודעה תיתפס כעניינית."
            if lang == "he"
            else "The message will be perceived as professional."
        ),
        "send_decision": "send_as_is",
        "follow_up_needed": False,
        "follow_up_reason": "",
        "safer_subject": None,
        "safer_body": body,
        "notes_for_sender": [],
        "ai_ok": True,
        "ai_error_code": None,
        "ai_error_message": None,
        "analysis_layer": "lexicon",
    }

# --------------------------------------------------
# Lexicon scoring
# --------------------------------------------------

def quick_risk_score(text: str, lang: str) -> Tuple[int, List[str]]:
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

    return score, list(dict.fromkeys(reasons))

# --------------------------------------------------
# Explicit emotion detection
# --------------------------------------------------

def has_explicit_emotion(text: str, lang: str) -> bool:
    lex = LEXICON.get(lang, LEXICON["he"])
    t = text.lower()
    for phrase in lex.get("explicit_emotion_phrases", []):
        if phrase.lower() in t:
            return True
    return False

# --------------------------------------------------
# Thread structure analysis
# --------------------------------------------------

def analyze_thread_structure(thread: Optional[List[ThreadMessage]]) -> dict:
    if not thread:
        return {"mode": "no_thread", "consecutive_from_me": 0}

    last_msgs = thread[-3:]
    authors = [m.author for m in last_msgs]

    consecutive = 0
    for a in reversed(authors):
        if a == "me":
            consecutive += 1
        else:
            break

    if all(a == "me" for a in authors):
        return {"mode": "self_sequence", "consecutive_from_me": consecutive}

    if "them" in authors and authors[-1] == "me":
        return {"mode": "dialog", "consecutive_from_me": consecutive}

    return {"mode": "no_thread", "consecutive_from_me": consecutive}

# --------------------------------------------------
# Main entry
# --------------------------------------------------

def analyze_before_send(
    subject: Optional[str],
    body: str,
    language: str = "auto",
    is_reply: bool = False,
    thread_context: Optional[List[ThreadMessage]] = None,
):
    lang = detect_lang(body, language)
    res = base_response(body, lang)

    score, reasons = quick_risk_score(body, lang)
    explicit_emotion = has_explicit_emotion(body, lang)

    # ---------- רגש מפורש = סיכון מינימום medium ----------
    if explicit_emotion:
        score = max(score, 4)
        res["intent"] = (
            "הבעת תסכול / רגש"
            if lang == "he"
            else "Emotional expression / frustration"
        )
        res["risk_factors"] = reasons + [
            "ביטוי רגשי ישיר" if lang == "he" else "Explicit emotional expression"
        ]
        res["recipient_interpretation"] = (
            "ההודעה עלולה להיתפס כלחוצה או רגשית."
            if lang == "he"
            else "The message may be perceived as emotionally charged."
        )
    else:
        res["risk_factors"] = reasons

    res["risk_level"] = risk_bucket(score)

    # ---------- החלטת מערכת מקומית עקבית ----------
    if res["risk_level"] == "low":
        res["send_decision"] = "send_as_is"
    elif res["risk_level"] == "medium":
        res["send_decision"] = "send_with_caution"
        res["notes_for_sender"].append(
            "ייתכן שכדאי לרכך מעט את הטון לפני שליחה."
            if lang == "he"
            else "You may want to slightly soften the tone before sending."
        )
    else:  # high
        res["send_decision"] = "rewrite_recommended"
        res["notes_for_sender"].append(
            "הניסוח הנוכחי עלול להסלים את השיח."
            if lang == "he"
            else "The current wording may escalate the conversation."
        )

    # ---------- אין שרשור ואין סיכון ----------
    if score == 0 and not explicit_emotion and not thread_context:
        res["analysis_layer"] = "lexicon_only"
        return res

    thread_info = analyze_thread_structure(thread_context)
    mode = thread_info["mode"]
    consecutive = thread_info["consecutive_from_me"]

    logger.info(
        "Thread analysis: mode=%s consecutive=%s score=%s emotion=%s",
        mode, consecutive, score, explicit_emotion
    )

    # ---------- רצף הודעות ממני ----------
    if mode == "self_sequence":
        res["analysis_layer"] = "self_sequence"
        if consecutive >= 2 and res["risk_level"] != "low":
            res["notes_for_sender"].append(
                "נשלחו כמה הודעות ברצף — ייתכן שהנמען יחווה זאת כהצפה."
                if lang == "he"
                else "Multiple consecutive messages may feel overwhelming."
            )
        return res

    # ---------- דיאלוג ----------
    if mode == "dialog" and res["risk_level"] == "low":
        res["analysis_layer"] = "dialog_no_ai"
        return res

    # ---------- Gemini ----------
    prompt = build_before_send_prompt(
        body=body,
        subject=subject,
        language=lang,
        is_reply=is_reply,
        thread_context=thread_context,
    )

    gem = generate_structured_json(prompt, BEFORE_SEND_SCHEMA)

    if gem.get("error"):
        res["ai_ok"] = False
        res["ai_error_code"] = gem.get("error")
        res["ai_error_message"] = gem.get("message") or ""
        res["analysis_layer"] = "gemini_failed"
        return res

    gem["ai_ok"] = True
    gem["analysis_layer"] = "gemini"
    return gem
