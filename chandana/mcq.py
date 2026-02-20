# mcq.py

import json
import re


def generate_mcqs(topic: str, context: str, llm, num_questions: int = 10):
    """
    Generate MCQs strictly as a LIST of DICTS.
    Any malformed output is discarded safely.
    """

    prompt = f"""
You are an examiner.

Generate exactly {num_questions} multiple-choice questions
based ONLY on the content below.

RULES (VERY IMPORTANT):
- Output ONLY valid JSON
- Output MUST be a JSON ARRAY
- Each item MUST contain:
  - question (string)
  - options (list of 4 strings)
  - correct_index (integer 0-3)
  - explanation (empty string "")

DO NOT include:
- numbering
- markdown
- extra text
- explanations
- metadata

CONTENT:
{context}

JSON OUTPUT:
"""

    response = llm.invoke(prompt)
    raw = response.content.strip()

    # --------- Extract JSON safely ---------
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        raise ValueError("❌ MCQ JSON parsing failed")

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        raise ValueError("❌ MCQ JSON parsing failed")

    # --------- Validate MCQs ---------
    valid_mcqs = []

    for item in data:
        if not isinstance(item, dict):
            continue

        if (
            "question" in item
            and isinstance(item["question"], str)
            and "options" in item
            and isinstance(item["options"], list)
            and len(item["options"]) == 4
            and "correct_index" in item
            and isinstance(item["correct_index"], int)
            and 0 <= item["correct_index"] < 4
        ):
            item["explanation"] = ""
            valid_mcqs.append(item)

    if not valid_mcqs:
        raise ValueError("❌ Invalid MCQ structure received")

    return valid_mcqs
