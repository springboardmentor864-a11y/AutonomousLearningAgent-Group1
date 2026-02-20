# pipeline.py

from llm import get_content_llm, get_mcq_llm
from content import generate_content
from mcq import generate_mcqs


def run_checkpoint(topic: str):
    content_llm = get_content_llm()
    content = generate_content(topic, content_llm)

    if not content or not isinstance(content, str):
        raise ValueError("❌ Learning content generation failed")

    mcq_llm = get_mcq_llm()
    mcqs = generate_mcqs(
        topic=topic,
        context=content,
        llm=mcq_llm
    )

    if not mcqs or not isinstance(mcqs, list):
        raise ValueError("❌ Invalid MCQ structure received")

    return {
        "topic": topic,
        "content": content,
        "mcqs": mcqs,
        "relevance_score": 0.0
    }
