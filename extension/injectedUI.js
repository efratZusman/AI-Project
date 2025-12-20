(function () {
  const MOCK_MODE = false;
  const THEME_KEY = 'ai_guard_theme';

  // ===============================
  // 🎨 Theme Management (Dark Mode)
  // ===============================
  function loadTheme() {
    const theme = localStorage.getItem(THEME_KEY) || 'light';
    if (theme === 'dark') {
      document.body.classList.add('ai-dark-mode');
    }
    return theme;
  }

  function toggleTheme() {
    const isDark = document.body.classList.toggle('ai-dark-mode');
    localStorage.setItem(THEME_KEY, isDark ? 'dark' : 'light');
    showToast(isDark ? '🌙 מצב כהה הופעל' : '☀️ מצב בהיר הופעל', 'info');
  }

  // ===============================
  // 🔔 Toast Notifications
  // ===============================
  function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `ai-toast ${type}`;
    
    const icons = {
      success: '✅',
      error: '❌',
      info: 'ℹ️',
      warning: '⚠️'
    };
    
    toast.innerHTML = `
      <div class="ai-toast-icon">${icons[type] || icons.info}</div>
      <div class="ai-toast-message">${message}</div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(20px)';
      toast.style.transition = 'all 0.3s';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  // ===============================
  // 📊 Risk Visualization
  // ===============================
  function createRiskMeter(riskLevel) {
    return `
      <div class="ai-risk-meter">
        <div class="ai-risk-meter-fill ${riskLevel}"></div>
      </div>
    `;
  }

  // ===============================
  // 🎯 Mock Analysis
  // ===============================
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

  // ===============================
  // 🌐 API Call
  // ===============================
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

  // ===============================
  // 🎨 Panel State
  // ===============================
  let panelRoot = null;
  let lastResult = null;
  let currentComposeContext = null;
  let applyHandlers = null;
  let lastAnalysisPayload = null; // ✅ לשמירת payload אחרון

  function closePanel() {
    if (!panelRoot) return;
    panelRoot.style.display = "none";
    lastResult = null;
    currentComposeContext = null;
  }

  // ===============================
  // 🏗️ Create Panel
  // ===============================
  function createPanel() {
    if (panelRoot) return panelRoot;

    panelRoot = document.createElement("div");
    panelRoot.id = "ai-guard-panel";
    panelRoot.innerHTML = `
      <div class="ai-guard-header">
        <div class="ai-guard-title">AI Communication Guard</div>
        <button class="ai-settings-btn" title="הגדרות">⚙️</button>
        <button class="ai-guard-close-btn">×</button>
      </div>

      <!-- Settings Menu -->
      <div class="ai-settings-menu">
        <div class="ai-settings-item" data-action="toggle-theme">
          <span>🌙 מצב כהה</span>
          <div class="ai-toggle"></div>
        </div>
      </div>

      <div class="ai-tab-content">
        <div class="ai-guard-subtitle">
          ניתוח טון וסיכונים לפני שליחה
          ${MOCK_MODE ? '<br><b style="color:#d00">MOCK MODE פעיל — אין פנייה לשרת</b>' : ""}
          <div class="ai-ai-status" style="margin-top:6px; font-size:12px;"></div>
        </div>

        <!-- Progress Bar -->
        <div class="ai-progress-container" style="display:none;">
          <div class="ai-progress-bar" style="width: 0%"></div>
        </div>

        <button class="ai-main-btn ai-btn-reanalyze" style="display:none;">🔄 נתח מחדש</button>

        <button class="ai-secondary-btn ai-btn-apply" style="display:none;" disabled>
          ✨ החל על הטיוטה
        </button>

        <div class="ai-loading" style="display:none; text-align:center; padding:16px;">
          <div class="ai-spinner"></div>
          <div style="margin-top:8px; font-size:13px; color:#555;">
            מנתח את ההודעה… אנא המתיני רגע
          </div>
        </div>

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
            <div class="ai-risk-meter-container"></div>
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

          <div class="ai-card ai-rewrite-card" style="display:none;">
            <h4><span class="ai-icon">✨</span> ניסוח בטוח יותר</h4>
            <div class="ai-field-safer-body ai-rewrite-box"></div>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(panelRoot);

    // Event Listeners
    panelRoot.querySelector(".ai-guard-close-btn").onclick = closePanel;
    
    // Settings Button
    const settingsBtn = panelRoot.querySelector(".ai-settings-btn");
    const settingsMenu = panelRoot.querySelector(".ai-settings-menu");
    settingsBtn.onclick = (e) => {
      e.stopPropagation();
      settingsMenu.classList.toggle('open');
    };

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!settingsMenu.contains(e.target) && !settingsBtn.contains(e.target)) {
        settingsMenu.classList.remove('open');
      }
    });

    // Theme Toggle
    panelRoot.querySelector('[data-action="toggle-theme"]').onclick = () => {
      toggleTheme();
      const toggle = panelRoot.querySelector('[data-action="toggle-theme"] .ai-toggle');
      toggle.classList.toggle('active');
    };

    // Initialize theme toggle state
    const isDark = document.body.classList.contains('ai-dark-mode');
    if (isDark) {
      panelRoot.querySelector('[data-action="toggle-theme"] .ai-toggle').classList.add('active');
    }

    // ===============================
    // 🔄 Analysis Function
    // ===============================
    async function runAnalysis(forceRefresh = false) {
      const payload = {
        subject: currentComposeContext?.subject || "",
        body: currentComposeContext?.body || "",
        language: "auto",
        is_reply: !!currentComposeContext?.isReply,
        thread_context: currentComposeContext?.thread_context || null
      };

      // ✅ Cache חכם - רק אם התוכן זהה לחלוטין
      const payloadKey = JSON.stringify(payload);
      if (!forceRefresh && lastAnalysisPayload === payloadKey && lastResult) {
        console.log('✅ Using cached analysis - תוכן זהה');
        displayResults(lastResult);
        showToast('📋 משתמש בניתוח קודם (תוכן זהה)', 'info', 2000);
        return;
      }

      const resultBox = panelRoot.querySelector(".ai-result");
      const applyBtn = panelRoot.querySelector(".ai-btn-apply");
      const aiStatus = panelRoot.querySelector(".ai-ai-status");
      const reanalyzeBtn = panelRoot.querySelector(".ai-btn-reanalyze");
      const loadingBox = panelRoot.querySelector(".ai-loading");
      const progressContainer = panelRoot.querySelector(".ai-progress-container");
      const progressBar = panelRoot.querySelector(".ai-progress-bar");

      // Show loading state
      loadingBox.style.display = "block";
      progressContainer.style.display = "block";
      resultBox.style.display = "none";
      applyBtn.disabled = true;
      aiStatus.textContent = "";

      // Animate progress bar
      let progress = 0;
      const progressInterval = setInterval(() => {
        progress += Math.random() * 30;
        if (progress > 90) progress = 90;
        progressBar.style.width = progress + '%';
      }, 200);

      if (reanalyzeBtn) {
        reanalyzeBtn.disabled = true;
        reanalyzeBtn.textContent = "מנתח...";
      }

      try {
        const data = await analyzeBeforeSend(payload);
        
        // Complete progress
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        
        setTimeout(() => {
          progressContainer.style.display = 'none';
          progressBar.style.width = '0%';
        }, 500);

        lastResult = data;
        lastAnalysisPayload = payloadKey; // ✅ שמור את ה-payload
        
        displayResults(data);
        showToast('✅ הניתוח הושלם בהצלחה', 'success');

      } catch (e) {
        clearInterval(progressInterval);
        progressContainer.style.display = 'none';
        console.error(e);
        showToast('❌ שגיאה בניתוח: ' + (e.message || e), 'error');
        applyBtn.disabled = true;
      } finally {
        loadingBox.style.display = "none";
        if (reanalyzeBtn) {
          reanalyzeBtn.disabled = false;
          reanalyzeBtn.textContent = "🔄 נתח מחדש";
        }
      }
    }

    function displayResults(data) {
      const resultBox = panelRoot.querySelector(".ai-result");
      const applyBtn = panelRoot.querySelector(".ai-btn-apply");
      const aiStatus = panelRoot.querySelector(".ai-ai-status");
      
      resultBox.style.display = "block";

      // AI Status
      if (data.ai_ok === false) {
        aiStatus.innerHTML = `<b style="color:#b91c1c">Gemini לא זמין:</b> ${data.ai_error_code || "UNKNOWN"} ${data.ai_error_message ? ("— " + data.ai_error_message) : ""}`;
      } else {
        aiStatus.innerHTML = `<span style="color:#166534"><b>✓ Gemini פעיל</b></span>`;
      }

      // Risk badge
      const riskBadge = panelRoot.querySelector(".ai-risk-badge");
      riskBadge.textContent = data.risk_level || "";
      riskBadge.className = "ai-badge ai-risk-badge";
      if (data.risk_level === "low") riskBadge.classList.add("ai-badge-low");
      else if (data.risk_level === "medium") riskBadge.classList.add("ai-badge-medium");
      else if (data.risk_level === "high") riskBadge.classList.add("ai-badge-high");

      // ✅ Risk meter ויזואלי
      const riskMeterContainer = panelRoot.querySelector(".ai-risk-meter-container");
      riskMeterContainer.innerHTML = createRiskMeter(data.risk_level);

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

      const rewriteCard = panelRoot.querySelector(".ai-rewrite-card");
      
      rewriteCard.style.display = "none";
      applyBtn.style.display = "none";
      applyBtn.disabled = true;

      if (
        data.ai_ok === true &&
        data.analysis_layer === "gemini" &&
        data.safer_body &&
        data.safer_body.trim()
      ) {
        panelRoot.querySelector(".ai-field-safer-body").textContent = data.safer_body;
        rewriteCard.style.display = "block";
        applyBtn.style.display = "block";
        applyBtn.disabled = false;
      }
    }

    panelRoot._runAnalysis = runAnalysis;

    // Re-analyze button
    panelRoot.querySelector(".ai-btn-reanalyze").onclick = async () => {
      await runAnalysis(true); // ✅ force refresh
      panelRoot.querySelector(".ai-btn-reanalyze").style.display = "none";
    };

    // Apply button
    panelRoot.querySelector(".ai-btn-apply").onclick = () => {
      if (lastResult && applyHandlers) {
        applyHandlers.onApply(lastResult, currentComposeContext);
        showToast('✨ השינויים הוחלו על הטיוטה', 'success');
        // ✅ אחרי החלה - נקה cache כי התוכן השתנה
        lastAnalysisPayload = null;
      }
    };

    return panelRoot;
  }

  // ===============================
  // 🚀 Open Panel
  // ===============================
  function openPanel(composeContext, handlers) {
    currentComposeContext = composeContext;
    applyHandlers = handlers;

    const panel = createPanel();
    panel.style.display = "block";

    const reanalyzeBtn = panel.querySelector(".ai-btn-reanalyze");
    if (reanalyzeBtn) reanalyzeBtn.style.display = "none";

    // Auto-analyze on open
    setTimeout(() => {
      panel._runAnalysis && panel._runAnalysis();
    }, 0);
  }

  // ===============================
  // 🌍 Initialize
  // ===============================
  loadTheme();

  // Expose API
  window.AIGuardUI = { 
    openPanel, 
    closePanel,
    showToast 
  };
})();