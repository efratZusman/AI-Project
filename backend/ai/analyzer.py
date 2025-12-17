# backend/ai/analyzer.py
# -*- coding: utf-8 -*-

import re
from typing import List, Optional, Tuple
from backend.ai.ai import generate_structured_json
from backend.ai.prompts import (
    EMOTION_SCHEMA,
    BEFORE_SEND_SCHEMA,
    build_emotion_prompt,
    build_before_send_prompt,
)
from backend.ai.lexicon import LEXICON
from backend.models import ThreadMessage

def base_response(body: str) -> dict:
    return {
        "intent": "הודעה עניינית",
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

def _detect_language(body: str, language: str) -> str:
    if language in ("he", "en"):
        return language
    if any("\u0590" <= ch <= "\u05EA" for ch in (body or "")):
        return "he"
    return "en"

def _bucket(score: int) -> str:
    if score <= 1:
        return "low"
    if score <= 4:
        return "medium"
    return "high"

def _decision_from_risk(risk_level: str) -> str:
    if risk_level == "low":
        return "send_as_is"
    if risk_level == "medium":
        return "send_with_caution"
    return "rewrite_recommended"

def _count_hits(text_lower: str, phrases: List[str]) -> Tuple[int, List[str]]:
    hits = []
    for p in phrases:
        if p and p.lower() in text_lower:
            hits.append(p)
    return len(hits), hits[:3]

def quick_risk_score(
    text: str,
    *,
    is_reply: bool = False,
    thread_context: Optional[List[ThreadMessage]] = None,
    language: str = "auto",
) -> Tuple[int, List[str]]:
    """
    Layer 1: ניתוח מהיר באמת + סיבות.
    מחזיר (score, reasons).
    """
    if not text or not text.strip():
        return 0, []

    lang = _detect_language(text, language)
    lex = LEXICON.get(lang, LEXICON["he"])

    t = text.strip()
    lower = t.lower()

    score = 0
    reasons: List[str] = []

    # קצר מאוד יכול להיות "אימפולסיבי"
    if len(t) < 25:
        score += 1
        reasons.append("טקסט קצר מאוד")

    # סימני הסלמה
    if any(mark in t for mark in lex["escalation_signs"]):
        score += 2
        reasons.append("סימני הסלמה (!!/???/?! וכו')")

    # האשמה בגוף שני (גם אם המילים לא בדיוק ברשימה)
    # עברית: את/אתה/אתם + לא/לא עשית/לא מגיבה
    if lang == "he":
        if re.search(r"\b(את|אתה|אתם)\b.*\bלא\b", t):
            score += 2
            reasons.append("מבנה של האשמה בגוף שני (את/אתה... לא...)")
    else:
        if re.search(r"\byou\b.*\b(didn't|never|ignored|failed)\b", lower):
            score += 2
            reasons.append("Direct accusation pattern")

    anger_n, anger_hits = _count_hits(lower, lex["anger"])
    if anger_n:
        score += min(anger_n, 3) * 2
        reasons.append(f"מילות כעס/תסכול (לדוגמה: {', '.join(anger_hits)})")

    pressure_n, pressure_hits = _count_hits(lower, lex["pressure"])
    if pressure_n:
        score += min(pressure_n, 3) * 2 + 1
        reasons.append(f"ביטויי לחץ/דחיפות (לדוגמה: {', '.join(pressure_hits)})")

    acc_n, acc_hits = _count_hits(lower, lex["accusation"])
    if acc_n:
        score += min(acc_n, 3) * 2 + 1
        reasons.append(f"ביטויי האשמה (לדוגמה: {', '.join(acc_hits)})")

    ins_n, ins_hits = _count_hits(lower, lex["insult_sensitive"])
    if ins_n:
        score += min(ins_n, 2) * 3
        reasons.append(f"מילים מעליבות/רגישות (לדוגמה: {', '.join(ins_hits)})")

    # מרככים מורידים מעט
    soft_n, _ = _count_hits(lower, lex["softeners"])
    if soft_n:
        score -= 1
        reasons.append("נמצאו מרככים (בבקשה/תודה/בלי לחץ וכו')")

    # Reply עם thread_context מוסיף רגישות (לא הסלמה אוטומטית כאן — זה יקרה בתזמור)
    if is_reply and thread_context:
        score += 1
        reasons.append("Reply עם thread_context")

    score = max(score, 0)
    return score, reasons[:6]

def analyze_before_send(
    subject: Optional[str],
    body: str,
    language: str = "auto",
    is_reply: bool = False,
    thread_context: Optional[List[ThreadMessage]] = None,
):
    """
    מנוע 3 שכבות:
    - Layer 1: heuristic + reasons
    - Layer 2: emotion (Gemini קל)
    - Layer 3: full analysis + rewrite (Gemini כבד)
    """

    # --- RULE: Reply עם thread_context => תמיד Layer 3 ---
    if is_reply and thread_context:
        prompt = build_before_send_prompt(body, subject, language, is_reply, thread_context)
        result = generate_structured_json(prompt, BEFORE_SEND_SCHEMA)
        if result.get("error"):
            res = base_response(body)
            res["analysis_layer"] = 3
            res["risk_level"] = "unknown"
            res["risk_factors"] = ["Reply עם שרשור: ניסינו ניתוח עומק אך Gemini נכשל."]
            res["send_decision"] = "send_with_caution"
            res["safer_body"] = body
            return res
        result["analysis_layer"] = 3
        # safety: החלטה עקבית
        result["send_decision"] = _decision_from_risk(result.get("risk_level", "medium"))
        return result

    # ---------- LAYER 1 ----------
    l1_score, l1_reasons = quick_risk_score(
        body,
        is_reply=is_reply,
        thread_context=thread_context,
        language=language,
    )

    # אם באמת רגוע לגמרי – לא קוראים ל-Gemini בכלל
    if l1_score <= 1:
        res = base_response(body)
        res["analysis_layer"] = 1
        res["risk_level"] = _bucket(l1_score)
        res["send_decision"] = _decision_from_risk(res["risk_level"])
        res["risk_factors"] = []
        return res

    # אם Layer 1 כבר “צועק” (כעס/לחץ/האשמה) -> דילוג Layer 2 וחיסכון בקריאה
    # זה יפתור בדיוק את המקרה שלך (כועסת/לא בסדר/מטופש וכו')
    if l1_score >= 4:
        prompt = build_before_send_prompt(body, subject, language, False, None)
        result = generate_structured_json(prompt, BEFORE_SEND_SCHEMA)
        if result.get("error"):
            res = base_response(body)
            res["analysis_layer"] = 3
            res["risk_level"] = _bucket(l1_score)
            res["risk_factors"] = l1_reasons or ["זוהו סימני לחץ/כעס בשכבה 1."]
            res["send_decision"] = _decision_from_risk(res["risk_level"])
            res["notes_for_sender"] = ["Gemini נכשל; מומלץ לעדן את הניסוח ידנית לפני שליחה."]
            return res
        result["analysis_layer"] = 3
        result["send_decision"] = _decision_from_risk(result.get("risk_level", "medium"))
        return result

    # ---------- LAYER 2 ----------
    emotion_result = generate_structured_json(build_emotion_prompt(body, language), EMOTION_SCHEMA)

    if emotion_result.get("error"):
        # אין רגש -> החלטה לפי L1 בלבד, אבל לא "send_as_is" אם יש סיכון בינוני+
        res = base_response(body)
        res["analysis_layer"] = 2
        res["risk_level"] = _bucket(l1_score)
        res["risk_factors"] = (l1_reasons or []) + ["ניתוח רגשי נכשל (fallback)."]
        res["send_decision"] = _decision_from_risk(res["risk_level"])
        res["safer_body"] = body
        return res

    emotion = (emotion_result.get("emotion") or "neutral").strip()
    confidence = float(emotion_result.get("confidence") or 0.0)

    # תנאי early-return אמיתי: רק אם L1 נמוך יחסית + רגש ניטרלי/חיובי בביטחון סביר
    if l1_score <= 2 and emotion in ("neutral", "positive") and confidence >= 0.55:
        res = base_response(body)
        res["analysis_layer"] = 2
        res["risk_level"] = "low"
        res["risk_factors"] = ["טון רגוע לפי מודל רגשי + מעט מאוד סימני סיכון."]
        res["send_decision"] = "send_as_is"
        res["safer_body"] = body
        return res

    # אחרת — אם יש tense/frustrated/sensitive בביטחון אפילו בינוני -> Layer 3
    if emotion in ("tense", "frustrated", "sensitive") and confidence >= 0.35:
        prompt = build_before_send_prompt(body, subject, language, False, None)
        result = generate_structured_json(prompt, BEFORE_SEND_SCHEMA)
        if result.get("error"):
            res = base_response(body)
            res["analysis_layer"] = 3
            res["risk_level"] = "medium"
            res["risk_factors"] = (l1_reasons or []) + [f"טון {emotion} (confidence≈{confidence:.2f}) אבל ניתוח עומק נכשל."]
            res["send_decision"] = "send_with_caution"
            res["safer_body"] = body
            return res
        result["analysis_layer"] = 3
        result["send_decision"] = _decision_from_risk(result.get("risk_level", "medium"))
        return result

    # אם הגענו לפה: לא מספיק כדי Layer 3, מחזירים Layer 2 “זהיר”
    res = base_response(body)
    res["analysis_layer"] = 2
    # ניקח bucket בינוני כברירת מחדל אם L1 לא 0
    res["risk_level"] = _bucket(max(l1_score, 2))
    res["risk_factors"] = (l1_reasons or []) + [f"טון: {emotion} (confidence≈{confidence:.2f})"]
    res["send_decision"] = _decision_from_risk(res["risk_level"])
    res["notes_for_sender"] = ["זה ניתוח ביניים. אם זה מייל רגיש — מומלץ להריץ ניתוח עומק."]
    res["safer_body"] = body
    return res

def analyze_follow_up(email_body: str, days_passed: int):
    return {"needs_follow_up": False, "urgency": "low", "suggested_follow_up": ""}
