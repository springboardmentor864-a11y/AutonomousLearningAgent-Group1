import json
import os
from typing import Dict, Any

PROGRESS_FILE = "student_progress.json"

def load_progress() -> Dict[str, Any]:
    """Load progress from JSON file."""
    if not os.path.exists(PROGRESS_FILE):
        return {}
    
    try:
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_progress(progress_data: Dict[str, Any]):
    """Save progress to JSON file."""
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump(progress_data, f, indent=4)
    except IOError as e:
        print(f"Error saving progress: {e}")

def update_topic_progress(topic: str, total: int, correct: int, attempted: int, relevance_score: float = 0.0):
    """Update progress for a specific topic and save."""
    progress = load_progress()
    
    if topic not in progress:
        progress[topic] = {
            "total": total,
            "correct": 0,
            "attempted": 0,
            "relevance_score": 0.0,
            "history": [] # Track attempts over time if needed
        }
    
    # We update the current state
    progress[topic]["total"] = total
    progress[topic]["correct"] = correct
    progress[topic]["attempted"] = attempted
    progress[topic]["relevance_score"] = relevance_score
    
    save_progress(progress)

def get_global_stats():
    """Calculate global statistics across all topics."""
    progress = load_progress()
    total_attempted = sum(p.get("attempted", 0) for p in progress.values())
    total_correct = sum(p.get("correct", 0) for p in progress.values())
    
    # Calculate average relevance score
    relevance_scores = [p.get("relevance_score", 0.0) for p in progress.values() if "relevance_score" in p]
    avg_relevance = (sum(relevance_scores) / len(relevance_scores)) if relevance_scores else 0.0
    
    return {
        "total_topics": len(progress),
        "total_attempted": total_attempted,
        "total_correct": total_correct,
        "avg_relevance": round(avg_relevance * 100, 1) # Scaling to percentage for display
    }
