const BASE_URL = "http://127.0.0.1:8000";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.action === "analyzeBeforeSend") {
    fetch(`${BASE_URL}/analyze-before-send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(message.payload),
    })
      .then(async (res) => {
        const data = await res.json();
        sendResponse(data);
      })
      .catch((err) => {
        sendResponse({ error: "FETCH_FAILED", message: err?.message || String(err) });
      });

    return true; // keep channel open
  }

  return false;
});
