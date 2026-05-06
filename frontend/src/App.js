import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ExamPage from "./pages/ExamPage";

import UploadForm from "./components/UploadForm";

// NEW PAGES (must exist in /pages)
import UploadAnswerKey from "./pages/UploadAnswerKey";
import QuestionPaper from "./pages/QuestionPaper";

import "./App.css";

function App() {
  return (
    <Router>
      <Routes>

        {/* AUTH */}
        <Route path="/" element={<Login />} />

        {/* DASHBOARD */}
        <Route path="/dashboard" element={<Dashboard />} />

        {/* EXAM DASHBOARD */}
        <Route path="/exam/:examId" element={<ExamPage />} />

        {/* UPLOAD ANSWER SHEET (your existing component) */}
        <Route path="/upload/:examId" element={<UploadForm />} />

        {/* NEW: TEACHER UPLOAD KEY PAGE */}
        <Route path="/upload-key/:examId" element={<UploadAnswerKey />} />

        {/* NEW: QUESTION PAPER VIEW */}
        <Route path="/question/:examId" element={<QuestionPaper />} />

      </Routes>
    </Router>
  );
}

export default App;