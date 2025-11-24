#!/bin/bash

# ML Concept Explainer - Setup Script

echo "🤖 ML Concept Explainer Setup"
echo "=============================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 not found. Please install Python 3.8+"; exit 1; }
echo "✓ Python found"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check for API key
if [ -f .env ]; then
    echo "✓ .env file found"
else
    echo "⚠️  No .env file found"
    echo "   Copy .env.example to .env and add your ANTHROPIC_API_KEY"
    echo ""
    echo "   Get your API key at: https://console.anthropic.com/"
fi
echo ""

# Build embedding store
echo "Building embedding store..."
echo "This will process PDFs and create embeddings (~2 minutes)"
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then
    python3 embeddings.py
    echo ""
    echo "✓ Embedding store created"
else
    echo "Skipped. Run 'python3 embeddings.py' when ready."
fi
echo ""

echo "=============================="
echo "Setup complete! 🎉"
echo ""
echo "To run the app:"
echo "  streamlit run app.py"
echo ""
echo "To test the RAG system:"
echo "  python3 rag_system.py"
echo ""