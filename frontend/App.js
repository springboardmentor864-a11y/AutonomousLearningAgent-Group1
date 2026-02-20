import React, { useState, useEffect } from "react";
import axios from "axios";

const API = "https://ai-learning-agent-yw53.onrender.com";
const TOPICS = [
  "data science", "data preprocessing", "EDA", "statistics", "visualization", 
  "feature engineering", "supervised learning", "unsupervised learning", 
  "model evaluation", "deep learning", "neural networks", "NLP", 
  "computer vision", "model deployment", "generative ai"
];

export default function App() {
  // --- USER & AUTH STATE ---
  const [user, setUser] = useState(localStorage.getItem("active_user") || "");
  const [loginInput, setLoginInput] = useState("");
  const [passInput, setPassInput] = useState(""); 
  const [userData, setUserData] = useState({ mastered: {}, attempts: {}, password: "" });

  // --- LEARNING & UI STATE ---
  const [topic, setTopic] = useState(TOPICS[0]);
  const [exp, setExp] = useState("");
  const [rel, setRel] = useState(null);
  const [quiz, setQuiz] = useState([]);
  const [answers, setAnswers] = useState([]);
  const [score, setScore] = useState(null);
  const [reteachText, setReteachText] = useState("");
  const [visibleHints, setVisibleHints] = useState({});

  // --- PERSISTENCE ---
  useEffect(() => {
    if (user) {
      const saved = localStorage.getItem(`data_${user}`);
      if (saved) setUserData(JSON.parse(saved));
      localStorage.setItem("active_user", user);
    }
  }, [user]);

  const saveProgress = (updatedData) => {
    setUserData(updatedData);
    localStorage.setItem(`data_${user}`, JSON.stringify(updatedData));
  };

  // --- NEW AUTH LOGIC ---
  const handleAuth = () => {
    if (!loginInput.trim() || !passInput.trim()) {
      alert("Please enter both Username and Password.");
      return;
    }
    const saved = localStorage.getItem(`data_${loginInput}`);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (parsed.password === passInput) {
        setUser(loginInput);
      } else {
        alert("ACCESS DENIED: Incorrect Password.");
      }
    } else {
      // Register new user on first login
      const newUser = { password: passInput, mastered: {}, attempts: {} };
      localStorage.setItem(`data_${loginInput}`, JSON.stringify(newUser));
      setUser(loginInput);
    }
  };

  const logout = () => {
    setUser("");
    setLoginInput("");
    setPassInput("");
    localStorage.removeItem("active_user");
    setExp(""); setQuiz([]);
  };

  // --- ACTIONS ---
  async function explain() {
    try {
      setExp(""); setQuiz([]); setScore(null); setReteachText("");
      const r = await axios.post(`${API}/explain`, { topic });
      setExp(r.data.explanation);
      setRel(r.data.score);
    } catch (err) { alert("Backend Connection Lost."); }
  }

  async function startQuiz() {
    const tries = userData.attempts[topic] || 0;
    if (tries >= 3 && !userData.mastered[topic]) {
      alert("CRITICAL: Attempt Limit Reached. System Locked for this module.");
      return;
    }
    try {
      const r = await axios.post(`${API}/quiz`, { topic, explanation: exp });
      const questions = Array.isArray(r.data) ? r.data : [];
      setQuiz(questions);
      setAnswers(new Array(questions.length).fill(null));
      setScore(null);
      setVisibleHints({});
    } catch (err) { console.error(err); }
  }

  async function submit() {
    try {
      const r = await axios.post(`${API}/submit`, { answers });
      const finalScore = r.data.score;
      setScore(finalScore);

      let updatedAttempts = { ...userData.attempts, [topic]: (userData.attempts[topic] || 0) + 1 };
      let updatedMastered = { ...userData.mastered };

      if (finalScore >= 3) {
        updatedMastered[topic] = true;
      } else {
        const resp = await axios.post(`${API}/reteach`, { topic });
        setReteachText(resp.data.reteach);
      }
      saveProgress({ password: userData.password || passInput, mastered: updatedMastered, attempts: updatedAttempts });
    } catch (err) { console.error(err); }
  }

  const masteredCount = Object.keys(userData.mastered).length;
  const progressPercent = Math.round((masteredCount / TOPICS.length) * 100);
  const currentAttempts = userData.attempts[topic] || 0;

  // --- LOGIN VIEW ---
  if (!user) {
    return (
      <div className="login-screen">
        <div className="container" style={{maxWidth: '400px'}}>
          <h1 style={{textAlign: 'center', color: '#00f6ff', textShadow: '0 0 10px #00f6ff', marginBottom: '20px'}}>
            AI LEARNING AGENT
          </h1>
          <div className="card neon-border" style={{textAlign: 'center', padding: '30px'}}>
            <h3 style={{color: '#94a3b8', fontSize: '0.8rem', letterSpacing: '2px', marginBottom: '20px'}}>
              USER AUTHENTICATION
            </h3>
            <input 
              className="neon-input"
              value={loginInput} 
              onChange={(e) => setLoginInput(e.target.value)} 
              placeholder="ENTER USERNAME"
              style={{marginBottom: '15px'}}
            />
            <input 
              className="neon-input"
              type="password"
              value={passInput} 
              onChange={(e) => setPassInput(e.target.value)} 
              placeholder="ENTER PASSWORD"
              style={{marginBottom: '20px'}}
            />
            <button 
              onClick={handleAuth} 
              style={{width: '100%'}}
            >
              INITIALIZE SESSION
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div style={{display: 'flex', justifyContent: 'space-between', padding: '10px 0'}}>
        <small style={{color: '#00f6ff', fontWeight: 'bold'}}> AGENT : {user.toUpperCase()}</small>
        <button className="small-btn" style={{background: 'none', border: '1px solid #f87171', color: '#f87171'}} onClick={logout}> LOGOUT </button>
      </div>

      <div className="card neon-border progress-dashboard">
        <div className="stat-grid">
          <div className="stat-item">
            <span className="stat-label">PROGRESS </span>
            <span className="stat-value">{progressPercent}%</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">MASTERED </span>
            <span className="stat-value">{masteredCount} / {TOPICS.length}</span>
          </div>
        </div>
        <div className="progress-bar-bg">
          <div className="progress-bar-fill" style={{ width: `${progressPercent}%` }}></div>
        </div>
      </div>

      <h1 style={{ textAlign: 'center', margin: '20px 0' }}>AI LEARNING AGENT</h1>

      <div className="card neon-border">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '20px' }}>
          <select 
            value={topic} 
            onChange={e => setTopic(e.target.value)} 
            className="neon-select"
            style={{ flex: 1 }}
          >
            {TOPICS.map(t => (
              <option key={t} value={t}>
                {userData.mastered[t] ? "★ " : ""}{t.toUpperCase()}
              </option>
            ))}
          </select>
          
          <div className={`attempt-monitor ${currentAttempts >= 3 && !userData.mastered[topic] ? 'locked' : 'available'}`}>
            <span className="attempt-label">ATTEMPT STATUS</span>
            <div className="attempt-indicators">
              {[1, 2, 3].map(i => (
                <div key={i} className={`dot ${currentAttempts >= i ? 'used' : 'ready'}`}></div>
              ))}
            </div>
            <small className="attempt-text">{currentAttempts} / 3 USED</small>
          </div>
        </div>
        
        <button onClick={explain} style={{ marginTop: '20px', width: '100%' }}>START LEARNING </button>
      </div>

      {userData.mastered[topic] && <div className="badge-notification">🏆 MASTERY ACHIEVED</div>}

      {exp && (
        <div className="card">
          <h2 style={{color: '#00f6ff'}}>EXPLANATION</h2>
          <div className="explanation-text" style={{whiteSpace: 'pre-wrap', lineHeight: '1.7', color: '#e2e8f0'}}>{exp}</div>
          
          <div className="relevance-box">
            <small style={{display: 'block', letterSpacing: '2px', color: '#39ff14'}}>RELEVANCE SCORE </small>
            <span className="big-score">{rel}/10</span>
          </div>
          
          <button onClick={startQuiz} style={{width: '100%'}}>START EVALUATION</button>
        </div>
      )}

      {quiz.length > 0 && (
        <div className="card">
          <h2 style={{borderBottom: '1px solid #00f6ff', paddingBottom: '10px'}}>KNOWLEDGE CHECK</h2>
          {quiz.map((q, qi) => (
            <div key={qi} className="quiz-q" style={{background: '#1e293b', padding: '15px', borderRadius: '8px', marginBottom: '15px'}}>
              <p><strong>{qi + 1}. {q.q}</strong></p>
              {q.options.map((o, oi) => (
                <label key={oi} className="option-label" style={{display: 'block', margin: '8px 0', cursor: 'pointer'}}>
                  <input type="radio" name={"q"+qi} onChange={() => { const a = [...answers]; a[qi] = oi; setAnswers(a); }} /> {o}
                </label>
              ))}
              <button className="small-btn" style={{background: 'none', border: '1px solid #39ff14', color: '#39ff14', fontSize: '0.7rem'}} onClick={() => setVisibleHints({...visibleHints, [qi]: !visibleHints[qi]})}>
                {visibleHints[qi] ? "HIDE HINT" : "HINT"}
              </button>
              {visibleHints[qi] && <div className="hint-box">💡 {q.hint}</div>}
            </div>
          ))}
          {score === null && <button onClick={submit} style={{width: '100%'}}>SUBMIT EVALUATION</button>}
        </div>
      )}

      {score !== null && (
        <div className={`card ${score < 3 ? 'status-fail' : 'status-pass'}`} style={{textAlign: 'center'}}>
          <h2>SCORE: {score} / 5</h2>
          {score < 3 ? (
            <div className="reteach-module">
              <h4 style={{color: '#f87171'}}>RETEACHING TRIGGERED</h4>
              <p style={{whiteSpace: 'pre-wrap'}}>{reteachText}</p>
              <button onClick={startQuiz} style={{background: '#f87171', width: '100%', marginTop: '10px'}}>RE-TRY EVALUATION</button>
            </div>
          ) : <p style={{color: '#39ff14', fontWeight: 'bold'}}>SYNC SUCCESSFUL. MASTERY LOGGED.</p>}
        </div>
      )}
    </div>
  );

}
