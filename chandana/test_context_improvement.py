
import os
import time
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

def test_context_processing():
    print("\n--- Testing Context Processing ---")
    try:
        from context_processing import get_context_processor
        processor = get_context_processor()
        
        text = (
            "Artificial Intelligence (AI) is intelligence demonstrated by machines. "
            "Machine Learning (ML) is a subset of AI. "
            "Deep Learning (DL) is a subset of ML."
        )
        
        print(f"Processing text: {text}")
        vector_store = processor.process_context(text)
        print("Context processed successfully.")
        
        query = "What is Machine Learning?"
        results = processor.search_relevant_chunks(query, k=1)
        
        if results:
            print(f"Search result for '{query}':")
            print(f"- {results[0].page_content}")
            print(f"- Metadata: {results[0].metadata}")
        else:
            print("No results found.")
            
    except ImportError as e:
        print(f"ImportError: {e} - Dependencies might not be installed yet.")
    except Exception as e:
        print(f"Error in context processing: {e}")

def test_context_gathering():
    print("\n--- Testing Context Gathering ---")
    try:
        from context_gathering import gather_context, is_context_good
        
        # Test is_context_good
        assert is_context_good("short") == False
        assert is_context_good("This is " * 50) == True
        print("is_context_good passed checks.")

        topic = "What is a neural network?"
        if os.getenv("GROQ_API_KEY"):
            print(f"Gathering context for: {topic}")
            # This might fail if no internet or invalid key, but we'll try
            context = gather_context(topic)
            print(f"Gathered Context Length: {len(context)}")
            print(f"Snippet: {context[:200]}...")
        else:
            print("Skipping LLM/Web gathered test (GROQ_API_KEY missing)")

    except ImportError as e:
        print(f"ImportError: {e} - Dependencies might not be installed yet.")
    except Exception as e:
        print(f"Error in context gathering: {e}")

if __name__ == "__main__":
    test_context_processing()
    test_context_gathering()
