// chatMonitor/chatState.js
(function () {
  const CONFIG = {
    SCORE_THRESHOLD: 6,
    MIN_MEANINGFUL_MESSAGES: 4,
    DEBOUNCE_MS: 90_000,
    CLEANUP_AFTER_MS: 20 * 60 * 1000, // 20 דקות
  };

  const statesByConversation = new Map();

  function getState(conversationKey) {
    if (!statesByConversation.has(conversationKey)) {
      statesByConversation.set(conversationKey, {
        score: 0,
        meaningfulMessages: 0,
        messages: [],
        lastAnalysisTs: 0,
        lastTouchedTs: Date.now(),
      });
    }

    const state = statesByConversation.get(conversationKey);
    state.lastTouchedTs = Date.now();
    return state;
  }

  function shouldAnalyze(state) {
    const now = Date.now();
    return (
      state.score >= CONFIG.SCORE_THRESHOLD &&
      state.meaningfulMessages >= CONFIG.MIN_MEANINGFUL_MESSAGES &&
      now - state.lastAnalysisTs > CONFIG.DEBOUNCE_MS
    );
  }

  function markAnalyzed(state) {
    state.lastAnalysisTs = Date.now();
    state.score = 0;
    state.meaningfulMessages = 0;
    state.messages = [];
  }

  // 🧹 ניקוי states ישנים
  setInterval(() => {
    const now = Date.now();
    for (const [key, state] of statesByConversation.entries()) {
      if (now - state.lastTouchedTs > CONFIG.CLEANUP_AFTER_MS) {
        statesByConversation.delete(key);
      }
    }
  }, 5 * 60 * 1000);

  window.ChatState = {
    getState,
    shouldAnalyze,
    markAnalyzed,
  };
})();
