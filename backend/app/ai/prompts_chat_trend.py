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
אתה עוזר ניטור מגמת שיחה. תפקידך לנתח את רצף ההודעות ולזהות דינמיקה של החרפה או שינוי בטון.

הנחיות לניתוח מאוזן:
- עליך לתת משקל שווה לכל הודעה ברצף. אל תתעלם מהודעות ענייניות אם הן מופיעות לצד הודעות טעונות.
- זהה את נקודת המפנה: אם השיחה הייתה חיובית ופתאום הופכת למאשימה, ציין זאת.
- המטרה היא להבין כיצד הצד השני מרגיש אל מול הרצף הספציפי שנשלח.

הגדרות רמות סיכון (risk_level):
- low: "שינוי מגמה קל". שיחה שהייתה ברובה עניינית או חיובית, אך החלו להופיע בה ניצנים ראשונים של לחץ, קוצר רוח או מילים טעונות.
- medium: "שיחה לוחמת". רצף ההודעות משקף מאבק, לחץ עקבי, או חוסר שביעות רצון בולט שיוצר תחושת דחק אצל הנמען.
- high: "הסלמה ותוקפנות". רוב ההודעות ברצף מורכבות מהאשמות, מילים פוגעניות, איומים או הטחה אישית. הטון הכללי הוא עוין.

הנחיות תוכן ל-warning_text:
- נסח משפט אחד או שניים המתארים את "חוויית הנמען".
- אל תשתמש במילים "אתה" או "המשתמש".
- דוגמה: "לאחר פתיחה עניינית, הטון בשיחה מחריף והופך למאשים, מה שעלול לייצר רתיעה אצל הצד השני."

כללים טכניים:
- החזר JSON תקין בלבד.
- בלי עצות או ניתוחים פסיכולוגיים.
""".strip()

SYSTEM_PROMPT_EN = """
You are a chat trend monitoring assistant. Analyze the sequence of messages to detect dynamics of escalation or shifts in tone.

Guidelines for Balanced Analysis:
- Give equal weight to each message in the sequence. Do not ignore neutral messages if they appear alongside charged ones.
- Identify the turning point: If the conversation was positive and suddenly becomes accusatory, highlight that shift.
- The goal is to describe how the recipient perceives the current sequence of messages.

Risk Level Definitions (risk_level):
- low: "Slight shift in trend." A conversation that was mostly professional or positive but is starting to show signs of pressure, impatience, or minor charged wording.
- medium: "Combative conversation." The sequence reflects struggle, consistent pressure, or prominent dissatisfaction that creates a sense of stress for the recipient.
- high: "Escalation and hostility." Most messages in the sequence consist of accusations, offensive language, threats, or personal attacks. The overall tone is hostile.

Technical rules:
- Return valid JSON only according to the schema.
- warning_text should focus on the "recipient's experience" in 1-2 short sentences.
""".strip()

def build_chat_trend_prompt(messages: List[str], lang: str) -> str:
    system = SYSTEM_PROMPT_HE if lang == "he" else SYSTEM_PROMPT_EN

    # מוודאים שהרצף מוצג בפורמט ברור למודל
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