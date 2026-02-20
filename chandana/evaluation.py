"""
Evaluation Framework for Milestone 1
Implements Context Relevance Scoring (1-5 scale) as per evaluation plan
"""

from typing import List, Dict, Optional
from datetime import datetime
from checkpoints import Checkpoint


# --------------------------------------------------
# Context Relevance Evaluation
# --------------------------------------------------
class ContextEvaluator:
    """Evaluates context relevance on a 1-5 scale based on checkpoint objectives."""
    
    @staticmethod
    def calculate_auto_relevance_score(checkpoint: Checkpoint, context: str) -> float:
        """
        Automatically calculate relevance score (0-1) based on objectives coverage.
        This is used internally before manual review.
        """
        if not context or not checkpoint.objectives:
            return 0.0
        
        context_lower = context.lower()
        objectives_hit = sum(
            1 for obj in checkpoint.objectives 
            if obj.lower() in context_lower
        )
        
        word_count = len(context.split())
        
        # Objectives coverage (60% weight)
        objectives_coverage = objectives_hit / len(checkpoint.objectives)
        
        # Content sufficiency (40% weight)
        content_sufficiency = min(1.0, word_count / 600)
        
        relevance_score = (objectives_coverage * 0.6 + content_sufficiency * 0.4)
        return min(1.0, relevance_score)
    
    @staticmethod
    def manual_relevance_guidelines() -> Dict[int, str]:
        """
        Guidelines for manual relevance scoring (1-5 scale).
        Used during evaluation phase.
        """
        return {
            5: "Excellent - Context directly addresses all objectives with clear, relevant information",
            4: "Good - Context addresses most objectives well with relevant information",
            3: "Adequate - Context addresses some objectives but may lack depth or relevance",
            2: "Poor - Context mentions objectives but is largely irrelevant or superficial",
            1: "Very Poor - Context is irrelevant or doesn't address the checkpoint objectives"
        }
    
    @staticmethod
    def evaluate_checkpoint_context(
        checkpoint: Checkpoint, 
        manual_score: Optional[int] = None
    ) -> Dict:
        """
        Evaluate a checkpoint's context.
        
        Args:
            checkpoint: The checkpoint to evaluate
            manual_score: Optional manual relevance score (1-5)
        
        Returns:
            Dictionary with evaluation results
        """
        if not checkpoint.context:
            return {
                "checkpoint_id": checkpoint.checkpoint_id,
                "topic": checkpoint.topic,
                "has_context": False,
                "auto_score": 0.0,
                "manual_score": manual_score,
                "validation_passed": False
            }
        
        auto_score = ContextEvaluator.calculate_auto_relevance_score(
            checkpoint, 
            checkpoint.context
        )
        
        # Calculate objectives coverage
        context_lower = checkpoint.context.lower()
        objectives_hit = [
            obj for obj in checkpoint.objectives 
            if obj.lower() in context_lower
        ]
        
        word_count = len(checkpoint.context.split())
        
        # Validation: auto score >= 0.6 and word_count > 200
        validation_passed = auto_score >= 0.6 and word_count > 200
        
        result = {
            "checkpoint_id": checkpoint.checkpoint_id,
            "topic": checkpoint.topic,
            "has_context": True,
            "auto_score": round(auto_score, 3),
            "auto_score_percent": round(auto_score * 100, 1),
            "manual_score": manual_score,
            "objectives_count": len(checkpoint.objectives),
            "objectives_hit": len(objectives_hit),
            "objectives_hit_list": objectives_hit,
            "objectives_missed": [
                obj for obj in checkpoint.objectives 
                if obj.lower() not in context_lower
            ],
            "word_count": word_count,
            "validation_passed": validation_passed,
            "status": checkpoint.status
        }
        
        return result


