import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load .env variables (GROQ_API_KEY, LANGCHAIN_API_KEY, etc.)
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "MentorFlow-Learning-Agent"


# Initialize LLM - it will automatically use LangSmith tracing since it's in your .env
llm = ChatGroq(
    model="llama-3.1-8b-instant", 
    api_key=os.getenv("GROQ_API_KEY")
)

def gather_context_with_validation(topic):
    prompt = f"""
Provide a deep-dive explanation of {topic} for a beginner. 
Length: 350-400 words. 
Format: 4 distinct paragraphs. 
At the end, provide a relevance score (1-10) to Data Science.

EXPLANATION:
[Detailed text here]

SCORE:
[Number only]
"""
    res = llm.invoke(prompt).content
    
    # 1. Split the response to get the explanation
    raw_explanation = res.split("SCORE:")[0].replace("EXPLANATION:", "").strip()
    
    # 2. REMOVE BOLD FORMATTING: This replaces all ** with an empty string
    clean_explanation = raw_explanation.replace("**", "")
    
    # 3. Clean the score
    score_match = re.search(r'\d+', res.split("SCORE:")[1])
    score = score_match.group(0) if score_match else "5"
    
    return clean_explanation, score, ""


def generate_quiz(topic, context):
    prompt = f"""
Using ONLY the following text: "{context}"
Create 5 MCQ questions. 
For each question, include a "hint" which is a direct quote from the text.
Return JSON ONLY. Do not include any intro text or explanations.

Format:
[
  {{"q": "question here", "options": ["a", "b", "c", "d"], "answer": 0, "hint": "quote here"}}
]
"""
    res = llm.invoke(prompt).content
    
    # Clean the response: find the first '[' and last ']'
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        if match:
            json_str = match.group(0)
            # Remove any potential trailing commas before the closing bracket
            json_str = re.sub(r',\s*\]', ']', json_str)
            return json_str
        return "[]"
    except Exception:
        return "[]"

def evaluate_quiz(user_answers, quiz):
    return sum(1 for i, q in enumerate(quiz) if user_answers[i] == q["answer"])

def reteach(topic):
    # Get the raw response from the LLM
    res = llm.invoke(f"Reteach {topic} simply for someone who failed a quiz.").content
    
    # CLEANING: Remove the bold markdown symbols
    clean_reteach = res.replace("**", "")
    

    return clean_reteach
