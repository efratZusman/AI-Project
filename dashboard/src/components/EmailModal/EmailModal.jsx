import "./EmailModal.css";

export default function EmailModal({ email, onClose }) {
  if (!email) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-container"
        onClick={(e) => e.stopPropagation()} // שלא יסגור בלחיצה פנימית
      >
        <button className="modal-close-btn" onClick={onClose}>
          ✕
        </button>

        <h2 className="modal-title">{email.subject || "ללא נושא"}</h2>

        <div className="modal-section">
          <strong>תקציר:</strong>
          <p>{email.summary}</p>
        </div>

        <div className="modal-section">
          <strong>קטגוריה:</strong> {email.category}
        </div>

        <div className="modal-section">
          <strong>עדיפות:</strong> {email.priority}
        </div>

        <div className="modal-section">
          <strong>טון:</strong> {email.tone}
        </div>

        <div className="modal-section">
          <strong>רגשות:</strong>
          <div className="chips">
            {email.emotions.map((e, i) => (
              <span className="chip" key={i}>
                {e}
              </span>
            ))}
          </div>
        </div>

        <div className="modal-section">
          <strong>משימות:</strong>
          <ul>
            {email.tasks.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
        </div>

        {email.deadline && (
          <div className="modal-section">
            <strong>דדליין:</strong> {email.deadline}
          </div>
        )}

        {email.missing_information.length > 0 && (
          <div className="modal-section">
            <strong>מידע חסר:</strong>
            <ul>
              {email.missing_information.map((m, i) => (
                <li key={i}>{m}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="modal-section">
          <strong>תגובה מוצעת:</strong>
          <p>{email.suggested_reply}</p>
        </div>

        <div className="modal-section">
          <strong>נוצר בתאריך:</strong>{" "}
          {new Date(email.created_at).toLocaleString()}
        </div>
      </div>
    </div>
  );
}
