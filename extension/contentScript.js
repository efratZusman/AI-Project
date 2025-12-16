// extension/contentScript.js
(function () {
  // כל כמה זמן לסרוק קומפוזים חדשים
  const POLL_INTERVAL = 1500;

  /**
   * בדיקה אם כפתור ה-Send בכלל רלוונטי:
   * - קיים בדום
   * - נראה לעין (לא hidden)
   */
  function isRealSendButton(sendBtn) {
    if (!sendBtn) return false;
    const style = window.getComputedStyle(sendBtn);
    if (
      style.display === "none" ||
      style.visibility === "hidden" ||
      style.opacity === "0"
    ) {
      return false;
    }
    return true;
  }

  /**
   * מחזיר את ה-footer של כפתור השליחה
   * ודואג שלא נוסיף עוד כפתור אם כבר קיים שם אחד.
   */
  function getFooterForSendBtn(sendBtn) {
    let footer = sendBtn.parentElement;
    if (!footer) return null;

    // אם כבר יש בפוטר את הכפתור שלנו – לא להוסיף שוב
    if (footer.querySelector(".ai-guard-trigger-btn")) {
      return null;
    }

    return footer;
  }

  /**
   * מנסה למצוא "שורש קומפוז" מסביב לכפתור ה-Send
   * זה מה שנשתמש בו כדי:
   * - לשלוף subject / body
   * - לזהות אם זה reply / new
   */
  function findComposeRoot(sendBtn) {
    if (!sendBtn) return document;

    const dialogRoot = sendBtn.closest("div[role='dialog']"); // חלון קופץ (new / reply / forward)
    if (dialogRoot) return dialogRoot;

    const inlineThreadRoot = sendBtn.closest(".btC"); // קומפוז בתוך שרשור
    if (inlineThreadRoot) return inlineThreadRoot;

    const mainRoot = sendBtn.closest(".nH"); // fallback כללי בג׳ימייל
    if (mainRoot) return mainRoot;

    return document;
  }

  /**
   * מוסיף כפתור "ניתוח לפני שליחה" ליד כפתור ה‑Send שנמצא
   */
  function attachButtonToSendButton(sendBtn) {
    // כפתור לא אמיתי / לא נראה → לא נוגעים
    if (!isRealSendButton(sendBtn)) return;

    const footer = getFooterForSendBtn(sendBtn);
    if (!footer) return;

    const composeRoot = findComposeRoot(sendBtn);

    const btn = document.createElement("button");
    btn.textContent = "ניתוח לפני שליחה";
    btn.className = "ai-guard-trigger-btn";

    btn.addEventListener("click", () => {
      if (!window.AIGmailUtils || !window.AIGuardUI) {
        console.warn("AI Guard scripts not ready (AIGmailUtils / AIGuardUI missing)");
        return;
      }

      // שליפת הטיוטה הנוכחית מג׳ימייל
      const ctx = window.AIGmailUtils.getComposeDraftData(composeRoot);

      // פתיחת הפאנל עם ההקשר של הקומפוז
      window.AIGuardUI.openPanel(ctx, {
        onApply: (analysisResult, composeContext) => {
          if (!analysisResult || !composeContext) return;

          const bodyEl = composeContext.bodyElement;
          const subjectInput =
            composeRoot.querySelector("input[name='subjectbox']") ||
            document.querySelector("input[name='subjectbox']");

          // החלפת גוף המייל לניסוח הבטוח
          if (analysisResult.safer_body && bodyEl) {
            bodyEl.innerText = analysisResult.safer_body;
          }

          // עדכון נושא אם קיים safer_subject
          if (analysisResult.safer_subject && subjectInput) {
            subjectInput.value = analysisResult.safer_subject;
          }
        }
      });
    });

    // סגירה אוטומטית של הפאנל כששולחים / סוגרים / מוחקים את הטיוטה
    function wireAutoCloseForCompose() {
      if (!window.AIGuardUI || !window.AIGuardUI.closePanel) return;

      // 1. שליחה
      sendBtn.addEventListener("click", () => {
        window.AIGuardUI.closePanel();
      });

      // 2. כפתורי סגירה / מחיקה בתוך אותו קומפוז
      const closeSelectors = [
        "img[aria-label='Close']",
        "img[aria-label='סגור']",
        "div[aria-label*='Discard draft']",
        "div[aria-label*='מחיקת טיוטה']"
      ];
      closeSelectors.forEach((sel) => {
        const btns = composeRoot.querySelectorAll(sel);
        btns.forEach((b) => {
          b.addEventListener("click", () => {
            window.AIGuardUI.closePanel();
          });
        });
      });
    }

    wireAutoCloseForCompose();

    // נכניס את הכפתור ליד כפתור השליחה (לפניו, כדי שיישב יפה)
    footer.insertBefore(btn, sendBtn);
  }

  /**
   * מחפש כפתורי שליחה קיימים ומוודא שבכל פוטר יש רק כפתור אחד שלנו
   */
  function scanForSendButtons() {
    try {
      const sendButtons = document.querySelectorAll(
        // אנגלית + עברית
        "div[role='button'][data-tooltip*='Send'], div[role='button'][data-tooltip*='שליחה']"
      );

      sendButtons.forEach((sendBtn) => {
        try {
          attachButtonToSendButton(sendBtn);
        } catch (e) {
          console.error("AI Guard: failed attaching button", e);
        }
      });
    } catch (e) {
      console.error("AI Guard: scanForSendButtons error", e);
    }
  }

  // מריצים מיד + כל זמן קצר, כדי לתפוס קומפוזים חדשים / reply בשרשור
  scanForSendButtons();
  setInterval(scanForSendButtons, POLL_INTERVAL);
})();
