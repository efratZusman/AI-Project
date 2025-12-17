import json
from typing import List, Optional
from backend.models import ThreadMessage


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
        "risk_level": {"type": "string"},
        "risk_factors": {"type": "array", "items": {"type": "string"}},
        "recipient_interpretation": {"type": "string"},
        "send_decision": {"type": "string"},
        "follow_up_needed": {"type": "boolean"},
        "follow_up_reason": {"type": "string"},
        "safer_subject": {"type": "string"},
        "safer_body": {"type": "string"},
        "notes_for_sender": {
            "type": "array",
            "items": {"type": "string"},
        },
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


def render_thread(thread: Optional[List[ThreadMessage]]) -> str:
    if not thread:
        return ""

    out = "Conversation context:\n"
    for msg in reversed(thread):
        who = "Sender" if msg.author == "me" else "Recipient"
        out += f"{who}: {msg.text.strip()}\n"

    return out


def build_emotion_prompt(body: str, language: str = "auto") -> str:
    is_hebrew = any("\u0590" <= ch <= "\u05EA" for ch in body)
    reply_language = "Hebrew" if is_hebrew or language == "he" else "English"

    return f"""
Classify emotional tone only.
Do NOT judge politeness or length.

Return ONLY JSON in {reply_language}.

Schema:
{json.dumps(EMOTION_SCHEMA)}

Message:
\"\"\"{body}\"\"\"
"""


def build_before_send_prompt(
    body: str,
    subject: Optional[str],
    language: str,
    is_reply: bool,
    thread_context: Optional[List[ThreadMessage]],
) -> str:
    is_hebrew = any("\u0590" <= ch <= "\u05EA" for ch in body)
    reply_language = "Hebrew" if is_hebrew or language == "he" else "English"

    thread_block = render_thread(thread_context) if is_reply else ""

    return f"""
You are an advanced communication risk analyzer.

Reply ONLY in {reply_language}.
Return ONLY valid JSON.

{thread_block}

Email subject:
{subject or "No subject"}

Email body:
\"\"\"{body}\"\"\"

Schema:
{json.dumps(BEFORE_SEND_SCHEMA)}
"""
