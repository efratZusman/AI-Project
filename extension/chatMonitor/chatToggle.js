// extension/chatMonitor/chatToggle.js
(function () {
  const KEY = "ai_chat_monitor_enabled";
  const BTN_ID = "ai-chat-toggle";

  // ✅ אל תזריקי פעמיים באותו פריים
  if (document.getElementById(BTN_ID)) return;

  // ✅ רק בפריים "אמיתי" של שיחה: יש הודעות + יש תיבת כתיבה
  const hasMessages = () => !!document.querySelector("div.DTp27d");
  const hasComposer = () =>
    !!document.querySelector("div[contenteditable='true'][role='textbox']") ||
    !!document.querySelector("div[contenteditable='true']");

  function isEnabled() {
    return localStorage.getItem(KEY) !== "false";
  }

  function setEnabled(v) {
    localStorage.setItem(KEY, v ? "true" : "false");
  }

  function ensureRelevantFrameOrRetry() {
    if (!hasMessages() || !hasComposer()) {
      setTimeout(ensureRelevantFrameOrRetry, 1200);
      return;
    }
    mount();
  }

  function mount() {
    if (document.getElementById(BTN_ID)) return;

    const btn = document.createElement("button");
    btn.id = BTN_ID;
    btn.type = "button";
    btn.innerHTML = `
      <span class="ai-pill" aria-hidden="true"></span>
      <span class="ai-label">מוניטור צ׳אט</span>
    `;

    function refresh() {
      const enabled = isEnabled();
      btn.dataset.enabled = String(enabled);
      btn.title = enabled ? "מוניטור צ׳אט פעיל (לחצי לכיבוי)" : "מוניטור צ׳אט כבוי (לחצי להפעלה)";
    }

    btn.addEventListener("click", () => {
      setEnabled(!isEnabled());
      refresh();
    });

    document.body.appendChild(btn);
    refresh();
  }

  ensureRelevantFrameOrRetry();
})();
