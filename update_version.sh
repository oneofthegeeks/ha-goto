#!/bin/bash

# Version update script for GoTo SMS integration
# Usage: ./update_version.sh <new_version>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    print_error "Please provide a version number (e.g., ./update_version.sh 1.1.1)"
    exit 1
fi

NEW_VERSION=$1

# Validate version format (basic check)
if ! [[ $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Invalid version format. Use semantic versioning (e.g., 1.1.1)"
    exit 1
fi

print_status "Updating version to $NEW_VERSION..."

# Get current version
CURRENT_VERSION=$(grep '"version"' custom_components/goto_sms/manifest.json | sed 's/.*"version": "\([^"]*\)".*/\1/')
print_status "Current version: $CURRENT_VERSION"

# Update manifest.json
print_status "Updating manifest.json..."
sed -i '' "s/\"version\": \"$CURRENT_VERSION\"/\"version\": \"$NEW_VERSION\"/" custom_components/goto_sms/manifest.json
print_success "Updated manifest.json"

# Update changelog
print_status "Updating CHANGELOG.md..."
# Add new version section at the top (after [Unreleased])
sed -i '' "/^## \[Unreleased\]/a\\
\\
## \[$NEW_VERSION\] - $(date +%Y-%m-%d)\\
\\
### Added\\
- \\
\\
### Changed\\
- \\
\\
### Fixed\\
- \\
\\
### Technical Improvements\\
- \\
" CHANGELOG.md
print_success "Updated CHANGELOG.md"

# Show what changed
print_status "Changes made:"
echo "  - manifest.json: $CURRENT_VERSION → $NEW_VERSION"
echo "  - CHANGELOG.md: Added new version section"

print_success "Version update completed!"
print_status "Next steps:"
print_status "1. Edit CHANGELOG.md to add your changes"
print_status "2. Run tests: ./test_before_commit.sh"
print_status "3. Commit changes and create release" 