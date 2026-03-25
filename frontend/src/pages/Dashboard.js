import React from "react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="dash-container">
      <h2>Teacher Dashboard</h2>

      <div className="cards">
        <div className="card" onClick={() => navigate("/upload")}>
          Upload Answer Sheets
        </div>

        <div className="card">
          Upload Answer Key
        </div>

        <div className="card">
          View Question Paper
        </div>

        <div className="card">
          Select Exam
        </div>
      </div>
    </div>
  );
}

export default Dashboard;