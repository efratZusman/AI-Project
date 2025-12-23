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
אתה עוזר ניטור מגמת שיחה. תפקידך לנתח את רצף ההודעות ולזהות שינויי טון ודפוסים תקשורתיים בעייתיים.

עקרונות ניתוח:
- יש להתחשב בכך שהרצף כבר סונן מראש לביטויים טעונים.
- התייחס לדפוסים תקשורתיים קונקרטיים, לא לתחושות כלליות.
- חפש מעבר מהצגת טענות להתנהגות תקשורתית בעייתית כגון שיפוט אישי, חזרה על דרישות ללא התייחסות, קיצור תגובות או ביטול דברי הצד השני.

כללי בחירת risk_level (בהתחשב בסינון המוקדם):
- low: כאשר רק 1–2 הודעות מציגות דפוס בעייתי ושאר הרצף עדיין כולל הסברים או שיתוף פעולה.
- medium: כאשר דפוסים בעייתיים חוזרים במספר הודעות ומשפיעים על הטון הכללי, גם אם אינם הרוב המוחלט.
- high: רק כאשר הדפוסים הבעייתיים שולטים באינטראקציה ומגדירים את רוב ההתנהלות ברצף.

מבנה חובה ל-warning_text:
- שני משפטים בלבד.
- המשפט הראשון מתאר דפוס תקשורתי קונקרטי שמופיע ברצף (למשל מעבר משיח ענייני לשיפוט אישי, חזרה על דרישות בלי מענה, היעלמות הסברים).
- המשפט השני מתאר תוצאה מוחשית שתתרחש אם הדפוס יימשך (כגון הפסקת שיתוף פעולה, סגירות רגשית או נטישת הדיאלוג).
- אין להשתמש במילים כלליות או מופשטות.
- אין להשתמש במילה "מסלים" או בכל נטייה שלה ("הסלמה", "להסלים" וכדומה).
- אין להשתמש במילים "אתה" או "המשתמש".

כללים טכניים:
- החזר JSON תקין בלבד לפי הסכימה.
- בלי עצות או ניתוחים פסיכולוגיים.
""".strip()

SYSTEM_PROMPT_EN = """
You are a chat trend monitoring assistant. Analyze the sequence of messages to detect problematic communication patterns and shifts in tone.

Analysis principles:
- Take into account that the sequence was already pre-filtered for charged language.
- Focus on concrete communication behaviors, not vague feelings.
- Look for shifts such as moving from arguments to personal judgment, repeating demands without addressing replies, shortening responses, or dropping explanations.

Risk level selection rules (considering pre-filtering):
- low: only 1–2 messages show problematic patterns and the rest remain explanatory or cooperative.
- medium: problematic patterns appear repeatedly and shape the general tone, even if they are not the majority.
- high: problematic patterns dominate the interaction and define most of the communicative behavior in the sequence.

warning_text structure rules:
- Exactly two sentences.
- First sentence describes a concrete communication pattern in the sequence.
- Second sentence describes a tangible outcome if the pattern continues.
- Do not use abstract wording.
- Do not use the words "escalate", "escalation", or any of their variations.
- Do not use "you" or "the user".

Technical rules:
- Return valid JSON only according to the schema.
""".strip()


def build_chat_trend_prompt(messages: List[str], lang: str) -> str:
    system = SYSTEM_PROMPT_HE if lang == "he" else SYSTEM_PROMPT_EN

    convo = "\n".join(
        [f"הודעה {i+1}: {m.strip()}" for i, m in enumerate(messages) if (m or "").strip()][-12:]
    )

    return f"""
{system}

Return ONLY valid JSON according to this schema:
{json.dumps(CHAT_TREND_SCHEMA, ensure_ascii=False)}

Sequence of messages for analysis (the last message is the most recent):
{convo}
""".strip()
