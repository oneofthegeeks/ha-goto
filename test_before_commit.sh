#!/bin/bash

# Test script to run before committing
# This runs the exact same tests as GitHub Actions

echo "🚀 Running GitHub Actions tests locally..."
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install tools if needed
source venv/bin/activate

# Install tools if not already installed
if ! command -v black &> /dev/null; then
    echo "📦 Installing linting tools..."
    pip install black flake8 isort
fi

# Run the tests
echo ""
echo "🔍 Running tests..."
python3 test_github_actions_local.py

# Store the exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 All tests passed! Safe to commit."
else
    echo "❌ Some tests failed. Please fix the issues before committing."
fi

exit $EXIT_CODE 