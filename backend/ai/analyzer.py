# backend/ai/analyzer.py
# -*- coding: utf-8 -*-

from typing import Optional, List, Tuple
from backend.ai.lexicon import LEXICON
from backend.ai.ai import generate_structured_json
from backend.ai.prompts import BEFORE_SEND_SCHEMA, build_before_send_prompt
from backend.models import ThreadMessage
import re

# -----------------------
# Utils
# -----------------------

def detect_lang(text: str, language: str) -> str:
    if language in ("he", "en"):
        return language
    return "he" if any("\u0590" <= ch <= "\u05EA" for ch in text) else "en"


def base_response(body: str, lang: str) -> dict:
    return {
        "intent": "העברת מסר מקצועי" if lang == "he" else "Professional message",
        "risk_level": "low",
        "risk_factors": [],
        "recipient_interpretation": "ההודעה תיתפס כעניינית.",
        "send_decision": "send_as_is",
        "follow_up_needed": False,
        "follow_up_reason": "",
        "safer_subject": None,
        "safer_body": body,
        "notes_for_sender": [],
        "analysis_layer": "local",
    }


# -----------------------
# Layer A – Lexicon Gate
# -----------------------

def quick_risk_score(
    text: str,
    lang: str,
    is_reply: bool,
) -> Tuple[int, List[str]]:

    if not text.strip():
        return 0, []

    lex = LEXICON.get(lang, LEXICON["he"])
    t = text.lower()
    score = 0
    reasons = []

    if any(m in text for m in lex["escalation_signs"]):
        score += 2
        reasons.append("סימני הסלמה")

    for p in lex["insult_phrases"]:
        if p.lower() in t:
            score += 8
            reasons.append("שפה פוגענית")

    for w in lex["pressure_phrases"]:
        if w.lower() in t:
            score += 3
            reasons.append("לחץ")

    for w in lex["accusation_phrases"]:
        if w.lower() in t:
            score += 3
            reasons.append("האשמה")

    if is_reply:
        score += 2
        reasons.append("תגובה בשרשור")

    return score, list(set(reasons))


# -----------------------
# Emergency fallback
# -----------------------

def emergency_soften(body: str, lang: str) -> str:
    text = body.strip()

    if lang == "he":
        text = re.sub(r"!{2,}", "!", text)
        text = re.sub(r"\bאני שונאת אותך\b", "אני מאוד נסערת מהמצב", text)
        if "אשמח" not in text:
            text += "\n\nאשמח שנוכל להתקדם בצורה עניינית."
    else:
        text = re.sub(r"!{2,}", "!", text)
        if "please" not in text.lower():
            text += "\n\nI’d like us to move forward constructively."

    return text


# -----------------------
# MAIN ENTRY
# -----------------------

def analyze_before_send(
    subject: Optional[str],
    body: str,
    language: str = "auto",
    is_reply: bool = False,
    thread_context: Optional[List[ThreadMessage]] = None,
):
    lang = detect_lang(body, language)

    # -------- Layer A: Lexicon --------
    score, reasons = quick_risk_score(body, lang, is_reply)

    if score == 0:
        return base_response(body, lang)

    # -------- Layer B: Gemini --------
    result = generate_structured_json(
        build_before_send_prompt(
            body=body,
            subject=subject,
            language=lang,
            is_reply=is_reply,
            thread_context=thread_context,
        ),
        BEFORE_SEND_SCHEMA,
    )

    if result.get("error"):
        return {
            **base_response(body, lang),
            "risk_level": "high",
            "risk_factors": [f"כשל AI ({result.get('error')}) – הופעל ניסוח בטוח"],
            "send_decision": "rewrite_recommended",
            "safer_body": emergency_soften(body, lang),
            "analysis_layer": "fallback",
        }

    result["analysis_layer"] = "gemini"
    return result
