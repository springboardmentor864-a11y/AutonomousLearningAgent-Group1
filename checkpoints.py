from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

# --------------------------------------------------
# Graceful imports
# --------------------------------------------------
try:
    from context_gathering import gather_context
    CONTEXT_AVAILABLE = True
except ImportError:
    CONTEXT_AVAILABLE = False
    def gather_context(topic: str, user_notes: Optional[str] = None) -> str:
        return f"[Fallback] Context gathering unavailable for topic: {topic}"

try:
    from graph import learning_graph
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False
    learning_graph = None


# --------------------------------------------------
# Checkpoint Dataclass
# --------------------------------------------------
@dataclass
class Checkpoint:
    checkpoint_id: str
    topic: str
    objectives: List[str]
    success_criteria: List[str]
    context: Optional[str] = None
    status: str = "not_started"
    relevance_score: Optional[float] = None
    attempts: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def gather_learning_context(self, user_notes: Optional[str] = None):
        """Gather learning context, optionally using LangGraph workflow."""
        self.status = "in_progress"
        self.attempts += 1
        
        # Option 1: Use LangGraph workflow if available
        if GRAPH_AVAILABLE and learning_graph is not None:
            from graph import AgentState
            
            # Prepare state for LangGraph
            initial_state: AgentState = {
                "cp_id": self.checkpoint_id,  # Using cp_id to avoid reserved name
                "topic": self.topic,
                "objectives": self.objectives,
                "success_criteria": self.success_criteria,
                "user_notes": user_notes,
                "context": None,
                "relevance_score": None,
                "manual_relevance_score": None,
                "source": None,
                "retry_count": 0,
                "validation_passed": False
            }
            
            # Run the graph workflow
            result = learning_graph.invoke(initial_state)
            
            self.context = result.get("context")
            self.relevance_score = result.get("relevance_score")
            return self.context
        
        # Option 2: Direct context gathering
        if CONTEXT_AVAILABLE:
            self.context = gather_context(self.topic, user_notes)
        else:
            self.context = gather_context(self.topic, user_notes)
        return self.context

    def evaluate_completion(self) -> dict:
        if not self.context:
            return {"completed": False, "message": "No context available"}

        word_count = len(self.context.split())
        objectives_hit = sum(
            1 for obj in self.objectives if obj.lower() in self.context.lower()
        )

        self.relevance_score = min(
            1.0,
            (word_count / 800) * 0.5 + (objectives_hit / len(self.objectives)) * 0.5
        )

        completed = self.relevance_score >= 0.6 and word_count > 200

        if completed:
            self.status = "completed"
            self.completed_at = datetime.now()

        return {
            "completed": completed,
            "relevance_score": self.relevance_score,
            "word_count": word_count,
            "objectives_hit": objectives_hit
        }

    def __str__(self):
        return f"[{self.status.upper()}] {self.checkpoint_id} → {self.topic}"


# --------------------------------------------------
# CHECKPOINT FACTORY FUNCTIONS (MULTIPLE TOPICS)
# --------------------------------------------------

def python_basics():
    return Checkpoint(
        "CP-PY-01",
        "Python Basics",
        ["Variables", "Data types", "Control flow"],
        ["Write basic Python programs"]
    )

def data_structures():
    return Checkpoint(
        "CP-DS-01",
        "Data Structures",
        ["Arrays", "Linked Lists", "Stacks", "Queues"],
        ["Choose appropriate data structures"]
    )

def algorithms():
    return Checkpoint(
        "CP-ALGO-01",
        "Algorithms",
        ["Sorting", "Searching", "Time Complexity"],
        ["Analyze algorithm efficiency"]
    )

def machine_learning():
    return Checkpoint(
        "CP-ML-01",
        "Machine Learning Basics",
        ["Supervised learning", "Unsupervised learning", "Model training"],
        ["Explain ML workflow"]
    )

def artificial_intelligence():
    return Checkpoint(
        "CP-AI-01",
        "Artificial Intelligence",
        ["Search algorithms", "Knowledge representation", "Reasoning"],
        ["Explain AI problem-solving methods"]
    )

def natural_language_processing():
    return Checkpoint(
        "CP-NLP-01",
        "Natural Language Processing",
        ["Tokenization", "Embeddings", "Text classification"],
        ["Process and analyze text data"]
    )

def databases():
    return Checkpoint(
        "CP-DB-01",
        "Databases",
        ["SQL queries", "Normalization", "Indexes"],
        ["Design basic database schemas"]
    )

def operating_systems():
    return Checkpoint(
        "CP-OS-01",
        "Operating Systems",
        ["Processes", "Threads", "Memory management"],
        ["Explain OS resource management"]
    )

def git_and_version_control():
    return Checkpoint(
        "CP-GIT-01",
        "Git & Version Control",
        ["Git commands", "Branches", "Merging"],
        ["Manage code using Git"]
    )

def software_engineering():
    return Checkpoint(
        "CP-SE-01",
        "Software Engineering",
        ["SDLC", "Design patterns", "Testing"],
        ["Build maintainable software"]
    )

