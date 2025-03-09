import React, { useState } from "react";
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import Help from './Help';
import { BrowserRouter } from "react-router-dom";
import { Route, Routes } from 'react-router-dom';
import Login from './Login';

const RootComponent = () => {
  const [userData, setUserData] = useState(null); // Store user input

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App userData={userData} />} />
        <Route path="/help" element={<Help userData={userData} />} />
        <Route path="/login" element={<Login setUserData={setUserData} />} />
      </Routes>
    </BrowserRouter>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<RootComponent />);
