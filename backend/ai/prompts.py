# backend/ai/prompts.py
# -*- coding: utf-8 -*-

import json
from typing import List, Optional
from backend.models import ThreadMessage

# ====== SCHEMAS ======

EMOTION_SCHEMA = {
    "type": "object",
    "properties": {
        "emotion": {
            "type": "string",
            "enum": ["neutral", "positive", "tense", "frustrated", "sensitive"],
        },
        "confidence": {
            "type": "number",
            "description": "0 to 1",
        },
    },
    "required": ["emotion", "confidence"],
}

BEFORE_SEND_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string"},
        "risk_level": {"type": "string"},  # low/medium/high
        "risk_factors": {"type": "array", "items": {"type": "string"}},
        "recipient_interpretation": {"type": "string"},
        "send_decision": {"type": "string"},  # send_as_is / send_with_caution / rewrite_recommended
        "follow_up_needed": {"type": "boolean"},
        "follow_up_reason": {"type": "string"},
        "safer_subject": {"type": "string"},
        "safer_body": {"type": "string"},
        "notes_for_sender": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "intent",
        "risk_level",
        "risk_factors",
        "recipient_interpretation",
        "send_decision",
        "follow_up_needed",
        "safer_body",
    ],
}

def _is_hebrew(text: str) -> bool:
    return any("\u0590" <= ch <= "\u05EA" for ch in (text or ""))

def render_thread(thread: Optional[List[ThreadMessage]]) -> str:
    """
    מצמצם thread כדי לא לפוצץ פרומפט:
    - שומר רק טקסטים קצרים
    - בלי מטא "On Wed..." אם מופיע (היינו רואים את זה בג׳ימייל)
    """
    if not thread:
        return ""

    out = "Conversation thread (older -> newer):\n"
    for msg in thread:
        who = "Sender" if msg.author == "me" else "Recipient"
        snippet = (msg.text or "").strip().replace("\n", " ")
        # ניקוי שורות "On ... wrote:" שמגיעות מציטוטים
        snippet = snippet.replace("wrote:", "").replace("On ", "")
        if len(snippet) > 220:
            snippet = snippet[:220] + "..."
        out += f"- {who}: {snippet}\n"
    return out

# ====== LAYER 2 (EMOTION) PROMPT ======

def build_emotion_prompt(body: str, language: str = "auto") -> str:
    """
    שכבה 2: סיווג רגשי חסכוני.
    דגש: לא להיות מחמיר. “יש ביקורת” != frustrated בהכרח.
    """
    reply_language = "Hebrew" if _is_hebrew(body) or language == "he" else "English"

    return f"""
You are a lightweight emotion classifier for email texts.

Return ONLY JSON.
Do NOT give advice. Do NOT rewrite.

Goal:
- Identify the sender's dominant emotional tone.

Important calibration:
- Professional criticism can still be "neutral".
- Use "frustrated" only when there is clear irritation/anger/blame.
- Use "tense" when there is pressure/urgency or sharpness, but not full anger.
- Use "sensitive" when topic is delicate (apology, bad news, personal/HR-like).

Reply ONLY in {reply_language}.
Return ONLY JSON with this schema:
{json.dumps(EMOTION_SCHEMA, ensure_ascii=False)}

Email body:
\"\"\"{body}\"\"\"
"""

# ====== LAYER 3 (FULL ANALYSIS) PROMPT ======

def build_before_send_prompt(
    body: str,
    subject: Optional[str],
    language: str,
    is_reply: bool,
    thread_context: Optional[List[ThreadMessage]],
) -> str:
    reply_language = "Hebrew" if _is_hebrew(body) or language == "he" else "English"
    thread_block = render_thread(thread_context) if (is_reply and thread_context) else "(no prior thread given)"

    return f"""
You are a communication coach (not a strict reviewer).

PRIMARY OUTPUT GOAL:
- Produce a safer rewrite of the CURRENT email (safer_body) that keeps the SAME intent,
  but reduces friction, blame, and escalation risk.

CRITICAL RULES (must follow):
1) safer_body must be ONLY the rewritten email body. Do NOT include:
   - quoted previous emails
   - "On Wed ... wrote" lines
   - conversation context
   - signatures you invent
   - metadata or analysis text inside safer_body
2) Always generate safer_body, even if risk is low.
3) Keep it human, concise, and professional. Not robotic, not overly apologetic.
4) Don't remove the request/goal. Soften tone, not substance.

If reply context exists, consider the dynamic (but do NOT copy it into safer_body):
{thread_block}

Tasks:
- intent: 1 short sentence
- risk_level: low / medium / high
- risk_factors: concrete, specific triggers
- recipient_interpretation: 1–2 sentences
- send_decision:
  - low -> send_as_is
  - medium -> send_with_caution
  - high -> rewrite_recommended
- safer_subject: optional
- safer_body: rewritten body (see rules)
- notes_for_sender: 1–3 practical tips

Reply ONLY in {reply_language}.
Return ONLY valid JSON according to this schema:
{json.dumps(BEFORE_SEND_SCHEMA, ensure_ascii=False)}

Email subject:
{subject or "No subject"}

Email body:
\"\"\"{body}\"\"\"
"""

__all__ = [
    "EMOTION_SCHEMA",
    "BEFORE_SEND_SCHEMA",
    "build_emotion_prompt",
    "build_before_send_prompt",
    "render_thread",
]
