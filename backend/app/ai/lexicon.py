# -*- coding: utf-8 -*-

ESCALATION_SIGNS = ["!!!!", "???", "?!", "!?", "!!!!!", "……", "...!!!"]

HE = {
    "negative_roots": [
        # כעס ותסכול
        "כועס", "כועסת", "כעס",
        "מתוסכל", "תסכול",
        "עצבני", "עצבנות",
        "מעצבן", "מרגיז",
        "נמאס", "נמאס לי",

        # בעייתיות ושיפוט
        "בעיה", "בעייתי", "בעייתית",
        "חמור", "חמורה",
        "לא תקין", "לא תקינה",
        "לא סביר", "בלתי סביר",
        "לא הגיוני", "הזוי",
        "מביך", "מיותר",
        "כשל", "כישלון",

        # ביטויי שלילה חזקים
        "ממש לא", "ממש ממש",
        "פשוט לא",
        "אין מצב", "אין סיכוי",
        "לא מקובל", "לא acceptable",
    ],

    "pressure_phrases": [
        # דחיפות ולחץ
        "עדיין לא", "עוד לא",
        "לא חזרת", "לא חזרת אליי",
        "לא קיבלתי תשובה", "לא ענית",
        "למה לא ענית", "למה אין תשובה",
        "כמה פעמים",
        "שלחתי כבר",
        "אני מחכה", "מחכה כבר",
        "כבר שבוע", "כבר ימים",

        "דחוף", "בדחיפות",
        "מייד", "מיידית", "עכשיו",
        "זה חייב", "חייב",
        "מצפה לתגובה", "תגובה מיידית",

        # הגזמה
        "אלף פעמים", "מיליון פעמים",
    ],

    "accusation_phrases": [
        # האשמה ישירה
        "את לא", "אתה לא", "אתם לא",
        "את לא מגיבה", "אתה לא מגיב",
        "את מתעלמת", "אתה מתעלם",

        "לא עשית", "לא טיפלת",
        "לא בדקת", "לא עדכנת",
        "הבטחת ולא", "אמרת ולא",
        "סיכמנו ולא",

        "היית אמור", "היית אמורה",
        "זה עלייך", "זה עליך",
        "באשמתך", "אשמתך",
    ],

    "insult_phrases": [
        # עלבונות וזלזול
        "שונא אותך", "שונאת אותך",
        "תתבייש", "תתבישי",
        "מטופש", "טיפשי",
        "אידיוט", "אידיוטי",
        "מגוחך", "פתטי",

        "חוסר אחריות",
        "חוסר מקצועיות",
        "זלזול",
        "בושה", "ביזיון",
    ],

    "explicit_emotion_phrases": [
        # התפרצות רגשית
        "די כבר", "די נו", "די!",
        "נמאס לי",
        "אין לי סבלנות",
        "כמה אפשר",
        "נו באמת",

        "אני כועסת", "אני כועס",
        "אין לי כוח",
        "תעני כבר",
        "למה את לא עונה",
    ],

    "softeners": [
        # מרככים (דווקא חשוב להשאיר)
        "בבקשה", "תודה", "תודה רבה",
        "אשמח", "אם אפשר",
        "כשנוח לך", "כשיתאפשר",
        "בלי לחץ", "ללא לחץ",
        "רק לבדוק", "רק לוודא",
        "אשמח לעדכון",
    ],

    "escalation_signs": ESCALATION_SIGNS,
}

EN = {
    "negative_roots": [
        "angry", "anger",
        "upset",
        "frustrat",   # frustrated / frustrating
        "annoy",
        "problem", "issue",
        "unacceptable",
        "ridiculous",
        "unreasonable",
        "not ok", "not okay",
        "this isn't ok",
    ],

    "pressure_phrases": [
        "still no answer",
        "still waiting",
        "asap", "urgent",
        "immediately", "right now",
        "why didn't you",
        "you didn't reply",
        "you never replied",
        "this must",
        "you have to",
        "no choice",
    ],

    "accusation_phrases": [
        "you didn't",
        "you never",
        "you ignored",
        "you forgot",
        "you failed",
        "you were supposed to",
        "it's your fault",
    ],

    "insult_phrases": [
        "i hate you", "hate you",
        "shame on you",
        "stupid", "idiotic",
        "pathetic",
        "unprofessional",
    ],

    "explicit_emotion_phrases": [
        "enough already",
        "i'm angry", "i am angry",
        "i'm upset",
        "fed up",
        "what's going on",
        "why aren't you replying",
        "answer already",
    ],

    "softeners": [
        "please", "thanks", "thank you",
        "whenever you can",
        "no rush",
        "just checking",
    ],

    "escalation_signs": ESCALATION_SIGNS,
}


LEXICON = {"he": HE, "en": EN}
