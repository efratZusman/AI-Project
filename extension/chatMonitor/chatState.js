// chatMonitor/chatState.js
(function () {
  const CONFIG = {
    SCORE_THRESHOLD: 4,
    MIN_MEANINGFUL_MESSAGES: 2,
  };

  const statesByConversation = new Map();

  function getState(key) {
    if (!statesByConversation.has(key)) {
      statesByConversation.set(key, {
        score: 0,
        meaningfulMessages: 0,
        messages: [],
        lastMessageTs: 0,          // מתי נוספה הודעה אחרונה
        lastAnalyzedMessageTs: 0,  // על איזו הודעה כבר ניתחנו
        lockedUntilNextMessage: false,
        enteredAt: 0,   // מתי נכנסנו לשיחה
        readyAt: 0,     // מאיזה זמן מותר לנתח
        currentConversationKey: null,
        lastAnalyzedAt: 0,   // מתי בוצע ניתוח אחרון (timestamp)
      });
    }
    return statesByConversation.get(key);
  }

// function shouldAnalyze(state) {
//   // ⛔ כבר ניתחנו את הרצף הזה → לא מנתחים שוב
//   if (state.lockedUntilNextMessage) {
//     return false;
//   }

//   // ❌ אין הודעה חדשה → אין ניתוח
//   if (state.lastMessageTs <= state.lastAnalyzedMessageTs) {
//     return false;
//   }

//   // 🟥 מסלול 1: סיכון רגשי
//   const riskBased =
//     state.score >= CONFIG.SCORE_THRESHOLD &&
//     state.meaningfulMessages >= CONFIG.MIN_MEANINGFUL_MESSAGES;

//   // 🟦 מסלול 2: דינמיקה מתמשכת
//   const flowBased =
//     state.meaningfulMessages >= 6;

//   return riskBased || flowBased;
// }

function shouldAnalyze(state) {
  const now = Date.now();

  // ⛔ ניתחנו לאחרונה – תני לשיחה להתקדם
  const COOLDOWN_MS = Math.min(120000, 30000 + state.meaningfulMessages * 10000);
  if (now - state.lastAnalyzedAt < COOLDOWN_MS) {
    return false;
  }

  // ❌ אין הודעה חדשה מאז הניתוח
  if (state.lastMessageTs <= state.lastAnalyzedMessageTs) {
    return false;
  }

  // 🟥 תנאי מינימלי לניתוח
  const hasFlow =
    state.messages.length >= 4 &&
    state.meaningfulMessages >= 2;

  return hasFlow;
}


function markAnalyzed(state) {
  const now = Date.now();

  state.lastAnalyzedMessageTs = state.lastMessageTs;
  state.lastAnalyzedAt = now;

  // 🔒 נועלים עד רצף חדש אמיתי
  state.lockedUntilNextMessage = true;

  // מאפסים צבירה
  state.messages = state.messages.slice(-10);
  state.meaningfulMessages = Math.min(state.meaningfulMessages, 3);
  state.score = 0;

}


  window.ChatState = { getState, shouldAnalyze, markAnalyzed };
})();
