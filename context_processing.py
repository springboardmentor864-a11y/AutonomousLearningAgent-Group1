"""
Context Processing Module for Milestone 2
Handles chunking, embedding, and vector store management.
"""

from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ContextProcessor:
    """Process context: chunk, embed, and store in vector store."""
    
    def __init__(self):
        # Lazy import for Splitter
        try:
             from langchain_text_splitters import RecursiveCharacterTextSplitter
             self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
            )
        except ImportError:
             logger.warning("RecursiveCharacterTextSplitter not found, using simple fallback.")
             self.text_splitter = self._get_fallback_splitter()

        # Real Embeddings using HuggingFace
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            logger.info("Initialized HuggingFaceEmbeddings (all-MiniLM-L6-v2)")
        except (ImportError, Exception) as e:
            logger.error(f"Failed to initialize HuggingFaceEmbeddings: {e}")
            logger.warning("Falling back to Mock Embeddings (NOT RECOMMENDED for production)")
            self.embeddings = self._get_mock_embeddings()

        self.vector_store: Optional[InMemoryVectorStore] = None

    def _get_fallback_splitter(self):
        class SimpleSplitter:
            def split_text(self, text):
                # Very naive splitting by character count
                return [text[i:i+1000] for i in range(0, len(text), 800)]
        return SimpleSplitter()
    
    def _get_mock_embeddings(self):
        """Fallback to mock embeddings if dependencies fail."""
        from langchain_core.embeddings import Embeddings
        import hashlib
        
        class MockEmbeddings(Embeddings):
            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                return [self.embed_query(t) for t in texts]
            
            def embed_query(self, text: str) -> List[float]:
                hash_obj = hashlib.sha256(text.encode())
                # Create deterministic vector of 384 dimensions
                hash_val = int(hash_obj.hexdigest(), 16)
                # Simple pseudo-random vector generation seeded by hash
                import random
                rng = random.Random(hash_val)
                return [rng.uniform(-1, 1) for _ in range(384)]
                
        return MockEmbeddings()

    def process_context(self, context: str, metadata: Optional[dict] = None) -> InMemoryVectorStore:
        """
        Process context: chunk, embed, and store in vector store.
        
        Args:
            context: The context text to process
            metadata: Optional metadata to attach to chunks
        
        Returns:
            InMemoryVectorStore with processed chunks
        """
        if not context:
            raise ValueError("Context cannot be empty")
        
        logger.info("Splitting text into chunks...")
        # Split context into chunks
        chunks = self.text_splitter.split_text(context)
        logger.info(f"Created {len(chunks)} chunks.")
        
        # Create documents with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            doc_metadata = (metadata or {}).copy()
            doc_metadata["chunk_index"] = i
            doc_metadata["total_chunks"] = len(chunks)
            documents.append(Document(page_content=chunk, metadata=doc_metadata))
        
        # Create vector store and add documents
        logger.info("Embedding documents and creating vector store...")
        self.vector_store = InMemoryVectorStore(embedding=self.embeddings)
        self.vector_store.add_documents(documents)
        
        return self.vector_store
    
    def search_relevant_chunks(self, query: str, k: int = 3) -> List[Document]:
        """
        Search for relevant chunks in the vector store.
        
        Args:
            query: Search query
            k: Number of results to return
        
        Returns:
            List of relevant documents
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call process_context first.")
        
        return self.vector_store.similarity_search(query, k=k)
    
    def get_all_chunks(self) -> List[Document]:
        """Get all chunks from the vector store."""
        if not self.vector_store:
            return []
        
        # Access internal store to get all documents
        # InMemoryVectorStore stores data in .store dictionary
        all_docs = []
        for doc_data in self.vector_store.store.values():
            all_docs.append(
                Document(
                    page_content=doc_data["text"],
                    metadata=doc_data.get("metadata", {})
                )
            )
        return sorted(all_docs, key=lambda x: x.metadata.get("chunk_index", 0))


# --------------------------------------------------
# Global instance
# --------------------------------------------------
_context_processor = None

def get_context_processor() -> ContextProcessor:
    """Get or create global context processor instance."""
    global _context_processor
    if _context_processor is None:
        _context_processor = ContextProcessor()
    return _context_processor
