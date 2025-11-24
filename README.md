# ML Concept Explainer: A RAG System for Learning

## Why I Built This

I built this after realizing that tools like Perplexity, ChatGPT Search, and Claude with web search all work using the same architecture:

1. **Embed the query** - Convert user's question into a vector
2. **Retrieve relevant content** - Use cosine similarity to find similar content in a vector database
3. **Generate answer** - Send retrieved chunks to an LLM to synthesize a response

I wanted to understand this pipeline deeply, so I built my own version focused on ML research papers.

## What This Does

Ask questions about machine learning concepts (embeddings, RAG, fine-tuning, etc.) and get answers synthesized from 6 research papers and articles, with citations.

**Example questions:**
- What are embeddings and why are they useful?
- How does RAG work?
- When should I use fine-tuning vs RAG?
- What is cosine similarity?

## The Architecture

### 1. PDF Processing (`pdf_processor.py`)

**Problem**: PDFs are long documents, but embeddings work best on paragraph-sized chunks.

**Solution**: 
- Extract text from each PDF
- Split into ~200 word chunks with 50 word overlap
- Overlap ensures we don't lose context at chunk boundaries

**Result**: Instead of 6 vectors (one per PDF), we have ~50-200 vectors (one per section), enabling fine-grained retrieval.

### 2. Embeddings (`embeddings.py`)

**What are embeddings?**
Embeddings are vectors (arrays of numbers) that represent semantic meaning. Similar concepts have similar vectors, which we measure using cosine similarity.

**Implementation**:
- Used `sentence-transformers` (open source, free)
- Model: `all-MiniLM-L6-v2` (384 dimensions, 80MB, fast)
- Each text chunk → 384-dimensional vector
- Stored as numpy arrays (pickled to disk)

**Why this model?**
- Small and fast (important for demos)
- Good semantic similarity performance
- No API costs (runs locally)

**Alternative models I considered**:
- OpenAI embeddings (better quality, but costs $)
- Larger sentence-transformers (better quality, slower)
- For production: would benchmark several models

### 3. Vector Storage

**The "vector database" is just**:
- A numpy array of embeddings
- A list of text chunks with metadata
- Pickled to disk for persistence

**Why not FAISS/Pinecone/ChromaDB?**
For learning, implementing from scratch shows I understand the fundamentals. Production systems would use:
- **FAISS**: Fast similarity search (billions of vectors)
- **Pinecone/ChromaDB**: Managed vector databases with filtering, metadata, etc.

### 4. RAG System (`rag_system.py`)

**The complete pipeline:**

```
User Query
    ↓
[1] Embed query → 384-dim vector
    ↓
[2] Cosine similarity search → top 5 chunks
    ↓
[3] Send chunks + query to Claude API
    ↓
[4] Claude synthesizes answer with citations
    ↓
Answer + Sources returned
```

**Key insight**: This is exactly how Perplexity works. They have a much larger corpus and better infrastructure, but the core algorithm is the same.

### 5. UI (`app.py`)

Simple Streamlit interface:
- Text input for questions
- Display answer with source citations
- Show similarity scores for transparency

## Design Decisions

### Why embeddings for retrieval?

**Compared to keyword search:**
- Keyword: Matches exact words (brittle)
- Embeddings: Matches semantic meaning (robust)

Example: Query "What are vector representations?" would match:
- ❌ Keyword search: Might miss papers that say "embeddings" instead of "vector representations"
- ✅ Embedding search: Finds semantically similar concepts regardless of exact wording

**When embeddings fail:**
- Multi-hop reasoning (need to connect info across many documents)
- Very specific technical queries (embeddings are semantic, not precise)
- Domain-specific jargon that wasn't in training data

### Why LLM for synthesis?

Retrieval alone just gives you relevant chunks. The LLM:
- Synthesizes information across multiple sources
- Explains concepts in natural language
- Provides citations
- Adapts tone/detail to the question

### Why RAG vs Fine-tuning?

**Use RAG when:**
- Your knowledge base changes frequently (just re-embed new docs)
- You want citations and transparency
- You don't have enough data to fine-tune (thousands of examples needed)
- You want to control what knowledge the model uses

**Use Fine-tuning when:**
- You need the model to learn new behaviors/styles (not just knowledge)
- You have thousands of training examples
- Latency matters (no retrieval step)
- You want knowledge "baked in" to the model

