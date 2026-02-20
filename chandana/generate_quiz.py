"""
Quiz Question Generator
Generates quiz questions for checkpoints.
"""

from checkpoints import get_all_checkpoints, Checkpoint
from context_gathering import gather_context
from question_generation import generate_questions
import sys
import json


def generate_quiz_for_checkpoint(checkpoint: Checkpoint, num_questions: int = 11) -> dict:
    """
    Generate quiz questions for a single checkpoint.
    
    Args:
        checkpoint: The checkpoint to generate questions for
        num_questions: Number of questions to generate
    
    Returns:
        Dictionary with checkpoint info and questions
    """
    print(f"\nGenerating quiz for: {checkpoint.topic}")
    print(f"Objectives: {', '.join(checkpoint.objectives)}")
    print("Gathering context...")
    
    # Gather context
    context = gather_context(checkpoint.topic)
    
    if not context:
        print("Warning: No context gathered. Cannot generate questions.")
        return None
    
    print(f"Context gathered ({len(context)} characters)")
    print("Generating questions...")
    
    # Generate questions
    questions = generate_questions(
        topic=checkpoint.topic,
        objectives=checkpoint.objectives,
        context=context,
        num_questions=num_questions
    )
    
    print(f"Generated {len(questions)} questions")
    
    return {
        "checkpoint_id": checkpoint.checkpoint_id,
        "topic": checkpoint.topic,
        "objectives": checkpoint.objectives,
        "context_length": len(context),
        "questions": questions
    }


def collect_user_answers(quiz_data: dict, skip_header: bool = False) -> dict:
    """
    Collect answers from the user for all quiz questions.
    
    Args:
        quiz_data: Dictionary containing quiz questions
        skip_header: If True, skip printing the header (used when called from print_quiz)
        
    Returns:
        Dictionary with user answers and evaluation results
    """
    if not skip_header:
        print("\n" + "=" * 80)
        print("QUIZ: " + quiz_data['topic'])
        print("Checkpoint ID: " + quiz_data['checkpoint_id'])
        print("=" * 80)
    
    print("\nPlease answer the following questions. Enter A, B, C, or D for each question.\n")
    
    user_answers = []
    questions = quiz_data.get('questions', [])
    
    for i, q in enumerate(questions, 1):
        print(f"\nQ{i}. {q.get('question', 'N/A')}")
        
        # Print options
        options = q.get('options', {})
        if options:
            for option in ['A', 'B', 'C', 'D']:
                if option in options:
                    print(f"   {option}) {options[option]}")
        
        # Get user answer
        while True:
            answer = input(f"\nYour answer for Q{i} (A/B/C/D): ").strip().upper()
            if answer in ['A', 'B', 'C', 'D']:
                user_answers.append(answer)
                break
            else:
                print("Invalid input. Please enter A, B, C, or D.")
    
    return {
        "user_answers": user_answers,
        "questions": questions
    }


def evaluate_quiz_answers(quiz_data: dict, user_answers: list) -> dict:
    """
    Evaluate user answers against correct answers and calculate relevance score.
    
    Args:
        quiz_data: Dictionary containing quiz questions with correct answers
        user_answers: List of user's answers (A, B, C, or D)
        
    Returns:
        Dictionary with evaluation results including relevance score
    """
    questions = quiz_data.get('questions', [])
    
    if len(questions) != len(user_answers):
        raise ValueError(f"Number of questions ({len(questions)}) doesn't match number of answers ({len(user_answers)})")
    
    correct_count = 0
    question_results = []
    
    for i, (q, user_answer) in enumerate(zip(questions, user_answers), 1):
        correct_answer = q.get('correct_answer', '').upper()
        is_correct = user_answer == correct_answer
        
        if is_correct:
            correct_count += 1
        
        question_results.append({
            "question_number": i,
            "question": q.get('question', 'N/A'),
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": q.get('explanation', 'N/A')
        })
    
    # Calculate relevance score based on percentage of correct answers (0-1 scale)
    total_questions = len(questions)
    relevance_score = correct_count / total_questions if total_questions > 0 else 0.0
    
    # Calculate percentage score (0-100)
    percentage_score = relevance_score * 100
    
    return {
        "total_questions": total_questions,
        "correct_answers": correct_count,
        "incorrect_answers": total_questions - correct_count,
        "relevance_score": round(relevance_score, 3),  # 0-1 scale
        "percentage_score": round(percentage_score, 1),  # 0-100 scale
        "question_results": question_results
    }


