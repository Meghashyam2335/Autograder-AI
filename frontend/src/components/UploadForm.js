import React, { useState } from "react";
import "./UploadForm.css";

function UploadForm() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      alert("Please upload a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);

      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h2>📄 AutoGrader</h2>

        <form onSubmit={handleSubmit}>
          <label className="upload-box">
            {file ? file.name : "Click to upload answer sheet"}
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
              hidden
            />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Processing..." : "Upload & Analyze"}
          </button>
        </form>

        {result && (
          <div className="result">
            <h3>Result</h3>
            <p><b>Text:</b> {result.extracted_text}</p>
            <p><b>Similarity:</b> {result.similarity}</p>
            <p><b>Score:</b> {result.score}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default UploadForm;