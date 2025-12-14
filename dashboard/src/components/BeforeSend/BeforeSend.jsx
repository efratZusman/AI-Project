import "./BeforeSend.css";
import { useState } from "react";
import { analyzeBeforeSend } from "../../services/api";

export default function BeforeSend() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!text.trim()) return;

    setLoading(true);
    const data = await analyzeBeforeSend(text);
    setResult(data);
    setLoading(false);
  };

  return (
    <div className="card">
      <h2 className="title">Before You Send</h2>
      <p className="subtitle">בדיקת סיכונים + ניסוח בטוח יותר לפני שליחה</p>

      <textarea
        className="input-box"
        placeholder="הדביקי כאן את הטיוטה שלך..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button className="action-btn" onClick={handleAnalyze} disabled={loading}>
        {loading ? "מנתח..." : "נתח לפני שליחה"}
      </button>

      {result && (
        <div className="result-box">
          <h3>Intent</h3>
          <p>{result.intent}</p>

          <h3>Risk Level</h3>
          <p className={`risk ${result.risk_level}`}>{result.risk_level}</p>

          <h3>Risk Factors</h3>
          <ul>
            {result.risk_factors.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>

          <h3>Recipient Interpretation</h3>
          <p>{result.recipient_interpretation}</p>

          <h3>Decision</h3>
          <p>{result.send_decision}</p>

          <h3>Safer Rewrite</h3>
          <div className="rewrite-box">{result.safer_body}</div>
        </div>
      )}
    </div>
  );
}
