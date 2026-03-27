import React from "react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  const exams = [
    { id: 1, name: "Modern Physics CAT1" },
    { id: 2, name: "Modern Physics CAT2" },
    { id: 3, name: "Computer Networks CAT2" }
  ];

  return (
    <div className="dash-container">
      <h2>Select Exam</h2>

      <div className="cards">
        {exams.map((exam) => (
          <div
            key={exam.id}
            className="card"
            onClick={() => navigate(`/exam/${exam.id}`, { state: exam })}
          >
            <h3>{exam.name}</h3>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;