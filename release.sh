#!/bin/bash

# Release script for GoTo SMS Home Assistant integration
# Usage: ./release.sh [version] [message]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if version is provided
if [ -z "$1" ]; then
    print_error "Please provide a version number (e.g., ./release.sh 1.1.0)"
    exit 1
fi

VERSION=$1
RELEASE_MESSAGE=${2:-"Release v$VERSION"}

print_status "Starting release process for version $VERSION..."

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_warning "You're not on the main branch. Current branch: $CURRENT_BRANCH"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if working directory is clean
if [ -n "$(git status --porcelain)" ]; then
    print_error "Working directory is not clean. Please commit or stash your changes first."
    git status --short
    exit 1
fi

# Run tests
print_status "Running tests..."
./test_before_commit.sh
if [ $? -ne 0 ]; then
    print_error "Tests failed. Please fix the issues before releasing."
    exit 1
fi
print_success "All tests passed!"

# Check if tag already exists
if git tag -l | grep -q "^v$VERSION$"; then
    print_error "Tag v$VERSION already exists!"
    exit 1
fi

# Create and push tag
print_status "Creating tag v$VERSION..."
git tag -a "v$VERSION" -m "$RELEASE_MESSAGE"
git push origin "v$VERSION"
print_success "Tag v$VERSION created and pushed!"

# Create GitHub release
print_status "Creating GitHub release..."
gh release create "v$VERSION" \
    --title "Release v$VERSION" \
    --notes-file CHANGELOG.md \
    --draft

if [ $? -eq 0 ]; then
    print_success "GitHub release draft created!"
    print_status "Please review and publish the release on GitHub:"
    print_status "https://github.com/oneofthegeeks/ha-goto/releases"
else
    print_warning "Failed to create GitHub release. You may need to:"
    print_warning "1. Install GitHub CLI: https://cli.github.com/"
    print_warning "2. Authenticate: gh auth login"
    print_warning "3. Create release manually on GitHub"
fi

print_success "Release process completed!"
print_status "Next steps:"
print_status "1. Review and publish the GitHub release"
print_status "2. Update HACS if needed"
print_status "3. Test the release in Home Assistant" 