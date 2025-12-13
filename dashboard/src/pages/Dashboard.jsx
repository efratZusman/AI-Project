// src/pages/Dashboard.jsx
import { useEffect, useState } from "react";
import "./Dashboard.css";

import EmailForm from "../components/EmailForm/EmailForm";
import HistoryList from "../components/HistoryList/HistoryList";
import AnalysisCard from "../components/AnalysisCard/AnalysisCard";
import {
  getHistory,
  getEmailById,
  deleteEmail,
  searchEmails,
  healthCheck,
} from "../services/api";

function Dashboard() {
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [filters, setFilters] = useState({
    q: "",
    category: "all",
    priority: "all",
  });
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [globalError, setGlobalError] = useState("");
  const [healthStatus, setHealthStatus] = useState(null);

  const loadHealth = async () => {
    try {
      const health = await healthCheck();
      setHealthStatus(health);
    } catch (err) {
      console.error(err);
      setHealthStatus({ status: "error" });
    }
  };

  const loadHistory = async () => {
    try {
      setLoadingHistory(true);
      const data = await getHistory();
      setEmails(data);
    } catch (err) {
      console.error(err);
      setGlobalError("שגיאה בטעינת ההיסטוריה מהשרת.");
    } finally {
      setLoadingHistory(false);
    }
  };

  const loadSearch = async (newFilters) => {
    try {
      setLoadingHistory(true);
      const hasFilters =
        (newFilters.q && newFilters.q.trim()) ||
        newFilters.category !== "all" ||
        newFilters.priority !== "all";

      if (!hasFilters) {
        await loadHistory();
        return;
      }

      const data = await searchEmails(newFilters);
      setEmails(data);
    } catch (err) {
      console.error(err);
      setGlobalError("שגיאה בביצוע חיפוש.");
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    loadHealth();
    loadHistory();
  }, []);

  const handleAnalyzeSuccess = (emailRecord) => {
    setSelectedEmail(emailRecord);
    setEmails((prev) => [emailRecord, ...prev]);
  };

  const handleSelectEmail = async (id) => {
    try {
      const full = await getEmailById(id);
      setSelectedEmail(full);
    } catch (err) {
      console.error(err);
      setGlobalError("לא הצלחנו לטעון את המייל שנבחר.");
    }
  };

  const handleDeleteEmail = async (id) => {
    const confirmDelete = window.confirm("למחוק את הרשומה הזו לצמיתות?");
    if (!confirmDelete) return;

    try {
      await deleteEmail(id);
      setEmails((prev) => prev.filter((e) => e.id !== id));
      if (selectedEmail?.id === id) {
        setSelectedEmail(null);
      }
    } catch (err) {
      console.error(err);
      setGlobalError("מחיקה נכשלה. נסי שוב.");
    }
  };

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
    loadSearch(newFilters);
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Email Insight AI</h1>
          <p className="dashboard-subtitle">
            דשבורד ניתוח מיילים חכם – לפרויקט הגמר ולתוסף העתידי שלך.
          </p>
        </div>

        <div className="dashboard-status">
          {healthStatus && (
            <span
              className={`health-pill health-${healthStatus.status === "ok" ? "ok" : "error"}`}
            >
              {healthStatus.status === "ok"
                ? "שרת פעיל · מודל AI מחובר"
                : "בעיה בחיבור לשרת / מודל"}
            </span>
          )}
        </div>
      </header>

      {globalError && <div className="dashboard-error">{globalError}</div>}

      <main className="dashboard-grid">
        <section className="dashboard-column">
          <EmailForm
            onAnalyzeSuccess={handleAnalyzeSuccess}
            onError={setGlobalError}
          />
        </section>

        <section className="dashboard-column">
          <AnalysisCard email={selectedEmail} />
        </section>

        <section className="dashboard-column dashboard-column-full">
          <HistoryList
            emails={emails}
            onSelectEmail={handleSelectEmail}
            onDeleteEmail={handleDeleteEmail}
            filters={filters}
            onFiltersChange={handleFiltersChange}
            loading={loadingHistory}
          />
        </section>
      </main>
    </div>
  );
}

export default Dashboard;