def print_quiz(quiz_data: dict, show_answers: bool = False, interactive: bool = False):
    """
    Print quiz questions in a formatted way.
    
    Args:
        quiz_data: Dictionary containing quiz data
        show_answers: Whether to show correct answers
        interactive: Whether to collect user answers and calculate relevance score
    """
    print("\n" + "=" * 80)
    print(f"QUIZ: {quiz_data['topic']}")
    print(f"Checkpoint ID: {quiz_data['checkpoint_id']}")
    print("=" * 80)
    print(f"\nLearning Objectives:")
    for obj in quiz_data['objectives']:
        print(f"  - {obj}")
    
    print(f"\n{'=' * 80}")
    print("MULTIPLE CHOICE QUESTIONS")
    print("=" * 80)
    
    for i, q in enumerate(quiz_data['questions'], 1):
        print(f"\nQ{i}. {q.get('question', 'N/A')}")
        
        # Print options
        options = q.get('options', {})
        if options:
            for option in ['A', 'B', 'C', 'D']:
                if option in options:
                    print(f"   {option}) {options[option]}")
        else:
            # Fallback for old format
            if q.get('answer_guidance'):
                print(f"   [Guidance: {q['answer_guidance']}]")
        
        # Show correct answer and explanation if requested
        if show_answers:
            correct = q.get('correct_answer', 'N/A')
            explanation = q.get('explanation', 'N/A')
            print(f"\n   Correct Answer: {correct}")
            print(f"   Explanation: {explanation}")
    
    if show_answers:
        print("\n" + "=" * 80)
        print("ANSWERS KEY")
        print("=" * 80)
        for i, q in enumerate(quiz_data['questions'], 1):
            correct = q.get('correct_answer', 'N/A')
            print(f"Q{i}: {correct}")
    
    # If interactive mode, collect answers and evaluate
    if interactive:
        print("\n" + "=" * 80)
        print("ANSWER THE QUESTIONS")
        print("=" * 80)
        answer_data = collect_user_answers(quiz_data, skip_header=True)
        evaluation = evaluate_quiz_answers(quiz_data, answer_data['user_answers'])
        
        # Print evaluation results
        print("\n" + "=" * 80)
        print("QUIZ RESULTS")
        print("=" * 80)
        print(f"\nTotal Questions: {evaluation['total_questions']}")
        print(f"Correct Answers: {evaluation['correct_answers']}")
        print(f"Incorrect Answers: {evaluation['incorrect_answers']}")
        print(f"\nRelevance Score: {evaluation['relevance_score']:.3f} (on 0-1 scale)")
        print(f"Percentage Score: {evaluation['percentage_score']:.1f}%")
        
        print("\n" + "=" * 80)
        print("DETAILED RESULTS")
        print("=" * 80)
        for result in evaluation['question_results']:
            status = "✓ CORRECT" if result['is_correct'] else "✗ INCORRECT"
            print(f"\nQ{result['question_number']}: {result['question']}")
            print(f"  Your Answer: {result['user_answer']}")
            print(f"  Correct Answer: {result['correct_answer']}")
            print(f"  Status: {status}")
            if not result['is_correct']:
                print(f"  Explanation: {result['explanation']}")
        
        print("\n" + "=" * 80)
        
        # Return evaluation results
        return evaluation
    
    print("\n" + "=" * 80)


