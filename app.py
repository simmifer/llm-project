"""
Streamlit UI for ML Concept Explainer

A simple web interface for the RAG system.
Run with: streamlit run app.py
"""

import streamlit as st
import os
from embeddings import EmbeddingStore
from rag_system import RAGSystem


# Page config
st.set_page_config(
    page_title="ML Concept Explainer",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("🤖 ML Concept Explainer")
st.markdown("""
Ask questions about machine learning concepts and get answers based on research papers and articles.

**How it works:**
1. Your question gets embedded into a vector
2. System finds most similar paper sections using cosine similarity
3. Claude synthesizes an answer from those sections
""")

# Initialize session state
if 'rag_system' not in st.session_state:
    with st.spinner("Loading embedding store..."):
        if os.path.exists("embedding_store.pkl"):
            store = EmbeddingStore()
            store.load("embedding_store.pkl")
            st.session_state.rag_system = RAGSystem(store)
            st.session_state.ready = True
        else:
            st.session_state.ready = False
            st.error("Embedding store not found. Run `python embeddings.py` first.")

if st.session_state.ready:
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        top_k = st.slider("Number of chunks to retrieve", min_value=3, max_value=10, value=5)
        
        st.markdown("---")
        st.markdown("""
        ### Example Questions
        - What are embeddings?
        - How does RAG work?
        - When should I use fine-tuning vs RAG?
        - What is cosine similarity?
        - How do vector databases work?
        """)
    
    # Main content
    query = st.text_input("Ask a question:", placeholder="What are embeddings and why are they useful?")
    
    if st.button("Ask", type="primary") or (query and len(query) > 0):
        if query:
            with st.spinner("Searching and generating answer..."):
                result = st.session_state.rag_system.ask(query, top_k=top_k)
            
            # Display answer
            st.markdown("## Answer")
            st.markdown(result['answer'])
            
            # Display sources
            st.markdown("---")
            st.markdown("## Sources")
            st.caption(f"Retrieved {result['retrieved_count']} relevant chunks")
            
            for i, source in enumerate(result['sources'], 1):
                with st.expander(f"📄 {source['source']} (similarity: {source['similarity']:.3f})"):
                    st.text(source['text'])
        else:
            st.warning("Please enter a question.")
    
    # History
    if 'history' not in st.session_state:
        st.session_state.history = []