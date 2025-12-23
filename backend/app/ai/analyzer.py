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
# Config
# --------------------------------------------------

GEMINI_SCORE_THRESHOLD = 6
LONG_TEXT_THRESHOLD = 600
VERY_LONG_TEXT_THRESHOLD = 1200

# --------------------------------------------------
# Utils
# --------------------------------------------------

def detect_lang(text: str, language: str) -> str:
    if language in ("he", "en"):
        return language

    if not (text or "").strip():
        return "he"  # ✅ ברירת מחדל בטוחה

    return "he" if any("\u0590" <= ch <= "\u05EA" for ch in text) else "en"


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
        "analysis_layer": "local_scoring",
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


def has_explicit_emotion(text: str, lang: str) -> bool:
    lex = LEXICON.get(lang, LEXICON["he"])
    t = text.lower()
    for phrase in lex.get("explicit_emotion_phrases", []):
        if phrase.lower() in t:
            return True
    return False

# --------------------------------------------------
# Thread structure
# --------------------------------------------------

def analyze_thread_structure(thread: Optional[List[ThreadMessage]]) -> dict:
    if not thread:
        return {"consecutive_from_me": 0}

    last_msgs = thread[-3:]
    authors = [m.author for m in last_msgs]

    consecutive = 0
    for a in reversed(authors):
        if a == "me":
            consecutive += 1
        else:
            break

    return {"consecutive_from_me": consecutive}

# --------------------------------------------------
# Unified score calculation
# --------------------------------------------------

def compute_total_score(
    body: str,
    lang: str,
) -> Tuple[int, List[str]]:
    score, reasons = quick_risk_score(body, lang)

    if has_explicit_emotion(body, lang):
        score += 4
        reasons.append(
            "ביטוי רגשי ישיר" if lang == "he" else "Explicit emotional expression"
        )

    length = len(body or "")
    if length > VERY_LONG_TEXT_THRESHOLD:
        score += 4
        reasons.append("טקסט ארוך מאוד" if lang == "he" else "Very long message")
    elif length > LONG_TEXT_THRESHOLD:
        score += 2
        reasons.append("טקסט ארוך" if lang == "he" else "Long message")

    return score, list(dict.fromkeys(reasons))

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
    lang = detect_lang(body or subject or "", language)
    res = base_response(body, lang)

    # ---------- RULE 1: THREAD ALWAYS GOES TO GEMINI ----------
    if thread_context:
        res["analysis_layer"] = "thread_forced_gemini"
        prompt = build_before_send_prompt(
            body=body,
            subject=subject,
            language=lang,
            is_reply=is_reply,
            thread_context=thread_context,
        )
        return _run_gemini(prompt, res)

    # ---------- RULE 2: VERY LONG MESSAGE ALWAYS GOES TO GEMINI ----------
    if len(body or "") > VERY_LONG_TEXT_THRESHOLD:
        res["analysis_layer"] = "long_text_forced_gemini"
        prompt = build_before_send_prompt(
            body=body,
            subject=subject,
            language=lang,
            is_reply=is_reply,
            thread_context=None,
        )
        return _run_gemini(prompt, res)

    # ---------- SCORING ----------
    total_score, reasons = compute_total_score(body, lang)
    res["risk_factors"] = reasons
    res["risk_level"] = risk_bucket(total_score)

    if res["risk_level"] == "medium":
        res["send_decision"] = "send_with_caution"
    elif res["risk_level"] == "high":
        res["send_decision"] = "rewrite_recommended"

# ---------- STOP: מתחת לסף → בלי Gemini ----------
    if total_score < GEMINI_SCORE_THRESHOLD:
        return res
    
# ---------- GEMINI ----------

    res["analysis_layer"] = "score_threshold_gemini"
    res["send_decision"] = "rewrite_recommended"

    prompt = build_before_send_prompt(
        body=body,
        subject=subject,
        language=lang,
        is_reply=is_reply,
        thread_context=None,
    )
    return _run_gemini(prompt, res)

# --------------------------------------------------
# Gemini runner
# --------------------------------------------------
def _run_gemini(prompt: str, res: dict) -> dict:
    gem = generate_structured_json(prompt, BEFORE_SEND_SCHEMA)

    if not isinstance(gem, dict) or gem.get("error"):
        res["ai_ok"] = False
        res["ai_error_code"] = gem.get("error") if isinstance(gem, dict) else None
        res["ai_error_message"] = gem.get("message") if isinstance(gem, dict) else ""
        res["analysis_layer"] = "gemini_failed"
        return res

    # ⭐ כאן השינוי הקריטי ⭐
    return {
        **res,               # שדות כלליים (lang וכו')
        **gem,               # 👈 Gemini דורס הכל
        "analysis_layer": "gemini",
        "ai_ok": True,
        "ai_error_code": None,
        "ai_error_message": None,
    }

