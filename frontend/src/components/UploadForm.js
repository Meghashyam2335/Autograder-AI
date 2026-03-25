import React, { useState } from "react";

function UploadForm() {
  const [file, setFile] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      alert("Please upload a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log(data); // debug

      alert("Upload successful");
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Upload Answer Sheet</h2>

      <form onSubmit={handleSubmit}>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <br /><br />

        <button type="submit">Upload</button>
      </form>
    </div>
  );
}

export default UploadForm;