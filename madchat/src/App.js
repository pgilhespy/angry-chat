import { Route, Routes, Link } from 'react-router-dom';
// import Help from './Help.js'

const App = () => {
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
      {/* <Link to="/help">Help</Link>

      <Routes>
        <Route path="/" element={<div>Welcome to the Home Page!</div>} />
        <Route path="/help" element={<Help />} />
      </Routes> */}
    </div>
  );
}

export default App;
