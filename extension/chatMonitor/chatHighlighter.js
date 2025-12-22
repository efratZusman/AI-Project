(function () {

  function escapeRegExp(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function mark(element, phrases, cssClass) {
    if (!Array.isArray(phrases)) return 0;

    let html = element.innerHTML;
    let hits = 0;

    phrases.forEach(p => {
      if (!p || !html.includes(p)) return;

      const r = new RegExp(escapeRegExp(p), "g");
      html = html.replace(
        r,
        `<span class="ai-lexicon-word ${cssClass}">${p}</span>`
      );
      hits++;
    });

    element.innerHTML = html;
    return hits;
  }

  function highlight(element, lang = "he") {
    if (!element || element.dataset.aiMarked === "true") return 0;
    element.dataset.aiMarked = "true";

    const lex = window.ChatLexicon?.LEXICON?.[lang];
    if (!lex) return 0;

    let score = 0;

    score += mark(element, lex.danger_phrases, "danger") * 4;
    score += mark(element, lex.neutral_phrases, "neutral") * 2;
    score -= mark(element, lex.positive_phrases, "positive") * 1;

    return Math.max(score, 0);
  }

  window.ChatHighlighter = { highlight };

})();
