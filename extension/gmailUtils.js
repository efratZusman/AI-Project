(function () {
  const BODY_SELECTORS = [
    "div[aria-label='Message body']",
    "div[aria-label='Edit your message']",
    "div[aria-label='Edit your reply']",
    "div[aria-label='Reply…']",
    "div[aria-label='Reply']",
    "div[aria-label='גוף ההודעה']",
    "div.editable[role='textbox']",
    "div[contenteditable='true'][g_editable='true']",
    "div[contenteditable='true'].Am.Al"
  ];

  function getSubject(composeRoot) {
    const input =
      composeRoot.querySelector("input[name='subjectbox']") ||
      document.querySelector("input[name='subjectbox']");
    return input ? input.value : "";
  }

  function getBodyElement(composeRoot) {
    for (const sel of BODY_SELECTORS) {
      const el = composeRoot.querySelector(sel);
      if (el) return el;
    }
    const container = composeRoot.closest(".nH") || document;
    for (const sel of BODY_SELECTORS) {
      const el = container.querySelector(sel);
      if (el) return el;
    }
    console.warn("AI Guard: body element not found");
    return null;
  }

  function detectIsReply(composeRoot) {
    const subject = getSubject(composeRoot) || "";
    if (/^(Re:|Fw:|Fwd:)/i.test(subject)) return true;

    const threadMsgs = composeRoot.closest(".nH")?.querySelectorAll(".adn");
    if (threadMsgs && threadMsgs.length > 0) return true;

    return false;
  }

  function extractThreadMessages(composeRoot) {
    const container = composeRoot.closest(".nH") || document;
    const nodes = container.querySelectorAll(".adn .a3s");
    const texts = [];

    nodes.forEach((n) => {
      const t = n.innerText || n.textContent || "";
      if (t.trim()) texts.push(t.trim());
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
    const body = bodyElement ? (bodyElement.innerText || bodyElement.textContent || "") : "";

    const isReply = detectIsReply(composeRoot);
    const thread_context = isReply ? extractThreadMessages(composeRoot) : null;

    return { subject, body, isReply, thread_context, bodyElement };
  }

  window.AIGmailUtils = { getComposeDraftData };
})();
