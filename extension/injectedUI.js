// extension/injectedUI.js
(function () {
  const BASE_URL = "http://127.0.0.1:8000";

  // true = עובד במצב MOCK בלי קריאות API אמיתיות
  const MOCK_MODE = false;

  // ============================================================
  // API WRAPPERS
  // ============================================================

  async function handleResponse(res) {
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Server error");
    return data;
  }

  function mockBeforeSend(payload) {
    return {
      intent: "כוונה חיובית — המייל מבקש הבהרה ידידותית.",
      risk_level: "low",
      risk_factors: ["טון ניטרלי", "לא נשמע ביקורתי", "אין מילות לחץ"],
      recipient_interpretation: "הנמען יבין זאת כמייל מקצועי וענייני.",
      send_decision: "send_as_is",
      follow_up_needed: false,
      safer_subject: payload.subject || "נושא משופר לדוגמה",
      safer_body: "זהו ניסוח בטוח יותר, שמיועד לבדיקה בזמן שה‑API מכובה.",
      notes_for_sender: ["את משתמשת ב‑Mock Mode — אין פניה אמיתית לשרת."],
    };
  }

  function mockFollowUp(body, days) {
    return {
      needs_follow_up: days > 2,
      urgency: days > 5 ? "high" : "medium",
      follow_up_reason: "עבר זמן ואין תגובה — מקובל לשלוח תזכורת.",
      suggested_follow_up:
        "רק רציתי לוודא שקיבלת את המייל הקודם. אשמח לעדכון כשנוח לך 🙂",
    };
  }

  async function analyzeBeforeSend(payload) {
    if (MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => resolve(mockBeforeSend(payload)), 300);
      });
    }
    const res = await fetch(`${BASE_URL}/analyze-before-send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return handleResponse(res);
  }

  async function analyzeFollowUp(email_body, days_passed) {
    if (MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => resolve(mockFollowUp(email_body, days_passed)), 300);
      });
    }
    const res = await fetch(`${BASE_URL}/analyze-follow-up`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email_body, days_passed }),
    });
    return handleResponse(res);
  }

  // ============================================================
  // UI PANEL
  // ============================================================

  let panelRoot = null;
  let lastResult = null;
  let currentComposeContext = null;
  let applyHandlers = null;

  function closePanel() {
    if (!panelRoot) return;
    panelRoot.style.display = "none";
    lastResult = null;
    currentComposeContext = null;
  }

  function createPanel() {
    if (panelRoot) return panelRoot;

    panelRoot = document.createElement("div");
    panelRoot.id = "ai-guard-panel";

    panelRoot.innerHTML = `
      <div class="ai-guard-header">
        <div class="ai-guard-title">AI Communication Guard</div>
        <button class="ai-guard-close-btn">×</button>
      </div>

      <div class="ai-guard-subtitle">
        ניתוח טון וסיכונים לפני שליחה + Follow-Up חכם
        <br>
        ${MOCK_MODE ? '<b style="color:#d00">MOCK MODE פעיל — אין פנייה לשרת</b>' : ""}
      </div>

      <div class="ai-guard-tabs">
        <button class="ai-tab ai-tab-before active">Before Send</button>
        <button class="ai-tab ai-tab-follow">Follow-Up</button>
      </div>

      <!-- BEFORE SEND TAB -->
      <div class="ai-tab-content ai-tab-content-before">
        <label class="ai-label">נושא</label>
        <input class="ai-input ai-input-subject" />

        <label class="ai-label">גוף המייל</label>
        <textarea class="ai-textarea ai-input-body"></textarea>

        <button class="ai-main-btn ai-btn-analyze-before">נתח</button>
        <button class="ai-secondary-btn ai-btn-apply" disabled>החל על הטיוטה</button>

        <div class="ai-result" style="display:none;">

          <div class="ai-card">
            <h4><span class="ai-icon">🎯</span> כוונה</h4>
            <p class="ai-field-intent"></p>
          </div>

          <div class="ai-card">
            <h4>
              <span class="ai-icon">⚠️</span> רמת סיכון
              <span class="ai-badge ai-risk-badge"></span>
            </h4>
            <ul class="ai-field-risk-factors"></ul>
          </div>

          <div class="ai-card">
            <h4><span class="ai-icon">🧠</span> איך זה יתקבל אצל הנמען</h4>
            <p class="ai-field-recipient"></p>
          </div>

          <div class="ai-card">
            <h4><span class="ai-icon">📩</span> החלטת מערכת</h4>
            <p class="ai-field-decision"></p>
          </div>

          <div class="ai-card">
            <h4><span class="ai-icon">📝</span> נושא מוצע</h4>
            <p class="ai-field-safer-subject"></p>
          </div>

          <div class="ai-card">
            <h4><span class="ai-icon">✨</span> ניסוח בטוח יותר</h4>
            <div class="ai-field-safer-body ai-rewrite-box"></div>
          </div>

          <div class="ai-card ai-thread-card" style="display:none;">
            <h4><span class="ai-icon">🗂️</span> שירשור קודם</h4>
            <div class="ai-timeline ai-thread-container"></div>
          </div>

        </div>
      </div>

      <!-- FOLLOW UP TAB -->
      <div class="ai-tab-content ai-tab-content-follow" style="display:none;">
        <label class="ai-label">מייל שנשלח</label>
        <textarea class="ai-textarea ai-input-follow-body"></textarea>

        <label class="ai-label">ימים מאז השליחה</label>
        <input type="number" class="ai-input ai-input-days" value="3" />

        <button class="ai-main-btn ai-btn-analyze-follow">בדוק</button>

        <div class="ai-result-follow" style="display:none;">
          <h4>נדרש פולואפ?</h4><p class="ai-field-needs-follow"></p>
          <h4>דחיפות</h4><p class="ai-field-urgency"></p>
          <h4>סיבה</h4><p class="ai-field-reason"></p>
          <h4>הודעה מוצעת</h4><div class="ai-field-follow-body ai-rewrite-box"></div>
        </div>
      </div>
    `;

    document.body.appendChild(panelRoot);

    // סגירת X
    panelRoot.querySelector(".ai-guard-close-btn").onclick = closePanel;

    // טאבס
    const tabBefore = panelRoot.querySelector(".ai-tab-before");
    const tabFollow = panelRoot.querySelector(".ai-tab-follow");
    const contentBefore = panelRoot.querySelector(".ai-tab-content-before");
    const contentFollow = panelRoot.querySelector(".ai-tab-content-follow");

    tabBefore.onclick = () => {
      tabBefore.classList.add("active");
      tabFollow.classList.remove("active");
      contentBefore.style.display = "block";
      contentFollow.style.display = "none";
    };

    tabFollow.onclick = () => {
      tabFollow.classList.add("active");
      tabBefore.classList.remove("active");
      contentBefore.style.display = "none";
      contentFollow.style.display = "block";
    };

    // BEFORE SEND — ניתוח
    panelRoot.querySelector(".ai-btn-analyze-before").onclick = async () => {
      const payload = {
        subject: panelRoot.querySelector(".ai-input-subject").value || "",
        body: panelRoot.querySelector(".ai-input-body").value || "",
        language: "auto",
        is_reply: !!currentComposeContext?.isReply,
        thread_context: currentComposeContext?.thread_context || null,
      };

      if (!payload.body.trim()) {
        alert("צריך גוף מייל כדי לנתח 🙂");
        return;
      }

      const resultBox = panelRoot.querySelector(".ai-result");
      const applyBtn = panelRoot.querySelector(".ai-btn-apply");

      resultBox.style.display = "none";
      applyBtn.disabled = true;

      try {
        const data = await analyzeBeforeSend(payload);
        lastResult = data;

        resultBox.style.display = "block";

        // Thread timeline
        const threadCard = panelRoot.querySelector(".ai-thread-card");
        const threadContainer = panelRoot.querySelector(".ai-thread-container");

        if (currentComposeContext?.thread_context?.length) {
          threadCard.style.display = "block";
          threadContainer.innerHTML = "";

          currentComposeContext.thread_context.forEach((msg) => {
            const div = document.createElement("div");
            div.className = "ai-tl-item";
            div.innerHTML = `
              <div class="ai-tl-author">
                ${msg.author === "me" ? "אני" : "הוא/היא"}:
              </div>
              <div class="ai-tl-text">${msg.text}</div>
            `;
            threadContainer.appendChild(div);
          });
        } else {
          threadCard.style.display = "none";
        }

        // Risk badge
        const riskBadge = panelRoot.querySelector(".ai-risk-badge");
        riskBadge.textContent = data.risk_level || "";
        riskBadge.className = "ai-badge ai-risk-badge";
        if (data.risk_level === "low") riskBadge.classList.add("ai-badge-low");
        else if (data.risk_level === "medium")
          riskBadge.classList.add("ai-badge-medium");
        else if (data.risk_level === "high")
          riskBadge.classList.add("ai-badge-high");

        panelRoot.querySelector(".ai-field-intent").textContent =
          data.intent || "";

        const ul = panelRoot.querySelector(".ai-field-risk-factors");
        ul.innerHTML = "";
        (data.risk_factors || []).forEach((f) => {
          const li = document.createElement("li");
          li.textContent = f;
          ul.appendChild(li);
        });

        panelRoot.querySelector(".ai-field-recipient").textContent =
          data.recipient_interpretation || "";
        panelRoot.querySelector(".ai-field-decision").textContent =
          data.send_decision || "";
        panelRoot.querySelector(".ai-field-safer-subject").textContent =
          data.safer_subject || "";
        panelRoot.querySelector(".ai-field-safer-body").textContent =
          data.safer_body || "";

        applyBtn.disabled = false;
      } catch (e) {
        console.error(e);
        alert("שגיאה בניתוח השרת: " + e.message);
        applyBtn.disabled = false;
      }
    };

    // APPLY SAFE VERSION
    panelRoot.querySelector(".ai-btn-apply").onclick = () => {
      if (lastResult && applyHandlers) {
        applyHandlers.onApply(lastResult, currentComposeContext);
      }
    };

    // FOLLOW UP
    panelRoot.querySelector(".ai-btn-analyze-follow").onclick = async () => {
      const body = panelRoot.querySelector(".ai-input-follow-body").value || "";
      const days =
        Number(panelRoot.querySelector(".ai-input-days").value) || 3;

      if (!body.trim()) {
        alert("צריך גוף מייל שנשלח");
        return;
      }

      const box = panelRoot.querySelector(".ai-result-follow");
      box.style.display = "none";

      try {
        const data = await analyzeFollowUp(body, days);

        box.style.display = "block";
        panelRoot.querySelector(".ai-field-needs-follow").textContent =
          data.needs_follow_up ? "כן" : "לא";
        panelRoot.querySelector(".ai-field-urgency").textContent =
          data.urgency || "";
        panelRoot.querySelector(".ai-field-reason").textContent =
          data.follow_up_reason || "";
        panelRoot.querySelector(".ai-field-follow-body").textContent =
          data.suggested_follow_up || "";
      } catch (e) {
        console.error(e);
        alert("שגיאה בניתוח Follow-Up: " + e.message);
      }
    };

    return panelRoot;
  }

  function openPanel(composeContext, handlers) {
    currentComposeContext = composeContext;
    applyHandlers = handlers;

    const panel = createPanel();
    panel.style.display = "block";

    panel.querySelector(".ai-input-subject").value =
      composeContext.subject || "";
    panel.querySelector(".ai-input-body").value =
      composeContext.body || "";
    panel.querySelector(".ai-input-follow-body").value =
      composeContext.body || "";
  }

  window.AIGuardUI = { openPanel, closePanel };
})();
