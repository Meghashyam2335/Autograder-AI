import React, { useState } from "react";
import { useParams } from "react-router-dom";
import "../components/UploadForm.css";

function UploadAnswerKey() {
  const { examId } = useParams();

  const [questionId, setQuestionId] = useState("");
  const [question, setQuestion] = useState("");
  const [key, setKey] = useState("");

  const handleUpload = async () => {
    if (!questionId || !question || !key) {
      alert("Fill all fields");
      return;
    }

    await fetch("http://localhost:5000/upload-key", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        exam_id: examId,
        question_id: questionId,
        question: question,
        key: key
      })
    });

    alert("Key uploaded!");
    setQuestionId("");
    setQuestion("");
    setKey("");
  };

  return (
    <div className="upload-container">
      <div className="upload-card">

        <h2>Upload Answer Key</h2>

        <div className="input-group">
          <input
            placeholder="Question ID (Q1, Q2...)"
            value={questionId}
            onChange={(e) => setQuestionId(e.target.value)}
          />
        </div>

        <div className="input-group">
          <textarea
            placeholder="Question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
        </div>

        <div className="input-group">
          <textarea
            placeholder="Answer Key"
            value={key}
            onChange={(e) => setKey(e.target.value)}
          />
        </div>

        <div className="button-wrapper">
          <button className="upload-btn" onClick={handleUpload}>
            Upload Key
          </button>
        </div>

      </div>
    </div>
  );
}

export default UploadAnswerKey;