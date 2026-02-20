# content.py

def generate_content(topic: str, llm) -> str:
    """
    Generates learning content for a checkpoint topic using an LLM.
    """

    prompt = f"""
You are a tutor.

Explain the topic "{topic}" clearly and simply.
Do NOT use bullet points.
Do NOT use steps.
Explain like teaching a beginner.
Keep it concise but complete.
"""

    response = llm.invoke(prompt)
    return response.content.strip()


def generate_feynman_for_mcq(
    question: str,
    correct_answer: str,
    context: str,
    llm,
) -> str:
    """
    Feynman explanation ONLY for an incorrectly answered MCQ.
    """

    prompt = f"""
A student answered this question incorrectly.

Question:
{question}

Correct answer:
{correct_answer}

Original learning content:
{context}

Explain the concept again using the Feynman Technique.
Use very simple language.
Assume the learner is a beginner.
Do not use bullet points.
Keep it short and clear.
"""

    response = llm.invoke(prompt)
    return response.content.strip()
