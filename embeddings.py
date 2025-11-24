"""
Embedding and Vector Storage Module

This script creates vector embeddings for text chunks and stores them.

Key concepts:
- Embeddings = vectors (arrays of numbers) that represent semantic meaning
- Similar meaning = close vectors (measured by cosine similarity)
- We use sentence-transformers (open source) instead of OpenAI to keep it free
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from typing import List, Dict, Tuple
import os


class EmbeddingStore:
    """
    Stores text chunks and their vector embeddings.
    
    This is a simple vector database implemented with numpy arrays.
    Production systems use FAISS, Pinecone, or ChromaDB, but this shows
    the fundamentals: it's just arrays of floats and cosine similarity.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize with a sentence transformer model.
        
        all-MiniLM-L6-v2 is a good default:
        - Small (80MB)
        - Fast
        - 384 dimensions
        - Good for semantic similarity
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.chunks = []
        self.embeddings = None
        
    def add_chunks(self, chunks: List[Dict[str, str]]):
        """
        Add text chunks and create their embeddings.
        
        This is where the magic happens: text → vectors
        """
        self.chunks = chunks
        texts = [chunk['text'] for chunk in chunks]
        
        print(f"Creating embeddings for {len(texts)} chunks...")
        # This line does the core work: text → 384-dimensional vectors
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"Created embeddings with shape: {self.embeddings.shape}")
        
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Search for chunks most similar to the query.
        
        This is the retrieval part of RAG:
        1. Embed the query (text → vector)
        2. Calculate cosine similarity between query vector and all chunk vectors
        3. Return top K most similar chunks
        """
        if self.embeddings is None:
            raise ValueError("No embeddings found. Call add_chunks first.")
        
        # Step 1: Embed the query
        query_embedding = self.model.encode([query])
        
        # Step 2: Calculate cosine similarity
        # This measures how "close" the query vector is to each chunk vector
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Step 3: Get top K indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return chunks with their similarity scores
        results = []
        for idx in top_indices:
            results.append((self.chunks[idx], similarities[idx]))
        
        return results
    
    def save(self, filepath: str):
        """Save the embedding store to disk."""
        data = {
            'chunks': self.chunks,
            'embeddings': self.embeddings
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        print(f"Saved embedding store to {filepath}")
    
    def load(self, filepath: str):
        """Load the embedding store from disk."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        self.chunks = data['chunks']
        self.embeddings = data['embeddings']
        print(f"Loaded embedding store from {filepath}")
        print(f"  → {len(self.chunks)} chunks")
        print(f"  → Embeddings shape: {self.embeddings.shape}")


if __name__ == "__main__":
    # Test the embedding store
    from pdf_processor import process_pdfs
    
    # Process PDFs
    print("Step 1: Processing PDFs...")
    chunks = process_pdfs("/mnt/project")
    
    # Create embeddings
    print("\nStep 2: Creating embeddings...")
    store = EmbeddingStore()
    store.add_chunks(chunks)
    
    # Save to disk
    print("\nStep 3: Saving to disk...")
    store.save("embedding_store.pkl")
    
    # Test search
    print("\nStep 4: Testing search...")
    query = "What are embeddings?"
    results = store.search(query, top_k=3)
    
    print(f"\nQuery: '{query}'")
    print("\nTop 3 results:")
    for i, (chunk, score) in enumerate(results, 1):
        print(f"\n{i}. Similarity: {score:.3f}")
        print(f"   Source: {chunk['source']}")
        print(f"   Text: {chunk['text'][:200]}...")