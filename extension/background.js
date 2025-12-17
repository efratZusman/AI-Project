chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "analyzeBeforeSend") {
    fetch("http://127.0.0.1:8000/analyze-before-send", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(message.payload)
    })
      .then(async (res) => {
        const data = await res.json();
        sendResponse(data);   // 🔥 זה החלק שחסר לך
      })
      .catch((err) => {
        sendResponse({ error: err.message });
      });

    return true; // 🔥 חובה: שומר את הערוץ פתוח
  }

  if (message.action === "analyzeFollowUp") {
    fetch("http://127.0.0.1:8000/analyze-follow-up", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(message)
    })
      .then(async (res) => {
        const data = await res.json();
        sendResponse(data);
      })
      .catch((err) => {
        sendResponse({ error: err.message });
      });

    return true;
  }
});
