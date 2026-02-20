def explain_prompt(topic):
    return f"Explain {topic} simply for beginners."

def relevance_prompt(context):
    return f"Rate relevance 1 to 5:\n{context}"

def quiz_prompt(context):
    return f"Create 3 MCQ questions from:\n{context}"

def reteach_prompt(topic):
    return f"Re-explain {topic} in very simple words."
