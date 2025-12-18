# -*- coding: utf-8 -*-

import json
from typing import List, Optional
from backend.models import ThreadMessage

BEFORE_SEND_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string"},
        "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
        "risk_factors": {"type": "array", "items": {"type": "string"}},
        "recipient_interpretation": {"type": "string"},
        "send_decision": {"type": "string", "enum": ["send_as_is", "send_with_caution", "rewrite_recommended"]},
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
    if not thread:
        return "(no prior thread)"
    out = "Conversation thread (for context only; DO NOT copy into output):\n"
    for msg in thread[-3:]:
        who = "Sender" if msg.author == "me" else "Recipient"
        snippet = (msg.text or "").strip().replace("\n", " ")
        if len(snippet) > 240:
            snippet = snippet[:240] + "..."
        out += f"- {who}: {snippet}\n"
    return out

def build_before_send_prompt(
    body: str,
    subject: Optional[str],
    language: str,
    is_reply: bool,
    thread_context: Optional[List[ThreadMessage]],
) -> str:
    reply_language = "Hebrew" if _is_hebrew(body) or language == "he" else "English"
    thread_block = render_thread(thread_context) if (is_reply and thread_context) else "(no prior thread)"

    return f"""
You are a communication coach (not a strict reviewer).

Goal:
- Keep the SAME intent and key facts.
- Reduce anger, blame, humiliation, and pressure.
- Make it firm but respectful and collaborative.
- Always provide a rewritten safer_body.

Hard rules:
- אתה חייב לענות בשפה שבה נכתבה ההודעה המקורית אם היא בעברית אתה חייב לענות בשפה העברית, אחרת באנגלית.
- Return ONLY valid JSON. No markdown. No explanations.
- NEVER include the thread / quoted emails / "On ... wrote:" / "Forwarded message" / lines starting with ">" inside safer_body.
- safer_body must contain ONLY the rewritten message the sender will send now.
- Do NOT copy any of the thread text into safer_body.
- Do NOT return the original body unchanged.

Risk rules:
- low: normal professional tone.
- medium: some tension/pressure; could be misread.
- high: insults, humiliation, personal attack, threats, harsh blame.

Conversation context (for understanding only):
{thread_block}

Return ONLY valid JSON in {reply_language} according to this schema:
{json.dumps(BEFORE_SEND_SCHEMA, ensure_ascii=False)}

Email subject:
{subject or "No subject"}

Email body to rewrite:
\"\"\"{body}\"\"\"
"""
