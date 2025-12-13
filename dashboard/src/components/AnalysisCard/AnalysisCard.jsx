// src/components/AnalysisCard.jsx
import "./AnalysisCard.css";

function Badge({ label, value }) {
  if (!value) return null;
  return (
    <span className="analysis-badge">
      <span className="analysis-badge-label">{label}</span>
      <span className="analysis-badge-value">{value}</span>
    </span>
  );
}

function AnalysisCard({ email }) {
  if (!email) {
    return (
      <div className="analysis-card empty">
        <h2 className="analysis-title">אין ניתוח נבחר</h2>
        <p className="analysis-empty-text">
          נתחי מייל חדש בצד שמאל או בחרי מייל מההיסטוריה כדי לראות את הניתוח
          המלא.
        </p>
      </div>
    );
  }

  const emotions = email.emotions || [];
  const tasks = email.tasks || [];
  const missing = email.missing_information || [];

  return (
    <div className="analysis-card">
      <div className="analysis-header">
        <div>
          <h2 className="analysis-title">פירוט ניתוח AI</h2>
          <p className="analysis-subtitle">
            תובנות עומק על בסיס המייל שבחרת, כולל משימות, כוונה וסיכונים.
          </p>
        </div>
        <div className="analysis-badges">
          <Badge label="קטגוריה" value={email.category} />
          <Badge label="עדיפות" value={email.priority} />
          <Badge label="טון" value={email.tone} />
          <Badge label="סיכון" value={email.risk_level} />
        </div>
      </div>

      <section className="analysis-section">
        <h3>סיכום</h3>
        <p>{email.summary}</p>
      </section>

      <section className="analysis-section">
        <h3>כוונת השולח</h3>
        <p>{email.intent}</p>
      </section>

      <section className="analysis-section grid-2">
        <div>
          <h3>רגשות שזוהו</h3>
          {emotions.length === 0 ? (
            <p className="analysis-muted">לא זוהו רגשות משמעותיים.</p>
          ) : (
            <ul className="pill-list">
              {emotions.map((emotion, idx) => (
                <li key={idx}>{emotion}</li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <h3>מידע חסר</h3>
          {missing.length === 0 ? (
            <p className="analysis-muted">לא זוהה מידע חסר מהותי.</p>
          ) : (
            <ul className="bullet-list">
              {missing.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          )}
        </div>
      </section>

      <section className="analysis-section">
        <h3>
          משימות לביצוע{" "}
          {email.deadline && (
            <span className="analysis-deadline">דדליין: {email.deadline}</span>
          )}
        </h3>
        {tasks.length === 0 ? (
          <p className="analysis-muted">לא זוהו משימות אקטיביות.</p>
        ) : (
          <ul className="bullet-list">
            {tasks.map((task, idx) => (
              <li key={idx}>{task}</li>
            ))}
          </ul>
        )}
      </section>

      <section className="analysis-section">
        <h3>טיוטת תשובה מוצעת</h3>
        <pre className="analysis-reply-block">{email.suggested_reply}</pre>
      </section>
    </div>
  );
}

export default AnalysisCard;
