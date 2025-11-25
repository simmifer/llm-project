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
from rate_limiter import RateLimiter, render_admin_panel, render_rate_limit_info


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
            
            # Get API key from Streamlit secrets (cloud) or environment (local)
            api_key = None
            try:
                api_key = st.secrets["ANTHROPIC_API_KEY"]
            except:
                api_key = os.environ.get("ANTHROPIC_API_KEY")
            
            st.session_state.rag_system = RAGSystem(store, api_key=api_key)
            st.session_state.ready = True
        else:
            st.session_state.ready = False
            st.error("Embedding store not found. Run `python embeddings.py` first.")

# Initialize rate limiter
if 'rate_limiter' not in st.session_state:
    # Get config from secrets with defaults
    try:
        max_queries = st.secrets.get("MAX_QUERIES_PER_SESSION", 5)
        max_input_length = st.secrets.get("MAX_INPUT_LENGTH", 500)
    except:
        max_queries = 5
        max_input_length = 500
    
    st.session_state.rate_limiter = RateLimiter(
        max_queries=max_queries,
        max_input_length=max_input_length
    )

if st.session_state.ready:
    rate_limiter = st.session_state.rate_limiter
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        top_k = st.slider("Number of chunks to retrieve", min_value=3, max_value=10, value=3)
        
        st.markdown("---")
        st.markdown("""
        ### Example Questions
        - What are embeddings?
        - How does RAG work?
        - When should I use fine-tuning vs RAG?
        - What is cosine similarity?
        - How do vector databases work?
        """)
        
        # Admin panel
        try:
            admin_password_hash = st.secrets.get("ADMIN_PASSWORD_HASH", "")
            if admin_password_hash:
                render_admin_panel(rate_limiter, admin_password_hash)
        except:
            pass  # No admin password configured
    
    # Show rate limit info
    render_rate_limit_info(rate_limiter)
    
    # Main content
    query = st.text_input(
        "Ask a question:", 
        placeholder="What are embeddings and why are they useful?",
        max_chars=rate_limiter.max_input_length
    )
    
    if st.button("Ask", type="primary") or (query and len(query) > 0):
        if query:
            # Check rate limit
            can_query, limit_msg = rate_limiter.can_query()
            
            if not can_query:
                st.error(f"🚫 {limit_msg}")
                st.info("💡 **Tip:** Refresh the page to start a new session with 5 more queries.")
            else:
                # Check input length
                valid_length, length_msg = rate_limiter.check_input_length(query)
                
                if not valid_length:
                    st.error(f"⚠️ {length_msg}")
                    st.info("Please shorten your question and try again.")
                else:
                    # Process query
                    with st.spinner("Searching and generating answer..."):
                        result = st.session_state.rag_system.ask(query, top_k=top_k)
                    
                    # Increment query count AFTER successful query
                    rate_limiter.increment_count()
                    
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