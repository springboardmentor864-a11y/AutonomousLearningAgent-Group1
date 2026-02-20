"""
Question Generation Module for Milestone 2
Generates multiple-choice questions (minimum 11, more than 10) per checkpoint based on context.
"""

from typing import List, Dict
from context_gathering import get_llm
from context_processing import get_context_processor
from tenacity import retry, stop_after_attempt, wait_exponential
import time
import logging

logger = logging.getLogger(__name__)


def generate_questions(
    topic: str,
    objectives: List[str],
    context: str,
    num_questions: int = 11
) -> List[Dict[str, any]]:
    """
    Generate multiple-choice questions based on context and objectives.
    
    Args:
        topic: The checkpoint topic
        objectives: List of learning objectives
        context: The gathered context
        num_questions: Number of questions to generate (minimum 11, more than 10)
    
    Returns:
        List of dictionaries with 'question', 'options', 'correct_answer', and 'explanation' keys
    """
    if not context:
        return []
    
    llm = get_llm()
    
    objectives_str = "\n".join(f"- {obj}" for obj in objectives)
    
    # Use more context for generating more questions
    context_length = min(len(context), 3500) if num_questions > 10 else min(len(context), 1500)
    
    prompt = f"""Generate {num_questions} multiple-choice assessment questions for the topic: {topic}

Learning Objectives:
{objectives_str}

Context (first {context_length} chars):
{context[:context_length]}

Generate {num_questions} multiple-choice questions that:
1. Test understanding of the key concepts from the objectives
2. Vary in difficulty (mix of basic, intermediate, and advanced)
3. Can be answered using the provided context
4. Focus on practical understanding rather than memorization
5. Each question should have exactly 4 options (A, B, C, D)
6. Cover all learning objectives comprehensively

For each question, provide:
- The question text
- 4 answer options (A, B, C, D) where one is correct and three are plausible distractors
- The correct answer (A, B, C, or D)
- Brief explanation of why the correct answer is right

Format your response as:
Q1: [question text]
A) [option A]
B) [option B]
C) [option C]
D) [option D]
Correct: [A/B/C/D]
Explanation: [brief explanation]

Q2: [question text]
A) [option A]
B) [option B]
C) [option C]
D) [option D]
Correct: [A/B/C/D]
Explanation: [brief explanation]

... and so on for all {num_questions} questions."""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=5, max=30))
    def run_llm_with_retry(prompt_text):
        return llm.invoke(prompt_text)

    try:
        response = run_llm_with_retry(prompt)
        questions = parse_multiple_choice_questions(response.content, num_questions, topic, objectives)
        return questions
    except Exception as e:
        logger.error(f"Question generation failed after retries: {e}")
        # Fallback: Generate simple multiple-choice questions
        return generate_fallback_questions(topic, objectives, num_questions)


def parse_multiple_choice_questions(llm_response: str, expected_count: int, topic: str, objectives: List[str]) -> List[Dict[str, any]]:
    """Parse multiple-choice questions from LLM response."""
    questions = []
    lines = llm_response.split('\n')
    
    current_question = None
    current_options = {}
    current_correct = None
    current_explanation = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Question line
        if line.startswith('Q') and ':' in line:
            # Save previous question if exists
            if current_question and current_options:
                questions.append({
                    "question": current_question,
                    "options": current_options,
                    "correct_answer": current_correct or "A",
                    "explanation": current_explanation or "Correct answer based on the learning objectives.",
                    "answer_guidance": current_explanation or "Select the option that best addresses the question."  # Keep for compatibility
                })
            
            # Extract new question
            parts = line.split(':', 1)
            if len(parts) == 2:
                current_question = parts[1].strip()
                current_options = {}
                current_correct = None
                current_explanation = None
        
        # Option lines (A), B), C), D))
        elif line and (line.startswith('A)') or line.startswith('B)') or line.startswith('C)') or line.startswith('D)')):
            option_label = line[0]
            option_text = line[2:].strip() if len(line) > 2 else line[2:]
            current_options[option_label] = option_text
        
        # Correct answer line
        elif line.startswith('Correct:') or line.startswith('correct:'):
            parts = line.split(':', 1)
            if len(parts) > 1:
                correct = parts[1].strip().upper()
                if correct in ['A', 'B', 'C', 'D']:
                    current_correct = correct
        
        # Explanation line
        elif line.startswith('Explanation:') or line.startswith('explanation:'):
            parts = line.split(':', 1)
            if len(parts) > 1:
                current_explanation = parts[1].strip()
        
        elif line and not current_question and '?' in line:
            # Question might not have Q prefix
            current_question = line
    
    # Add last question
    if current_question and current_options:
        questions.append({
            "question": current_question,
            "options": current_options,
            "correct_answer": current_correct or "A",
            "explanation": current_explanation or "Correct answer based on the learning objectives.",
            "answer_guidance": current_explanation or "Select the option that best addresses the question."
        })
    
    # Ensure we have expected count - fill with fallbacks
    if len(questions) < expected_count:
        fallback_questions = generate_fallback_questions(topic, objectives, expected_count - len(questions))
        questions.extend(fallback_questions)
    
    return questions[:expected_count]


def generate_fallback_questions(topic: str, objectives: List[str], num_questions: int) -> List[Dict[str, any]]:
    """Generate simple fallback multiple-choice questions."""
    questions = []
    
    # Common multiple-choice options for fallback
    common_options = {
        "A": "Option A (correct answer)",
        "B": "Option B (distractor)",
        "C": "Option C (distractor)",
        "D": "Option D (distractor)"
    }
    
    for i, obj in enumerate(objectives[:num_questions]):
        questions.append({
            "question": f"What is {obj} in the context of {topic}?",
            "options": {
                "A": f"{obj} is a fundamental concept in {topic}",
                "B": f"{obj} is unrelated to {topic}",
                "C": f"{obj} is only used in advanced {topic}",
                "D": f"{obj} is deprecated in {topic}"
            },
            "correct_answer": "A",
            "explanation": f"The correct answer is A. {obj} is a fundamental concept in {topic}.",
            "answer_guidance": f"Select the option that best explains {obj} in {topic}."
        })
    
    # Fill remaining with generic questions
    while len(questions) < num_questions:
        questions.append({
            "question": f"Which of the following best describes a key concept in {topic}?",
            "options": {
                "A": "A fundamental principle that applies broadly",
                "B": "An optional feature with limited use",
                "C": "A deprecated concept no longer used",
                "D": "An advanced topic not covered in basics"
            },
            "correct_answer": "A",
            "explanation": "The correct answer is A, as fundamental principles apply broadly in the topic.",
            "answer_guidance": "Select the option that best describes a key concept."
        })
    
    return questions
