# backend/ai/prompts.py
import json
from typing import List, Optional
from backend.models import ThreadMessage

# ========= SCHEMAS =========

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
        "risk_level": {"type": "string"},  # expected: low / medium / high
        "risk_factors": {"type": "array", "items": {"type": "string"}},
        "recipient_interpretation": {"type": "string"},
        "send_decision": {"type": "string"},  # expected: send_as_is / send_with_changes / dont_send
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

# ========= HELPERS =========


def _is_hebrew(text: str) -> bool:
    return any("\u0590" <= ch <= "\u05EA" for ch in text)


def render_thread(thread: Optional[List[ThreadMessage]]) -> str:
    """
    הופך את ה-thread לרשימה קצרה שהמודל יכול להבין.
    שים לב: זה רק הקשר תקשורתי, לא מקום לשיפוט.
    """
    if not thread:
        return ""

    out = "Conversation thread (oldest first):\n"
    for msg in thread:  # oldest -> newest
        who = "Sender" if msg.author == "me" else "Recipient"
        out += f"{who}: {msg.text.strip()}\n"
    return out


# ========= LAYER 2 – EMOTION PROMPT =========


def build_emotion_prompt(body: str, language: str = "auto") -> str:
    """
    שכבה 2 – זיהוי טון רגשי בלבד, בלי שיפוט ובלי המלצות.
    משתמשים בזה כדי להחליט האם צריך שכבה 3.
    """
    reply_language = "Hebrew" if _is_hebrew(body) or language == "he" else "English"

    return f"""
You are an EMOTION CLASSIFIER only.

Your job:
- Detect the main emotional tone of the message.
- Do NOT judge politeness, professionalism, or formatting.
- Do NOT decide whether to send the email.
- Do NOT rewrite or give advice.

Allowed emotion values:
- "neutral"
- "positive"
- "tense"
- "frustrated"
- "sensitive"

"confidence" is a number from 0 to 1.

Return ONLY valid JSON in {reply_language} that matches this schema:
{json.dumps(EMOTION_SCHEMA, ensure_ascii=False)}

Message to analyze:
\"\"\"{body}\"\"\"
"""


# ========= LAYER 3 – FULL BEFORE-SEND ANALYSIS PROMPT =========


def build_before_send_prompt(
    body: str,
    subject: Optional[str],
    language: str,
    is_reply: bool,
    thread_context: Optional[List[ThreadMessage]],
) -> str:
    """
    שכבה 3 – ניתוח מלא. מגיעים לכאן רק במקרים שצריך.
    הדגש: יועץ תקשורת אנושי, לא "שומר סף מחמיר".
    """
    reply_language = "Hebrew" if _is_hebrew(body) or language == "he" else "English"
    thread_block = render_thread(thread_context) if is_reply and thread_context else ""

    return f"""
You are a **communication coach**, not a strict moderator.

Your goals:
- Help the sender communicate clearly, respectfully, and effectively.
- Assume most emails are basically okay.
- Only mark something as "high" risk when there is a real chance
  of misunderstanding, conflict escalation, or damage to trust.

Context:
- This tool is used *before sending* an email.
- Sometimes it is a fresh email, sometimes a reply in an ongoing thread.
- You may see up to a few recent messages from the thread for context.

Thread history (if any):
{thread_block or "No prior thread shown."}

Email subject:
{subject or "No subject"}

Email body:
\"\"\"{body}\"\"\"

Important guidelines:
- Be lenient with normal day‑to‑day messages.
- Do NOT police minor wording or personal style.
- Focus on:
  - tone that might sound harsh, accusatory, or impatient,
  - ambiguous requests that could confuse the recipient,
  - sensitive topics (money, performance, complaints, deadlines),
  - replies written in visible frustration.

Fields to return:

- intent
  * Short description of what the sender is trying to achieve.
- risk_level
  * One of: "low", "medium", "high".
  * "low" = almost certainly fine.
  * "medium" = small risk; a softer phrasing could help.
  * "high" = real risk of conflict, escalation, or hurt feelings.
- risk_factors
  * Concrete reasons for the risk_level (if any).
- recipient_interpretation
  * How the recipient is likely to read this email, given the thread.
- send_decision
  * One of:
    - "send_as_is" – safe enough to send.
    - "send_with_changes" – suggest a safer rephrasing.
    - "dont_send" – recommend not sending as written.
- follow_up_needed
  * Whether the sender will probably need to follow up later.
- follow_up_reason
  * Optional explanation.
- safer_subject
  * Optional alternative subject line (same language as the email).
- safer_body
  * A safer, clearer version of the email in the same language.
  * Keep it short, human, and natural – not robotic.
- notes_for_sender
  * Optional list of friendly tips or observations.

Return ONLY valid JSON in {reply_language} that matches this schema:
{json.dumps(BEFORE_SEND_SCHEMA, ensure_ascii=False)}
"""
