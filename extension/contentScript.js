(function () {
  const POLL_INTERVAL = 1500;

  function isRealSendButton(sendBtn) {
    if (!sendBtn) return false;
    const style = window.getComputedStyle(sendBtn);
    if (style.display === "none" || style.visibility === "hidden" || style.opacity === "0") {
      return false;
    }
    return true;
  }

  function getFooterForSendBtn(sendBtn) {
    const footer = sendBtn.parentElement;
    if (!footer) return null;
    if (footer.querySelector(".ai-guard-trigger-btn")) return null;
    return footer;
  }

  function findComposeRoot(sendBtn) {
    if (!sendBtn) return document;
    const dialogRoot = sendBtn.closest("div[role='dialog']");
    if (dialogRoot) return dialogRoot;
    const inlineThreadRoot = sendBtn.closest(".btC");
    if (inlineThreadRoot) return inlineThreadRoot;
    const mainRoot = sendBtn.closest(".nH");
    if (mainRoot) return mainRoot;
    return document;
  }

  function attachButtonToSendButton(sendBtn) {
    if (!isRealSendButton(sendBtn)) return;
    const footer = getFooterForSendBtn(sendBtn);
    if (!footer) return;

    const composeRoot = findComposeRoot(sendBtn);

    const btn = document.createElement("button");
    btn.textContent = "ניתוח לפני שליחה";
    btn.className = "ai-guard-trigger-btn";
    btn.classList.add("ai-guard-trigger-btn");

    btn.addEventListener("click", () => {
      if (!window.AIGmailUtils || !window.AIGuardUI) {
        console.warn("AI Guard scripts not ready (AIGmailUtils / AIGuardUI missing)");
        return;
      }

      const ctx = window.AIGmailUtils.getComposeDraftData(composeRoot);

      window.AIGuardUI.openPanel(ctx, {
        onApply: (analysisResult, composeContext) => {
          if (!analysisResult || !composeContext) return;

          const bodyEl = composeContext.bodyElement;
          const subjectInput =
            composeRoot.querySelector("input[name='subjectbox']") ||
            document.querySelector("input[name='subjectbox']");

          if (analysisResult.safer_body && bodyEl) {
            bodyEl.innerText = analysisResult.safer_body;
          }
          if (analysisResult.safer_subject && subjectInput) {
            subjectInput.value = analysisResult.safer_subject;
          }
        }
      });
    });

    footer.insertBefore(btn, sendBtn);
  }

  function scanForSendButtons() {
    const sendButtons = document.querySelectorAll(
      "div[role='button'][data-tooltip*='Send'], div[role='button'][data-tooltip*='שליחה']"
    );

    sendButtons.forEach((sendBtn) => {
      try {
        attachButtonToSendButton(sendBtn);
      } catch (e) {
        console.error("AI Guard: failed attaching button", e);
      }
    });
  }

  scanForSendButtons();
  setInterval(scanForSendButtons, POLL_INTERVAL);
})();
