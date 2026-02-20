from langgraph.graph import StateGraph
from typing import TypedDict, Optional, List, Any
from typing_extensions import Annotated

from context_gathering import gather_context
from context_processing import get_context_processor
from question_generation import generate_questions
from understanding_verification import simulate_learner_answers, evaluate_all_answers

# --------------------------------------------------
# Agent State (SINGLE SOURCE OF TRUTH)
# --------------------------------------------------
class AgentState(TypedDict):
    cp_id: str  # checkpoint_id renamed to avoid LangGraph reserved name
    topic: str
    objectives: List[str]
    success_criteria: List[str]
    user_notes: Optional[str]
    context: Optional[str]
    relevance_score: Optional[float]  # 0-1 scale
    manual_relevance_score: Optional[int]  # 1-5 scale for manual evaluation
    source: Optional[str]  # "user_notes", "llm", or "web_search"
    retry_count: int
    validation_passed: bool
    # Milestone 2 fields
    vector_store: Optional[Any]  # InMemoryVectorStore
    processed_chunks: Optional[List[Any]]  # List of Document chunks
    questions: Optional[List[dict]]  # List of question dictionaries
    learner_answers: Optional[List[str]]  # List of learner answers
    verification_score: Optional[float]  # Percentage score 0-100
    verification_passed: Optional[bool]  # True if score >= 70%
    question_evaluations: Optional[List[dict]]  # Individual question scores
    interactive_mode: Optional[bool]  # Enable interactive quiz


# --------------------------------------------------
# Node: Gather Context
# --------------------------------------------------
def gather_context_node(state: AgentState) -> dict:
    """Gather context with priority: user_notes > LLM > web search"""
    topic = state["topic"]
    user_notes = state.get("user_notes")
    retry_count = state.get("retry_count", 0)
    
    # Only use user notes on first attempt (don't retry with user notes)
    if retry_count > 0:
        user_notes = None
    
    context = gather_context(topic, user_notes)
    
    # Determine source
    if user_notes and context == user_notes:
        source = "user_notes"
    elif "search" in str(context).lower() or "Tavily" in str(context):
        source = "web_search"
    else:
        source = "llm"
    
    return {
        "context": context,
        "source": source,
        "retry_count": retry_count  # Keep retry count
    }


# --------------------------------------------------
# Node: Validate Context
# --------------------------------------------------
def validate_context(state: AgentState) -> dict:
    """
    Validate context relevance based on checkpoint objectives.
    Returns a relevance score (0-1) based on how well context matches objectives.
    """
    context = state.get("context", "")
    objectives = state.get("objectives", [])
    
    if not context:
        return {
            "relevance_score": 0.0,
            "validation_passed": False
        }
    
    word_count = len(context.split())
    context_lower = context.lower()
    
    # Check how many objectives are mentioned in the context
    objectives_hit = sum(
        1 for obj in objectives 
        if obj.lower() in context_lower
    )
    
    # Calculate relevance score (0-1 scale)
    # Factor 1: Objectives coverage (50% weight)
    objectives_coverage = objectives_hit / len(objectives) if objectives else 0.0
    
    # Factor 2: Content sufficiency (30% weight)
    # Minimum 200 words for good content, max at 800 words
    content_sufficiency = min(1.0, word_count / 800) if word_count > 200 else (word_count / 200) * 0.5
    
    # Factor 3: Quality keywords (20% weight)
    # Check for educational/learning keywords
    quality_keywords = ["explain", "example", "concept", "definition", "how", "why", "understand"]
    keyword_presence = sum(1 for kw in quality_keywords if kw in context_lower) / len(quality_keywords)
    
    relevance_score = (
        objectives_coverage * 0.5 +
        content_sufficiency * 0.3 +
        keyword_presence * 0.2
    )
    
    # Validation passes if relevance >= 0.6 and word_count > 200
    validation_passed = relevance_score >= 0.6 and word_count > 200
    
    return {
        "relevance_score": relevance_score,
        "validation_passed": validation_passed
    }


# --------------------------------------------------
# Conditional Retry Logic
# --------------------------------------------------
def should_retry(state: AgentState) -> str:
    """
    Determine if we should retry context gathering.
    Returns: "retry" or "end"
    """
    MAX_RETRIES = 2

    retry_count = state.get("retry_count", 0)
    validation_passed = state.get("validation_passed", False)
    
    # Only retry if validation failed and we haven't exceeded max retries
    if not validation_passed and retry_count < MAX_RETRIES:
        return "retry"
    return "end"


# --------------------------------------------------
# Retry Increment Node (increments retry count before retry)
# --------------------------------------------------
def increment_retry_node(state: AgentState) -> dict:
    """Increment retry count before retrying context gathering."""
    retry_count = state.get("retry_count", 0)
    return {
        "retry_count": retry_count + 1
    }


# --------------------------------------------------
# Build LangGraph
# --------------------------------------------------
graph = StateGraph(AgentState)

graph.add_node("gather_context", gather_context_node)
graph.add_node("validate_context", validate_context)
graph.add_node("increment_retry", increment_retry_node)

graph.set_entry_point("gather_context")

graph.add_edge("gather_context", "validate_context")

# After incrementing retry, go back to gather_context
graph.add_edge("increment_retry", "gather_context")


# --------------------------------------------------
# Milestone 2 Nodes
# --------------------------------------------------

