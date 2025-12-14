import "./Dashboard.css";
import BeforeSend from "../components/BeforeSend/BeforeSend";
import FollowUp from "../components/FollowUp/FollowUp";

export default function Dashboard() {
  return (
    <div className="dashboard">
      <h1 className="title">AI Communication Guard</h1>

      <p className="subtitle">
        כלי הבטיחות החכם שלך לפני שליחת מיילים — וניהול Follow-Up חכם.
      </p>

      <div className="grid">
        <BeforeSend />
        <FollowUp />
      </div>
    </div>
  );
}
