(function () {
  function show(text) {
    if (!text) return;

    let el = document.querySelector(".ai-chat-warning");
    if (!el) {
      el = document.createElement("div");
      el.className = "ai-chat-warning";
      document.body.appendChild(el);
    }

    el.innerText = text;
    el.style.opacity = "1";

    clearTimeout(el._t);
    el._t = setTimeout(() => (el.style.opacity = "0"), 6000);
  }

  window.ChatWarnings = { show };
})();
