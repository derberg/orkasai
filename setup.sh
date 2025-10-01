#!/bin/bash
# OrcasAI Setup Script
# This script sets up the virtual environment and installs dependencies

echo "🐋 Setting up OrcasAI Pod System..."
echo "=================================="

# Check if Python 3.12 is installed
if ! command -v /opt/homebrew/bin/python3.12 &> /dev/null; then
    echo "❌ Python 3.12 is not installed. Please install Python 3.12 via Homebrew."
    echo "   Run: brew install python@3.12"
    exit 1
fi

# Display Python version
echo "✅ Python version: $(/opt/homebrew/bin/python3.12 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    /opt/homebrew/bin/python3.12 -m venv venv
    echo "✅ Virtual environment created in ./venv/"
else
    echo "✅ Virtual environment already exists in ./venv/"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Start using OrcasAI:"
echo "   python orcasai.py list"
echo "   python orcasai.py run content_creation --topic 'Your topic here'"
echo ""
echo "🐋 Your orcas are ready to work together!"
