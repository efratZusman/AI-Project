# -*- coding: utf-8 -*-

ESCALATION_SIGNS = ["!!", "???", "?!", "!?", "!!!!!", "……", "...!!!"]

HE = {
    "negative_roots": [
        "כועס", "כועסת", "כעס", "מתוסכל", "מתוסכלת", "מבאס", "מעצבן", "מרגיז", "נמאס",
        "בעיה", "בעייתי", "בעייתית", "חמור", "חמורה", "לא תקין", "לא תקינה",
        "לא סביר", "בלתי סביר", "לא הגיוני", "הזוי", "מביך", "מיותר", "כשל", "כישלון",
        "ממש לא", "ממש ממש", "פשוט לא", "אין מצב", "אין סיכוי",
    ],
    "pressure_phrases": [
        "עדיין לא", "עדיין לא חזרת", "עדיין לא חזרת אליי", "עדיין לא החזרת תשובה",
        "עדיין לא קיבלתי תשובה", "לא קיבלתי תשובה", "לא ענית", "לא ענית לי",
        "למה לא ענית", "למה אין תשובה", "כמה פעמים", "שלחתי כבר", "אני מחכה כבר",
        "מחפשת אותך", "כל השבוע", "כבר שבוע", "דחוף", "בדחיפות", "מייד", "עכשיו",
        "תבדקו אלף פעמים", "תבדקו מיליון פעמים", "אלף פעמים", "מיליון פעמים",
        "מצפה לתגובה", "תגובה מיידית", "זה חייב", "חייב",
    ],
    "accusation_phrases": [
        "את לא", "אתה לא", "אתם לא",
        "את לא מגיבה", "אתה לא מגיב", "אתם לא מגיבים",
        "את מתעלמת", "אתה מתעלם", "אתם מתעלמים",
        "לא עשית", "לא עשיתם", "לא טיפלת", "לא טיפלתם",
        "הבטחת ולא", "אמרת ולא", "סיכמנו ולא",
        "היית אמור", "היית אמורה", "הייתם אמורים",
        "זה עלייך", "זה עליך", "זה באשמתך", "אשמתך",
    ],
    "insult_phrases": [
        "אני שונאת אותך", "שונא אותך", "שונאת אותך",
        "תתבייש", "תתבישי", "תתבישו",
        "מטופש", "טיפשי", "אידיוט", "אידיוטי", "מגוחך", "פתטי",
        "חוסר אחריות", "חוסר מקצועיות", "זלזול",
        "בושה", "זאת בושה", "ביזיון",
    ],
    "softeners": [
        "בבקשה", "תודה", "תודה רבה", "אשמח", "אם אפשר",
        "כשנוח לך", "כשיתאפשר", "בלי לחץ", "ללא לחץ",
        "מנסה להבין", "רק לוודא", "אשמח לעדכון",
    ],
    "escalation_signs": ESCALATION_SIGNS,
}

EN = {
    "negative_roots": [
        "angry", "upset", "frustrated", "frustrating", "annoying",
        "problem", "issue", "unacceptable", "ridiculous", "unreasonable",
        "not ok", "not okay", "this isn't ok", "this is not ok",
    ],
    "pressure_phrases": [
        "still no answer", "still waiting", "asap", "urgent", "immediately",
        "why didn't you", "you didn't reply", "you never replied",
        "this must", "you have to", "no choice",
    ],
    "accusation_phrases": [
        "you didn't", "you never", "you ignored", "you forgot", "you failed",
        "you were supposed to", "it's your fault",
    ],
    "insult_phrases": [
        "i hate you", "hate you", "shame on you",
        "stupid", "idiotic", "nonsense", "pathetic", "unprofessional",
    ],
    "softeners": ["please", "thanks", "thank you", "whenever you can", "no rush"],
    "escalation_signs": ESCALATION_SIGNS,
}

LEXICON = {"he": HE, "en": EN}
