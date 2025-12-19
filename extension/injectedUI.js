(function () {
  const MOCK_MODE = false;

  function mockBeforeSend(payload) {
    return {
      intent: "כוונה חיובית — בקשה עניינית.",
      risk_level: "low",
      risk_factors: ["טון ניטרלי"],
      recipient_interpretation: "הנמען יבין זאת כמייל מקצועי.",
      send_decision: "send_as_is",
      follow_up_needed: false,
      follow_up_reason: "",
      safer_subject: payload.subject || "",
      safer_body: payload.body || "",
      notes_for_sender: ["Mock mode פעיל."],
      analysis_layer: "mock",
      ai_ok: true,
      ai_error_code: null,
      ai_error_message: null
    };
  }

  async function analyzeBeforeSend(payload) {
    if (MOCK_MODE) {
      return new Promise((resolve) => setTimeout(() => resolve(mockBeforeSend(payload)), 200));
    }

    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        { action: "analyzeBeforeSend", payload },
        (response) => {
          if (chrome.runtime.lastError) {
            reject(new Error(chrome.runtime.lastError.message));
            return;
          }
          if (response?.error) {
            reject(new Error(response.message || response.error));
            return;
          }
          resolve(response);
        }
      );
    });
  }

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
        ניתוח טון וסיכונים לפני שליחה
        <br>
        ${MOCK_MODE ? '<b style="color:#d00">MOCK MODE פעיל — אין פנייה לשרת</b>' : ""}
        <div class="ai-ai-status" style="margin-top:6px; font-size:12px;"></div>
      </div>

      <div class="ai-tab-content ai-tab-content-before">
        <label class="ai-label">נושא</label>
        <input class="ai-input ai-input-subject" />
        <label class="ai-label">גוף המייל</label>
        <textarea class="ai-textarea ai-input-body"></textarea>
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
            <h4><span class="ai-icon">✨</span> ניסוח בטוח יותר</h4>
            <div class="ai-field-safer-body ai-rewrite-box"></div>
            <div class="ai-field-no-rewrite" style="margin-top:8px; font-size:12px; color:#b45309; display:none;">
              אין ניסוח מחדש כרגע (Gemini לא זמין). מוצגות אזהרות בלבד.
            </div>
          </div>

          <div class="ai-card ai-thread-card" style="display:none;">
            <h4><span class="ai-icon">🗂️</span> שירשור קודם</h4>
            <div class="ai-timeline ai-thread-container"></div>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(panelRoot);
    panelRoot.querySelector(".ai-guard-close-btn").onclick = closePanel;

    panelRoot.querySelector(".ai-btn-analyze-before").onclick = async () => {
      const payload = {
        subject: panelRoot.querySelector(".ai-input-subject").value || "",
        body: panelRoot.querySelector(".ai-input-body").value || "",
        language: "auto",
        is_reply: !!currentComposeContext?.isReply,
        thread_context: currentComposeContext?.thread_context || null
      };

      if (!payload.body.trim()) {
        alert("צריך גוף מייל כדי לנתח 🙂");
        return;
      }

      const resultBox = panelRoot.querySelector(".ai-result");
      const applyBtn = panelRoot.querySelector(".ai-btn-apply");
      const aiStatus = panelRoot.querySelector(".ai-ai-status");
      const noRewrite = panelRoot.querySelector(".ai-field-no-rewrite");

      resultBox.style.display = "none";
      applyBtn.disabled = true;
      aiStatus.textContent = "";
      noRewrite.style.display = "none";

      try {
        const data = await analyzeBeforeSend(payload);
        lastResult = data;
        resultBox.style.display = "block";

        // סטטוס AI ברור למעלה
        if (data.ai_ok === false) {
          aiStatus.innerHTML = `<b style="color:#b91c1c">Gemini לא זמין:</b> ${data.ai_error_code || "UNKNOWN"} ${data.ai_error_message ? ("— " + data.ai_error_message) : ""}`;
          noRewrite.style.display = "block";
        } else {
          aiStatus.innerHTML = `<span style="color:#166534"><b>Gemini פעיל</b></span>`;
        }

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
              <div class="ai-tl-author">${msg.author === "me" ? "אני" : "הוא/היא"}:</div>
              <div class="ai-tl-text"></div>
            `;
            div.querySelector(".ai-tl-text").textContent = msg.text || "";
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
        else if (data.risk_level === "medium") riskBadge.classList.add("ai-badge-medium");
        else if (data.risk_level === "high") riskBadge.classList.add("ai-badge-high");

        panelRoot.querySelector(".ai-field-intent").textContent = data.intent || "";

        const ul = panelRoot.querySelector(".ai-field-risk-factors");
        ul.innerHTML = "";
        (data.risk_factors || []).forEach((f) => {
          const li = document.createElement("li");
          li.textContent = f;
          ul.appendChild(li);
        });

        panelRoot.querySelector(".ai-field-recipient").textContent = data.recipient_interpretation || "";
        panelRoot.querySelector(".ai-field-decision").textContent = data.send_decision || "";

        panelRoot.querySelector(".ai-field-safer-body").textContent = data.safer_body || "";

        // ✅ Apply רק אם Gemini באמת נתן rewrite
        const canApply = (data.ai_ok !== false) && !!(data.safer_body && data.safer_body.trim());
        applyBtn.disabled = !canApply;

      } catch (e) {
        console.error(e);
        alert("שגיאה בניתוח: " + (e.message || e));
        applyBtn.disabled = true;
      }
    };

    panelRoot.querySelector(".ai-btn-apply").onclick = () => {
      if (lastResult && applyHandlers) {
        applyHandlers.onApply(lastResult, currentComposeContext);
      }
    };

    return panelRoot;
  }

  function openPanel(composeContext, handlers) {
    currentComposeContext = composeContext;
    applyHandlers = handlers;

    const panel = createPanel();
    panel.style.display = "block";

    panel.querySelector(".ai-input-subject").value = composeContext.subject || "";
    panel.querySelector(".ai-input-body").value = composeContext.body || "";

    // ⏱️ ניתוח אוטומטי מיד עם פתיחת הפאנל
    setTimeout(() => {
      const analyzeBtn = panel.querySelector(".ai-btn-analyze-before");
      if (analyzeBtn) {
        analyzeBtn.click();
      }
    }, 0);
  }

  window.AIGuardUI = { openPanel, closePanel };
})();
