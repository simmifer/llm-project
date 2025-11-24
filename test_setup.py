"""
Test Script - Verify Setup Without API Key

This tests the embedding and retrieval parts of the system
without needing Claude API access.
"""

import sys
import os

print("🧪 Testing ML Concept Explainer Setup")
print("=" * 60)

# Test 1: Dependencies
print("\n1. Testing dependencies...")
try:
    import PyPDF2
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    from sentence_transformers import SentenceTransformer
    print("   ✓ All dependencies installed")
except ImportError as e:
    print(f"   ✗ Missing dependency: {e}")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 2: PDF Processing
print("\n2. Testing PDF processing...")
try:
    from pdf_processor import process_pdfs
    
    # Check if PDFs exist
    pdf_dir = "/mnt/project"
    if not os.path.exists(pdf_dir):
        print(f"   ✗ PDF directory not found: {pdf_dir}")
        sys.exit(1)
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    print(f"   ✓ Found {len(pdf_files)} PDF files")
    
    # Test processing one PDF
    test_pdf = os.path.join(pdf_dir, pdf_files[0])
    from pdf_processor import extract_text_from_pdf, chunk_text
    text = extract_text_from_pdf(test_pdf)
    chunks = chunk_text(text, chunk_size=200)
    print(f"   ✓ Processed test PDF into {len(chunks)} chunks")
    
except Exception as e:
    print(f"   ✗ PDF processing failed: {e}")
    sys.exit(1)

# Test 3: Embeddings
print("\n3. Testing embedding model...")
try:
    from embeddings import EmbeddingStore
    
    store = EmbeddingStore()
    print("   ✓ Embedding model loaded successfully")
    
    # Test embedding creation
    test_texts = ["This is a test sentence.", "Another test sentence."]
    embeddings = store.model.encode(test_texts)
    print(f"   ✓ Created embeddings with shape: {embeddings.shape}")
    
    # Test similarity
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    print(f"   ✓ Cosine similarity calculation works: {similarity:.3f}")
    
except Exception as e:
    print(f"   ✗ Embedding test failed: {e}")
    sys.exit(1)

# Test 4: Check for existing embedding store
print("\n4. Checking for embedding store...")
if os.path.exists("embedding_store.pkl"):
    print("   ✓ Embedding store exists")
    try:
        store = EmbeddingStore()
        store.load("embedding_store.pkl")
        print(f"   ✓ Loaded {len(store.chunks)} chunks")
        
        # Test search
        results = store.search("What are embeddings?", top_k=3)
        print(f"   ✓ Search works, found {len(results)} results")
        print(f"\n   Sample result:")
        print(f"   Source: {results[0][0]['source']}")
        print(f"   Similarity: {results[0][1]:.3f}")
        print(f"   Text preview: {results[0][0]['text'][:100]}...")
        
    except Exception as e:
        print(f"   ⚠️  Embedding store exists but failed to load: {e}")
else:
    print("   ⚠️  Embedding store not found")
    print("   Run: python embeddings.py (this will take ~2 minutes)")

# Test 5: Claude API (optional)
print("\n5. Checking Claude API setup...")
api_key = os.environ.get("ANTHROPIC_API_KEY")
if api_key and api_key != "your_api_key_here":
    print("   ✓ API key found in environment")
    print("   (Not testing API call to avoid charges)")
else:
    print("   ⚠️  No API key found")
    print("   Set ANTHROPIC_API_KEY environment variable")
    print("   Or create .env file with your key")
    print("   (This is only needed for the full RAG system)")

# Summary
print("\n" + "=" * 60)
print("Test Summary:")
print("=" * 60)

if os.path.exists("embedding_store.pkl"):
    print("✅ System is ready to use!")
    print("\nNext steps:")
    print("  - To use web UI: streamlit run app.py")
    print("  - To test RAG: python rag_system.py")
else:
    print("⚠️  Almost ready!")
    print("\nNext step:")
    print("  - Run: python embeddings.py")
    print("  - This will process PDFs and create embeddings (~2 minutes)")
    print("\nThen:")
    print("  - To use web UI: streamlit run app.py")
    print("  - To test RAG: python rag_system.py")

print("\n📚 See QUICKSTART.md for detailed instructions")
print("=" * 60)