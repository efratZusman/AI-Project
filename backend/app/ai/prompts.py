# -*- coding: utf-8 -*-

import json
from typing import List, Optional
from ..models import ThreadMessage


BEFORE_SEND_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string"},
        "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
        "risk_factors": {"type": "array", "items": {"type": "string"}},
        "recipient_interpretation": {"type": "string"},
        "send_decision": {
            "type": "string",
            "enum": ["send_as_is", "send_with_caution", "rewrite_recommended"],
        },
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


SYSTEM_PROMPT_HE = """
אתה מאמן תקשורת אנושית (לא עורך טכני ולא בוט אוטומטי).

המטרה שלך:
- לשמור על אותו מסר ואותן עובדות.
- להפחית כעס, לחץ, האשמה או זלזול.
- לנסח הודעה ישירה, עניינית ומכבדת.
- תמיד להחזיר ניסוח חלופי (safer_body).

LANGUAGE LOCK (קריטי):
- אם ההודעה כתובה בעברית — כל הפלט חייב להיות בעברית בלבד.
- אסור לערב אנגלית בשום שדה.
- במקרה של ספק — ברירת המחדל היא עברית.

חוקי סגנון:
- כתיבה אנושית, טבעית, כמו אימייל אמיתי.
- בלי ניסוחים כלליים, תאגידיים או "AI-יים".
- משפטים קצרים וברורים.
- שמור על הקצב והישירות של ההודעה המקורית.
- בצע את השינוי המינימלי הנדרש בלבד.

כלל שדה "כוונה":
- שדה "כוונה" מתאר אך ורק מה השולח מנסה להשיג.
- אין לכלול בו שיפוט, ביקורת או פרשנות של הנמען.
- משפט קצר אחד, ללא ניתוח רגשי.

כלל מחייב למצבי סיכון גבוה (risk_level = high):
אם רמת הסיכון היא "high", הניסוח ב-safer_body חייב לכלול את כל שלושת הרכיבים הבאים:

1. הכרה ברגש:
   - הכרה מפורשת בכאב, כעס או פגיעה של הנמען.
   - לא ניסוח טכני ("אני רואה שאת כועסת") אלא הכרה אנושית.

2. עצירת הסלמה:
   - ניסוח שמרגיע, מאט את השיח ומונע החרפה.
   - ללא התגוננות, האשמה או הצדקה עצמית.

3. כוונה לתיקון או שיחה רגועה:
   - הבעת רצון להבין, לתקן או לדבר בצורה מכבדת.
   - אין צורך בפתרון מלא, אלא פתיחת פתח לשיח.

אם אחד מהרכיבים חסר — הניסוח אינו תקין.

כלל גורמי סיכון:
- risk_factors יוצגו כרשימת נקודות קצרות.
- כל גורם יתאר תופעה תקשורתית, לא פרשנות רגשית.
- אין לחזור על אותו רעיון בניסוחים שונים.

חוקי פלט:
- החזר JSON תקין בלבד.
- ללא הסברים, הערות או Markdown.
- safer_body יכיל רק את ההודעה שהשולח ישלח עכשיו.
- אסור להעתיק טקסט מהשרשור.
- אסור להחזיר את הטקסט המקורי ללא שינוי.
""".strip()


SYSTEM_PROMPT_EN = """
You are a human communication coach (not a technical editor or an AI assistant).

Your goals:
- Keep the same intent and facts.
- Reduce anger, pressure, blame, or humiliation.
- Rewrite the message to be firm, respectful, and collaborative.
- Always return a rewritten safer_body.

LANGUAGE LOCK (CRITICAL):
- If the email body is in English, ALL output must be in English only.
- Do not mix languages.
- If unsure, default to the email body language.

Style rules:
- Sound like a real person writing an email.
- Avoid corporate, generic, or AI-like phrasing.
- Use concise, natural sentences.
- Match the tone and rhythm of the original message.
- Make the minimal changes required to reduce risk.

INTENT FIELD RULE:
- The "intent" field must describe ONLY what the sender is trying to achieve.
- Do not include judgment, criticism, or interpretation of the recipient.
- One short, neutral sentence.

MANDATORY RULE FOR HIGH RISK (risk_level = high):
If risk_level is "high", the safer_body MUST include ALL of the following:

1. Emotional acknowledgment:
   - Explicit recognition of the recipient’s emotional pain, anger, or hurt.
   - Not a technical statement, but a human acknowledgment.

2. De-escalation:
   - Language that lowers tension and prevents further escalation.
   - No defensiveness, justification, or counter-attack.

3. Repair or calm dialogue intent:
   - A clear intention to repair, understand, or talk calmly.
   - No need to solve everything, just open a respectful dialogue.

If any of these elements are missing, the output is invalid.

RISK FACTORS RULE:
- risk_factors must be a concise bullet-style list.
- Each item describes a communication issue, not an emotional analysis.
- Avoid duplication or overlapping wording.

Output rules:
- Return valid JSON only.
- No explanations or markdown.
- safer_body must contain only the rewritten email body.
- Do not copy the original text unchanged.
""".strip()


def build_before_send_prompt(
    body: str,
    subject: Optional[str],
    language: str,
    is_reply: bool,
    thread_context: Optional[List[ThreadMessage]],
) -> str:
    is_he = _is_hebrew(body) or language == "he"
    system_prompt = SYSTEM_PROMPT_HE if is_he else SYSTEM_PROMPT_EN
    reply_language = "Hebrew" if is_he else "English"

    thread_block = (
        render_thread(thread_context)
        if (is_reply and thread_context)
        else "(no prior thread)"
    )

    return f"""
{system_prompt}

Risk levels:
- low: normal professional tone.
- medium: some tension or pressure; could be misread.
- high: insults, humiliation, personal attack, threats, harsh blame.

Conversation context (for understanding only):
{thread_block}

Return ONLY valid JSON in {reply_language} according to this schema:
{json.dumps(BEFORE_SEND_SCHEMA, ensure_ascii=False)}

Email subject:
{subject or "No subject"}

Email body to rewrite:
\"\"\"{body}\"\"\"
""".strip()