def save_quiz_to_file(quiz_data: dict, filename: str):
    """Save quiz to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(quiz_data, f, indent=2, ensure_ascii=False)
    print(f"\nQuiz saved to {filename}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("=" * 80)
        print("QUIZ QUESTION GENERATOR")
        print("=" * 80)
        print("\nUsage:")
        print("  python generate_quiz.py <checkpoint_id> [num_questions] [--save] [--answers] [--interactive]")
        print("  python generate_quiz.py all [num_questions]")
        print("  python generate_quiz.py list")
        print("\nOptions:")
        print("  --save        Save quiz to JSON file")
        print("  --answers     Show correct answers and explanations")
        print("  --interactive Collect user answers and calculate relevance score")
        print("\nNote: Minimum 11 questions per checkpoint (more than 10)")
        print("\nExamples:")
        print("  python generate_quiz.py CP-PY-01 15")
        print("  python generate_quiz.py CP-PY-01 15 --save")
        print("  python generate_quiz.py CP-PY-01 15 --answers")
        print("  python generate_quiz.py CP-PY-01 15 --interactive")
        print("  python generate_quiz.py all 12")
        print("=" * 80)
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        # List all checkpoints
        checkpoints = get_all_checkpoints()
        print("=" * 80)
        print("AVAILABLE CHECKPOINTS")
        print("=" * 80)
        for cp in checkpoints:
            print(f"  {cp.checkpoint_id:12} - {cp.topic}")
            print(f"    Objectives: {', '.join(cp.objectives[:3])}{'...' if len(cp.objectives) > 3 else ''}")
        print("=" * 80)
        return
    
    # Get number of questions (default 11 - more than 10)
    num_questions = 11
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        num_questions = int(sys.argv[2])
        # Ensure at least 11 questions
        if num_questions < 11:
            num_questions = 11
    
    # Check for flags
    save_to_file = "--save" in sys.argv
    interactive_mode = "--interactive" in sys.argv
    
    if command == "all":
        # Generate quizzes for all checkpoints
        checkpoints = get_all_checkpoints()
        print(f"\nGenerating quizzes for {len(checkpoints)} checkpoints...")
        
        all_quizzes = []
        for i, checkpoint in enumerate(checkpoints, 1):
            print(f"\n[{i}/{len(checkpoints)}] Processing {checkpoint.checkpoint_id}...")
            quiz_data = generate_quiz_for_checkpoint(checkpoint, num_questions)
            if quiz_data:
                all_quizzes.append(quiz_data)
                print_quiz(quiz_data)
                if save_to_file:
                    filename = f"quiz_{checkpoint.checkpoint_id}.json"
                    save_quiz_to_file(quiz_data, filename)
        
        # Save combined file
        if save_to_file:
            combined_filename = "quizzes_all.json"
            with open(combined_filename, 'w', encoding='utf-8') as f:
                json.dump(all_quizzes, f, indent=2, ensure_ascii=False)
            print(f"\nAll quizzes saved to {combined_filename}")
        
        print(f"\nGenerated quizzes for {len(all_quizzes)} checkpoints")
    
    else:
        # Generate quiz for specific checkpoint
        checkpoint_id = sys.argv[1]
        checkpoints = get_all_checkpoints()
        checkpoint = next((cp for cp in checkpoints if cp.checkpoint_id == checkpoint_id), None)
        
        if not checkpoint:
            print(f"Error: Checkpoint '{checkpoint_id}' not found.")
            print("\nAvailable checkpoints:")
            for cp in checkpoints:
                print(f"  {cp.checkpoint_id} - {cp.topic}")
            return
        
        # Check for flags
        show_answers = "--answers" in sys.argv or "--show-answers" in sys.argv
        
        quiz_data = generate_quiz_for_checkpoint(checkpoint, num_questions)
        if quiz_data:
            evaluation_result = print_quiz(quiz_data, show_answers=show_answers, interactive=interactive_mode)
            
            # Save quiz data
            if save_to_file:
                filename = f"quiz_{checkpoint_id}.json"
                save_quiz_to_file(quiz_data, filename)
            
            # Save evaluation results if interactive mode was used
            if interactive_mode and evaluation_result:
                eval_filename = f"quiz_evaluation_{checkpoint_id}.json"
                with open(eval_filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        "checkpoint_id": checkpoint_id,
                        "topic": quiz_data['topic'],
                        "evaluation": evaluation_result
                    }, f, indent=2, ensure_ascii=False)
                print(f"\nEvaluation results saved to {eval_filename}")


if __name__ == "__main__":
    main()
