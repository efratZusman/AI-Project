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

  const [filters, setFilters] = useState({
    q: "",
    category: "all",
    priority: "all",
  });

  const [selectedEmail, setSelectedEmail] = useState(null);

  const loadEmails = async () => {
    setLoading(true);
    const data = await getHistory();
    setEmails(data);
    setLoading(false);
  };

  useEffect(() => {
    loadEmails();
  }, []);

  const handleFiltersChange = async (newFilters) => {
    setFilters(newFilters);
    setLoading(true);
    const data = await searchEmails(newFilters);
    setEmails(data);
    setLoading(false);
  };

  const handleSelectEmail = async (id) => {
    const email = await getEmailById(id);
    setSelectedEmail(email);
  };

  const handleDeleteEmail = async (id) => {
    await deleteEmail(id);
    loadEmails();
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
          onSelectEmail={handleSelectEmail}
          onDeleteEmail={handleDeleteEmail}
        />
      </div>

      <EmailModal email={selectedEmail} onClose={() => setSelectedEmail(null)} />
    </div>
  );
}