def web_development():
    return Checkpoint(
        "CP-WEB-01",
        "Web Development",
        ["HTML", "CSS", "JavaScript", "HTTP protocols"],
        ["Build interactive web applications"]
    )

def cloud_computing():
    return Checkpoint(
        "CP-CLOUD-01",
        "Cloud Computing",
        ["AWS", "Azure", "GCP", "Virtualization"],
        ["Deploy applications on cloud platforms"]
    )

def docker_containers():
    return Checkpoint(
        "CP-DOCKER-01",
        "Docker & Containers",
        ["Containers", "Images", "Dockerfile", "Docker Compose"],
        ["Containerize applications using Docker"]
    )

def computer_networks():
    return Checkpoint(
        "CP-NET-01",
        "Computer Networks",
        ["TCP/IP", "OSI model", "Routers", "Switches"],
        ["Understand network architecture and protocols"]
    )

def cybersecurity():
    return Checkpoint(
        "CP-SEC-01",
        "Cybersecurity",
        ["Encryption", "Authentication", "Firewalls", "Vulnerabilities"],
        ["Implement security best practices"]
    )

def api_development():
    return Checkpoint(
        "CP-API-01",
        "API Development",
        ["REST", "JSON", "HTTP methods", "Authentication"],
        ["Design and implement RESTful APIs"]
    )

def react_frontend():
    return Checkpoint(
        "CP-REACT-01",
        "React Frontend Development",
        ["Components", "State management", "Hooks", "JSX"],
        ["Build modern frontend applications with React"]
    )

def deep_learning():
    return Checkpoint(
        "CP-DL-01",
        "Deep Learning",
        ["Neural networks", "Backpropagation", "CNNs", "RNNs"],
        ["Implement deep learning models"]
    )

def computer_vision():
    return Checkpoint(
        "CP-CV-01",
        "Computer Vision",
        ["Image processing", "Feature detection", "Object recognition", "CNN"],
        ["Process and analyze images using computer vision"]
    )

def distributed_systems():
    return Checkpoint(
        "CP-DIST-01",
        "Distributed Systems",
        ["Consistency", "CAP theorem", "Load balancing", "Replication"],
        ["Design distributed system architectures"]
    )

def microservices():
    return Checkpoint(
        "CP-MICRO-01",
        "Microservices Architecture",
        ["Service decomposition", "API Gateway", "Service discovery", "Communication"],
        ["Design and implement microservices-based systems"]
    )

def devops():
    return Checkpoint(
        "CP-DEVOPS-01",
        "DevOps",
        ["CI/CD", "Infrastructure as Code", "Monitoring", "Automation"],
        ["Implement DevOps practices and pipelines"]
    )

def data_science():
    return Checkpoint(
        "CP-DS-02",
        "Data Science",
        ["Data cleaning", "EDA", "Statistical analysis", "Data visualization"],
        ["Perform data analysis and generate insights"]
    )

def system_design():
    return Checkpoint(
        "CP-SD-01",
        "System Design",
        ["Scalability", "Reliability", "Caching", "Database design"],
        ["Design scalable and reliable systems"]
    )

def kubernetes():
    return Checkpoint(
        "CP-K8S-01",
        "Kubernetes",
        ["Pods", "Services", "Deployments", "Helm"],
        ["Orchestrate containerized applications with Kubernetes"]
    )


# --------------------------------------------------
# CHECKPOINT COLLECTION
# --------------------------------------------------
def get_all_checkpoints() -> List[Checkpoint]:
    return [
        # Original 10 checkpoints
        python_basics(),
        data_structures(),
        algorithms(),
        machine_learning(),
        artificial_intelligence(),
        natural_language_processing(),
        databases(),
        operating_systems(),
        git_and_version_control(),
        software_engineering(),
        # New 15 checkpoints
        web_development(),
        cloud_computing(),
        docker_containers(),
        computer_networks(),
        cybersecurity(),
        api_development(),
        react_frontend(),
        deep_learning(),
        computer_vision(),
        distributed_systems(),
        microservices(),
        devops(),
        data_science(),
        system_design(),
        kubernetes()
    ]


# --------------------------------------------------
# PROCESSING LOGIC
# --------------------------------------------------
def process_checkpoint(cp: Checkpoint):
    print(f"\n>> Processing: {cp.topic}")
    cp.gather_learning_context()

    evaluation = cp.evaluate_completion()
    print(f"   Status: {cp.status}")
    print(f"   Relevance Score: {cp.relevance_score}")
    print(f"   Message: {'Completed' if evaluation['completed'] else 'Needs improvement'}")


# --------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------
if __name__ == "__main__":
    print("=" * 70)
    print("AUTONOMOUS LEARNING CHECKPOINT SYSTEM")
    print("=" * 70)

    checkpoints = get_all_checkpoints()

    for checkpoint in checkpoints:
        process_checkpoint(checkpoint)

    print("\nAll checkpoints processed.")
    print("=" * 70)
