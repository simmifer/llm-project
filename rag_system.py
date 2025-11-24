"""
RAG (Retrieval Augmented Generation) System

This combines:
1. Retrieval: Use embeddings to find relevant chunks
2. Generation: Send chunks to LLM to synthesize an answer

This is exactly how Perplexity, ChatGPT Search, and Claude with web search work.
"""

import anthropic
import os
from typing import List, Dict, Tuple
from embeddings import EmbeddingStore


class RAGSystem:
    """
    Complete RAG pipeline: query → retrieve → generate
    """
    
    def __init__(self, embedding_store: EmbeddingStore, api_key: str = None):
        """
        Initialize with an embedding store and Claude API key.
        
        Note: For this demo, we're using Claude, but you could use
        OpenAI, Llama, or any other LLM.
        """
        self.store = embedding_store
        self.client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Step 1: Retrieve relevant chunks using embeddings.
        
        This is pure vector similarity - no LLM involved yet.
        """
        return self.store.search(query, top_k=top_k)
    
    def generate_answer(self, query: str, retrieved_chunks: List[Tuple[Dict, float]]) -> Dict:
        """
        Step 2: Generate answer using LLM with retrieved context.
        
        This is where the LLM synthesizes information from multiple sources.
        """
        # Build context from retrieved chunks
        context = ""
        sources = []
        
        for i, (chunk, score) in enumerate(retrieved_chunks, 1):
            context += f"\n[Source {i}: {chunk['source']}, similarity={score:.3f}]\n"
            context += chunk['text'] + "\n"
            sources.append({
                'source': chunk['source'],
                'chunk_id': chunk['chunk_id'],
                'similarity': float(score),
                'text': chunk['text'][:200] + "..."  # Preview
            })
        
        # Create prompt for Claude
        prompt = f"""You are a helpful AI assistant answering questions about machine learning concepts based on research papers and articles.

Here are the most relevant excerpts from the documents:

{context}

Based on these excerpts, please answer the following question. Be specific and cite which sources support your answer.

Question: {query}

Answer:"""
        
        # Call Claude API
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        answer = message.content[0].text
        
        return {
            'query': query,
            'answer': answer,
            'sources': sources,
            'retrieved_count': len(retrieved_chunks)
        }
    
    def ask(self, query: str, top_k: int = 5) -> Dict:
        """
        Complete RAG pipeline: query → retrieve → generate
        
        This is the main interface for asking questions.
        """
        print(f"\nQuery: {query}")
        print("=" * 80)
        
        # Step 1: Retrieve
        print(f"Retrieving top {top_k} relevant chunks...")
        retrieved = self.retrieve(query, top_k=top_k)
        
        print(f"Found {len(retrieved)} chunks")
        print("\nTop sources:")
        for i, (chunk, score) in enumerate(retrieved[:3], 1):
            print(f"  {i}. {chunk['source']} (similarity: {score:.3f})")
        
        # Step 2: Generate
        print("\nGenerating answer with Claude...")
        result = self.generate_answer(query, retrieved)
        
        return result


if __name__ == "__main__":
    # Test the RAG system
    print("Loading embedding store...")
    store = EmbeddingStore()
    
    # Try to load existing store, or create new one
    if os.path.exists("embedding_store.pkl"):
        store.load("embedding_store.pkl")
    else:
        print("No embedding store found. Run embeddings.py first to create one.")
        exit(1)
    
    # Initialize RAG system
    rag = RAGSystem(store)
    
    # Test query
    query = "What are embeddings and why are they useful?"
    result = rag.ask(query, top_k=5)
    
    print("\n" + "=" * 80)
    print("ANSWER:")
    print("=" * 80)
    print(result['answer'])
    
    print("\n" + "=" * 80)
    print("SOURCES:")
    print("=" * 80)
    for i, source in enumerate(result['sources'], 1):
        print(f"\n{i}. {source['source']} (similarity: {source['similarity']:.3f})")
        print(f"   {source['text']}")