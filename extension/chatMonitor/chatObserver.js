// chatMonitor/chatObserver.js
(function () {
  const MESSAGE_SELECTOR = "div.DTp27d";
  const RETRY_MS = 1500;

  let observer = null;
  let retryTimer = null;
  let stopped = false;

  function getRuntimeSafe() {
    try {
      const rt = globalThis?.chrome?.runtime;
      // לפעמים rt קיים אבל נזרק כשנוגעים בו — לכן try/catch מעל
      if (!rt || !rt.id) return null;
      return rt;
    } catch (e) {
      return null;
    }
  }

  function stopAll() {
    if (stopped) return;
    stopped = true;

    try { observer?.disconnect(); } catch {}
    observer = null;

    if (retryTimer) {
      clearTimeout(retryTimer);
      retryTimer = null;
    }
  }

  // מונע callbacks אחרי ניווט/פריים שנזרק
  window.addEventListener("pagehide", stopAll, { once: true });
  window.addEventListener("beforeunload", stopAll, { once: true });

  function isChatMonitorEnabled() {
    try {
      return localStorage.getItem("ai_chat_monitor_enabled") !== "false";
    } catch {
      return true;
    }
  }

  function getConversationKey() {
    return location.pathname + location.hash;
  }

  function safeSendMessage(payload, cb) {
    const rt = getRuntimeSafe();
    if (!rt) {
      stopAll();
      return;
    }
    try {
      rt.sendMessage(payload, (res) => {
        // גם פה: אם בזמן ההחזרה הקונטקסט נפל, לא נרצה לזרוק
        if (stopped) return;
        cb?.(res);
      });
    } catch (e) {
      // זה המקום הקלאסי של "Extension context invalidated"
      stopAll();
    }
  }

  function scheduleRetry() {
    if (stopped) return;
    retryTimer = setTimeout(init, RETRY_MS);
  }

  function init() {
    userInteracted = false;
    if (stopped) return;
    if (!getRuntimeSafe()) {
      stopAll();
      return;
    }

    const messages = document.querySelectorAll(MESSAGE_SELECTOR);
    if (!messages.length) {
      scheduleRetry();
      return;
    }
const conversationKey = getConversationKey();
const state = window.ChatState.getState(conversationKey);

// 🔁 כניסה לשיחה חדשה (או רענון שיחה)
if (state.currentConversationKey !== conversationKey) {
  const now = Date.now();

  state.currentConversationKey = conversationKey;
  state.enteredAt = now;
  state.readyAt = now + 2000; // grace period לטעינה

  // reset מלא לשיחה
  state.score = 0;
  state.meaningfulMessages = 0;
  state.messages = [];
  state.lastMessageTs = 0;
  state.lastAnalyzedMessageTs = 0;
  state.lockedUntilNextMessage = false;
}


    // לא ליצור observer פעמיים
    if (observer) return;


    observer = new MutationObserver((mutations) => {
      if (stopped) return;

      if (!getRuntimeSafe()) {
        stopAll();
        return;
      }

      if (!isChatMonitorEnabled()) return;

      const conversationKey = getConversationKey();
      const state = window.ChatState.getState(conversationKey);


      for (const m of mutations) {
        for (const node of m.addedNodes) {
          if (stopped) return;
          if (!(node instanceof HTMLElement)) continue;
          
          const msgEl = node.matches?.(MESSAGE_SELECTOR)
            ? node
            : node.querySelector?.(MESSAGE_SELECTOR);

          if (!msgEl) continue;

          // ⛔ אם זו הודעה שכבר נראתה (history load / מעבר שיחה) – לא לנתח
          if (msgEl.dataset.aiSeen === "true") continue;
          // מסמנים שזו הודעה חדשה בפעם הראשונה
          msgEl.dataset.aiSeen = "true";

          const text = msgEl.innerText || "";
          const words = text.split(/\s+/).filter(Boolean).length;

          const score = window.ChatHighlighter.highlight(msgEl, "he");

// ⛔ עדיין בשלב טעינת שיחה – לא צוברים state
if (Date.now() < state.readyAt) {
  continue;
}

state.lastMessageTs = Date.now();
state.lockedUntilNextMessage = false;

state.messages.push(text);

if (words >= 5) {
  state.meaningfulMessages += 1;
}

state.score += score;


          if (window.ChatState.shouldAnalyze(state)) {
            safeSendMessage(
              {
                action: "analyzeChatTrend",
                messages: state.messages.slice(-30),
                conversationKey,
              },
              (res) => {
                if (!res) return;

                if (res.ai_ok === false) {
                  window.ChatWarnings.showError("מערכת הניטור אינה זמינה כרגע.");
                  return;
                }

                if (res.warning_text && res.risk_level) {
                  window.ChatWarnings.show(res.warning_text, res.risk_level);
                }
              }
            );

            window.ChatState.markAnalyzed(state);
          }
        }
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });
    }

  init();
})();
