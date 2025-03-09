import { Link } from 'react-router-dom';
import React, { useState, useEffect } from'react';
import { FaQuestionCircle } from 'react-icons/fa'
// import Help from './Help.js'

const App = ({ userData }) => {

  const [value, setValue] = useState(null)
  const [message, setMessage] = useState(null)
  const [previousChats, setPreviousChats] = useState([])
  const [currentTitle, setCurrentTitle] = useState(null)

  const createNewChat = () => {
    setMessage(null)
    setValue("")
    setCurrentTitle(null)
  }

  const handleClick  = (uniqueTitles) => {
    setCurrentTitle(uniqueTitles)
    setMessage(null)
    setValue("") 
  }

  const getMessages = async () => {
    const options = {
      method: "POST",
      body : JSON.stringify({
        message: value
      }),
      headers: {
        "Content-Type": "application/json"
      }
    }
    
    try{
      const response = await fetch('http://localhost:8000/completions', options)
      const data = await response.json()
      console.log(data)
      setMessage(data.choices[0].message)
    }catch(error){
      console.error(error)
    }
  }

  useEffect(() => {
    console.log(currentTitle, value, message)
    if(!currentTitle && value && message) {
      setCurrentTitle(value)
    }
    if(currentTitle && value && message){
      setPreviousChats(prevChats => (
        [...prevChats,
          {
            title: currentTitle,
            role:"user",
            content: value
          },
          {
            title: currentTitle,
            role:message.role,
            content: message.content
          }
        ]
      ))
    }

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
  }, [message, currentTitle, userData])

  console.log(previousChats)

  const currentChat = previousChats.filter(previousChats => previousChats.title === currentTitle)
  const uniqueTitles = Array.from(new Set(previousChats.map(previousChat => previousChat.title)))
  console.log(uniqueTitles)

  console.log(value)

  return (
    <div className="app">
      <section className="side-bar">
        <button onClick={createNewChat}>+ New chat</button>
        <ul className="history">
          {uniqueTitles?.map((uniqueTitles, index) => (<li key={index} onClick={() => handleClick(uniqueTitles)}>{uniqueTitles}</li>))}
        </ul>
        <nav>
          <p>Angry Bot pvt. ltd.</p> 
        </nav>
      </section>
      <section className="main">
        {!currentTitle && <h1>Angry Bot</h1>}
        <ul className="feed">
          {currentChat?.map((chatMessage, index) => <li key={index} className={`${chatMessage.role}`}>
            <p className='role'>{chatMessage.role}:</p>
            <p>{chatMessage.content}</p>
          </li>)}
        </ul>
        <div className="bottom-section">
          <div className="input-container">
            <input value={value} onChange={(e) => setValue(e.target.value)}/>
            <div id="submit" className="arrowUp" onClick={getMessages}>➢</div>
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
