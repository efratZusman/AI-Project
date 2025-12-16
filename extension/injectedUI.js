(function () {
  const BASE_URL = "http://127.0.0.1:8000";

  // ---- API HELPERS ----
  async function handleResponse(res) {
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Server error");
    return data;
  }

  async function analyzeBeforeSend(payload) {
    const res = await fetch(`${BASE_URL}/analyze-before-send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  }

  async function analyzeFollowUp(email_body, days_passed) {
    const res = await fetch(`${BASE_URL}/analyze-follow-up`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email_body, days_passed })
    });
    return handleResponse(res);
  }

  // ---- STATE ----
  let panelRoot = null;
  let lastResult = null;
  let currentComposeContext = null;
  let applyHandlers = null;

  // ---- PANEL CREATION ----
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
        ניתוח טון וסיכונים לפני שליחה + Follow-Up חכם.
      </div>

      <div class="ai-guard-tabs">
        <button class="ai-tab ai-tab-before active">Before Send</button>
        <button class="ai-tab ai-tab-follow">Follow-Up</button>
      </div>

      <!-- BEFORE SEND TAB -->
      <div class="ai-tab-content ai-tab-content-before">
        <label class="ai-label">נושא</label>
        <input type="text" class="ai-input ai-input-subject" placeholder="נושא המייל..." />

        <label class="ai-label">גוף המייל</label>
        <textarea class="ai-textarea ai-input-body" placeholder="גוף המייל..."></textarea>

        <label class="ai-checkbox-row">
          <input type="checkbox" class="ai-input-is-reply" />
          זהו מייל Reply עם שירשור קודם
        </label>

        <button class="ai-main-btn ai-btn-analyze-before">נתח לפני שליחה</button>
        <button class="ai-secondary-btn ai-btn-apply" disabled>החל על הטיוטה</button>

        <div class="ai-result" style="display:none;">
          <h4>כוונה (Intent)</h4><p class="ai-field-intent"></p>
          <h4>רמת סיכון</h4><p class="ai-field-risk"></p>
          <h4>גורמי סיכון</h4><ul class="ai-field-risk-factors"></ul>
          <h4>איך זה יתקבל</h4><p class="ai-field-recipient"></p>
          <h4>המלצה</h4><p class="ai-field-decision"></p>
          <h4>נושא מוצע</h4><p class="ai-field-safer-subject"></p>
          <h4>ניסוח בטוח יותר</h4><div class="ai-field-safer-body ai-rewrite-box"></div>
        </div>
      </div>

      <!-- FOLLOW UP TAB -->
      <div class="ai-tab-content ai-tab-content-follow" style="display:none;">
        <label class="ai-label">גוף המייל שנשלח</label>
        <textarea class="ai-textarea ai-input-follow-body"></textarea>

        <label class="ai-label">כמה ימים עברו?</label>
        <input type="number" min="1" value="3" class="ai-input ai-input-days" />

        <button class="ai-main-btn ai-btn-analyze-follow">בדיקת Follow-Up</button>

        <div class="ai-result-follow" style="display:none;">
          <h4>צריך פולואפ?</h4><p class="ai-field-needs-follow"></p>
          <h4>רמת דחיפות</h4><p class="ai-field-urgency"></p>
          <h4>למה?</h4><p class="ai-field-reason"></p>
          <h4>הודעה מוצעת</h4><div class="ai-field-follow-body ai-rewrite-box"></div>
        </div>
      </div>
    `;

    document.body.appendChild(panelRoot);

    // --- CLOSE BUTTON ---
    panelRoot.querySelector(".ai-guard-close-btn").addEventListener("click", () => {
      panelRoot.style.display = "none";
    });

    // --- TABS ---
    const tabBefore = panelRoot.querySelector(".ai-tab-before");
    const tabFollow = panelRoot.querySelector(".ai-tab-follow");
    const contentBefore = panelRoot.querySelector(".ai-tab-content-before");
    const contentFollow = panelRoot.querySelector(".ai-tab-content-follow");

    tabBefore.addEventListener("click", () => {
      tabBefore.classList.add("active");
      tabFollow.classList.remove("active");
      contentBefore.style.display = "block";
      contentFollow.style.display = "none";
    });

    tabFollow.addEventListener("click", () => {
      tabFollow.classList.add("active");
      tabBefore.classList.remove("active");
      contentBefore.style.display = "none";
      contentFollow.style.display = "block";
    });

    // ---- BEFORE SEND: ANALYZE ----
    panelRoot.querySelector(".ai-btn-analyze-before").addEventListener("click", async () => {
      const subjectEl = panelRoot.querySelector(".ai-input-subject");
      const bodyEl = panelRoot.querySelector(".ai-input-body");
      const isReplyEl = panelRoot.querySelector(".ai-input-is-reply");

      const payload = {
        subject: subjectEl.value || "",
        body: bodyEl.value || "",
        language: "auto",
        is_reply: isReplyEl.checked,
        thread_context: currentComposeContext?.thread_context || null
      };

      if (!payload.body.trim()) {
        alert("צריך גוף מייל כדי לנתח");
        return;
      }

      const resultBox = panelRoot.querySelector(".ai-result");
      const applyBtn = panelRoot.querySelector(".ai-btn-apply");

      applyBtn.disabled = true;
      resultBox.style.display = "none";

      try {
        const data = await analyzeBeforeSend(payload);
        lastResult = data;

        // Fill UI
        resultBox.style.display = "block";
        panelRoot.querySelector(".ai-field-intent").textContent = data.intent || "";
        panelRoot.querySelector(".ai-field-risk").textContent = data.risk_level || "";

        const ul = panelRoot.querySelector(".ai-field-risk-factors");
        ul.innerHTML = "";
        (data.risk_factors || []).forEach((r) => {
          const li = document.createElement("li");
          li.textContent = r;
          ul.appendChild(li);
        });

        panelRoot.querySelector(".ai-field-recipient").textContent =
          data.recipient_interpretation || "";

        panelRoot.querySelector(".ai-field-decision").textContent = data.send_decision || "";
        panelRoot.querySelector(".ai-field-safer-subject").textContent = data.safer_subject || "";
        panelRoot.querySelector(".ai-field-safer-body").textContent = data.safer_body || "";

        applyBtn.disabled = false;

      } catch (e) {
        console.error(e);
        alert("שגיאה בקריאה לשרת: " + e.message);
      }
    });

    // ---- APPLY SAFE VERSION TO GMAIL ----
    panelRoot.querySelector(".ai-btn-apply").addEventListener("click", () => {
      if (!lastResult || !applyHandlers) return;

      applyHandlers.onApply(lastResult, currentComposeContext);
    });

    // ---- FOLLOW UP ----
    panelRoot.querySelector(".ai-btn-analyze-follow").addEventListener("click", async () => {
      const bodyEl = panelRoot.querySelector(".ai-input-follow-body");
      const daysEl = panelRoot.querySelector(".ai-input-days");

      const body = bodyEl.value || "";
      const days = Number(daysEl.value) || 3;

      if (!body.trim()) {
        alert("צריך גוף מייל שנשלח");
        return;
      }

      const resultBox = panelRoot.querySelector(".ai-result-follow");
      resultBox.style.display = "none";

      try {
        const data = await analyzeFollowUp(body, days);
        resultBox.style.display = "block";

        panelRoot.querySelector(".ai-field-needs-follow").textContent =
          data.needs_follow_up ? "כן" : "לא";

        panelRoot.querySelector(".ai-field-urgency").textContent = data.urgency || "";
        panelRoot.querySelector(".ai-field-reason").textContent = data.follow_up_reason || "";
        panelRoot.querySelector(".ai-field-follow-body").textContent =
          data.suggested_follow_up || "";
      } catch (e) {
        console.error(e);
        alert("שגיאה בקריאה לשרת: " + e.message);
      }
    });

    return panelRoot;
  }

  // ---- OPEN PANEL WITH COMPOSE CONTEXT ----
  function openPanel(composeContext, handlers) {
    currentComposeContext = composeContext;
    applyHandlers = handlers || null;

    const panel = createPanel();
    panel.style.display = "block";

    // fill initial data
    panel.querySelector(".ai-input-subject").value = composeContext.subject || "";
    panel.querySelector(".ai-input-body").value = composeContext.body || "";
    panel.querySelector(".ai-input-is-reply").checked = !!composeContext.isReply;

    // default into follow-up
    panel.querySelector(".ai-input-follow-body").value = composeContext.body || "";
  }

  // expose globally
  window.AIGuardUI = { openPanel };
})();
