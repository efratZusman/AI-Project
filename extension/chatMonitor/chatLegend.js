// chatMonitor/chatLegend.js
(function () {
  const BTN_ID = "ai-chat-toggle";
  const LEGEND_ID = "ai-chat-legend";

  function mountLegend() {
    const toggleBtn = document.getElementById(BTN_ID);
    if (!toggleBtn) return false;

    if (document.getElementById(LEGEND_ID)) return true;

    const legend = document.createElement("div");
    legend.id = LEGEND_ID;
    legend.className = "ai-chat-legend";
    legend.innerHTML = `
      <div><span class="dot danger"></span> שלילי / תוקפני</div>
      <div><span class="dot neutral"></span> מתח / לחץ</div>
      <div><span class="dot positive"></span> חיובי / מרכך</div>
    `;

    document.body.appendChild(legend);
    return true;
  }

  // 🔁 חכי עד שה־toggle יופיע בפריים הזה
  const iv = setInterval(() => {
    if (mountLegend()) clearInterval(iv);
  }, 300);

  setTimeout(() => clearInterval(iv), 10_000);
})();
