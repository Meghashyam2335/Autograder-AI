import "./UploadForm.css";

import React, { useState } from "react";
import { useParams } from "react-router-dom";

function UploadForm() {
  const { examId } = useParams();

  const [file, setFile] = useState(null);
  const [studentId, setStudentId] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    setError(null);
    setResult(null);

    if (!file || !studentId) {
      setError("Select file and student");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("student_id", studentId);
    formData.append("exam_id", examId);
    formData.append("question_id", "Q1");

    try {
      setLoading(true);

      const res = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error);

      setResult(data);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
  <div className="upload-container">
    <div className="math-bg">
  <span className="symbol" style={{ left: "10%", top: "80%", animationDuration: "14s" }}>∑</span>
  <span className="symbol" style={{ left: "25%", top: "70%", animationDuration: "18s" }}>∫</span>
  <span className="symbol" style={{ left: "40%", top: "85%", animationDuration: "16s" }}>π</span>
  <span className="symbol" style={{ left: "55%", top: "75%", animationDuration: "20s" }}>√</span>
  <span className="symbol" style={{ left: "70%", top: "90%", animationDuration: "15s" }}>∆</span>
  <span className="symbol" style={{ left: "85%", top: "65%", animationDuration: "19s" }}>x²</span>
  <span className="symbol" style={{ left: "15%", top: "60%", animationDuration: "17s" }}>f(x)</span>
  <span className="symbol" style={{ left: "60%", top: "50%", animationDuration: "21s" }}>∞</span>
  <span className="symbol" style={{ left: "80%", top: "40%", animationDuration: "22s" }}>≈</span>
    </div>
    <div className="upload-card">

      <h2>Upload Answer Sheet</h2>

      <div className="input-group">
        <select onChange={(e) => setStudentId(e.target.value)}>
          <option value="">Select Student</option>
          <option value="S1">Student 1</option>
          <option value="S2">Student 2</option>
          <option value="S3">Student 3</option>
        </select>
      </div>

      <div className="input-group">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
        />
      </div>

      <div className="button-wrapper">
        <button
          className="upload-btn"
          onClick={handleUpload}
          disabled={loading}
        >
          {loading ? "Processing..." : "Upload"}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result-box">
          <h3>Score: {result.score}</h3>
          <p>{result.feedback}</p>
        </div>
      )}

    </div>
  </div>
);
}

export default UploadForm;