export const LEXICON = {
  he: {
    negative_roots: [
      "כועס","כועסת","כעס","מתוסכל","מתוסכלת","מבאס","מעצבן","מרגיז","נמאס",
      "בעיה","בעייתי","בעייתית","חמור","חמורה","לא תקין","לא תקינה","לא סביר","בלתי סביר",
      "לא הגיוני","הזוי","מביך","מיותר","כשל","כישלון","ממש לא","ממש ממש","פשוט לא","אין מצב","אין סיכוי"
    ],
    pressure_phrases: [
      "עדיין לא","עדיין לא חזרת","עדיין לא החזרת תשובה","עדיין לא קיבלתי תשובה",
      "לא קיבלתי תשובה","לא ענית","לא ענית לי","למה לא ענית","כמה פעמים","שלחתי כבר",
      "אני מחכה כבר","מחפשת אותך","כל השבוע","כבר שבוע","דחוף","בדחיפות","מייד","עכשיו",
      "תבדקו אלף פעמים","תבדקו מיליון פעמים","אלף פעמים","מיליון פעמים","מצפה לתגובה","תגובה מיידית","זה חייב","חייב"
    ],
    accusation_phrases: [
      "את לא","אתה לא","אתם לא","את לא מגיבה","את מתעלמת","לא עשית","לא טיפלת",
      "הבטחת ולא","אמרת ולא","סיכמנו ולא","היית אמור","היית אמורה","זה עלייך","זה באשמתך","אשמתך"
    ],
    insult_phrases: [
      "אני שונאת אותך","שונאת אותך","שונא אותך","תתבייש","תתבישי","תתבישו",
      "מטופש","טיפשי","אידיוט","אידיוטי","מגוחך","פתטי","חוסר אחריות","חוסר מקצועיות","זלזול","בושה","זאת בושה","ביזיון"
    ],
    softeners: ["בבקשה","תודה","תודה רבה","אשמח","אם אפשר","כשנוח לך","כשיתאפשר","בלי לחץ","ללא לחץ","מנסה להבין","רק לוודא","אשמח לעדכון"],
    escalation_signs: ["!!","???","?!","!?","!!!!!","……","...!!!"]
  },
  en: {
    negative_roots: ["angry","upset","frustrated","frustrating","annoying","problem","issue","unacceptable","ridiculous","unreasonable","not ok","not okay","this isn't ok","this is not ok"],
    pressure_phrases: ["still no answer","still waiting","asap","urgent","immediately","why didn't you","you didn't reply","you never replied","this must","you have to","no choice"],
    accusation_phrases: ["you didn't","you never","you ignored","you forgot","you failed","you were supposed to","it's your fault"],
    insult_phrases: ["i hate you","hate you","shame on you","stupid","idiotic","nonsense","pathetic","unprofessional"],
    softeners: ["please","thanks","thank you","whenever you can","no rush"],
    escalation_signs: ["!!","???","?!","!?","!!!!!","……","...!!!"]
  }
};

export function quickRiskScoreClient(text, lang = "he") {
  if (!text || !text.trim()) return 0;
  const lex = LEXICON[lang] || LEXICON.he;
  const raw = text.trim();
  const t = raw.toLowerCase();
  let score = 0;

  if (lex.escalation_signs.some(m => raw.includes(m))) score += 2;
  if (lex.insult_phrases.some(p => t.includes(p.toLowerCase()))) score += 8;

  lex.negative_roots.forEach(w => { if (t.includes(w.toLowerCase())) score += 2; });
  lex.pressure_phrases.forEach(w => { if (t.includes(w.toLowerCase())) score += 3; });
  lex.accusation_phrases.forEach(w => { if (t.includes(w.toLowerCase())) score += 3; });

  lex.softeners.forEach(w => { if (t.includes(w.toLowerCase())) score -= 1; });

  return Math.max(score, 0);
}
