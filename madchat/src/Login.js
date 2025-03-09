import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import './Login.css'

const Login = ({ setUserData }) => {
  const [name, setName] = useState("");
  const [gender, setGender] = useState("");
  const [age, setAge] = useState("");

  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setUserData({ name, gender, age });
    navigate("/");
  };

  return (
    <div className="login-container">
      <h2>Enter Your Information</h2>
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