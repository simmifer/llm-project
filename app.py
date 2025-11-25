"""
Streamlit UI for ML Concept Explainer

A simple web interface for the RAG system.
Run with: streamlit run app.py
"""

from dotenv import load_dotenv
load_dotenv()  # Load .env file

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

# Custom CSS for better styling
st.markdown("""
    <style>
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

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
            
            # Display token usage
            if 'tokens' in result:
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Input Tokens", f"{result['tokens']['input']:,}")
                with col2:
                    st.metric("Output Tokens", f"{result['tokens']['output']:,}")
                with col3:
                    # Calculate cost (approximate)
                    cost = (result['tokens']['input'] / 1_000_000 * 3.0) + (result['tokens']['output'] / 1_000_000 * 15.0)
                    st.metric("Cost", f"${cost:.4f}")
            
            # Display inline source badges
            st.markdown("---")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("### 📚 Sources Used")
                st.caption(f"Retrieved {result['retrieved_count']} relevant chunks • Click to expand")
            with col2:
                expand_all = st.checkbox("Expand all", value=False)
            
            # Create columns for source badges
            cols = st.columns(min(len(result['sources']), 3))
            
            # Display each source in an expandable card
            for i, source in enumerate(result['sources']):
                col_idx = i % 3
                with cols[col_idx]:
                    # Color-code by similarity score
                    if source['similarity'] > 0.4:
                        badge_color = "🟢"
                        badge_label = "High"
                    elif source['similarity'] > 0.3:
                        badge_color = "🟡"
                        badge_label = "Med"
                    else:
                        badge_color = "🟠"
                        badge_label = "Low"
                    
                    with st.expander(f"{badge_color} Source {i+1} • {badge_label} ({source['similarity']:.2f})", expanded=expand_all):
                        st.caption(f"**{source['source']}**")
                        st.caption(f"Chunk #{source['chunk_id']} • Similarity: {source['similarity']:.3f}")
                        st.markdown("---")
                        st.text(source['text'])
        else:
            st.warning("Please enter a question.")
    
    # History
    if 'history' not in st.session_state:
        st.session_state.history = []