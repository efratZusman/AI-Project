const BASE_URL = "http://127.0.0.1:8000";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.action === "analyzeBeforeSend") {
    fetch(`${BASE_URL}/analyze-before-send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(message.payload),
    })
      .then(async (res) => {
        let data = null;
        try {
          data = await res.json();
        } catch (e) {
          return sendResponse({ error: "BAD_JSON_FROM_SERVER", message: String(e) });
        }
        sendResponse(data);
      })
      .catch((err) => {
        sendResponse({ error: "FETCH_FAILED", message: err?.message || String(err) });
      });

    return true;
  }

  return false;
});
