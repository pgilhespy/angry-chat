import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import './Login.css';

const Login = ({ setUserData }) => {
  // Check if we already have userData in localStorage
  const [name, setName] = useState("");
  const [gender, setGender] = useState("");
  const [age, setAge] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  // On component mount, check if we have saved user data
  useEffect(() => {
    const savedUserData = localStorage.getItem('userData');
    if (savedUserData) {
      try {
        const parsed = JSON.parse(savedUserData);
        // If we have saved data, auto-populate the form
        if (parsed.name) setName(parsed.name);
        if (parsed.gender) setGender(parsed.gender);
        if (parsed.age) setAge(parsed.age);

        // Option: Auto-navigate to home if user data exists
        setUserData(parsed);
        navigate("/home");
      } catch (e) {
        console.error("Error parsing saved user data:", e);
        // Clear corrupted data
        localStorage.removeItem('userData');
      }
    }
  }, [navigate, setUserData]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    // Validate inputs
    if (!name.trim()) {
      setError("Name is required");
      return;
    }

    // Create the userData object with proper types
    const userData = {
      name: name.trim(),
      gender: gender.trim(),
      age: age ? parseInt(age, 10) : ""
    };

    // Save to state via the prop function
    setUserData(userData);

    // Save to localStorage for persistence
    localStorage.setItem('userData', JSON.stringify(userData));

    // Navigate to the home page
    navigate("/home");
  };

  return (
    <div className="login-container">
      <h2>Angry Chat</h2>
      <h1>Enter Your Information</h1>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Name (Required)</label>
          <input id="name" className="login-input" type="text" placeholder="Your name" value={name} onChange={e => setName(e.target.value)} required style={{ borderColor: name.trim() ? "" : "red" }} />
        </div>
        <div className="form-group">
          <label htmlFor="gender">Gender (Optional)</label>
          <input id="gender" className="login-input" value={gender} onChange={e => setGender(e.target.value)} />
        </div>
        <div className="form-group">
          <label htmlFor="age">Age (Optional)</label>
          <input id="age" className="login-input" type="number" min="1" max="120" placeholder="Your age" value={age} onChange={e => setAge(e.target.value)} />
        </div>

        <button className="login-button" type="submit">Start Chatting</button>
      </form >
    </div >
  );
};

export default Login;