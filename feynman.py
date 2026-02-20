# feynman.py

from llm import get_feynman_llm


def feynman_explain(question: str, user_answer: str, correct_answer: str, context: str) -> str:
    """
    Simple Feynman-style explanation:
    - Why the user's answer is wrong
    - What the correct idea is
    - Explained simply, no steps, no bullets
    """

    llm = get_feynman_llm()

    prompt = f"""
You are a patient tutor.

The student answered a question incorrectly.

Question:
{question}

Student's answer:
{user_answer}

Correct answer:
{correct_answer}

Learning context:
{context}

Explain in very simple language:
- why the student's answer is wrong
- what the correct idea actually means

Do not use steps.
Do not use bullet points.
Keep it short and friendly.
"""

    response = llm.invoke(prompt)
    return response.content.strip()
