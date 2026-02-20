import json
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from state import LearningState

# Load .env file
load_dotenv()

# Debug: check if API key loaded
print("GROQ KEY:", os.getenv("GROQ_API_KEY"))  # Remove later

# Initialize Groq LLM
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),   # IMPORTANT LINE
    model="llama-3.1-8b-instant",
    temperature=0.4
)

# -------------------------------
def gather_context(state: LearningState):
    prompt = f"""
Provide accurate learning content for the topic:
{state.concept}

Include:
- Definition
- Key points
- Simple real-life example
"""
    state.context = llm.invoke(prompt).content.strip()


# -------------------------------
def validate_context(state: LearningState):
    prompt = f"""
Rate how relevant this content is for the topic.

Topic:
{state.concept}

Content:
{state.context}

Return ONLY a number between 0 and 100.
"""
    response = llm.invoke(prompt).content.strip()
    digits = "".join(c for c in response if c.isdigit())
    state.relevance_score = int(digits) if digits else 80


# -------------------------------
def explain_concept(state: LearningState):
    prompt = f"""
Explain "{state.concept}" to a beginner.

Rules:
- Simple language
- Step-by-step
- Use examples

Context:
{state.context}
"""
    state.explanation = llm.invoke(prompt).content.strip()


# -------------------------------
def generate_quiz(state: LearningState):
    prompt = f"""
Create 3 multiple-choice questions from the content below.

Content:
{state.context}

Return ONLY valid JSON.
No markdown. No explanation.

Format EXACTLY like this:

[
  {{
    "question": "Question text",
    "options": {{
      "A": "option text",
      "B": "option text",
      "C": "option text",
      "D": "option text"
    }},
    "answer": "A"
  }}
]
"""
    raw = llm.invoke(prompt).content.strip()

    try:
        data = json.loads(raw)
    except Exception:
        raise ValueError(f"Quiz generation failed. Output was:\n{raw}")

    state.quiz_questions = data
    state.correct_answers = [q["answer"] for q in data]


# -------------------------------
def evaluate_student(state: LearningState):
    state.attempts += 1
    correct = 0

    for i, ans in enumerate(state.student_answers):
        if ans == state.correct_answers[i]:
            correct += 1

    state.student_score = int((correct / len(state.correct_answers)) * 100)


# -------------------------------
def feynman_explain(state: LearningState):
    prompt = f"""
Explain "{state.concept}" using the Feynman technique.

Rules:
- Very simple words
- Real-life analogy
- Beginner friendly
"""
    state.explanation = llm.invoke(prompt).content.strip()
