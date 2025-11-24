"""
PDF Extraction and Chunking Module

This script extracts text from PDFs and chunks them into smaller sections
for embedding. Chunking is necessary because:
1. Embeddings work best on 100-500 word chunks (paragraph-sized)
2. Smaller chunks = more precise retrieval
3. Instead of "which paper?" we get "which specific section?"
"""

import PyPDF2
import re
from typing import List, Dict
import os


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text


def clean_text(text: str) -> str:
    """Clean extracted text by removing excessive whitespace and special chars."""
    # Remove multiple newlines
    text = re.sub(r'\n+', '\n', text)
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-\']', ' ', text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks of approximately chunk_size words.
    
    Overlap ensures we don't lose context at chunk boundaries.
    Example: If chunk 1 ends mid-sentence, chunk 2 starts earlier to capture full context.
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if len(chunk.split()) > 20:  # Only keep chunks with at least 20 words
            chunks.append(chunk)
    
    return chunks


def process_pdfs(pdf_directory: str) -> List[Dict[str, str]]:
    """
    Process all PDFs in a directory and return chunked documents.
    
    Returns: List of dicts with 'source', 'chunk_id', and 'text' keys
    """
    all_chunks = []
    
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    
    print(f"Found {len(pdf_files)} PDF files")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_directory, pdf_file)
        print(f"Processing: {pdf_file}")
        
        # Extract and clean text
        raw_text = extract_text_from_pdf(pdf_path)
        clean = clean_text(raw_text)
        
        # Chunk the text
        chunks = chunk_text(clean, chunk_size=200, overlap=50)
        
        # Store with metadata
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                'source': pdf_file,
                'chunk_id': i,
                'text': chunk
            })
        
        print(f"  → Created {len(chunks)} chunks")
    
    print(f"\nTotal chunks: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    # Test with the project PDFs
    pdf_dir = "data"
    chunks = process_pdfs(pdf_dir)
    
    # Show a sample
    print("\nSample chunk:")
    print(f"Source: {chunks[0]['source']}")
    print(f"Text: {chunks[0]['text'][:200]}...")