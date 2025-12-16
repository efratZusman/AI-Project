// extension/contentScript.js

(function () {
  const POLL_INTERVAL = 1500;

  /**
   * מחזיר את ה-footer של כפתור השליחה
   */
  function getFooterForSendBtn(sendBtn) {
    // בדרך כלל זה ה-parent הישיר
    let footer = sendBtn.parentElement;
    if (!footer) return null;

    // אם כבר יש בפוטר את הכפתור שלנו – לא להוסיף שוב
    if (footer.querySelector(".ai-guard-trigger-btn")) {
      return null;
    }
    return footer;
  }

  /**
   * מוסיף כפתור "ניתוח לפני שליחה" ליד כפתור ה‑Send שנמצא
   */
  function attachButtonToSendButton(sendBtn) {
    const footer = getFooterForSendBtn(sendBtn);
    if (!footer) return;

    // מנסים למצוא "שורש קומפוז" הגיוני מסביב לכפתור
    const composeRoot =
      sendBtn.closest("div[role='dialog']") || // חלון קופץ (new / reply / forward)
      sendBtn.closest(".btC") ||               // קומפוז בתוך שרשור
      sendBtn.closest(".nH") ||                // fallback
      document;

    const btn = document.createElement("button");
    btn.textContent = "ניתוח לפני שליחה";
    btn.className = "ai-guard-trigger-btn";

    btn.addEventListener("click", () => {
      if (!window.AIGmailUtils || !window.AIGuardUI) {
        console.warn("AI Guard scripts not ready");
        return;
      }

      // שליפת הטיוטה הנוכחית מג׳ימייל
      const ctx = window.AIGmailUtils.getComposeDraftData(composeRoot);

      window.AIGuardUI.openPanel(ctx, {
        onApply: (analysisResult, composeContext) => {
          const bodyEl = composeContext.bodyElement;
          const subjectInput =
            composeRoot.querySelector("input[name='subjectbox']") ||
            document.querySelector("input[name='subjectbox']");

          if (analysisResult.safer_body && bodyEl) {
            // החלפת גוף המייל לניסוח הבטוח
            bodyEl.innerText = analysisResult.safer_body;
          }
          if (analysisResult.safer_subject && subjectInput) {
            subjectInput.value = analysisResult.safer_subject;
          }
        }
      });
    });

    // נכניס את הכפתור ליד כפתור השליחה (לפניו, כדי שיישב יפה)
    footer.insertBefore(btn, sendBtn);
  }

  /**
   * מחפש כפתורי שליחה קיימים ומוודא שבכל פוטר יש רק כפתור אחד שלנו
   */
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

  // מריצים מיד + כל זמן קצר, כדי לתפוס קומפוזים חדשים / reply בשרשור
  scanForSendButtons();
  setInterval(scanForSendButtons, POLL_INTERVAL);
})();
