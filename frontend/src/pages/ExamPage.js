import React from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import "./Dashboard.css";

function ExamPage() {
  const { examId } = useParams();
  const navigate = useNavigate();
  const { state } = useLocation();

  return (
    <div className="dash-container">
      <h2>{state?.name || `Exam ${examId}`}</h2>

      <div className="cards">
        <div className="card" onClick={() => navigate(`/upload/${examId}`)}>
          Upload Answer Sheet
        </div>

        <div className="card" onClick={() => navigate(`/upload-key/${examId}`)}>
          Upload Answer Key
        </div>

        <div className="card" onClick={() => navigate(`/question/${examId}`)}>
          View Question Paper
        </div>
      </div>
    </div>
  );
}

export default ExamPage;