import "./AnalysisResult.css";

export default function AnalysisResult({ data }) {
  if (!data) return null;

  return (
    <div className="analysis-card">
      <h3>תוצאות ניתוח</h3>

      <div className="analysis-section">
        <strong>סיכום:</strong>
        <p>{data.summary}</p>
      </div>

      <div className="analysis-grid">
        <div><strong>קטגוריה:</strong> {data.category}</div>
        <div><strong>עדיפות:</strong> {data.priority}</div>
        <div><strong>טון:</strong> {data.tone}</div>
        <div><strong>רמת סיכון:</strong> {data.risk_level}</div>
      </div>

      <div className="analysis-section">
        <strong>רגשות:</strong>
        <ul>{data.emotions.map((e, i) => <li key={i}>{e}</li>)}</ul>
      </div>

      <div className="analysis-section">
        <strong>משימות:</strong>
        <ul>{data.tasks.map((t, i) => <li key={i}>{t}</li>)}</ul>
      </div>

      <div className="analysis-section">
        <strong>התגובה המוצעת:</strong>
        <p>{data.suggested_reply}</p>
      </div>
    </div>
  );
}
