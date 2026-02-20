import streamlit as st
import asyncio
import re
import json
import os
from datetime import datetime
from state import LearningState
from learning_agent import (
    gather_context, validate_context, explain_concept,
    generate_quiz,  feynman_explain
)
from checkpoints import CHECKPOINTS

st.set_page_config(
    page_title="🤖 Autonomous Learning Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔥 PERSISTENT STORAGE CONFIGURATION
PROGRESS_FILE = "learning_progress.json"

def load_progress():
    """Load progress from file with fallback to default"""
    default_progress = {concept: {
        'completed': False, 'score': 0, 'attempts': 0, 'best_score': 0,
        'last_score': 0, 'feynman_level': 0, 'feynman_attempts_used': 0,
        'last_updated': datetime.now().isoformat()
    } for concept in CHECKPOINTS}
    
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                loaded = json.load(f)
                for concept in CHECKPOINTS:
                    if concept not in loaded:
                        loaded[concept] = default_progress[concept]
                    else:
                        for key in default_progress[concept]:
                            if key not in loaded[concept]:
                                loaded[concept][key] = default_progress[concept][key]
                return loaded
        except:
            st.warning("⚠️ Corrupted progress file. Using defaults.")
    return default_progress

def save_progress(progress):
    """Save progress to file"""
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, indent=2)
        return True
    except Exception as e:
        st.error(f"⚠️ Failed to save progress: {e}")
        return False

