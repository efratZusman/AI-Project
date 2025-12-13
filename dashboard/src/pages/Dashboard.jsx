// src/pages/Dashboard.jsx

import { useState, useEffect } from "react";
import "./Dashboard.css";

import EmailForm from "../components/EmailForm/EmailForm";
import HistoryList from "../components/HistoryList/HistoryList";
import EmailModal from "../components/EmailModal/EmailModal";

import {
  getHistory,
  searchEmails,
  deleteEmail,
  getEmailById,
} from "../services/api";

export default function Dashboard() {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(false);

  // מסננים ברירת מחדל
  const [filters, setFilters] = useState({
    q: "",
    category: "all",
    priority: "all",
  });

  // מודל – אינדקס במערך
  const [selectedIndex, setSelectedIndex] = useState(null);

  // ------------ טעינת כל ההיסטוריה ------------
  const loadEmails = async () => {
    setLoading(true);
    const data = await getHistory();
    setEmails(data);
    setLoading(false);
  };

  useEffect(() => {
    loadEmails();
  }, []);

  // ------------ שינוי מסננים ------------
  const handleFiltersChange = async (newFilters) => {
    setFilters(newFilters);
    setLoading(true);
    const data = await searchEmails(newFilters);
    setEmails(data);
    setLoading(false);
  };

  // ------------ פתיחת מודל ------------
  const openEmailModal = (id) => {
    const index = emails.findIndex((e) => e.id === id);
    if (index !== -1) setSelectedIndex(index);
  };

  // ------------ סגירת מודל ------------
  const closeModal = () => setSelectedIndex(null);

  // ------------ ניווט בין אימיילים ------------
  const goNext = () => {
    if (selectedIndex < emails.length - 1) {
      setSelectedIndex(selectedIndex + 1);
    }
  };

  const goPrev = () => {
    if (selectedIndex > 0) {
      setSelectedIndex(selectedIndex - 1);
    }
  };

  // ------------ מחיקה ------------
  const handleDeleteEmail = async (id) => {
    await deleteEmail(id);
    await loadEmails();

    // אם מחקת בזמן שהמודל פתוח → לסגור ולהימנע מבאגים
    if (selectedIndex !== null) closeModal();
  };

  return (
    <div className="dashboard-container">
      <h1 className="dashboard-title">AI Email Analyzer Dashboard</h1>

      <div className="dashboard-grid">
        <EmailForm onEmailAnalyzed={loadEmails} />

        <HistoryList
          emails={emails}
          loading={loading}
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onSelectEmail={openEmailModal}
          onDeleteEmail={handleDeleteEmail}
        />
      </div>

      {/* ---- מודל ---- */}
      {selectedIndex !== null && (
        <EmailModal
          email={emails[selectedIndex]}
          onClose={closeModal}
          onNext={goNext}
          onPrev={goPrev}
          hasNext={selectedIndex < emails.length - 1}
          hasPrev={selectedIndex > 0}
        />
      )}
    </div>
  );
}
