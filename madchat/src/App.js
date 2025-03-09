import React, { useEffect } from "react";
import { Link } from 'react-router-dom';
import { FaQuestionCircle } from 'react-icons/fa'

const App = ({ userData }) => {
  useEffect(() => {
    const sendUserData = async () => {
      if (!userData) return; 

      try {
        const response = await fetch("/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            userData: userData
          }),
        });

        if (!response.ok) {
          throw new Error("Failed to send data");
        }

        console.log("Data sent successfully!");
      } catch (error) {
        console.error("Error sending data:", error);
      }
    };

    sendUserData();
  }, [userData]);

  return (
    <div className="app">
      <section className="side-bar">
        <button>+ New chat</button>
        <ul className="history"></ul>
        <nav>
          <p>Angry Bot pvt. ltd.</p> 
        </nav>
      </section>
      <section className="main">
        <h1>Angry Bot</h1>
        <ul className="feed">
          
        </ul>
        <div className="bottom-section">
          <div className="input-container">
            <input/>
            <div id="submit">➢</div>
          </div>
          <p className="info">
          A chatbot with an attitude—Angry Bot starts annoyed and only gets worse.
          </p>
        </div>
      </section>

      <Link to="/help" style={{ padding: "10px"}}>
        <FaQuestionCircle size={20} />
      </Link>
    </div>
  );
}

export default App;
