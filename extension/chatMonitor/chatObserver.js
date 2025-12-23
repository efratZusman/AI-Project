(function () {
    const MESSAGE_SELECTOR = "div.DTp27d";
    const RETRY_MS = 1500;

    function isChatMonitorEnabled() {
        return localStorage.getItem("ai_chat_monitor_enabled") !== "false";
    }

    function init() {
        const messages = document.querySelectorAll(MESSAGE_SELECTOR);
        if (!messages.length) {
            setTimeout(init, RETRY_MS);
            return;
        }

        const observer = new MutationObserver((mutations) => {
            if (!isChatMonitorEnabled()) return;

            mutations.forEach(m => {
                m.addedNodes.forEach(node => {
                    if (!(node instanceof HTMLElement)) return;

                    const msgEl = node.matches?.(MESSAGE_SELECTOR)
                        ? node
                        : node.querySelector?.(MESSAGE_SELECTOR);

                    if (!msgEl) return;

                    const text = msgEl.innerText || "";
                    const words = text.split(/\s+/).length;

                    const score = window.ChatHighlighter.highlight(msgEl, "he");

                    const state = window.ChatState.state;
                    state.score += score;
                    state.messages.push(text);

                    if (words >= 5) state.meaningfulMessages += 1;

                    if (window.ChatState.shouldAnalyze()) {
                        chrome.runtime.sendMessage(
                            {
                                action: "analyzeChatTrend",
                                messages: state.messages.slice(-10),
                            },
                            (res) => {
                                if (!res) return;

                                if (res.ai_ok === false) {
                                    window.ChatWarnings.showError(
                                        "מערכת הניטור אינה זמינה כרגע. ייתכן שהמידע אינו מנותח בזמן אמת."
                                    );
                                    return;
                                }

                                if (res.warning_text && res.risk_level) {
                                    window.ChatWarnings.show(res.warning_text, res.risk_level);
                                }
                            }
                        );

                        window.ChatState.markAnalyzed();
                    }
                });
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }

    init();
})();
