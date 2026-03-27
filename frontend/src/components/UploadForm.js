import React, { useState } from "react";
import { useParams } from "react-router-dom";
import "./UploadForm.css";

function UploadForm() {
  const { examId } = useParams();

  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("examId", examId);

    try {
      setLoading(true);

      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log("Backend Response:", data);
      setResult(data);
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-bg">
      <div className="upload-card">

        <h2>Upload Answer Sheets</h2>
        <p className="subtitle">Exam ID: {examId}</p>

        {/* Upload Box */}
        <label className="upload-box">
          {file ? file.name : "Choose File"}
          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
            hidden
          />
        </label>

        {/* Upload Button */}
        <button onClick={handleUpload}>Upload</button>

        {/* Loading */}
        {loading && <p className="loading">Processing... ⏳</p>}

        {/* Result */}
        {result && (
          <div className="result-box">
            <h3>Score: {result.score}</h3>
            <p><strong>Extracted Text:</strong></p>
            <p className="text">{result.extracted_text}</p>
          </div>
        )}

      </div>
    </div>
  );
}

export default UploadForm;


