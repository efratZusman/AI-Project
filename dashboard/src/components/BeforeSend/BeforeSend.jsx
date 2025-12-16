import "./BeforeSend.css";
import { useState } from "react";
import { analyzeBeforeSend } from "../../services/api";

export default function BeforeSend() {
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [isReply, setIsReply] = useState(false);
  const [threadRaw, setThreadRaw] = useState(""); // טקסט שהמשתמש מדביק
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // הופך טקסט חופשי של שירשור לרשימה של הודעות
  const parseThread = () => {
    if (!threadRaw.trim()) return null;

    return threadRaw
      .split("\n---\n") // מחלק הודעות לפי מפריד
      .map((block) => ({
        author: block.startsWith("me:") ? "me" : "them",
        text: block.replace(/^me:|^them:/, "").trim(),
      }));
  };

  const handleAnalyze = async () => {
    if (!body.trim()) return;
    setLoading(true);
    setError("");

    const threadContext = isReply ? parseThread() : null;

    try {
      const data = await analyzeBeforeSend(subject, body, isReply, threadContext);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="title">Before You Send</h2>
      <p className="subtitle">בדיקה חכמה לפני שליחה — כולל שירשור</p>

      <input
        className="input-box"
        placeholder="נושא המייל..."
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
      />

      <textarea
        className="input-box"
        placeholder="גוף המייל..."
        value={body}
        onChange={(e) => setBody(e.target.value)}
      />

      <label style={{ marginTop: "10px", display: "flex", gap: "8px" }}>
        <input
          type="checkbox"
          checked={isReply}
          onChange={(e) => setIsReply(e.target.checked)}
        />
        זהו מייל Reply?
      </label>

      {isReply && (
        <textarea
          className="input-box"
          style={{ height: "120px" }}
          placeholder={`שימי כאן את השירשור — לדוגמה:\nthem: למה לא ענית?\n---\nme: שלחתי כבר אתמול\n---\nthem: לא ראיתי את זה`}
          value={threadRaw}
          onChange={(e) => setThreadRaw(e.target.value)}
        />
      )}

      <button className="action-btn" onClick={handleAnalyze} disabled={loading}>
        {loading ? "מנתח..." : "נתח לפני שליחה"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <div className="result-box">
          <h3>Intent</h3>
          <p>{result.intent}</p>

          <h3>Risk Level</h3>
          <p className={`risk ${result.risk_level}`}>{result.risk_level}</p>

          <h3>Risk Factors</h3>
          <ul>
            {result.risk_factors?.map((r, i) => <li key={i}>{r}</li>)}
          </ul>

          <h3>Recipient Interpretation</h3>
          <p>{result.recipient_interpretation}</p>

          <h3>Decision</h3>
          <p>{result.send_decision}</p>

          <h3>Safer Subject</h3>
          <p>{result.safer_subject}</p>

          <h3>Safer Body</h3>
          <div className="rewrite-box">{result.safer_body}</div>
        </div>
      )}
    </div>
  );
}
