(function () {
  function ensureEl() {
    let el = document.querySelector(".ai-chat-warning");
    if (!el) {
      el = document.createElement("div");
      el.className = "ai-chat-warning";
      document.body.appendChild(el);
    }
    return el;
  }

  function show(text, riskLevel = "low") {
    if (!text) return;

    const el = ensureEl();

    el.textContent = text;
    el.classList.remove("error", "low", "medium", "high");
    el.classList.add("visible", "warning", riskLevel);

    clearTimeout(el._t);
    el._t = setTimeout(() => {
      el.classList.remove("visible");
    }, 6000);
  }

  function showError(text) {
    if (!text) return;

    const el = ensureEl();

    el.textContent = "⚠️ " + text;
    el.classList.remove("warning", "low", "medium", "high");
    el.classList.add("visible", "error");

    clearTimeout(el._t);
    el._t = setTimeout(() => {
      el.classList.remove("visible");
    }, 8000);
  }

  window.ChatWarnings = { show, showError };
})();
