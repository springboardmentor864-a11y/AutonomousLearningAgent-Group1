# run_agent.py - SAME STRUCTURE, just works with enhanced agent
import asyncio
from checkpoints import CHECKPOINTS
from state import LearningState
from learning_agent import (
    gather_context, validate_context, explain_concept,
    generate_quiz, evaluate_student, feynman_explain
)

async def main():
    print("🚀 Enhanced ML Learning Agent - Detailed Content + Code Examples!")
    
    while True:
        print("\n📚 Available Learning Topics:")
        for i, cp in enumerate(CHECKPOINTS, start=1):
            print(f"  {i}. {cp}")
        
        choice = input("\n🎯 Enter topic number (or 'exit'): ")
        if choice.lower() == "exit":
            break
        
        if not choice.isdigit() or int(choice) not in range(1, len(CHECKPOINTS) + 1):
            print("❌ Invalid choice. Try again.")
            continue
        
        concept = CHECKPOINTS[int(choice) - 1]
        print(f"\n🔥 Learning: {concept}")
        print("=" * 60)
        
        state = LearningState(concept=concept)
        
        # 🔥 STEP 1: Detailed Context Gathering
        print("📖 Gathering detailed technical context...")
        await gather_context(state)
        await validate_context(state)
        print(f"✅ Context ready! Relevance: {state.relevance_score}%")
        
        # 🔥 STEP 2: COMPREHENSIVE EXPLANATION (NEW!)
        print("\n🎓 Generating detailed explanation with examples & code...")
        await explain_concept(state)
        print("\n" + "="*60)
        print(state.explanation)
        print("="*60)
        
        # 🔥 STEP 3: Hands-on Quiz Loop
        ready = input("\n🚀 Ready for hands-on quiz? (y/n): ").lower()
        if ready != 'y':
            continue
            
        while True:
            print("\n" + "="*60)
            print("📝 HANDS-ON QUIZ (Code + Features)")
            await generate_quiz(state)
            print("\n" + state.quiz)
            
            state.student_answers = input("\n💬 Enter answers (e.g., 1:B 2:C 3:A 4:D): ")
            await evaluate_student(state)
            
            print(f"\n🎯 Score: {state.student_score}/100 | Attempts: {state.attempts}")
            
            if state.student_score >= 70:
                print("🎉 CONGRATULATIONS! Mastered this topic! 🎉")
                break
            else:
                print("🔄 Score < 70 → Feynman Technique + Code Breakdown")
                await feynman_explain(state)
                print("\n🧠" + state.explanation)

if __name__ == "__main__":
    asyncio.run(main())
