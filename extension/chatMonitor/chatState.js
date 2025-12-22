(function () {
  const CONFIG = {
    SCORE_THRESHOLD: 6,
    MIN_MEANINGFUL_MESSAGES: 4,
    MIN_WORDS_PER_MESSAGE: 5,
    DEBOUNCE_MS: 90_000,
  };

  const state = {
    score: 0,
    meaningfulMessages: 0,
    messages: [],
    lastAnalysisTs: 0,
  };

  function shouldAnalyze() {
    const now = Date.now();
    return (
      state.score >= CONFIG.SCORE_THRESHOLD &&
      state.meaningfulMessages >= CONFIG.MIN_MEANINGFUL_MESSAGES &&
      now - state.lastAnalysisTs > CONFIG.DEBOUNCE_MS
    );
  }

  function markAnalyzed() {
    state.lastAnalysisTs = Date.now();
  }

  window.ChatState = { state, shouldAnalyze, markAnalyzed };
})();
