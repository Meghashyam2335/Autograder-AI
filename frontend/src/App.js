import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ExamPage from "./pages/ExamPage";
import UploadForm from "./components/UploadForm";

import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/exam/:examId" element={<ExamPage />} />
        <Route path="/upload/:examId" element={<UploadForm />} />
        <Route path="/upload-key/:examId" element={<div>Upload Key Page</div>} />
        <Route path="/question/:examId" element={<div>Question Paper Page</div>} />
      </Routes>
    </Router>
  );
}

export default App;