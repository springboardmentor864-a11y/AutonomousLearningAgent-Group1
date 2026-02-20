from checkpoints import CHECKPOINTS
from state import LearningState
from learning_agent import (
    gather_context,
    validate_context,
    explain_concept,
    generate_quiz,
    evaluate_student,
    feynman_explain
)

while True:
    print("\n📚 Available Concepts:")
    for i, cp in enumerate(CHECKPOINTS, start=1):
        print(f"{i}. {cp}")

    choice = input("\nEnter concept number (or 'exit'): ")

    if choice.lower() == "exit":
        break

    if not choice.isdigit() or int(choice) not in range(1, len(CHECKPOINTS) + 1):
        print("❌ Invalid choice")
        continue

    # Create proper state object
    state = LearningState()
    state.concept = CHECKPOINTS[int(choice) - 1]

    # Step 1: Gather + validate context
    gather_context(state)
    validate_context(state)

    print(f"\n📊 Context Relevance Score: {state.relevance_score} / 100")

    # Step 2: Explain
    explain_concept(state)
    print("\n🧠 Explanation:\n")
    print(state.explanation)

    # Step 3: Quiz loop
    while True:
        generate_quiz(state)
        print("\n📝 Quiz:\n")
        print(state.quiz)

        state.student_answers = []

        for i, q in enumerate(state.quiz_questions):
            ans = input(f"Answer for Q{i+1} (A/B/C/D): ").strip().upper()
            state.student_answers.append(ans)

        evaluate_student(state)

        print(f"\n📊 Student Score: {state.student_score} / 100")
        print(f"🔁 Attempts: {state.attempts}")

        if state.student_score >= 70:
            print("✅ Passed this concept!")
            break
        else:
            print("❌ Score < 70 → Re-explaining using Feynman technique\n")
            feynman_explain(state)
            print("🧠 Simplified Explanation:\n")
            print(state.explanation)

    print("\n🔚 Checkpoint complete. Choose next concept.")
