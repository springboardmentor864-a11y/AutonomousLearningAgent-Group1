import streamlit as st
from state import LearningState
from learning_agent import (
    gather_context,
    validate_context,
    explain_concept,
    generate_quiz,
    evaluate_student,
    feynman_explain
)

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Autonomous Learning Agent",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =====================================================
# PROFESSIONAL SAAS UI CSS
# =====================================================
st.markdown("""
<style>

/* ---------- ROOT ---------- */
:root {
    --bg: #070910;
    --card: rgba(255,255,255,0.06);
    --border: rgba(255,255,255,0.12);
    --text: #e5e7eb;
    --muted: #9ca3af;
    --primary: #7c3aed;
}

/* ---------- PAGE ---------- */
.stApp {
    background: radial-gradient(circle at top, #1b1035, #070910);
    font-family: Inter, system-ui, sans-serif;
    color: var(--text);
}

/* ---------- NAVBAR ---------- */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 22px 40px;
}

.nav-left {
    font-weight: 900;
    font-size: 18px;
}

.nav-right span {
    margin-left: 28px;
    font-size: 14px;
    color: var(--muted);
    cursor: pointer;
}

/* ---------- HERO ---------- */
.hero {
    text-align: center;
    margin: 80px 0;
}

.hero h1 {
    font-size: 64px;
    font-weight: 900;
    line-height: 1.1;
    background: linear-gradient(90deg, #c084fc, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    max-width: 700px;
    margin: 18px auto;
    font-size: 18px;
    color: var(--muted);
}

.hero-btn {
    display: inline-block;
    margin-top: 30px;
    padding: 14px 36px;
    border-radius: 999px;
    background: linear-gradient(90deg, #7c3aed, #9333ea);
    color: white;
    font-weight: 800;
}

/* ---------- CARD ---------- */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 28px;
    padding: 30px;
    margin-bottom: 28px;
    backdrop-filter: blur(18px);
}

/* ---------- QUIZ CARD ---------- */
.quiz-card {
    background: rgba(255,255,255,0.08);
    border-left: 6px solid #7c3aed;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 16px;
}

/* ---------- BUTTON ---------- */
button[kind="primary"] {
    background: linear-gradient(90deg, #7c3aed, #9333ea) !important;
    border-radius: 999px !important;
    font-weight: 800 !important;
    padding: 12px 30px !important;
}

/* ====================================================
   BRIGHT QUIZ OPTIONS (IMPORTANT PART)
   ==================================================== */
div[role="radiogroup"] > label {
    background: #ffffff !important;
    color: #111827 !important;
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 10px;
    border: 2px solid #e5e7eb;
    font-weight: 600;
    transition: all 0.2s ease;
}

div[role="radiogroup"] > label:hover {
    background: #f5f3ff !important;
    border-color: #7c3aed;
}

div[role="radiogroup"] > label[data-checked="true"] {
    background: #ede9fe !important;
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.3);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE
# =====================================================
if "stage" not in st.session_state:
    st.session_state.stage = "landing"
    st.session_state.state = None
    st.session_state.quiz_generated = False

# =====================================================
# LANDING PAGE
# =====================================================
if st.session_state.stage == "landing":

    st.markdown("""
    <div class="navbar">
        <div class="nav-left">⚡ Autonomous Agent</div>
        <div class="nav-right">
            <span>Features</span>
            <span>Developers</span>
            <span>Blog</span>
            <span style="color:#c084fc">Join waitlist</span>
        </div>
    </div>

    <div class="hero">
        <h1>Boost your<br>learning with AI.</h1>
        <p>
            Elevate your understanding effortlessly with an autonomous AI
            that teaches, evaluates, and adapts until mastery.
        </p>
        <div class="hero-btn">Start for free</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    topic = st.text_input("Enter a topic you want to learn")

    if st.button("🚀 Launch Learning Agent"):
        if topic.strip():
            state = LearningState()
            state.concept = topic.strip()
            with st.spinner("Initializing autonomous agent..."):
                gather_context(state)
                validate_context(state)
                explain_concept(state)
            st.session_state.state = state
            st.session_state.stage = "content"
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# CONTENT STAGE
# =====================================================
elif st.session_state.stage == "content":
    state = st.session_state.state

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 🧠 Concept Explanation")
    st.write(state.explanation)
    st.progress(state.relevance_score / 100)

    if st.button("📝 Start Quiz"):
        st.session_state.stage = "quiz"

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# QUIZ STAGE
# =====================================================
elif st.session_state.stage == "quiz":
    state = st.session_state.state

    if not st.session_state.quiz_generated:
        generate_quiz(state)
        st.session_state.quiz_generated = True

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 📝 Knowledge Check")

    state.student_answers = []

    for i, q in enumerate(state.quiz_questions):
        st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
        st.markdown(f"**Q{i+1}. {q['question']}**")
        ans = st.radio(
            "Choose one:",
            list(q["options"].keys()),
            format_func=lambda x: q["options"][x],
            key=f"q_{i}"
        )
        state.student_answers.append(ans)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("✅ Submit Quiz"):
        evaluate_student(state)
        if state.student_score >= 70:
            st.success("🎉 Topic mastered successfully!")
            st.session_state.stage = "done"
        else:
            st.warning("❌ Below threshold. Simplifying explanation...")
            feynman_explain(state)
            st.session_state.quiz_generated = False
            st.session_state.stage = "feynman"

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# FEYNMAN STAGE
# =====================================================
elif st.session_state.stage == "feynman":
    state = st.session_state.state

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 🔁 Simplified Explanation (Feynman Technique)")
    st.write(state.explanation)

    if st.button("🔄 Try Quiz Again"):
        st.session_state.stage = "quiz"

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# DONE STAGE
# =====================================================
elif st.session_state.stage == "done":
    st.balloons()
    st.success("✅ You have achieved mastery!")

    if st.button("📚 Learn Another Topic"):
        st.session_state.stage = "landing"
        st.session_state.state = None
        st.session_state.quiz_generated = False
