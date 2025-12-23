# backend/app/ai/analyzer_chat_trend.py
# -*- coding: utf-8 -*-
import logging
from typing import List
from .ai import generate_structured_json
from .prompts_chat_trend import CHAT_TREND_SCHEMA, build_chat_trend_prompt

logger = logging.getLogger("chat_trend")

def detect_lang_from_messages(messages: List[str], language: str) -> str:
    if language in ("he", "en"):
        return language
    text = " ".join(messages or [])
    return "he" if any("\u0590" <= ch <= "\u05EA" for ch in (text or "")) else "en"

def analyze_chat_trend(messages: List[str], language: str = "auto") -> dict:
    lang = detect_lang_from_messages(messages, language)

    # ברירת מחדל בטוחה
    fallback = {"risk_level": "low", "warning_text": "", "ai_ok": False}

    # אם אין הודעות — אין מה לנתח
    msgs = [m for m in (messages or []) if (m or "").strip()]
    if not msgs:
        return fallback

    prompt = build_chat_trend_prompt(msgs[-30:], lang)
    gem = generate_structured_json(prompt, CHAT_TREND_SCHEMA)

    # ⭐ התיקון הקריטי כאן
    if not isinstance(gem, dict) or gem.get("error"):
        logger.warning("Gemini chat trend failed: %s", getattr(gem, "get", lambda _: gem)("error"))
        return {**fallback, "ai_ok": False}

    # ניקוי: להבטיח קצר
    warning = (gem.get("warning_text") or "").strip()
    if len(warning) > 220:
        warning = warning[:220].rsplit(" ", 1)[0].strip()

    return {
        "risk_level": gem.get("risk_level", "low"),
        "warning_text": warning,
        "ai_ok": True,
    }