# --------------------------------------------------
# Batch Evaluation
# --------------------------------------------------
def evaluate_checkpoint_batch(
    checkpoints: List[Checkpoint],
    manual_scores: Optional[Dict[str, int]] = None
) -> Dict:
    """
    Evaluate multiple checkpoints and generate evaluation report.
    
    Args:
        checkpoints: List of checkpoints to evaluate
        manual_scores: Optional dict mapping checkpoint_id to manual score (1-5)
    
    Returns:
        Dictionary with batch evaluation results
    """
    if manual_scores is None:
        manual_scores = {}
    
    evaluator = ContextEvaluator()
    results = []
    
    for checkpoint in checkpoints:
        manual_score = manual_scores.get(checkpoint.checkpoint_id)
        result = evaluator.evaluate_checkpoint_context(checkpoint, manual_score)
        results.append(result)
    
    # Calculate statistics
    auto_scores = [r["auto_score"] for r in results if r["has_context"]]
    manual_scores_list = [r["manual_score"] for r in results if r["manual_score"] is not None]
    
    stats = {
        "total_checkpoints": len(checkpoints),
        "checkpoints_with_context": sum(1 for r in results if r["has_context"]),
        "validation_passed_count": sum(1 for r in results if r["validation_passed"]),
        "average_auto_score": round(sum(auto_scores) / len(auto_scores), 3) if auto_scores else 0.0,
        "average_manual_score": round(sum(manual_scores_list) / len(manual_scores_list), 2) if manual_scores_list else None,
        "validation_pass_rate": round(
            sum(1 for r in results if r["validation_passed"]) / len(results) * 100, 
            1
        ) if results else 0.0
    }
    
    # Success criteria: average manual score >= 4/5
    if manual_scores_list:
        milestone_success = stats["average_manual_score"] >= 4.0
        stats["milestone_1_success"] = milestone_success
    else:
        stats["milestone_1_success"] = None
        stats["note"] = "Manual scores not provided. Please review and score contexts manually."
    
    return {
        "evaluation_date": datetime.now().isoformat(),
        "results": results,
        "statistics": stats,
        "guidelines": evaluator.manual_relevance_guidelines()
    }


# --------------------------------------------------
# Report Generation
# --------------------------------------------------
def print_evaluation_report(evaluation_result: Dict):
    """Print a formatted evaluation report."""
    print("=" * 80)
    print("MILESTONE 1 EVALUATION REPORT")
    print("=" * 80)
    print(f"Evaluation Date: {evaluation_result['evaluation_date']}\n")
    
    stats = evaluation_result["statistics"]
    print("SUMMARY STATISTICS")
    print("-" * 80)
    print(f"Total Checkpoints: {stats['total_checkpoints']}")
    print(f"Checkpoints with Context: {stats['checkpoints_with_context']}")
    print(f"Validation Passed: {stats['validation_passed_count']}/{stats['total_checkpoints']}")
    print(f"Validation Pass Rate: {stats['validation_pass_rate']}%")
    print(f"Average Auto Score: {stats['average_auto_score']:.3f} (0-1 scale)")
    
    if stats['average_manual_score']:
        print(f"Average Manual Score: {stats['average_manual_score']:.2f}/5.0")
        if stats.get('milestone_1_success'):
            print("\n✅ MILESTONE 1 SUCCESS: Average relevance score >= 4/5")
        else:
            print("\n❌ MILESTONE 1 FAILED: Average relevance score < 4/5")
    else:
        print("\n⚠️  Manual scores not provided. Please review contexts manually.")
        print("\nManual Relevance Scoring Guidelines:")
        for score, description in evaluation_result['guidelines'].items():
            print(f"  {score}: {description}")
    
    print("\n" + "=" * 80)
    print("DETAILED RESULTS")
    print("=" * 80)
    
    for result in evaluation_result["results"]:
        print(f"\n[{result['checkpoint_id']}] {result['topic']}")
        print(f"  Status: {result['status']}")
        if result['has_context']:
            print(f"  Auto Score: {result['auto_score']:.3f} ({result['auto_score_percent']}%)")
            if result['manual_score']:
                print(f"  Manual Score: {result['manual_score']}/5")
            print(f"  Word Count: {result['word_count']}")
            print(f"  Objectives: {result['objectives_hit']}/{result['objectives_count']} covered")
            if result['objectives_hit_list']:
                print(f"    ✓ Hit: {', '.join(result['objectives_hit_list'])}")
            if result['objectives_missed']:
                print(f"    ✗ Missed: {', '.join(result['objectives_missed'])}")
            print(f"  Validation: {'PASSED' if result['validation_passed'] else 'FAILED'}")
        else:
            print("  ⚠️  No context available")
    
    print("\n" + "=" * 80)
