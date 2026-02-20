"""
Understanding Verification Module for Milestone 2
Evaluates learner answers against context and calculates scores.
"""

from typing import List, Dict, Optional
from context_gathering import get_llm
from context_processing import get_context_processor
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


def evaluate_answer(
    question_data: Dict[str, any],
    learner_answer: str,
    context: str
) -> Dict[str, float]:
    """
    Evaluate a learner's answer against the context.
    Supports both open-ended (LLM graded) and Multiple Choice (exact match).
    """
    question_text = question_data.get("question", "")
    correct_answer = question_data.get("correct_answer")
    
    # --- Multiple Choice Grading ---
    if correct_answer and len(learner_answer.strip()) <= 3:
        # Assume single letter answer for MC
        user_choice = learner_answer.strip().upper().strip('.')
        correct_choice = correct_answer.strip().upper().strip('.')
        
        if user_choice == correct_choice:
            return {
                "score": 1.0,
                "feedback": f"Correct! {question_data.get('explanation', '')}"
            }
        else:
            return {
                "score": 0.0,
                "feedback": f"Incorrect. The correct answer was {correct_choice}. {question_data.get('explanation', '')}"
            }

    # --- Open Ended Grading (Legacy/Fallback) ---
    answer_guidance = question_data.get("answer_guidance")
    
    if not learner_answer or len(learner_answer.strip()) < 1:
        return {
            "score": 0.0,
            "feedback": "Answer is too short or empty."
        }
    
    llm = get_llm()
    guidance_text = f"\nGuidance for good answer: {answer_guidance}" if answer_guidance else ""
    
    prompt = f"""Evaluate this learner's answer to the following question.

Question: {question_text}

Learner's Answer:
{learner_answer}

Context (for reference):
{context[:1200]}
{guidance_text}

Evaluate the answer on a scale of 0.0 to 1.0 based on:
1. Accuracy (0-0.4): Is the answer factually correct?
2. Completeness (0-0.3): Does it address all parts of the question?
3. Clarity (0-0.2): Is it well-explained and clear?
4. Relevance (0-0.1): Is it relevant to the question asked?

Provide your evaluation as:
Score: [0.0 to 1.0]
Feedback: [brief feedback]"""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=5, max=30))
    def run_eval_llm(prompt_text):
        return llm.invoke(prompt_text)

    try:
        response = run_eval_llm(prompt)
        result = parse_evaluation(response.content)
        return result
    except Exception as e:
        logger.error(f"Answer evaluation failed after retries: {e}")
        return evaluate_answer_fallback(question_text, learner_answer, context)


def parse_evaluation(llm_response: str) -> Dict[str, float]:
    """Parse evaluation from LLM response."""
    score = 0.5  # Default score
    feedback = "Evaluation completed."
    
    lines = llm_response.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('Score:') or line.startswith('score:'):
            try:
                # Extract number
                parts = line.split(':')
                if len(parts) > 1:
                    score_str = parts[1].strip()
                    # Extract first float
                    import re
                    match = re.search(r'([0-9]*\.?[0-9]+)', score_str)
                    if match:
                        score = float(match.group(1))
                        score = max(0.0, min(1.0, score))  # Clamp to 0-1
            except:
                pass
        
        elif line.startswith('Feedback:') or line.startswith('feedback:'):
            parts = line.split(':', 1)
            if len(parts) > 1:
                feedback = parts[1].strip()
    
    return {
        "score": score,
        "feedback": feedback
    }


def evaluate_answer_fallback(question: str, learner_answer: str, context: str) -> Dict[str, float]:
    """Fallback evaluation using simple keyword matching."""
    question_lower = question.lower()
    answer_lower = learner_answer.lower()
    context_lower = context.lower()
    
    # Extract key terms from question
    question_words = set(word for word in question_lower.split() if len(word) > 4)
    
    # Check if answer mentions question terms
    mentioned_terms = sum(1 for term in question_words if term in answer_lower)
    
    # Check if answer relates to context
    context_words = set(word for word in context_lower.split() if len(word) > 4)
    answer_words = set(word for word in answer_lower.split() if len(word) > 4)
    overlap = len(answer_words.intersection(context_words))
    
    # Simple scoring
    score = min(1.0, (mentioned_terms / max(len(question_words), 1)) * 0.5 + (overlap / 10) * 0.5)
    
    feedback = "Answer evaluated using keyword matching. "
    if score > 0.7:
        feedback += "Good coverage of relevant concepts."
    elif score > 0.4:
        feedback += "Some relevant points covered."
    else:
        feedback += "Limited relevance to the question."
    
    return {
        "score": score,
        "feedback": feedback
    }


def evaluate_all_answers(
    questions: List[Dict[str, str]],
    learner_answers: List[str],
    context: str
) -> Dict[str, any]:
    """
    Evaluate all learner answers and calculate overall score.
    
    Args:
        questions: List of question dictionaries
        learner_answers: List of learner answers (same order as questions)
        context: The context material
    
    Returns:
        Dictionary with overall_score, question_scores, and feedback
    """
    if len(questions) != len(learner_answers):
        raise ValueError("Number of questions must match number of answers")
    
    question_scores = []
    total_score = 0.0
    
    for i, (question_data, answer) in enumerate(zip(questions, learner_answers)):
        evaluation = evaluate_answer(
            question_data,
            answer,
            context
        )
        
        question_scores.append({
            "question_index": i,
            "question": question_data["question"],
            "answer": answer,
            "score": evaluation["score"],
            "feedback": evaluation["feedback"]
        })
        
        total_score += evaluation["score"]
    
    # Calculate percentage score
    overall_score = (total_score / len(questions)) * 100
    
    return {
        "overall_score": overall_score,  # Percentage 0-100
        "question_scores": question_scores,
        "passed": overall_score >= 70.0
    }


def simulate_learner_answers(
    questions: List[Dict[str, str]],
    context: str,
    quality: str = "medium"  # "poor", "medium", "good"
) -> List[str]:
    """
    Simulate learner answers for testing purposes.
    
    Args:
        questions: List of questions
        context: Context material
        quality: Quality of simulated answers
    
    Returns:
        List of simulated answers
    """
    llm = get_llm()
    
    if quality == "poor":
        prompt_prefix = "Provide brief, incomplete answers that miss key points:"
    elif quality == "good":
        prompt_prefix = "Provide detailed, accurate, and complete answers:"
    else:  # medium
        prompt_prefix = "Provide reasonably good answers with some gaps:"
    
    all_questions = "\n\n".join(f"Q{i+1}: {q['question']}" for i, q in enumerate(questions))
    
    prompt = f"""{prompt_prefix}

Context:
{context[:1500]}

Questions:
{all_questions}

Provide answers for each question. Format as:
A1: [answer to question 1]
A2: [answer to question 2]
..."""
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=5, max=30))
    def run_sim_llm(prompt_text):
        return llm.invoke(prompt_text)

    try:
        response = run_sim_llm(prompt)
        answers = parse_simulated_answers(response.content, len(questions))
        return answers
    except Exception as e:
        logger.error(f"Answer simulation failed after retries: {e}")
        # Fallback: Generate simple answers
        return [f"Answer to question about {q['question'][:50]}..." for q in questions]


def parse_simulated_answers(llm_response: str, expected_count: int) -> List[str]:
    """Parse simulated answers from LLM response."""
    answers = []
    lines = llm_response.split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith('A') and line[1].isdigit() and ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                answers.append(parts[1].strip())
    
    # Fill if needed
    while len(answers) < expected_count:
        answers.append("This is a simulated answer.")
    
    return answers[:expected_count]
