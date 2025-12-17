// extension/shared/lexicon.js
// לקסיקון משותף ל-client (צ'אט) ולבדיקות מהירות.
// מקביל ל-backend/ai/lexicon.py (מומלץ לשמור אותם מסונכרנים).

export const hebrewLexicon = {
  anger: [
    "כועס","כועסת","כעס","מעצבן","מרגיז","מתסכל","מבאס",
    "נמאס","די כבר","ממש לא בסדר","לא בסדר","זה לא תקין","לא תקין",
    "זה הזוי","הזוי","מטופש","טיפשי","מביך","חמור","חמורה",
    "בלתי נסבל","בלתי סביר","לא הגיוני"
  ],
  pressure: [
    "עדיין לא","עדיין לא חזרת","עדיין לא החזרת","עדיין אין תשובה",
    "לא קיבלתי תשובה","לא ענית","לא ענית לי","למה לא ענית",
    "מחפשת אותך","אני מחכה","כבר שבוע","כל השבוע",
    "דחוף","בדחיפות","מייד","עכשיו","asap",
    "תבדקו אלף פעמים","תבדקו מיליון פעמים","אלף פעמים","מיליון פעמים",
    "זה חייב","חייב","אין מצב","אין סיכוי"
  ],
  accusation: [
    "את לא","אתה לא","אתם לא",
    "את לא מגיבה","אתה לא מגיב","אתם לא מגיבים",
    "את מתעלמת","אתה מתעלם","אתם מתעלמים",
    "לא עשית","לא עשיתם","לא טיפלת","לא טיפלתם",
    "הבטחת ולא","אמרת ולא","סיכמנו ולא","היית אמור","היית אמורה",
    "זה עלייך","זה באשמתך","אשמתך"
  ],
  insultSensitive: [
    "מטופש","טיפשי","אידיוטי","מגוחך","פתטי",
    "חוסר אחריות","חוסר מקצועיות","עצלנות","זלזול",
    "בזבוז זמן","בזבזת לי זמן","ביזבוז זמן"
  ],
  escalationSigns: ["!!", "???", "?!", "!?", "!!!!!"],
  softeners: [
    "בבקשה","תודה","תודה רבה","אשמח","אם אפשר","כשנוח לך",
    "בלי לחץ","מנסה להבין","רק לוודא","אשמח לעדכון"
  ],
};

export const englishLexicon = {
  anger: ["angry","frustrated","this is not ok","unacceptable","ridiculous","upset","not ok","not okay"],
  pressure: ["still no answer","still waiting","asap","urgent","immediately","why didn't you","you didn't reply","you never replied"],
  accusation: ["you didn't","you never","you ignored","you forgot","you failed","you were supposed to","it's your fault"],
  insultSensitive: ["stupid","idiotic","nonsense","pathetic","unprofessional"],
  escalationSigns: ["!!", "???", "?!", "!?", "!!!!!"],
  softeners: ["please","thanks","thank you","whenever you can","no rush"],
};

export function quickRiskScoreClient(text, lang = "he") {
  if (!text || !text.trim()) return { score: 0, reasons: [] };

  const t = text.trim();
  const lower = t.toLowerCase();
  const lex = lang === "en" ? englishLexicon : hebrewLexicon;

  let score = 0;
  const reasons = [];

  if (t.length < 25) { score += 1; reasons.push("טקסט קצר מאוד"); }

  if (lex.escalationSigns.some((m) => t.includes(m))) {
    score += 2; reasons.push("סימני הסלמה");
  }

  const hitList = (arr) => arr.filter(x => lower.includes(String(x).toLowerCase())).slice(0,3);

  const angerHits = hitList(lex.anger);
  if (angerHits.length) { score += Math.min(angerHits.length,3)*2; reasons.push(`כעס/תסכול (${angerHits.join(", ")})`); }

  const pressureHits = hitList(lex.pressure);
  if (pressureHits.length) { score += Math.min(pressureHits.length,3)*2 + 1; reasons.push(`לחץ/דחיפות (${pressureHits.join(", ")})`); }

  const accHits = hitList(lex.accusation);
  if (accHits.length) { score += Math.min(accHits.length,3)*2 + 1; reasons.push(`האשמה (${accHits.join(", ")})`); }

  const insHits = hitList(lex.insultSensitive);
  if (insHits.length) { score += Math.min(insHits.length,2)*3; reasons.push(`מילים מעליבות/רגישות (${insHits.join(", ")})`); }

  if (lex.softeners.some((s) => lower.includes(String(s).toLowerCase()))) {
    score -= 1; reasons.push("מרככים קיימים");
  }

  score = Math.max(score, 0);
  return { score, reasons: reasons.slice(0,6) };
}
