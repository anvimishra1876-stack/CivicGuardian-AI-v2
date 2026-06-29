#!/bin/bash
# CivicGuardian AI Setup Script
echo "🏛️ Setting up CivicGuardian AI..."

# Install dependencies
pip install -r requirements.txt

# Copy env file if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file. Add your GEMINI_API_KEY to enable AI explanations."
fi

echo ""
echo "✅ Setup complete! Run with:"
echo "   streamlit run app.py"
echo ""
echo "💡 Optional: Add your GEMINI_API_KEY to .env for AI-powered explanations."
