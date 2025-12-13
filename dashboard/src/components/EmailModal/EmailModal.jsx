import "./EmailModal.css";
import { useEffect } from "react";

export default function EmailModal({
  email,
  onClose,
  onNext,
  onPrev,
  hasNext,
  hasPrev,
}) {
  if (!email) return null;

  // סגירה בלחיצה על ESC
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, []);

  const copyReply = () => {
    navigator.clipboard.writeText(email.suggested_reply);
    alert("התשובה הועתקה ✔");
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-card"
        onClick={(e) => e.stopPropagation()} // כדי שלא יסגור בלחיצה על התוכן
      >
        {/* כפתור סגירה */}
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>

        {/* ניווט בין אימיילים */}
        <div className="modal-nav">
          <button disabled={!hasPrev} onClick={onPrev}>
            ◀ קודם
          </button>
          <button disabled={!hasNext} onClick={onNext}>
            הבא ▶
          </button>
        </div>

        <h2 className="modal-title">{email.subject || "ללא נושא"}</h2>

        <div className="modal-section">
          <h4>תוכן המייל</h4>
          <p>{email.body}</p>
        </div>

        <div className="modal-section">
          <h4>סיכום AI</h4>
          <p>{email.summary}</p>
        </div>

        <div className="modal-details-grid">
          <div>
            <strong>קטגוריה:</strong> {email.category}
          </div>
          <div>
            <strong>עדיפות:</strong> {email.priority}
          </div>
          <div>
            <strong>טון:</strong> {email.tone}
          </div>
          <div>
            <strong>רגשות:</strong> {email.emotions?.join(", ")}
          </div>
          <div>
            <strong>כוונה:</strong> {email.intent}
          </div>
          <div>
            <strong>סיכון:</strong> {email.risk_level}
          </div>
        </div>

        <div className="modal-section">
          <h4>משימות</h4>
          <ul>
            {email.tasks?.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
        </div>

        <div className="modal-section">
          <h4>מידע חסר</h4>
          {email.missing_information?.length ? (
            <ul>
              {email.missing_information.map((m, i) => (
                <li key={i}>{m}</li>
              ))}
            </ul>
          ) : (
            <p>אין מידע חסר 🤍</p>
          )}
        </div>

        <div className="modal-section">
          <h4>תגובה מוצעת</h4>
          <pre className="modal-reply">{email.suggested_reply}</pre>

          <button className="copy-btn" onClick={copyReply}>
            📋 העתק תגובה
          </button>
        </div>
      </div>
    </div>
  );
}
