import React, { useState, useEffect } from 'react';
import { Home, PieChart, BookOpen, User, LogOut } from 'lucide-react';
import { DashboardContent } from './components/DashboardContent';
import { Login, Signup, ForgotPassword } from './components/Auth';
import './components/styles.css';

const API_URL = "https://your-backend-url.onrender.com";

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [stage, setStage] = useState('dashboard'); // dashboard, learning
  const [learningStage, setLearningStage] = useState('home'); // home, teaching, quiz, report, feynman, reassessment, final

  // Auth State
  const [authMode, setAuthMode] = useState('login'); // login, signup

  // Learning State
  const [topics, setTopics] = useState({});
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [content, setContent] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [quizResult, setQuizResult] = useState(null);
  const [feynmanExplanations, setFeynmanExplanations] = useState(null);
  const [reassessmentQuestions, setReassessmentQuestions] = useState(null);
  const [reassessmentAnswers, setReassessmentAnswers] = useState({});
  const [finalResult, setFinalResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/topics`)
      .then(res => res.json())
      .then(data => setTopics(data))
      .catch(err => console.error("Failed to fetch topics:", err));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setStage('dashboard');
  };

  const handleSelectTopic = async (code) => {
    setLoading(true);
    setSelectedTopic(code);
    try {
      const res = await fetch(`${API_URL}/content/${code}`);
      const data = await res.json();
      setContent(data);
      setLearningStage('teaching');
      setStage('learning');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const startQuiz = () => {
    setLearningStage('quiz');
    setCurrentQuestionIndex(0);
    setUserAnswers({});
  };

  const submitQuiz = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/evaluate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          topic: selectedTopic,
          user_answers: userAnswers
        })
      });
      const data = await res.json();
      setQuizResult(data);
      setLearningStage('report');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const startFeynman = async () => {
    setLoading(true);
    try {
      const weakConcepts = quizResult.weak_concepts;
      const res = await fetch(`${API_URL}/feynman_explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: selectedTopic,
          concepts: weakConcepts
        })
      });
      const data = await res.json();
      setFeynmanExplanations(data);
      setLearningStage('feynman');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const startReassessment = async () => {
    setLoading(true);
    try {
      const previousQs = content.questions.map(q => q.q);
      const res = await fetch(`${API_URL}/reassessment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: selectedTopic,
          previous_questions: previousQs
        })
      });
      const data = await res.json();
      setReassessmentQuestions(data);
      setReassessmentAnswers({});
      setLearningStage('reassessment');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const submitReassessment = () => {
    let correct = 0;
    reassessmentQuestions.forEach((q, idx) => {
      // Logic for matching answers (string vs int index)
      let correctOption = "";
      if (typeof q.a === 'number') {
        correctOption = q.opts[q.a - 1]; // assuming a is 1-based index
      } else {
        correctOption = q.a;
      }
      if (reassessmentAnswers[idx] === correctOption) correct++;
    });

    const score = (correct / reassessmentQuestions.length) * 100;

    // Save final result if needed, but endpoint for final save isn't explicit in backend.
    // We can just show result locally.

    setFinalResult({
      score,
      passed: score >= 70
    });
    setLearningStage('final');
  };

  const resetApp = () => {
    setLearningStage('home');
    setSelectedTopic(null);
    setContent(null);
    setQuizResult(null);
    setFeynmanExplanations(null);
    setStage('dashboard'); // Return to dashboard
  };

  // --- RENDERING ---

  if (!token) {
    return (
      <div style={{ height: '100vh', background: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {authMode === 'login' && (
          <Login onLogin={(t) => setToken(t)} onSwitchToSignup={() => setAuthMode('signup')} onForgotPassword={() => setAuthMode('forgot')} />
        )}
        {authMode === 'signup' && (
          <Signup onLogin={(t) => setToken(t)} onSwitchToLogin={() => setAuthMode('login')} />
        )}
        {authMode === 'forgot' && (
          <ForgotPassword onBackToLogin={() => setAuthMode('login')} />
        )}
      </div>
    );
  }

  // Authenticated View
  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <div className="sidebar">
        <h2 style={{ color: '#4f46e5', fontWeight: 'bold', fontSize: '1.5rem', marginBottom: '2rem' }}>NeoVihar AI</h2>
        <div className="sidebar-nav">
          <div className={`nav-item ${stage === 'dashboard' ? 'active' : ''}`} onClick={() => setStage('dashboard')}>
            <PieChart size={20} />
            <span>Dashboard</span>
          </div>
          <div className={`nav-item ${stage === 'learning' ? 'active' : ''}`} onClick={() => { setStage('learning'); setLearningStage('home'); }}>
            <BookOpen size={20} />
            <span>Learning Modules</span>
          </div>
          {/* Add more items like 'Practice', 'Review' based on user image */}
          <div className="nav-item">
            <User size={20} />
            <span>Profile</span>
          </div>

          <div style={{ flex: 1 }}></div>

          <div className="nav-item" onClick={handleLogout} style={{ color: '#ef4444' }}>
            <LogOut size={20} />
            <span>Logout</span>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content">
        {stage === 'dashboard' && <DashboardContent token={token} />}

        {stage === 'learning' && (
          <div>
            {learningStage === 'home' && (
              <div className="card fade-in">
                <h1 style={{ marginBottom: '1.5rem' }}>Select a Module</h1>
                <div className="btn-grid">
                  {Object.entries(topics).map(([code, name]) => (
                    <button key={code} className="topic-card" onClick={() => handleSelectTopic(code)}>
                      <span className="icon">📚</span>
                      <span className="label">{name}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {learningStage === 'teaching' && content && (
              <div className="card fade-in">
                <h2>{topics[selectedTopic]}</h2>
                <div className="explanation-card">
                  <p style={{ whiteSpace: 'pre-line' }}>{content.context}</p>
                </div>
                <button className="primary" onClick={startQuiz}>Start Checkpoint Quiz</button>
              </div>
            )}

            {/* ... Other stages (quiz, report, feynman, reassessment, final) ... */}
            {/* To keep file size manageable, I'm reusing logic from previous App.jsx but simplified here. */}

            {learningStage === 'quiz' && content && (
              <div className="card fade-in">
                <h3>Question {currentQuestionIndex + 1} of {content.questions.length}</h3>
                <p className="question-text">{content.questions[currentQuestionIndex].q}</p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {content.questions[currentQuestionIndex].opts.map((opt) => (
                    <button
                      key={opt}
                      className={`option-btn ${userAnswers[content.questions[currentQuestionIndex].id] === opt ? 'selected' : ''}`}
                      onClick={() => setUserAnswers(prev => ({ ...prev, [content.questions[currentQuestionIndex].id]: opt }))}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
                <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'flex-end' }}>
                  {currentQuestionIndex === content.questions.length - 1 ? (
                    <button className="primary" onClick={submitQuiz}>Submit Quiz</button>
                  ) : (
                    <button className="primary" onClick={() => setCurrentQuestionIndex(prev => prev + 1)}>Next</button>
                  )}
                </div>
              </div>
            )}

            {learningStage === 'report' && quizResult && (
              <div className="card fade-in">
                <h1>Diagnostic Report: {quizResult.score.toFixed(0)}%</h1>
                <span className={`badge ${quizResult.passed ? 'passed' : 'failed'}`}>
                  {quizResult.passed ? 'PASSED' : 'REINFORCEMENT NEEDED'}
                </span>
                <div style={{ marginTop: '2rem' }}>
                  {quizResult.passed ? (
                    <button className="primary" onClick={resetApp}>Complete Module</button>
                  ) : (
                    <button className="primary" onClick={startFeynman}>Proceed to Feynman Learning</button>
                  )}
                </div>
              </div>
            )}

            {learningStage === 'feynman' && feynmanExplanations && (
              <div className="card fade-in">
                <h1>Feynman Explanations</h1>
                {Object.entries(feynmanExplanations).map(([concept, expr], idx) => (
                  <div key={idx} className="explanation-card">
                    <h3>{concept}</h3>
                    <p>{expr}</p>
                  </div>
                ))}
                <button className="primary" onClick={startReassessment}>Start Reassessment</button>
              </div>
            )}

            {learningStage === 'reassessment' && reassessmentQuestions && (
              <div className="card fade-in">
                <h1>Reassessment Quiz</h1>
                {reassessmentQuestions.map((q, idx) => (
                  <div key={idx} style={{ marginBottom: '2rem' }}>
                    <p><strong>{idx + 1}. {q.q}</strong></p>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {q.opts.map((opt) => (
                        <button
                          key={opt}
                          className={`option-btn ${reassessmentAnswers[idx] === opt ? 'selected' : ''}`}
                          onClick={() => setReassessmentAnswers(prev => ({ ...prev, [idx]: opt }))}
                        >
                          {opt}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
                <button className="primary" onClick={submitReassessment}>Submit Final Answers</button>
              </div>
            )}

            {learningStage === 'final' && finalResult && (
              <div className="card fade-in">
                <h1>Final Results: {finalResult.score.toFixed(0)}%</h1>
                <button className="primary" onClick={resetApp}>Return to Dashboard</button>
              </div>
            )}

          </div>
        )}
      </div>
    </div>
  );
}

export default App;
