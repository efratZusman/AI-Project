// extension/gmailUtils.js

(function () {
  const BODY_SELECTORS = [
    "div[aria-label='Message body']",
    "div[aria-label='גוף ההודעה']",
    "div.editable[role='textbox']",
    "div[contenteditable='true'].Am.Al"
  ];

  function getSubject(composeRoot) {
    // קודם מתוך הקומפוז הנוכחי
    const input =
      composeRoot.querySelector("input[name='subjectbox']") ||
      document.querySelector("input[name='subjectbox']"); // fallback כללי
    return input ? input.value : "";
  }

  function getBodyElement(composeRoot) {
    for (const sel of BODY_SELECTORS) {
      const el = composeRoot.querySelector(sel);
      if (el) return el;
    }

    // fallback – אם לא מצאנו בגבולות הקומפוז (למקרה של HTML קצת שונה בריפליי)
    for (const sel of BODY_SELECTORS) {
      const el = document.querySelector(sel);
      if (el) return el;
    }

    return null;
  }

  function getBody(composeRoot) {
    const el = getBodyElement(composeRoot);
    if (!el) return "";
    return el.innerText || el.textContent || "";
  }

  function detectIsReply(composeRoot) {
    const subject = getSubject(composeRoot) || "";
    if (/^(Re:|Fw:|Fwd:)/i.test(subject)) return true;

    // אם יש הודעות קודמות מתחת – כנראה reply בתוך שרשור
    const threadBelow = composeRoot.closest(".nH")?.querySelectorAll(".adn");
    return threadBelow && threadBelow.length > 0;
  }

  function extractThreadMessages() {
    const nodes = document.querySelectorAll(".adn .a3s");
    const texts = [];

    nodes.forEach((n) => {
      const t = n.innerText || n.textContent || "";
      const cleaned = t.trim();
      if (cleaned) texts.push(cleaned);
    });

    const last = texts.slice(-3);

    return last.map((text, idx) => ({
      author: idx % 2 === 0 ? "them" : "me",
      text,
      timestamp: null
    }));
  }

  function getComposeDraftData(composeRoot) {
    const subject = getSubject(composeRoot);
    const bodyElement = getBodyElement(composeRoot);
    const body = bodyElement
      ? bodyElement.innerText || bodyElement.textContent || ""
      : "";
    const isReply = detectIsReply(composeRoot);
    const thread_context = isReply ? extractThreadMessages() : null;

    return { subject, body, isReply, thread_context, bodyElement };
  }

  window.AIGmailUtils = {
    getComposeDraftData
  };
})();
