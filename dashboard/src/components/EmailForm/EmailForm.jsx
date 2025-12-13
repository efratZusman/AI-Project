// src/components/EmailForm.jsx
import { useState } from "react";
import "./EmailForm.css";
import { analyzeEmail } from "../../services/api";

function EmailForm({ onAnalyzeSuccess, onError }) {
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!body.trim()) {
      onError?.("יש להזין תוכן מייל לניתוח.");
      return;
    }

    try {
      setLoading(true);
      onError?.("");
      const result = await analyzeEmail({ subject, body });
      onAnalyzeSuccess(result);
    } catch (err) {
      console.error(err);
      onError?.("אירעה שגיאה בזמן ניתוח המייל. נסי שוב.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSubject("");
    setBody("");
  };

  return (
    <div className="email-form-card">
      <h2 className="email-form-title">ניתוח מייל חדש</h2>
      <p className="email-form-subtitle">
        הדביקי מייל שקיבלת, והמערכת תבצע ניתוח עומק ותציע תגובה חכמה.
      </p>

      <form onSubmit={handleSubmit} className="email-form">
        <div className="email-form-field">
          <label>נושא</label>
          <input
            type="text"
            placeholder="נושא המייל (לא חובה)"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />
        </div>

        <div className="email-form-field">
          <label>תוכן המייל</label>
          <textarea
            rows={8}
            placeholder="הדביקי כאן את תוכן המייל..."
            value={body}
            onChange={(e) => setBody(e.target.value)}
          />
        </div>

        <div className="email-form-actions">
          <button
            type="button"
            className="secondary-btn"
            onClick={handleReset}
            disabled={loading}
          >
            ניקוי
          </button>

          <button type="submit" className="primary-btn" disabled={loading}>
            {loading ? "מנתח..." : "ניתוח מייל"}
          </button>
        </div>

        <p className="email-form-hint">
          ⚡ הניתוח מתבצע עם Gemini דרך השרת שלך, כולל שמירה למסד הנתונים.
        </p>
      </form>
    </div>
  );
}

export default EmailForm;
