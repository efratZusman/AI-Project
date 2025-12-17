# backend/ai/lexicon.py
# -*- coding: utf-8 -*-

"""
לקסיקון משותף לזיהוי מהיר של טון/סיכון (Layer 1).
מטרות:
- כיסוי רחב מספיק כדי שלא "ניפול" ל-Layer 1 בטעות
- עדיין מהיר (O(n))
- ניתן לשיתוף לוגי עם לקסיקון ה-extension (extension/shared/lexicon.js)
"""

# מילים/שורשים של כעס/תסכול
ANGER_FRUSTRATION_HE = [
    "כועס", "כועסת", "כעס", "מעצבן", "מרגיז", "מתסכל", "מבאס",
    "נמאס", "די כבר", "ממש לא בסדר", "לא בסדר", "זה לא תקין", "לא תקין",
    "זה הזוי", "הזוי", "מטופש", "טיפשי", "מביך", "חמור", "חמורה",
    "פשוט לא", "ממש לא", "בלתי נסבל", "בלתי סביר", "לא הגיוני"
]

# ביטויי לחץ / דחיפות / אולטימטום
PRESSURE_PHRASES_HE = [
    "עדיין לא", "עדיין לא חזרת", "עדיין לא החזרת", "עדיין אין תשובה",
    "לא קיבלתי תשובה", "לא ענית", "לא ענית לי", "למה לא ענית",
    "מחפשת אותך", "אני מחכה", "כבר שבוע", "כל השבוע",
    "דחוף", "בדחיפות", "מייד", "עכשיו", "ASAP",
    "תבדקו אלף פעמים", "תבדקו מיליון פעמים", "אלף פעמים", "מיליון פעמים",
    "זה חייב", "חייב", "אין מצב", "אין סיכוי", "מבחינתי זה"
]

# האשמה ישירה / מתקפה אישית / ייחוס כוונה שלילית
ACCUSATION_PATTERNS_HE = [
    "את לא", "אתה לא", "אתם לא",
    "את לא מגיבה", "אתה לא מגיב", "אתם לא מגיבים",
    "את מתעלמת", "אתה מתעלם", "אתם מתעלמים",
    "לא עשית", "לא עשיתם", "לא טיפלת", "לא טיפלתם",
    "הבטחת ולא", "אמרת ולא", "סיכמנו ולא", "היית אמור", "היית אמורה",
    "זה עלייך", "זה באשמתך", "אשמתך"
]

# נושאים רגישים/מעליבים
INSULT_SENSITIVE_HE = [
    "מטופש", "טיפשי", "אידיוטי", "מגוחך", "פתטי",
    "חוסר אחריות", "חוסר מקצועיות", "עצלנות", "זלזול",
    "בזבוז זמן", "בזבזת לי זמן", "ביזבוז זמן"
]

# סימני הסלמה
ESCALATION_SIGNS = [
    "!!", "???", "?!", "!?", "!!!!!"
]

# מרככים (מוריד מעט סיכון)
SOFTENERS_HE = [
    "בבקשה", "תודה", "תודה רבה", "אשמח", "אם אפשר", "כשנוח לך",
    "בלי לחץ", "מנסה להבין", "רק לוודא", "אשמח לעדכון"
]

# --- English MVP ---
ANGER_FRUSTRATION_EN = [
    "angry", "frustrated", "this is not ok", "this isn't ok", "unacceptable",
    "ridiculous", "annoying", "upset", "not okay", "not ok"
]

PRESSURE_PHRASES_EN = [
    "still no answer", "still waiting", "asap", "urgent", "immediately",
    "why didn't you", "you didn't reply", "you never replied",
    "this must", "you have to", "no choice"
]

ACCUSATION_PATTERNS_EN = [
    "you didn't", "you never", "you ignored", "you forgot", "you failed",
    "you were supposed to", "it's your fault"
]

INSULT_SENSITIVE_EN = [
    "stupid", "idiotic", "nonsense", "pathetic", "unprofessional"
]

SOFTENERS_EN = [
    "please", "thanks", "thank you", "whenever you can", "no rush"
]

LEXICON = {
    "he": {
        "anger": ANGER_FRUSTRATION_HE,
        "pressure": PRESSURE_PHRASES_HE,
        "accusation": ACCUSATION_PATTERNS_HE,
        "insult_sensitive": INSULT_SENSITIVE_HE,
        "escalation_signs": ESCALATION_SIGNS,
        "softeners": SOFTENERS_HE,
    },
    "en": {
        "anger": ANGER_FRUSTRATION_EN,
        "pressure": PRESSURE_PHRASES_EN,
        "accusation": ACCUSATION_PATTERNS_EN,
        "insult_sensitive": INSULT_SENSITIVE_EN,
        "escalation_signs": ESCALATION_SIGNS,
        "softeners": SOFTENERS_EN,
    },
}
