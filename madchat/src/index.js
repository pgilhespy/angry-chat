import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import Help from './Help';
import { BrowserRouter } from "react-router-dom";
import { Route, Routes } from 'react-router-dom';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/help" element={<Help />} />
    </Routes>
  </BrowserRouter>
);
