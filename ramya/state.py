from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class LearningState:
    concept: str = ""
    context: str = ""
    explanation: str = ""
    initial_explanation: str = ""
    quiz: str = ""
    quiz_variation: int = 0
    student_answers: str = ""
    student_score: int = 0
    attempts: int = 0
    relevance_score: int = 0
    wrong_questions: List[int] = field(default_factory=list)
    feynman_level: int = 0
    correct_answers: List[str] = field(default_factory=list)
