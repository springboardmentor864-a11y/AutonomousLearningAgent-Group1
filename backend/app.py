from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent import gather_context_with_validation, generate_quiz, evaluate_quiz, reteach
import json

app = FastAPI()

# Enable CORS so your React frontend can communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global cache to store the current session's quiz questions
quiz_cache = []

@app.post("/explain")
def explain(data: dict):
    # Generates a detailed 3-paragraph explanation and relevance score
    ctx, score, proof = gather_context_with_validation(data["topic"])
    return {
        "explanation": ctx,
        "score": score,
        "proof": proof # This is the full proof, though your UI now uses per-question proofs
    }


@app.post("/quiz")
def quiz(data: dict):
    global quiz_cache
    raw = generate_quiz(data["topic"], data["explanation"])
    
    try:
        # If agent.py already cleaned it, raw is a valid JSON string
        quiz_cache = json.loads(raw)
    except json.JSONDecodeError:
        # Emergency backup parsing
        try:
            start = raw.find("[")
            end = raw.rfind("]") + 1
            quiz_cache = json.loads(raw[start:end])
        except Exception:
            quiz_cache = [] # Return empty list instead of crashing
            
    return quiz_cache



@app.post("/submit")
def submit(data: dict):
    # Compares user_answers list against the stored quiz_cache
    result = evaluate_quiz(data["answers"], quiz_cache)
    return {"score": result}


@app.post("/reteach")
def reteach_api(data: dict):
    # Provides a simplified review if the user fails the quiz
    return {"reteach": reteach(data["topic"])}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)