**For this use case**: RAG is perfect because:
- Small corpus (6 papers)
- Papers might change/expand
- Need citations
- Fine-tuning on 6 papers wouldn't work anyway

### Why Claude vs other LLMs?

- Long context window (200K tokens)
- Good at following instructions for citations
- API is simple to use

Could easily swap for OpenAI, Llama, etc.

## When RAG Breaks Down

Understanding limitations shows engineering maturity:

1. **Not enough context**: If answer requires reasoning across 20+ papers, but we only retrieve 10 chunks, LLM might miss key info
   - Solution: Retrieve more chunks (but watch token limits)
   - Better solution: Hierarchical retrieval or query decomposition

2. **Wrong retrieval**: Semantic similarity doesn't always match what you need
   - Example: "transformer architecture" might retrieve papers about electrical transformers if corpus is mixed
   - Solution: Better corpus curation, hybrid search (keyword + semantic)

3. **Hallucination despite sources**: LLM might still make stuff up even with good sources
   - Solution: Prompt engineering, temperature tuning, citation requirements

4. **Needs reasoning beyond retrieval**: Math proofs, novel synthesis, "what if" scenarios
   - RAG retrieves existing knowledge; it doesn't create new insights
   - Solution: Use RAG for facts, rely on LLM's reasoning for synthesis

## What I Learned

**Surprising findings:**
- Chunk size matters more than I expected (100-300 words is sweet spot)
- Overlap is crucial - without it, sentences get cut mid-thought
- Top 5 chunks usually sufficient; top 10 adds more noise than signal
- Similarity scores above 0.3 are usually relevant; below 0.2 are noise

**If I were to improve this:**
- Add keyword search alongside embeddings (hybrid search)
- Implement re-ranking (retrieve 20, re-rank to top 5)
- Add query expansion ("embeddings" → also search "vector representations")
- Cache embeddings for common queries
- Add evaluation metrics (how often are answers correct?)

## How to Run

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set Claude API key
export ANTHROPIC_API_KEY="your-key-here"
```

### Build the embedding store
```bash
# This processes PDFs and creates embeddings (~2 minutes)
python embeddings.py
```

### Run the web UI
```bash
# Launch Streamlit app
streamlit run app.py
```

### Or use command line
```bash
# Test the RAG system directly
python rag_system.py
```

## Project Structure

```
ml-concept-explainer/
├── pdf_processor.py      # Extract and chunk PDFs
├── embeddings.py         # Create and store embeddings
├── rag_system.py         # RAG pipeline (retrieve + generate)
├── app.py                # Streamlit UI
├── requirements.txt      # Dependencies
├── README.md             # This file
└── embedding_store.pkl   # Cached embeddings (generated)
```

## Technical Stack

- **PDF extraction**: PyPDF2
- **Embeddings**: sentence-transformers (HuggingFace)
- **Vector ops**: numpy + scikit-learn
- **LLM**: Claude 4 Sonnet via Anthropic API
- **UI**: Streamlit
- **Storage**: Pickle (simple & effective for demos)

## Next Steps

**To expand this project:**
1. Add more papers (ArXiv has APIs for downloading papers)
2. Implement FAISS for faster search (important at scale)
3. Add evaluation: compare answers to ground truth
4. Try different embedding models and benchmark
5. Add chat history (multi-turn conversations)
6. Deploy to web (Streamlit Cloud, Heroku, etc.)

**To demonstrate deeper understanding:**
- Implement dimensionality reduction (PCA on embeddings)
- Add BM25 keyword search alongside embeddings
- Implement re-ranking with cross-encoders
- Add query decomposition for complex questions
- Build evaluation metrics (precision@k, NDCG)

## Connection to My Work

This project directly relates to problems I've solved in production:
- **LLM API optimization**: Understanding embeddings helps optimize prompt construction
- **Feature engineering**: Semantic similarity is useful for recommendation engines
- **Cost management**: Local embeddings vs API calls is a cost/quality tradeoff

The key insight from building this: **RAG is not magic**. It's just:
1. Vectors representing meaning
2. Distance calculations
3. Prompt augmentation

Understanding these pieces makes it possible to debug, optimize, and improve RAG systems in production.

---

**Built with curiosity 🤖**
