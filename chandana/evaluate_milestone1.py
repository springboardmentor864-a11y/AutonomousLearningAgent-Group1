"""
Milestone 1 Evaluation Script
Evaluates context gathering and validation for checkpoints.
"""

from checkpoints import get_all_checkpoints
from evaluation import evaluate_checkpoint_batch, print_evaluation_report
from graph import learning_graph, AgentState

import os


def main():
    print("=" * 80)
    print("MILESTONE 1: CHECKPOINT STRUCTURE & CONTEXT GATHERING")
    print("Evaluation Script")
    print("=" * 80)
    print()
    
    # Get test checkpoints (using first 5-10 as per evaluation plan)
    all_checkpoints = get_all_checkpoints()
    test_checkpoints = all_checkpoints[:10]  # Use first 10 for evaluation
    
    print(f"Processing {len(test_checkpoints)} test checkpoints...")
    print()
    
    # Process each checkpoint using LangGraph
    processed_checkpoints = []
    
    for i, checkpoint in enumerate(test_checkpoints, 1):
        print(f"[{i}/{len(test_checkpoints)}] Processing: {checkpoint.topic}")
        
        # Prepare state for LangGraph
        initial_state: AgentState = {
            "cp_id": checkpoint.checkpoint_id,  # Using cp_id to avoid reserved name
            "topic": checkpoint.topic,
            "objectives": checkpoint.objectives,
            "success_criteria": checkpoint.success_criteria,
            "user_notes": None,  # Can be provided here for testing
            "context": None,
            "relevance_score": None,
            "manual_relevance_score": None,
            "source": None,
            "retry_count": 0,
            "validation_passed": False
        }
        
        # Run the graph workflow
        try:
            result = learning_graph.invoke(initial_state)
            
            # Update checkpoint with results
            checkpoint.context = result.get("context")
            checkpoint.relevance_score = result.get("relevance_score")
            checkpoint.status = "completed" if result.get("validation_passed") else "in_progress"
            
            print(f"  Status: {checkpoint.status}")
            print(f"  Source: {result.get('source', 'unknown')}")
            print(f"  Relevance Score: {checkpoint.relevance_score:.3f}" if checkpoint.relevance_score else "  Relevance Score: N/A")
            print(f"  Validation: {'PASSED' if result.get('validation_passed') else 'FAILED'}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
            checkpoint.status = "error"
        
        processed_checkpoints.append(checkpoint)
        print()
    
    print("-" * 80)
    print("Running evaluation...")
    print("-" * 80)
    print()
    
    # Run evaluation (without manual scores - user should add these)
    evaluation_result = evaluate_checkpoint_batch(processed_checkpoints)
    
    # Print evaluation report
    print_evaluation_report(evaluation_result)
    
    # Instructions for manual scoring
    print("\n" + "=" * 80)
    print("MANUAL EVALUATION INSTRUCTIONS")
    print("=" * 80)
    print("""
To complete the evaluation, manually review each checkpoint's context and score:
1. Review the gathered context for each checkpoint
2. Score relevance on a 1-5 scale based on how well it addresses the objectives
3. Add manual scores using the evaluation framework

Example:
    manual_scores = {
        "CP-PY-01": 5,  # Excellent
        "CP-DS-01": 4,  # Good
        ...
    }
    
    evaluation_result = evaluate_checkpoint_batch(checkpoints, manual_scores)
    print_evaluation_report(evaluation_result)

Success Criteria for Milestone 1:
- Average relevance score >= 4/5 across test checkpoints
- Agent correctly identifies and attempts to re-fetch context if initial results are irrelevant
    """)
    
    # Print context snippets for manual review
    print("\n" + "=" * 80)
    print("CONTEXT SAMPLES FOR MANUAL REVIEW")
    print("=" * 80)
    print("(First 200 characters of each context)")
    print()
    
    for checkpoint in processed_checkpoints[:5]:  # Show first 5 for review
        if checkpoint.context:
            print(f"[{checkpoint.checkpoint_id}] {checkpoint.topic}")
            print(f"Objectives: {', '.join(checkpoint.objectives)}")
            context_preview = checkpoint.context[:200].replace('\n', ' ')
            print(f"Context: {context_preview}...")
            print(f"Full context length: {len(checkpoint.context)} characters")
            print()


if __name__ == "__main__":
    main()
