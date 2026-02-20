from dotenv import load_dotenv
from langchain_groq import ChatGroq
from tavily import TavilyClient
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ContextGatherer:
    """
    Handles gathering context from various sources (User Notes, LLM, Web Search).
    """

    def __init__(self):
        self._llm = None
        self._tavily = None

    @property
    def llm(self):
        """Lazy initialization of Groq LLM."""
        if self._llm is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment")
            self._llm = ChatGroq(
                model="llama-3.1-8b-instant",
                temperature=0,
                max_retries=2
            )
        return self._llm

    @property
    def tavily(self):
        """Lazy initialization of Tavily Client."""
        if self._tavily is None:
            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                raise ValueError("TAVILY_API_KEY not found in environment")
            self._tavily = TavilyClient(api_key=api_key)
        return self._tavily

    def is_context_good(self, text: str) -> bool:
        """
        Check if the context is of sufficient quality.
        - Non-empty
        - At least 50 words
        - Doesn't contain refusal phrases
        """
        if not text:
            return False
        
        words = text.split()
        if len(words) < 50:
            return False
            
        refusal_phrases = [
            "i cannot answer", "i'm sorry", "i am sorry", 
            "i cannot provide", "as an ai", "i don't have information"
        ]
        text_lower = text.lower()
        if any(phrase in text_lower for phrase in refusal_phrases):
             # Strict check: if it's ONLY a refusal, it's bad. 
             # But sometimes it says "As an AI... here is what I found".
             # So we check if the refusal is the dominant part or if the text is short.
             if len(words) < 100: 
                 return False
                 
        return True

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _get_llm_explanation(self, topic: str) -> Optional[str]:
        """Get explanation from LLM with retries."""
        try:
            prompt = (
                f"You are an expert tutor. Create a comprehensive, clear, and beginner-friendly explanation "
                f"of the topic: '{topic}'. \n"
                f"Structure: \n"
                f"1. Definition\n"
                f"2. Key Concepts\n"
                f"3. Real-world Examples\n"
                f"Do NOT include conversational filler like 'Here is an explanation'."
            )
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise # Retry will catch this

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _search_web(self, topic: str) -> Optional[str]:
        """Search web with retries."""
        try:
             search_result = self.tavily.search(
                query=topic,
                max_results=5,
                search_depth="advanced"
            )
             
             combined_text = "\n\n".join(
                f"Source: {item.get('title', 'Unknown')}\n{item.get('content', '')}"
                for item in search_result.get("results", [])
            )
             return combined_text
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            raise

    def gather_context(self, topic: str, user_notes: Optional[str] = None) -> str:
        """
        Main method to gather context.
        Priority:
        1. User notes (if valid)
        2. LLM Generation
        3. Web Search
        """
        logger.info(f"Gathering context for: {topic}")

        # 1. User Notes
        if user_notes and self.is_context_good(user_notes):
            logger.info("Using provided user notes.")
            return user_notes

        # 2. LLM Generation
        try:
            logger.info("Attempting LLM generation...")
            llm_text = self._get_llm_explanation(topic)
            if llm_text and self.is_context_good(llm_text):
                return llm_text
            logger.warning("LLM response was insufficient.")
        except Exception:
             logger.warning("All LLM retries failed.")

        # 3. Web Search
        try:
            logger.info("Fallback to Web Search...")
            web_text = self._search_web(topic)
            if web_text and self.is_context_good(web_text):
                return web_text
            logger.warning("Web search content was insufficient.")
        except Exception:
            logger.warning("All Web Search retries failed.")

        return f"No sufficient context could be gathered for topic: {topic}"

# Singleton instance for backwards compatibility if needed, 
# though creating a new instance is preferred.
_gatherer = ContextGatherer()

def gather_context(topic: str, user_notes: Optional[str] = None) -> str:
    """Wrapper function to maintain backward compatibility."""
    return _gatherer.gather_context(topic, user_notes)

def is_context_good(text: str) -> bool:
    """Wrapper function to maintain backward compatibility."""
    return _gatherer.is_context_good(text)

def get_llm():
    """Wrapper to expose LLM if needed elsewhere."""
    return _gatherer.llm
