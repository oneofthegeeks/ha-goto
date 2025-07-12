#!/bin/bash

# GitHub Repository Setup Script for GoTo SMS Integration
# This script helps you initialize the git repository and prepare for GitHub

set -e

echo "🚀 Setting up GitHub repository for GoTo SMS Integration"
echo "========================================================"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
else
    echo "✅ Git repository already exists"
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: GoTo SMS Home Assistant Integration

- OAuth2 authentication with GoTo Connect API
- Automatic token refresh functionality
- SMS notification service (notify.goto_sms)
- Config flow for UI-based configuration
- Comprehensive error handling and logging
- English translations for the UI
- MIT License and contribution guidelines"

echo ""
echo "✅ Repository setup complete!"
echo ""
echo "Next steps:"
echo "1. Create a new repository on GitHub: https://github.com/new"
echo "2. Choose a repository name (e.g., 'ha-goto')"
echo "3. Make it public or private as preferred"
echo "4. Don't initialize with README, .gitignore, or license (we already have them)"
echo "5. After creating the repository, run these commands:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/ha-goto.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "6. Update the README.md file to replace 'your-username' with your actual GitHub username"
echo ""
echo "🎉 Your GoTo SMS integration is ready for GitHub!" 