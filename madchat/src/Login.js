import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import './Login.css'

const Login = ({ setUserData }) => {
  // Check if we already have userData in localStorage
  const [name, setName] = useState("");
  const [gender, setGender] = useState("");
  const [age, setAge] = useState("");

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
      }
    }
  }, [navigate, setUserData]);

  const handleSubmit = (e) => {
    e.preventDefault();

    // Create the userData object
    const userData = { name, gender, age };

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
      <form onSubmit={handleSubmit}>
        <input className="login-input" type="text" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} required />
        <input className="login-input" type="text" placeholder="Gender" value={gender} onChange={(e) => setGender(e.target.value)} required />
        <input className="login-input" type="number" placeholder="Age" value={age} onChange={(e) => setAge(e.target.value)} required />
        <button className="login-button" type="submit">Submit</button>
      </form>
    </div>
  );
};

export default Login;