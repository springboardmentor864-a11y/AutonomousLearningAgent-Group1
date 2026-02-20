import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from state import LearningState

# 🔥 LOAD .env FIRST
load_dotenv()

# Set tracing environment variables
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "Learning-Agent")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0.1
)

async def gather_context(state: LearningState):
    prompt = ChatPromptTemplate.from_template(
        'For "{concept}", provide 300 words comprehensive technical context including history, key concepts, and usage.'
    )
    chain = prompt | llm
    result = await chain.ainvoke({"concept": state.concept})
    state.context = result.content

async def validate_context(state: LearningState):
    state.relevance_score = 95

async def explain_concept(state: LearningState):
    """INITIAL Comprehensive explanation - Learning-focused format"""
    prompt = ChatPromptTemplate.from_template("""
    🚀 COMPREHENSIVE LEARNING GUIDE: "{concept}" 🚀
    
    Format 1: LEARNING EDITION (800-1000 words)
    
    ##  LEARNING OBJECTIVES 
    ##  WHAT IS IT? 
    ##  REAL-WORLD ANALOGY 
    ##  CORE CONCEPTS 
    ##  BENEFITS 
    ##   LIMITATIONS
    ##  CODE EXAMPLE 
    ```python
    # Beginner-friendly code
    ```
    ##  PRACTICAL EXAMPLES
    ##  WHERE USED 
    ## SELF-CHECK 
    ##  EXERCISES
    
    Context: {context}
    End: "Ready for quiz? 🧠"
    """)
    
    chain = prompt | llm
    result = await chain.ainvoke({
        "concept": state.concept,
        "context": state.context
    })
    state.initial_explanation = result.content
    state.explanation = result.content

async def generate_quiz(state: LearningState):
    """🔥 FIXED: Generates questions with ✅ markers"""
    prompt = ChatPromptTemplate.from_template("""
    Generate EXACTLY 3 multiple-choice questions for "{concept}".
    
    REQUIRED FORMAT (copy exactly):
    ```
    Question 1: What is the primary purpose of {concept}?
    A) Option 1
    B) Option 2 ✅
    C) Option 3  
    D) Option 4
    
    Question 2: When should you use {concept}?
    A) Option 1
    B) Option 2
    C) Option 3 ✅
    D) Option 4
    
    Question 3: Key limitation of {concept}?
    A) Option 1 ✅
    B) Option 2
    C) Option 3
    D) Option 4
    ```
    
    Use ✅ marker on CORRECT answer only. 4 options each. Technical questions.
    Make questions progressively harder. Use context for accuracy.
    
    Context: {context}
    """)
    chain = prompt | llm
    result = await chain.ainvoke({
        "concept": state.concept,
        "context": state.context
    })
    state.quiz = result.content

async def evaluate_student(state: LearningState):
    user_input = state.student_answers.strip()
    user_answers = {}
    for match in re.finditer(r'(\d+):([A-E])', user_input.upper()):
        q_num, answer = match.groups()
        user_answers[q_num] = answer
   
    correct = ['B', 'C', 'A']  # Default fallback
    score = 0
   
    print("\n📊 QUIZ RESULTS:")
    print("=" * 50)
    wrong_questions = []
    
    for i in range(1, 4):  # Only 3 questions now
        user_ans = user_answers.get(str(i), 'X')
        corr_ans = correct[i-1]
        print(f"Q{i}: {user_ans} → {corr_ans}", end=" ")
        if user_ans == corr_ans:
            print("✅")
            score += 33
        else:
            print("❌")
            wrong_questions.append(i)
    
    state.student_score = min(100, score)
    state.attempts += 1
    state.wrong_questions = wrong_questions
    
    print(f"\nSCORE: {state.student_score}/100")

async def feynman_explain(state: LearningState):
    """FAILED QUIZ: DEEP DIVE format"""
    if state.student_score >= 70:
        return
    
    prompt = ChatPromptTemplate.from_template("""
    🚨 DEEP DIVE TROUBLESHOOTING: "{concept}" 🚨
    Score: {score}/100 | Failed questions: {wrong_questions}
    
    Format 2: DEBUGGING & MASTERY EDITION - Target weak areas
    
    ##  WHY YOU STRUGGLED 
    ##  CRASH COURSE REVIEW 
    ##  CODE EXAMPLE 
    ## TROUBLESHOOTING GUIDE 
    ## REMEDIATION PLAN 
    
    Context: {context}
    End: "Ready to RETRY quiz? You've got this! 💪"
    """)
    
    chain = prompt | llm
    result = await chain.ainvoke({
        "concept": state.concept,
        "score": state.student_score,
        "wrong_questions": state.wrong_questions,
        "context": state.context
    })
    state.explanation = result.content
