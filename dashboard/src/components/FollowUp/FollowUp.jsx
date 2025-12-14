import "./FollowUp.css";
import { useState } from "react";
import { analyzeFollowUp } from "../../services/api";

export default function FollowUp() {
  const [body, setBody] = useState("");
  const [days, setDays] = useState(3);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!body.trim()) return;

    setLoading(true);
    const data = await analyzeFollowUp(body, days);
    setResult(data);
    setLoading(false);
  };

  return (
    <div className="card">
      <h2 className="title">Follow-Up Guardian</h2>
      <p className="subtitle">האם צריך פולואפ? ואם כן — מה לכתוב?</p>

      <textarea
        className="input-box"
        placeholder="הדביקי כאן את גוף המייל המקורי..."
        value={body}
        onChange={(e) => setBody(e.target.value)}
      />

      <label>כמה ימים עברו?</label>
      <input
        type="number"
        min="1"
        className="days-input"
        value={days}
        onChange={(e) => setDays(Number(e.target.value))}
      />

      <button className="action-btn" onClick={handleAnalyze} disabled={loading}>
        {loading ? "מנתח..." : "בדיקת Follow-Up"}
      </button>

      {result && (
        <div className="result-box">
          <h3>צריך פולואפ?</h3>
          <p>{result.needs_follow_up ? "כן" : "לא"}</p>

          <h3>רמת דחיפות</h3>
          <p>{result.urgency}</p>

          {result.follow_up_reason && (
            <>
              <h3>למה?</h3>
              <p>{result.follow_up_reason}</p>
            </>
          )}

          <h3>הודעת פולואפ מוצעת:</h3>
          <div className="rewrite-box">{result.suggested_follow_up}</div>
        </div>
      )}
    </div>
  );
}
