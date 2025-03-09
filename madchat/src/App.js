import { Link, useNavigate, useLocation } from 'react-router-dom';
import React, { useState, useEffect, useRef } from 'react';
import { FaQuestionCircle, FaEllipsisV, FaEdit, FaTrash, FaUser, FaSignOutAlt, FaChartBar, FaTimes } from 'react-icons/fa';

const App = () => {
  // Navigation for redirect
  const navigate = useNavigate();

  // State management
  const [value, setValue] = useState('');
  const [previousChats, setPreviousChats] = useState([]);
  const [currentTitle, setCurrentTitle] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [messageCount, setMessageCount] = useState(0);

  // User data state from localStorage
  const [userData, setUserData] = useState(() => {
    try {
      // Attempt to get user data from localStorage
      const savedUserData = localStorage.getItem('userData');
      // If it exists, parse and return it, otherwise return null
      return savedUserData ? JSON.parse(savedUserData) : null;
    } catch (e) {
      console.error("Error loading user data from localStorage:", e);
      return null;
    }
  });

  // Dropdown menu state
  const [activeDropdown, setActiveDropdown] = useState(null);

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [modalAction, setModalAction] = useState(''); // 'edit' or 'delete'
  const [selectedTitle, setSelectedTitle] = useState('');
  const [newTitle, setNewTitle] = useState('');

  // Reference to the chat feed for auto-scrolling
  const feedRef = useRef(null);

  // Personality and performance parameters - these will change automatically
  const [angerLevel, setAngerLevel] = useState(0);
  const [glitchLevel, setGlitchLevel] = useState(0);

  // Fixed parameters - no more use_prompt_utils toggle as it's always true
  const personalityMode = "normal";
  const temperature = 0.7;
  const topP = 0.9;
  const maxNewTokens = 150;
  const systemPrompt = null;

  // Calculate remaining messages
  const remainingMessages = 20 - messageCount;

  // Check for userData and redirect if empty
  useEffect(() => {
    if (!userData) {
      navigate('/');
    }
  }, [userData, navigate]);

  // Click outside handler for dropdown menu
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (activeDropdown && !event.target.closest('.dropdown-menu') &&
        !event.target.closest('.dropdown-trigger')) {
        setActiveDropdown(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [activeDropdown]);

  // Generate a unique title for a new conversation
  const generateUniqueTitle = (firstMessage) => {
    const preview = firstMessage.length > 20 ? firstMessage.substring(0, 20) + '...' : firstMessage;
    return `${preview}`;
  };

  // Load conversations from localStorage on component mount
  useEffect(() => {
    const savedChats = localStorage.getItem('previousChats');

    if (savedChats) {
      setPreviousChats(JSON.parse(savedChats));
    }
  }, []);

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('previousChats', JSON.stringify(previousChats));
  }, [previousChats]);

  // Auto-scroll to bottom of chat when messages change
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [previousChats, currentTitle]);

  // Function to update anger and glitch levels based on message count
  const updateLevelsBasedOnMessageCount = (count) => {
    // Update anger level (increases by 10 every 2 messages)
    const newAngerLevel = Math.floor(count / 2) * 10;
    setAngerLevel(newAngerLevel > 100 ? 100 : newAngerLevel);

    // Update glitch level (starts at message 10, increases every 2 messages)
    if (count >= 10) {
      // Calculate how many increments after message 10
      // Message 11-12: 0.3, 13-14: 0.4, 15-16: 0.5, 17-18: 0.6, 19-20: 0.7
      const glitchIncrement = Math.floor((count - 10) / 2);
      const newGlitchLevel = 0.3 + (glitchIncrement * 0.1);
      setGlitchLevel(newGlitchLevel > 0.7 ? 0.7 : newGlitchLevel);
    } else {
      setGlitchLevel(0);
    }
  };

  // Logout function - clear user data
  const handleLogout = () => {
    // Clear user data from state
    setUserData(null);

    // Clear user data from localStorage
    localStorage.removeItem('userData');

    // Reset conversation state
    setValue('');
    setCurrentTitle(null);
    setConversationId(null);
    setMessageCount(0);
    setAngerLevel(0);
    setGlitchLevel(0);

    // Navigate back to login
    navigate('/');
  };

  // Create a new chat conversation
  const createNewChat = () => {
    if (currentTitle && messageCount > 0 && !window.confirm("Start a new chat? This will reset your message count and anger levels.")) {
      return;
    }

    setValue('');
    setCurrentTitle(null);
    setConversationId(null);
    setMessageCount(0);
    setAngerLevel(0);
    setGlitchLevel(0);
  };

  // Handle clicking on an existing conversation
  const handleClick = (title) => {
    // Find all messages for this conversation
    const conversationMessages = previousChats.filter(chat => chat.title === title);

    if (conversationMessages.length === 0) return;

    // Count user messages in this conversation
    const userMessageCount = conversationMessages.filter(msg => msg.role === "user").length;

    setCurrentTitle(title);
    setValue('');
    setMessageCount(userMessageCount);

    // Update anger and glitch levels based on the message count in this conversation
    updateLevelsBasedOnMessageCount(userMessageCount);

    // Find the conversation ID associated with this title
    const conversation = conversationMessages[0];
    if (conversation && conversation.conversationId) {
      setConversationId(conversation.conversationId);
    }
  };

  // Toggle dropdown menu
  const toggleDropdown = (title, e) => {
    e.stopPropagation(); // Prevent triggering the conversation selection
    setActiveDropdown(activeDropdown === title ? null : title);
  };

  // Open modal for editing conversation title
  const openEditModal = (title, e) => {
    e.stopPropagation(); // Prevent triggering the conversation selection
    setModalAction('edit');
    setSelectedTitle(title);
    setNewTitle(title);
    setShowModal(true);
    setActiveDropdown(null); // Close dropdown
  };

  // Open modal for deleting conversation
  const openDeleteModal = (title, e) => {
    e.stopPropagation(); // Prevent triggering the conversation selection
    setModalAction('delete');
    setSelectedTitle(title);
    setShowModal(true);
    setActiveDropdown(null); // Close dropdown
  };

  // Close the modal
  const closeModal = () => {
    setShowModal(false);
    setSelectedTitle('');
    setNewTitle('');
  };

  // Handle title edit
  const handleEditTitle = () => {
    if (!newTitle.trim()) {
      alert("Title cannot be empty");
      return;
    }

    // Update all messages with the selected title to have the new title
    const updatedChats = previousChats.map(chat => {
      if (chat.title === selectedTitle) {
        return { ...chat, title: newTitle };
      }
      return chat;
    });

    setPreviousChats(updatedChats);

    // If the edited title is the current one, update currentTitle
    if (selectedTitle === currentTitle) {
      setCurrentTitle(newTitle);
    }

    closeModal();
  };

  // Handle conversation deletion
  const handleDeleteConversation = () => {
    // Remove all messages with the selected title
    const updatedChats = previousChats.filter(chat => chat.title !== selectedTitle);
    setPreviousChats(updatedChats);

    // If the deleted conversation is the current one, reset to empty state
    if (selectedTitle === currentTitle) {
      setCurrentTitle(null);
      setConversationId(null);
      setMessageCount(0);
      setAngerLevel(0);
      setGlitchLevel(0);
    }

    closeModal();
  };

  // Send message to the backend and process response
  const getMessages = async () => {
    if (!value.trim()) return; // Prevent sending empty messages

    // Check if user has reached the message limit
    if (messageCount >= 20) {
      alert("You've reached the maximum of 20 messages for this conversation. Please start a new chat.");
      return;
    }

    const userInput = value;
    setValue(''); // Clear input immediately for better UX

    // Increment message count
    const newMessageCount = messageCount + 1;
    setMessageCount(newMessageCount);

    // Update anger and glitch levels based on new message count
    updateLevelsBasedOnMessageCount(newMessageCount);

    // Generate a unique title for new conversations
    const chatTitle = currentTitle || generateUniqueTitle(userInput);

    if (!currentTitle) {
      setCurrentTitle(chatTitle);
    }

    // Add user message to chat immediately for better UX
    const userMessage = {
      title: chatTitle,
      role: "user",
      content: userInput,
      conversationId: conversationId,
      timestamp: new Date().toISOString()
    };

    setPreviousChats(prevChats => [...prevChats, userMessage]);

    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message_content: userInput,
          conversation_id: conversationId,
          system_prompt: systemPrompt,
          anger_level: angerLevel,
          personality_mode: personalityMode,
          glitch_level: glitchLevel,
          // use_prompt_utils is removed as it's the default on the server
          temperature: temperature,
          top_p: topP,
          max_new_tokens: maxNewTokens,
          userData: userData
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from server');
      }

      const data = await response.json();

      // Set conversation ID from response if this is a new conversation
      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

      // Add bot response to chat
      const botMessage = {
        title: chatTitle,
        role: "assistant",
        content: data.response,
        conversationId: data.conversation_id,
        timestamp: new Date().toISOString()
      };

      setPreviousChats(prevChats => [...prevChats, botMessage]);
    } catch (error) {
      console.error('Error sending/receiving message:', error);
      // Add error message to chat
      setPreviousChats(prevChats => [
        ...prevChats,
        {
          title: chatTitle,
          role: "system",
          content: "Error: Could not get a response. Please try again.",
          conversationId: conversationId,
          timestamp: new Date().toISOString()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key for sending messages
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      getMessages();
    }
  };

  // Filter chats by current conversation
  const currentChat = previousChats.filter(chat => chat.title === currentTitle);

  // Get unique conversation titles and sort by timestamp (most recent first)
  const uniqueTitles = Array.from(
    new Set(previousChats.map(chat => chat.title))
  ).filter(title => title).sort((a, b) => {
    // Find the latest message in each conversation
    const aLatestMsg = [...previousChats.filter(chat => chat.title === a)]
      .sort((m1, m2) => new Date(m2.timestamp || 0) - new Date(m1.timestamp || 0))[0];
    const bLatestMsg = [...previousChats.filter(chat => chat.title === b)]
      .sort((m1, m2) => new Date(m2.timestamp || 0) - new Date(m1.timestamp || 0))[0];

    // Sort by timestamp (most recent first)
    return new Date(bLatestMsg?.timestamp || 0) - new Date(aLatestMsg?.timestamp || 0);
  });

  return (
    <div className="app" style={{ display: 'flex', flexDirection: 'column', overflowY: 'hidden' }}>
      <Navbar
        userData={userData}
        handleLogout={handleLogout}
        angerLevel={angerLevel}
        glitchLevel={glitchLevel}
        messageCount={messageCount}
      />

      <div style={{ display: 'flex', height: '100%', overflow: 'hidden' }}> {/* Adjust height to account for navbar */}
        <section className="side-bar">
          <button onClick={createNewChat} style={{ cursor: 'pointer' }}>+ New chat</button>
          <ul className="history">
            {uniqueTitles?.map((title, index) => (
              <li
                key={index}
                onClick={() => handleClick(title)}
                style={{
                  position: 'relative',
                  backgroundColor: currentTitle === title ? '#ececec' : 'transparent',
                  borderRadius: '8px',
                  padding: '10px',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div style={{ maxWidth: 'calc(100% - 30px)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {title}
                </div>
                <div
                  className="dropdown-trigger"
                  style={{ cursor: 'pointer', padding: '5px' }}
                  onClick={(e) => toggleDropdown(title, e)}
                >
                  <FaEllipsisV size={14} />
                </div>

                {/* Dropdown Menu */}
                {activeDropdown === title && (
                  <div
                    className="dropdown-menu"
                    style={{
                      position: 'absolute',
                      right: '30px',
                      top: '30px',
                      backgroundColor: 'white',
                      boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
                      borderRadius: '4px',
                      zIndex: 10,
                      minWidth: '120px'
                    }}
                  >
                    <div
                      style={{ padding: '8px 15px', display: 'flex', alignItems: 'center', cursor: 'pointer', borderBottom: '1px solid #f1f1f1' }}
                      onClick={(e) => openEditModal(title, e)}
                    >
                      <FaEdit style={{ marginRight: '8px', fontSize: '14px' }} />
                      <span>Edit title</span>
                    </div>
                    <div
                      style={{ padding: '8px 15px', display: 'flex', alignItems: 'center', cursor: 'pointer', color: '#ff4757' }}
                      onClick={(e) => openDeleteModal(title, e)}
                    >
                      <FaTrash style={{ marginRight: '8px', fontSize: '14px' }} />
                      <span>Delete</span>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
          <nav>
            <p>Angry Bot pvt. ltd.</p>
          </nav>
        </section>

        <section className="main">
          {!currentTitle && <h1>Angry Bot</h1>}
          <ul className="feed" ref={feedRef}>
            {currentChat?.map((chatMessage, index) => (
              <li
                key={index}
                className={chatMessage.role}
                style={{
                  display: 'flex',
                  flexDirection: chatMessage.role === 'user' ? 'row-reverse' : 'row',
                  alignItems: 'flex-start',
                  margin: '15px 0',
                  width: '100%'
                }}
              >
                <p
                  className='role'
                  style={{
                    marginRight: chatMessage.role === 'user' ? '0' : '10px',
                    marginLeft: chatMessage.role === 'user' ? '10px' : '0',
                    fontSize: '13px',
                    fontWeight: 'bold',
                    alignSelf: 'center'
                  }}
                >
                  {chatMessage.role === 'user' ? ': You' : 'Assistant :'}
                </p>
                <div
                  className="message-bubble"
                  style={{
                    backgroundColor: chatMessage.role === 'user' ? '#4A90E2' : '#444654',
                    color: 'rgba(255, 255, 255, 0.8)',
                    padding: '15px 20px',
                    borderRadius: '12px',
                    boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
                    maxWidth: '300px',
                    maxHeight: '300px',
                    overflowY: 'auto',
                    wordWrap: 'break-word'
                  }}
                >
                  <p style={{ margin: 0, lineHeight: '1.5' }}>{chatMessage.content}</p>
                </div>
              </li>
            ))}
            {isLoading && (
              <li
                style={{
                  display: 'flex',
                  flexDirection: 'row',
                  alignItems: 'flex-start',
                  margin: '15px 0',
                  width: '100%'
                }}
              >
                <p
                  className='role'
                  style={{
                    marginRight: '10px',
                    fontSize: '13px',
                    fontWeight: 'bold',
                    alignSelf: 'center'
                  }}
                >
                  assistant:
                </p>
                <div
                  className="message-bubble"
                  style={{
                    backgroundColor: '#444654',
                    color: 'rgba(255, 255, 255, 0.8)',
                    padding: '15px 20px',
                    borderRadius: '12px',
                    boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
                    maxWidth: '300px',
                    opacity: 0.7
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span>Typing</span>
                    <span className="loading-dots" style={{ display: 'inline-block', marginLeft: '4px' }}>
                      <span style={{
                        display: 'inline-block',
                        marginLeft: '2px',
                        animation: 'bounce 1.4s infinite ease-in-out both',
                        animationDelay: '0s',
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: 'currentColor'
                      }}></span>
                      <span style={{
                        display: 'inline-block',
                        marginLeft: '2px',
                        animation: 'bounce 1.4s infinite ease-in-out both',
                        animationDelay: '0.2s',
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: 'currentColor'
                      }}></span>
                      <span style={{
                        display: 'inline-block',
                        marginLeft: '2px',
                        animation: 'bounce 1.4s infinite ease-in-out both',
                        animationDelay: '0.4s',
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: 'currentColor'
                      }}></span>
                      <style>{`
                        @keyframes bounce {
                          0%, 80%, 100% { transform: scale(0); }
                          40% { transform: scale(1); }
                        }
                      `}</style>
                    </span>
                  </div>
                </div>
              </li>
            )}
          </ul>

          <div className="bottom-section">
            <div className="input-container">
              <input
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={remainingMessages > 0 ? `Type your message...` : "Max messages reached. Start a new chat."}
              />
              <div
                id="submit"
                className="arrowUp"
                onClick={remainingMessages > 0 ? getMessages : createNewChat}
                style={remainingMessages <= 0 ? { backgroundColor: '#ff4757' } : {}}
              ></div>
            </div>
            <p className="info">
              A chatbot with an attitude—Bot gets angrier with each message and starts glitching after message 10.
            </p>
          </div>
        </section>
      </div>

      <Link to="/help" className='help-button'>
        <FaQuestionCircle size={20} />
      </Link>

      {/* Modal for edit/delete operations */}
      {
        showModal && (
          <div className="modal-overlay" style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000
          }}>
            <div className="modal-content" style={{
              backgroundColor: '#ffffff',
              padding: '20px',
              borderRadius: '8px',
              maxWidth: '400px',
              width: '90%',
              boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)'
            }}>
              <h2 style={{ marginTop: 0 }}>
                {modalAction === 'edit' ? 'Edit Conversation Title' : 'Delete Conversation'}
              </h2>

              {modalAction === 'edit' ? (
                <div>
                  <p>Change the title for this conversation:</p>
                  <input
                    type="text"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '10px',
                      marginBottom: '15px',
                      borderRadius: '4px',
                      border: '1px solid #ddd'
                    }}
                  />
                </div>
              ) : (
                <p>Are you sure you want to delete this conversation? This action cannot be undone.</p>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
                <button
                  onClick={closeModal}
                  style={{
                    padding: '8px 15px',
                    backgroundColor: '#f2f2f2',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={modalAction === 'edit' ? handleEditTitle : handleDeleteConversation}
                  style={{
                    padding: '8px 15px',
                    backgroundColor: modalAction === 'edit' ? '#4A90E2' : '#ff4757',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  {modalAction === 'edit' ? 'Save' : 'Delete'}
                </button>
              </div>
            </div>
          </div>
        )
      }
    </div >
  );
};

export default App;


const Navbar = ({ userData, handleLogout, angerLevel, glitchLevel, messageCount }) => {
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [showStatsPanel, setShowStatsPanel] = useState(false);

  const profileRef = useRef(null);
  const statsRef = useRef(null);

  // Handle click outside to close dropdowns
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setShowProfileDropdown(false);
      }
      if (statsRef.current && !statsRef.current.contains(event.target) &&
        event.target.id !== 'stats-toggle') {
        setShowStatsPanel(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <nav style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '4px 10px',
      backgroundColor: '#f9f9f9',
      borderBottom: '1px solid #e1e1e1',
      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
      position: 'relative',
      top: 0,
      zIndex: 100
    }}>
      <div className="logo" style={{ fontWeight: 'bold', fontSize: '20px' }}>
        Angry Bot
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        {/* Stats Icon */}
        <div style={{ position: 'relative' }}>
          <button
            id="stats-toggle"
            onClick={() => setShowStatsPanel(!showStatsPanel)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '8px',
              borderRadius: '50%',
              backgroundColor: showStatsPanel ? '#e1e1e1' : 'transparent'
            }}
          >
            <FaChartBar size={20} />
          </button>

          {/* Stats Panel */}
          {showStatsPanel && (
            <div
              ref={statsRef}
              style={{
                position: 'absolute',
                right: 0,
                top: '40px',
                backgroundColor: 'white',
                borderRadius: '8px',
                boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
                padding: '15px',
                width: '250px',
                zIndex: 10
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h4 style={{ margin: 0 }}>Bot Stats</h4>
                <button
                  onClick={() => setShowStatsPanel(false)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer' }}
                >
                  <FaTimes size={14} />
                </button>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <div style={{ marginBottom: '5px', fontSize: '14px' }}>
                  <strong>Messages:</strong> {messageCount}/20
                </div>
                <div style={{ marginBottom: '5px', fontSize: '14px' }}>
                  <strong>Anger Level:</strong> {angerLevel}/100
                </div>
                <div style={{ marginBottom: '5px', fontSize: '14px' }}>
                  <strong>Glitch Level:</strong> {glitchLevel.toFixed(1)}
                </div>
                <div style={{ height: '5px', width: '100%', backgroundColor: '#f0f0f0', borderRadius: '3px', marginTop: '5px' }}>
                  <div
                    style={{
                      height: '100%',
                      width: `${(messageCount / 20) * 100}%`,
                      backgroundColor: messageCount < 10 ? '#4A90E2' : messageCount < 16 ? '#ff9933' : '#ff4757',
                      borderRadius: '3px',
                      transition: 'width 0.3s ease-in-out'
                    }}
                  />
                </div>
              </div>

              <div style={{ fontSize: '12px', color: '#666' }}>
                Bot gets angrier every 2 messages and starts glitching after message 10.
              </div>
            </div>
          )}
        </div>

        {/* Profile Icon */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowProfileDropdown(!showProfileDropdown)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '8px',
              borderRadius: '50%',
              backgroundColor: showProfileDropdown ? '#e1e1e1' : 'transparent'
            }}
          >
            <FaUser size={20} />
          </button>

          {/* Profile Dropdown */}
          {showProfileDropdown && (
            <div
              ref={profileRef}
              style={{
                position: 'absolute',
                right: 0,
                top: '40px',
                backgroundColor: 'white',
                borderRadius: '8px',
                boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
                padding: '15px',
                width: '200px',
                zIndex: 10
              }}
            >
              <h4 style={{ margin: '0 0 10px 0', borderBottom: '1px solid #eee', paddingBottom: '10px' }}>
                User Profile
              </h4>
              {userData ? (
                <>
                  <div style={{ marginBottom: '15px' }}>
                    <div style={{ marginBottom: '5px' }}><strong>Name:</strong> {userData.name}</div>
                    {userData.age && <div style={{ marginBottom: '5px' }}><strong>Age:</strong> {userData.age}</div>}
                    {userData.gender && <div style={{ marginBottom: '5px' }}><strong>Gender:</strong> {userData.gender}</div>}
                  </div>
                  <button
                    onClick={() => {
                      handleLogout();
                      setShowProfileDropdown(false);
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px',
                      width: '100%',
                      padding: '8px',
                      backgroundColor: '#ff4757',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontWeight: 'bold'
                    }}
                  >
                    <FaSignOutAlt size={14} />
                    <span>Logout</span>
                  </button>
                </>
              ) : (
                <div>Please log in</div>
              )}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};