# 🌟 COMPLETE CSS - ONE LINE
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }
.main-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); padding: 3rem 2rem; border-radius: 0 0 30px 30px; color: white; text-align: center; box-shadow: 0 15px 50px rgba(102,126,234,0.4); }
.content-section { background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%); padding: 3.5rem; border-radius: 30px; box-shadow: 0 25px 70px rgba(0,0,0,0.12); margin: 2.5rem 0; }
.content-card, .quiz-card { padding: 2.5rem; background: linear-gradient(145deg, #f8fafc, #e2e8f0); border-radius: 25px; margin: 2rem 0; border-left: 5px solid #3b82f6; }
.results-section { padding: 2.5rem; background: linear-gradient(145deg, #fef3c7, #fde68a); border-radius: 25px; border-left: 6px solid #f59e0b; margin: 2rem 0; }
.feynman-card { padding: 2.5rem; background: linear-gradient(145deg, #e0f2fe, #b9d9eb); border-radius: 25px; border-left: 6px solid #0ea5e9; margin: 2rem 0; }
.explanation-good { background: rgba(16,185,129,0.1); padding: 1.5rem; border-radius: 15px; border-left: 4px solid #10b981; margin: 1rem 0; }
.explanation-wrong { background: rgba(239,68,68,0.1); padding: 1.5rem; border-radius: 15px; border-left: 4px solid #ef4444; margin: 1rem 0; }
.progress-bar { background: #e5e7eb; height: 12px; border-radius: 6px; overflow: hidden; margin: 1.5rem 0; }
.progress-fill { background: linear-gradient(90deg, #10b981, #34d399); height: 100%; border-radius: 6px; }
.topic-progress { background: rgba(255,255,255,0.9); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border-left: 4px solid #3b82f6; }
.feynman-limit { background: rgba(239,68,68,0.15); padding: 1.5rem; border-radius: 15px; border-left: 4px solid #ef4444; margin: 1rem 0; }
.persistence-notice { background: rgba(16,185,129,0.15); padding: 1rem; border-radius: 10px; border-left: 4px solid #10b981; margin: 1rem 0; }
.stButton > button { transition: all 0.2s ease !important; }
.stButton > button:focus { outline: none !important; box-shadow: none !important; }
.stButton > button:active { transform: scale(0.98) !important; }
.stButton > button:disabled { opacity: 0.6 !important; cursor: not-allowed !important; }
</style>
""", unsafe_allow_html=True)

# 🔥 INITIALIZE PERSISTENT STATE
if 'active_page' not in st.session_state:
    st.session_state.active_page = "topics"
if 'learning_state' not in st.session_state:
    st.session_state.learning_state = None
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = None

# 🔥 LOAD PERSISTENT PROGRESS FIRST
st.session_state.progress = load_progress()

if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'student_answers' not in st.session_state:
    st.session_state.student_answers = {}
if 'parsed_questions' not in st.session_state:
    st.session_state.parsed_questions = []
if 'quiz_evaluation' not in st.session_state:
    st.session_state.quiz_evaluation = None
if 'learning_phase' not in st.session_state:
    st.session_state.learning_phase = "initial"
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = []
if 'feynman_explanation' not in st.session_state:
    st.session_state.feynman_explanation = ""
if 'content_cache' not in st.session_state:
    st.session_state.content_cache = {}
if 'quiz_seed' not in st.session_state:
    st.session_state.quiz_seed = 0

def run_async_safe(coro_func, state):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        future = asyncio.ensure_future(coro_func(state))
        loop.run_until_complete(future)
        loop.close()
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

def safe_evaluate_quiz(student_answers, correct_answers, total_questions):
    correct_count = 0
    min_length = min(len(student_answers), len(correct_answers), total_questions)
    for i in range(min_length):
        student_ans = student_answers.get(i)
        correct_ans = correct_answers[i] if i < len(correct_answers) else None
        if student_ans == correct_ans:
            correct_count += 1
    return (correct_count / total_questions) * 100 if total_questions > 0 else 0

async def generate_dynamic_feynman(state, score, feynman_level):
    try:
        await feynman_explain(state)
        state.student_score = score
        state.feynman_level = feynman_level
        explanation = f"""🧠 FEYNMAN TECHNIQUE - Level {feynman_level + 1} 

📚 CONCEPT: {state.concept}

🎯 SIMPLIFIED EXPLANATION (Auto-generated from your score: {score:.0f}%):
{state.explanation}

💡 KEY TAKEAWAYS:
• Focus on the core pattern you missed
• Practice these specific edge cases next time
• Score < 70% → This explanation gets simpler each time!

🚀 NEXT: Take the quiz again to master this!"""
        return explanation
    except Exception as e:
        return f"🧠 Feynman Level {feynman_level + 1}: Please retry the quiz to generate explanation for {state.concept}"

# 🎨 HEADER
st.markdown("""
<div class="main-header">
    <h1 style='font-size: 3.5rem;'>🤖 Autonomous Learning Agent</h1>
""", unsafe_allow_html=True)

# 🔥 SAVE PROGRESS ON EVERY RERUN
save_progress(st.session_state.progress)

with st.sidebar:
    st.markdown('<div style="padding: 2rem; background: rgba(30,41,59,0.95); border-radius: 25px; color: white;"><h3>🎓 ML Academy</h3></div>', unsafe_allow_html=True)
    
    if save_progress(st.session_state.progress):
        st.markdown('<div class="persistence-notice"> Progress Saved</div>', unsafe_allow_html=True)
    
    if st.session_state.progress:
        sample_progress = list(st.session_state.progress.values())[0]
        last_updated = datetime.fromisoformat(sample_progress['last_updated']).strftime('%Y-%m-%d %H:%M')
    
    if st.button("📚 Topics", use_container_width=True, type="secondary"):
        st.session_state.active_page = "topics"; st.rerun()
    if st.button("📈 Progress", use_container_width=True, type="secondary"):
        st.session_state.active_page = "progress"; st.rerun()
    
    if st.button("🔄 Reset All Progress", type="primary", use_container_width=True):
        st.session_state.progress = {concept: {
            'completed': False, 'score': 0, 'attempts': 0, 'best_score': 0,
            'last_score': 0, 'feynman_level': 0, 'feynman_attempts_used': 0,
            'last_updated': datetime.now().isoformat()
        } for concept in CHECKPOINTS}
        save_progress(st.session_state.progress)
        st.success("✅ Progress reset!")
        st.rerun()

# 🔥 MAIN TOPICS PAGE
if st.session_state.active_page == "topics":
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    
    st.markdown("## 🎯 Select ML Topic")
    cols = st.columns(2)
    for i, topic in enumerate(CHECKPOINTS):
        with cols[i % 2]:
            progress = st.session_state.progress.get(topic, {'best_score': 0})
            status = "✅" if progress['completed'] else "🔄"
            if st.button(f"{status} {i+1}. {topic[:35]}", key=f"topic_{i}", use_container_width=True, type="secondary"):
                st.session_state.selected_topic = topic
                with st.spinner(f"Loading {topic} content..."):
                    state = LearningState(concept=topic)
                    run_async_safe(gather_context, state)
                    run_async_safe(validate_context, state)
                    run_async_safe(explain_concept, state)
                    st.session_state.learning_state = state
                    st.session_state.content_cache[topic] = state.explanation
                    
                    st.session_state.learning_phase = "content"
                    st.session_state.current_question = 0
                    st.session_state.student_answers = {}
                    st.session_state.parsed_questions = []
                    st.session_state.correct_answers = []
                    st.session_state.quiz_evaluation = None
                    st.session_state.feynman_explanation = ""
                    st.session_state.quiz_seed = 0
                st.rerun()
    
    if st.session_state.selected_topic and st.session_state.learning_state:
        state = st.session_state.learning_state
        topic = st.session_state.selected_topic
        progress = st.session_state.progress[topic]
        
        st.markdown(f'<div class="topic-progress">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([2,1,1,1])
        with col1: st.markdown(f"{topic} - {'✅ MASTERED' if progress['completed'] else '🔄 Learning'}")
        with col2: st.metric("Best", f"{progress['best_score']}/100")
        with col3: st.metric("Attempts", progress['attempts'])
        with col4: st.metric("Feynman", f"{progress['feynman_level']}/{progress['feynman_attempts_used']}/3")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 🔥 CONTENT PHASE
        if st.session_state.learning_phase == "content":
            st.markdown(f'<div class="content-card">', unsafe_allow_html=True)
            st.markdown(f"# {topic}")
            st.markdown("## 📖 Core Concept")
            content = st.session_state.content_cache.get(topic, state.explanation)
            st.markdown(content)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("Start Quiz", key="start_quiz_content_v2", type="primary", use_container_width=True):
                with st.spinner("Generating questions..."):
                    st.session_state.quiz_seed += 1
                    state.explanation = content
                    state.quiz_variation = st.session_state.quiz_seed
                    run_async_safe(generate_quiz, state)
                    
                    questions_raw = re.split(r'(Question \d+:)', state.quiz or "")
                    parsed_questions = []
                    correct_answers = []
                    
                    for i in range(1, len(questions_raw), 2):
                        if i+1 < len(questions_raw):
                            q_text = questions_raw[i+1].strip()
                            lines = q_text.split('\n')
                            if lines:
                                question = lines[0].strip()
                                options = {}
                                for line in lines[1:]:
                                    match = re.match(r'^([A-D])\)\s*(.+)', line.strip())
                                    if match:
                                        # FIXED: Remove ✅ indicator from options display
                                        option_text = match.group(2).strip().replace('✅', '').strip()
                                        options[match.group(1)] = option_text
                                        # Store correct answer separately (look for original ✅)
                                        if '✅' in match.group(2):
                                            correct_answers.append(match.group(1))
                                parsed_questions.append({'question': question, 'options': options})
                    
                    st.session_state.parsed_questions = parsed_questions[:3]
                    st.session_state.correct_answers = correct_answers[:3] or ['B', 'C', 'A']
                    
                    # 🔥 PERSISTENT UPDATE
                    st.session_state.progress[topic]['attempts'] += 1
                    st.session_state.progress[topic]['last_updated'] = datetime.now().isoformat()
                    save_progress(st.session_state.progress)
                    st.session_state.learning_phase = "quiz"
                st.rerun()
        
        # 🔥 QUIZ PHASE
        elif st.session_state.learning_phase == "quiz":
            questions = st.session_state.parsed_questions
            if not questions:
                st.error("❌ No questions available.")
                if st.button("← Back to Content"):
                    st.session_state.learning_phase = "content"
                    st.rerun()
                st.stop()
            
            current_q = st.session_state.current_question
            total = len(questions)
            
            st.markdown(f'<div class="quiz-card">', unsafe_allow_html=True)
            st.markdown("## 🎯 Quiz")
            
            progress_pct = ((current_q + 1) / total) * 100
            st.markdown(f"""
            <div style='font-size: 1.3rem; font-weight: 700;'>
                Q{current_q + 1} of {total}
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress_pct}%"></div>
            </div>
            """, unsafe_allow_html=True)
            
            q_data = questions[current_q]
            st.markdown(f"{q_data['question']}")
            
            selected_answer = st.session_state.student_answers.get(current_q)
            
            for letter, text in q_data['options'].items():
                is_selected = selected_answer == letter
                btn_key = f"opt_{current_q}_{letter}_v4"
                
                if st.button(
                    f"{letter}) {text[:55]}{'...' if len(text)>55 else ''}",
                    key=btn_key,
                    type="primary" if is_selected else "secondary",
                    use_container_width=True,
                    disabled=bool(selected_answer and not is_selected)
                ):
                    st.session_state.student_answers[current_q] = letter
                    st.rerun()
                
                if is_selected:
                    st.markdown(f"""
                    <div style='background: rgba(16,185,129,0.15); padding: 0.8rem; border-radius: 10px; border-left: 5px solid #10b981; margin: 0.5rem 0;'>
                    SELECTED: {letter}
                    </div>
                    """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1,1,3])
            with col1:
                if current_q > 0:
                    if st.button("⬅️ Previous", key=f"prev_{current_q}_v2"):
                        st.session_state.current_question -= 1
                        st.rerun()
            with col2:
                if selected_answer and current_q < total-1:
                    if st.button("➡️ Next", key=f"next_{current_q}_v2"):
                        st.session_state.current_question += 1
                        st.rerun()
            with col3:
                if current_q == total-1 and selected_answer:
                    if st.button("SUBMIT QUIZ", key="submit_quiz_v4", type="primary", use_container_width=True):
                        score = safe_evaluate_quiz(st.session_state.student_answers, st.session_state.correct_answers, total)
                        st.session_state.quiz_evaluation = {
                            'score': score, 'correct_count': round(score/100 * total), 'total': total,
                            'correct_answers': st.session_state.correct_answers,
                            'student_answers': list(st.session_state.student_answers.values())
                        }
                        prog = st.session_state.progress[topic]
                        prog['last_score'] = score
                        prog['best_score'] = max(prog['best_score'], score)
                        if score >= 70:
                            prog['completed'] = True
                        prog['last_updated'] = datetime.now().isoformat()
                        save_progress(st.session_state.progress)
                        st.session_state.learning_phase = "results"
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 🔥 RESULTS PHASE - SIMPLIFIED: "Q1.wrong" format
        elif st.session_state.learning_phase == "results":
            eval_data = st.session_state.quiz_evaluation
            score = eval_data['score']
            st.markdown(f'<div class="results-section">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1,2,1])
            with col1: st.markdown(f"{eval_data['correct_count']}/{eval_data['total']}")
            with col2: st.markdown(f"Score: {eval_data['score']:.0f}/100")
            with col3: st.markdown(f"{'🎉 PASSED' if score >= 70 else '🔄 FAILED'}")
            
            st.markdown("## Detailed Feedback")
            for i, q_data in enumerate(st.session_state.parsed_questions):
                user_ans = eval_data['student_answers'][i] if i < len(eval_data['student_answers']) else '?'
                
                if user_ans == st.session_state.correct_answers[i]:
                    st.markdown(f'<div class="explanation-good">Q{i+1}.correct</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="explanation-wrong">Q{i+1}.wrong</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if score < 70 and st.session_state.progress[topic]['feynman_attempts_used'] < 3:
                    if st.button("🧠 Feynman Explanation", key="feynman_results_v4", type="primary", use_container_width=True):
                        feynman_level = st.session_state.progress[topic]['feynman_level']
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        explanation = loop.run_until_complete(generate_dynamic_feynman(state, score, feynman_level))
                        loop.close()
                        
                        st.session_state.feynman_explanation = explanation
                        st.session_state.progress[topic]['feynman_level'] += 1
                        st.session_state.progress[topic]['feynman_attempts_used'] += 1
                        st.session_state.progress[topic]['last_updated'] = datetime.now().isoformat()
                        save_progress(st.session_state.progress)
                        st.session_state.learning_phase = "feynman"
                        st.rerun()
                elif score >= 70:
                    st.markdown('<div class="explanation-good">PASSED! No Feynman needed - you mastered it!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div class="feynman-limit">
                        Feynman Limit Reached (3/3 attempts used)
                        Practice more quizzes to improve!
                    </div>
                    ''', unsafe_allow_html=True)
            
            with col2:
                if st.button("🔄 New Quiz", key="new_quiz_results_v4", type="secondary", use_container_width=True):
                    st.session_state.learning_phase = "content"
                    st.session_state.current_question = 0
                    st.session_state.student_answers = {}
                    st.session_state.quiz_seed += 1
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 🔥 FEYNMAN PHASE
        elif st.session_state.learning_phase == "feynman":
            st.markdown(f'<div class="feynman-card">', unsafe_allow_html=True)
            st.markdown("## 🧠 Feynman Technique")
            st.markdown(f"Level {st.session_state.progress[topic]['feynman_level']} - Generated from your last score")
            st.markdown("---")
            st.markdown(st.session_state.feynman_explanation)
            st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                if st.button("New Quiz", key="new_quiz_feynman_v4", type="primary", use_container_width=True):
                    st.session_state.learning_phase = "content"
                    st.session_state.current_question = 0
                    st.session_state.student_answers = {}
                    st.session_state.quiz_seed += 1
                    st.rerun()
            with col2:
                if st.button("🔄 Retry Quiz (Same)", key="retry_quiz_feynman_v4", type="secondary", use_container_width=True):
                    st.session_state.learning_phase = "quiz"
                    st.session_state.current_question = 0
                    st.session_state.student_answers = {}
                    st.rerun()
            with col3:
                if st.button("📚 Next Topic", key="next_topic_feynman_v4", type="secondary", use_container_width=True):
                    idx = (CHECKPOINTS.index(topic) + 1) % len(CHECKPOINTS)
                    st.session_state.selected_topic = CHECKPOINTS[idx]
                    st.session_state.learning_phase = "content"
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# 🔥 PROGRESS PAGE
elif st.session_state.active_page == "progress":
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown("# 📈 Learning Progress")
    
    total = len(CHECKPOINTS)
    completed = sum(1 for p in st.session_state.progress.values() if p['completed'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("✅ Mastered", f"{completed}/{total}")
    with col2: st.metric("📊 Avg Best", f"{sum(p['best_score'] for p in st.session_state.progress.values())//max(1,total)}/100")
    with col3: st.metric("🎯 Attempts", sum(p['attempts'] for p in st.session_state.progress.values()))
    with col4: st.metric("🧠 Feynman", f"{sum(p['feynman_attempts_used'] for p in st.session_state.progress.values())}/3 per topic")
    
    st.progress(completed/total)
    
    progress_data = []
    for topic, data in st.session_state.progress.items():
        status = "✅ Mastered" if data['completed'] else f"🔄 {data['best_score']}%"
        feynman_status = f"{data['feynman_level']}/{data['feynman_attempts_used']}/3"
        last_updated = datetime.fromisoformat(data['last_updated']).strftime('%b %d')
        progress_data.append({
            'Topic': topic[:25], 'Best': f"{data['best_score']}/100",
            'Attempts': data['attempts'], 'Feynman': feynman_status, 
            'Status': status, 'Updated': last_updated
        })
    
    st.dataframe(progress_data, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
