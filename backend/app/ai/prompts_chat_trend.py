# backend/app/ai/prompts_chat_trend.py
# -*- coding: utf-8 -*-
import json
from typing import List

CHAT_TREND_SCHEMA = {
    "type": "object",
    "properties": {
        "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
        "warning_text": {"type": "string"},
    },
    "required": ["risk_level", "warning_text"],
}

SYSTEM_PROMPT_HE = """
אתה עוזר ניטור מגמת שיחה.
המטרה: להחזיר אזהרה קצרה (משפט-שניים) אם תוכן ההודעות מצביע על נטייה לקיצוניות,
בין אם לשליליות (לחץ, הסלמה, תוקפנות) ובין אם לחיוב מוגזם או אינטנסיבי.

הנחיות תוכן:
- התייחס אך ורק לאופי, לטון ולכיוון הכללי של ההודעות.
- מותר לציין כיצד רצף ההודעות עשוי להישמע או להיתפס בצד השני של השיחה.
- אל תתייחס למשתמש, לדובר, או לכוונות אישיות.
- אל תשתמש בלשון פנייה ("אתה", "המשתמש").
- נסח באופן ניטרלי ותיאורי, המתמקד ברוח ובמגמה של השיחה בלבד.

כללים טכניים:
- החזר JSON תקין בלבד.
- warning_text בעברית בלבד.
- warning_text קצר: 1–2 משפטים.
- בלי עצות, בלי ניתוחים, בלי פירוט.
- אם אין נטייה לקיצוניות או סיכון: החזר warning_text ריק "" ורמת סיכון low.
""".strip()

SYSTEM_PROMPT_EN = """
You are a chat trend monitoring assistant.
Goal: return a very short warning (1–2 sentences) if the message content shows a trend toward extremity,
either negative (pressure, escalation, hostility) or overly intense positive tone.

Content guidelines:
- Refer only to the tone, wording, and overall direction of the messages.
- You may describe how the sequence of messages might sound or be perceived by the other side.
- Do not refer to any user, speaker, or personal intent.
- Do not address anyone directly ("you", "the user").
- Phrase the warning in a neutral, descriptive manner about the conversation trend only.

Technical rules:
- Return valid JSON only.
- warning_text in English only.
- warning_text must be short: 1–2 sentences.
- If no extremity or risk is detected: warning_text must be empty "" and risk_level low.
""".strip()

def build_chat_trend_prompt(messages: List[str], lang: str) -> str:
    system = SYSTEM_PROMPT_HE if lang == "he" else SYSTEM_PROMPT_EN

    # שומרים על זה קצר וברור כדי שהמודל לא יסטה לטקסט חופשי
    convo = "\n".join(
        [f"- {m.strip()}" for m in messages if (m or "").strip()][:12]
    )

    return f"""
{system}

Return ONLY valid JSON according to this schema:
{json.dumps(CHAT_TREND_SCHEMA, ensure_ascii=False)}

Last messages (most recent last):
{convo}
""".strip()