def process_context_node(state: AgentState) -> dict:
    """
    Process context: chunk, embed, and store in vector store.
    """
    context = state.get("context")
    if not context:
        return {
            "vector_store": None,
            "processed_chunks": []
        }
    
    processor = get_context_processor()
    topic = state.get("topic", "")
    objectives = state.get("objectives", [])
    
    metadata = {
        "topic": topic,
        "objectives": ", ".join(objectives),
        "cp_id": state.get("cp_id", "")
    }
    
    try:
        vector_store = processor.process_context(context, metadata)
        chunks = processor.get_all_chunks()
        
        return {
            "vector_store": vector_store,
            "processed_chunks": [chunk.page_content for chunk in chunks]
        }
    except Exception as e:
        print(f"[WARN] Context processing failed: {e}")
        return {
            "vector_store": None,
            "processed_chunks": []
        }


def generate_questions_node(state: AgentState) -> dict:
    """
    Generate 11+ multiple-choice questions (with 4 options each) based on processed context.
    """
    context = state.get("context")
    topic = state.get("topic", "")
    objectives = state.get("objectives", [])
    
    if not context:
        return {"questions": []}
    
    try:
        # Generate 11+ questions (minimum 11, more than 10 as per requirements)
        questions = generate_questions(topic, objectives, context, num_questions=11)
        return {"questions": questions}
    except Exception as e:
        print(f"[WARN] Question generation failed: {e}")
        return {"questions": []}


def verify_understanding_node(state: AgentState) -> dict:
    """
    Verify learner understanding by evaluating answers.
    For now, simulates learner answers; in production, would accept user input.
    """
    questions = state.get("questions", [])
    context = state.get("context", "")
    
    if not questions or not context:
        return {
            "verification_score": 0.0,
            "verification_passed": False,
            "learner_answers": [],
            "question_evaluations": []
        }
    
    # Interactive Mode: Ask User
    if state.get("interactive_mode"):
        topic = state.get("topic", "Unknown Topic")
        print(f"\n   [INTERACTIVE QUIZ] {topic}")
        print(f"   Please answer {len(questions)} questions.")
        
        learner_answers = []
        for i, q in enumerate(questions, 1):
            print(f"\n   Q{i}: {q.get('question')}")
            options = q.get('options', {})
            for key in sorted(options.keys()):
                 print(f"      {key}) {options[key]}")
            
            while True:
                user_input = input(f"   Your Answer (A/B/C/D): ").strip().upper()
                if user_input in ['A', 'B', 'C', 'D']:
                    learner_answers.append(user_input)
                    break
                print("   Invalid input. Please enter A, B, C, or D.")
    else:
        # Simulate learner answers (for batch/demo mode)
        try:
            learner_answers = simulate_learner_answers(questions, context, quality="medium")
        except Exception as e:
            print(f"[WARN] Simulation failed: {e}")
            learner_answers = ["A"] * len(questions) # Fallback

    try:
        # Evaluate all answers
        evaluation_result = evaluate_all_answers(questions, learner_answers, context)
        
        return {
            "learner_answers": learner_answers,
            "verification_score": evaluation_result["overall_score"],
            "verification_passed": evaluation_result["passed"],
            "question_evaluations": evaluation_result["question_scores"]
        }
    except Exception as e:
        print(f"[WARN] Understanding verification failed: {e}")
        return {
            "verification_score": 0.0,
            "verification_passed": False,
            "learner_answers": [],
            "question_evaluations": []
        }


def feynman_placeholder_node(state: AgentState) -> dict:
    """
    Placeholder for Feynman technique node (to be implemented in future milestones).
    """
    print("[INFO] Feynman technique node called (placeholder)")
    return {}


# --------------------------------------------------
# Conditional Logic: Proceed or Halt
# --------------------------------------------------
def should_proceed(state: AgentState) -> str:
    """
    Determine if learning should proceed based on verification score.
    Returns: "proceed" if score >= 70%, "halt" if < 70%
    """
    verification_score = state.get("verification_score")
    verification_passed = state.get("verification_passed", False)
    
    if verification_passed and verification_score is not None and verification_score >= 70.0:
        return "proceed"
    else:
        return "halt"


# --------------------------------------------------
# Update Graph with Milestone 2 Nodes
# --------------------------------------------------
graph.add_node("process_context", process_context_node)
graph.add_node("generate_questions", generate_questions_node)
graph.add_node("verify_understanding", verify_understanding_node)
graph.add_node("feynman_placeholder", feynman_placeholder_node)

# Helper function for validation routing
def route_after_validation(state: AgentState) -> str:
    """Route after validation: process context if passed, otherwise retry or end."""
    if state.get("validation_passed"):
        return "process_context"
    else:
        return should_retry(state)

# Update flow: After validation passes, process context
graph.add_conditional_edges(
    "validate_context",
    route_after_validation,
    {
        "process_context": "process_context",
        "retry": "increment_retry",
        "end": "__end__"
    }
)

# After processing context, generate questions
graph.add_edge("process_context", "generate_questions")

# After generating questions, verify understanding
graph.add_edge("generate_questions", "verify_understanding")

# After verification, decide to proceed or halt
graph.add_conditional_edges(
    "verify_understanding",
    should_proceed,
    {
        "proceed": "__end__",  # In future: link to next milestone
        "halt": "feynman_placeholder"  # Placeholder for Feynman technique
    }
)

# After Feynman placeholder, end (or loop back in future)
graph.add_edge("feynman_placeholder", "__end__")

learning_graph = graph.compile()
