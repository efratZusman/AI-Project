console.log("Gmail Guard content script loaded");

// נכנס כל פעם שנפתח חלון כתיבת מייל
function initComposeWatcher() {
  const observer = new MutationObserver(() => {
    const footer = document.querySelector(".aoI"); // אזור הכפתורים למטה
    const sendButton = document.querySelector("div[role='button'][data-tooltip*='Send']");

    if (footer && sendButton) {
      injectAnalyzeButton(footer);
    }
  });

  observer.observe(document.body, { childList: true, subtree: true });
}

function injectAnalyzeButton(footer) {
  if (document.querySelector("#ai-guard-analyze-btn")) return;

  const btn = document.createElement("button");
  btn.id = "ai-guard-analyze-btn";
  btn.innerText = "Analyze";
  btn.className = "ai-guard-analyze-btn";

  btn.addEventListener("click", handleAnalyzeClick);

  footer.appendChild(btn);
}

async function handleAnalyzeClick() {
  const subjectEl = document.querySelector("input[name='subjectbox']");
  const bodyEl = document.querySelector(".Am.Al.editable");

  const subject = subjectEl ? subjectEl.value : "";
  const body = bodyEl ? bodyEl.innerText : "";

  if (!body.trim()) {
    alert("אין טקסט לנתח");
    return;
  }

  const payload = {
    subject,
    body,
    language: "auto"
  };

  try {
    const res = await fetch("http://127.0.0.1:8000/analyze-before-send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!res.ok) {
      console.error("Backend error:", data);
      alert("שגיאה בשרת בזמן ניתוח המייל");
      return;
    }

    showAnalysisPopup({ subject, body, analysis: data });
  } catch (err) {
    console.error("Error calling backend:", err);
    alert("לא ניתן להתחבר לשרת ניתוח (בדקי שהוא רץ)");
  }
}

// -------- POPUP בתוך Gmail --------

function showAnalysisPopup({ subject, body, analysis }) {
  // אם כבר יש popup – להסיר
  const existing = document.querySelector("#ai-guard-popup");
  if (existing) existing.remove();

  const container = document.createElement("div");
  container.id = "ai-guard-popup";
  container.className = "ai-guard-popup";

  container.innerHTML = `
    <div class="ai-guard-popup-header">
      <div>
        <h3>AI Communication Guard</h3>
        <p class="ai-guard-risk">
          רמת סיכון: <span class="risk-${analysis.risk_level || "medium"}">
            ${analysis.risk_level || "medium"}
          </span>
        </p>
      </div>
      <button class="ai-guard-close-btn">×</button>
    </div>

    <div class="ai-guard-tabs">
      <button class="ai-guard-tab ai-guard-tab-active" data-tab="original">טיוטה מקורית</button>
      <button class="ai-guard-tab" data-tab="safe">ניסוח בטוח</button>
    </div>

    <div class="ai-guard-content">
      <div class="ai-guard-section">
        <h4>נושא</h4>
        <div class="ai-guard-subject original-subject">${subject || "(ללא נושא)"}</div>
        <div class="ai-guard-subject safe-subject" style="display:none;">
          ${analysis.safer_subject || subject || "(ללא נושא)"}
        </div>
      </div>

      <div class="ai-guard-section">
        <h4>גוף המייל</h4>
        <div class="ai-guard-text original-body">
${escapeHtml(body)}
        </div>
        <div class="ai-guard-text safe-body" style="display:none;">
${escapeHtml(analysis.safer_body || "")}
        </div>
      </div>

      <div class="ai-guard-section">
        <h4>הסבר קצר</h4>
        <p>${analysis.explanation || ""}</p>
      </div>
    </div>

    <div class="ai-guard-footer">
      <button class="ai-guard-apply-btn">החלף לגרסה הבטוחה</button>
    </div>
  `;

  document.body.appendChild(container);

  // כפתור סגירה
  container.querySelector(".ai-guard-close-btn").onclick = () => container.remove();

  // טאבים
  const tabs = container.querySelectorAll(".ai-guard-tab");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const selected = tab.dataset.tab; // "original" or "safe"

      tabs.forEach(t => t.classList.remove("ai-guard-tab-active"));
      tab.classList.add("ai-guard-tab-active");

      const originalSubject = container.querySelector(".original-subject");
      const safeSubject = container.querySelector(".safe-subject");
      const originalBody = container.querySelector(".original-body");
      const safeBody = container.querySelector(".safe-body");

      const showSafe = selected === "safe";

      originalSubject.style.display = showSafe ? "none" : "block";
      originalBody.style.display = showSafe ? "none" : "block";
      safeSubject.style.display = showSafe ? "block" : "none";
      safeBody.style.display = showSafe ? "block" : "none";
    });
  });

  // כפתור "החלף לגרסה הבטוחה"
  const applyBtn = container.querySelector(".ai-guard-apply-btn");
  applyBtn.addEventListener("click", () => {
    const subjectEl = document.querySelector("input[name='subjectbox']");
    const bodyEl = document.querySelector(".Am.Al.editable");

    if (subjectEl) {
      subjectEl.value = analysis.safer_subject || subjectEl.value;
    }
    if (bodyEl && analysis.safer_body) {
      bodyEl.innerText = analysis.safer_body;
    }

    container.remove();
  });
}

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// התחלה
initComposeWatcher();
