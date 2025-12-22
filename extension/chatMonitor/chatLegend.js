(function () {
  const BTN_ID = "ai-chat-toggle";
  const LEGEND_ID = "ai-chat-legend";

  function mountLegendAboveToggle() {
    const toggleBtn = document.getElementById(BTN_ID);
    if (!toggleBtn) return false; // לא הפריים הנכון (או עוד לא נטען)

    if (document.getElementById(LEGEND_ID)) return true; // כבר קיים בפריים הזה

    const legend = document.createElement("div");
    legend.id = LEGEND_ID;
    legend.className = "ai-chat-legend";
    legend.innerHTML = `
      <div><span class="dot danger"></span> שלילי / תוקפני</div>
      <div><span class="dot neutral"></span> מתח / לחץ</div>
      <div><span class="dot positive"></span> חיובי / מרכך</div>
    `;

    toggleBtn.parentNode.insertBefore(legend, toggleBtn);
    return true;
  }

  // נסי מיד
  if (mountLegendAboveToggle()) return;

  // ואם עוד לא קיים, חכי עד שיופיע (בדיוק כמו שעשית בטוגל)
  const iv = setInterval(() => {
    if (mountLegendAboveToggle()) clearInterval(iv);
  }, 300);

  // גיבוי: עצירה אחרי 10 שניות כדי לא לרוץ לנצח
  setTimeout(() => clearInterval(iv), 10000);
})();
