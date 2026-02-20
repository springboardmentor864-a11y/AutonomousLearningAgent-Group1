class LearningState:
    def __init__(self):
        self.concept = ""
        self.context = ""
        self.explanation = ""
        self.quiz_questions = []   # list of dicts
        self.correct_answers = []
        self.student_answers = []
        self.student_score = 0
        self.relevance_score = 0
        self.attempts = 0
