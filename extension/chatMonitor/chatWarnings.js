(function () {
  function getColorByRisk(risk) {
    switch (risk) {
      case "high":
        return "#c62828"; // אדום
      case "medium":
        return "#ef6c00"; // כתום
      case "low":
      default:
        return "#555"; // ניטרלי
    }
  }

  function show(text, riskLevel = "low") {
    if (!text) return;

    let el = document.querySelector(".ai-chat-warning");
    if (!el) {
      el = document.createElement("div");
      el.className = "ai-chat-warning";
      document.body.appendChild(el);
    }

    el.innerText = text;
    el.style.backgroundColor = getColorByRisk(riskLevel);
    el.style.opacity = "1";

    clearTimeout(el._t);
    el._t = setTimeout(() => (el.style.opacity = "0"), 6000);
  }

  function showError(text) {
    let el = document.querySelector(".ai-chat-warning");
    if (!el) {
      el = document.createElement("div");
      el.className = "ai-chat-warning";
      document.body.appendChild(el);
    }

    el.innerText = text;
    el.style.backgroundColor = "#444"; 
    el.style.opacity = "1";

    clearTimeout(el._t);
    el._t = setTimeout(() => (el.style.opacity = "0"), 8000);
  }

  window.ChatWarnings = { show, showError };
})();
