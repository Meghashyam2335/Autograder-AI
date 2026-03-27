import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

function Login() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);

  const handleLogin = (e) => {
    e.preventDefault();

    if (username && password) {
      navigate("/dashboard");
    } else {
      alert("Enter credentials");
    }
  };

  return (
    <div className="bg">
      <div className="login-card">
        <h2>AutoGrader</h2>
        <p className="subtitle">Teacher Login</p>

        <form onSubmit={handleLogin}>
          <div className="input-box">
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <label>Username</label>
          </div>

          <div className="input-box">
            <input
              type={show ? "text" : "password"}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <label>Password</label>

            <span className="toggle" onClick={() => setShow(!show)}>
              {show ? "🙈" : "👁"}
            </span>
          </div>

          <button type="submit">Login</button>
        </form>
      </div>
    </div>
  );
}

export default Login;