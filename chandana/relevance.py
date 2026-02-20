# relevance.py
from llm import get_relevance_llm


def evaluate_relevance(content: str, mcqs: list) -> float:
    """
    Returns a relevance score (1–5) indicating how well MCQs match the content.
    """

    llm = get_relevance_llm()

    questions = "\n".join(
        [f"- {mcq['question']}" for mcq in mcqs if "question" in mcq]
    )

    prompt = f"""
You are an evaluator.

Learning content:
{content}

Questions:
{questions}

Rate how well the questions match the content on a scale of 1 to 5.
Only return a number.
"""

    response = llm.invoke(prompt).content.strip()

    try:
        score = float(response)
        return min(max(score, 1.0), 5.0)
    except:
        return 3.0
