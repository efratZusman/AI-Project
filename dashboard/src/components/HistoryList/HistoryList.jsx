// src/components/HistoryList.jsx
import "./HistoryList.css";

function HistoryList({
  emails,
  onSelectEmail,
  onDeleteEmail,
  filters,
  onFiltersChange,
  loading,
}) {
  const handleInputChange = (field, value) => {
    onFiltersChange({
      ...filters,
      [field]: value,
    });
  };

  return (
    <div className="history-card">
      <div className="history-header">
        <div>
          <h2 className="history-title">היסטוריית ניתוחים</h2>
          <p className="history-subtitle">
            שמירה אוטומטית של כל המיילים שנותחו עם ה־AI.
          </p>
        </div>
      </div>

      <div className="history-filters">
        <div className="history-filter-group">
          <label>חיפוש חופשי</label>
          <input
            type="text"
            placeholder="חיפוש לפי נושא, תוכן או סיכום..."
            value={filters.q}
            onChange={(e) => handleInputChange("q", e.target.value)}
          />
        </div>

        <div className="history-filter-group">
          <label>קטגוריה</label>
          <select
            value={filters.category}
            onChange={(e) => handleInputChange("category", e.target.value)}
          >
            <option value="all">הכל</option>
            <option value="finance">כספים</option>
            <option value="kids_school">בית ספר / ילדים</option>
            <option value="health">בריאות</option>
            <option value="study_work">לימודים / עבודה</option>
            <option value="general">כללי</option>
          </select>
        </div>

        <div className="history-filter-group">
          <label>עדיפות</label>
          <select
            value={filters.priority}
            onChange={(e) => handleInputChange("priority", e.target.value)}
          >
            <option value="all">הכל</option>
            <option value="high">גבוהה</option>
            <option value="medium">בינונית</option>
            <option value="low">נמוכה</option>
          </select>
        </div>
      </div>

      <div className="history-list">
        {loading && <div className="history-loading">טוען נתונים...</div>}

        {!loading && emails.length === 0 && (
          <div className="history-empty">
            עדיין אין מיילים בהיסטוריה או שהחיפוש לא מצא תוצאות.
          </div>
        )}

        {!loading &&
          emails.map((email) => (
            <div
              key={email.id}
              className="history-item"
              onClick={() => onSelectEmail(email.id)}
            >
              <div className="history-item-main">
                <div className="history-item-top">
                  <span className="history-item-category">
                    {email.category || "general"}
                  </span>
                  <span
                    className={`history-item-priority priority-${email.priority}`}
                  >
                    {email.priority}
                  </span>
                </div>

                <div className="history-item-subject">
                  {email.subject || "ללא נושא"}
                </div>

                <div className="history-item-summary">
                  {email.summary || email.body?.slice(0, 120) + "..."}
                </div>

                <div className="history-item-meta">
                  <span>{new Date(email.created_at).toLocaleString()}</span>
                  {email.tone && (
                    <span className="history-chip">
                      טון: <strong>{email.tone}</strong>
                    </span>
                  )}
                </div>
              </div>

              <button
                className="history-delete-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteEmail(email.id);
                }}
              >
                ✕
              </button>
            </div>
          ))}
      </div>
    </div>
  );
}

export default HistoryList;
