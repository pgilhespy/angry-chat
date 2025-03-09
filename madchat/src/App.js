import { Link } from 'react-router-dom';

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
            <div id="submit" className="arrowUp"></div>
          </div>
          <p className="info">
          A chatbot with an attitude—Angry Bot starts annoyed and only gets worse.
          </p>
        </div>
      </section>
      <Link to="/help">Help</Link>
    </div>
  );
}

export default App;
