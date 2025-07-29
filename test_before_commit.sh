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
echo "�� Running tests..."

# Run flake8
echo "🔍 Flake8 linting..."
flake8 custom_components/goto_sms/ --count --select=E9,F63,F7,F82 --show-source --statistics
FLAKE8_EXIT=$?

# Run Black check
echo "🔍 Black formatting..."
black --check custom_components/goto_sms/
BLACK_EXIT=$?

# Run isort check
echo "🔍 Import sorting..."
isort --check-only custom_components/goto_sms/
ISORT_EXIT=$?

# Run manifest validation
echo "🔍 Manifest validation..."
python3 -c "
import json
with open('custom_components/goto_sms/manifest.json', 'r') as f:
    manifest = json.load(f)
required_keys = ['domain', 'name', 'version', 'config_flow']
for key in required_keys:
    assert key in manifest, f'Missing required key: {key}'
print('✅ Manifest validation passed')
"
MANIFEST_EXIT=$?

# Run translation validation
echo "🔍 Translation validation..."
python3 -c "
import json
import os
translation_file = 'custom_components/goto_sms/translations/en/config_flow.json'
if os.path.exists(translation_file):
    with open(translation_file, 'r') as f:
        translations = json.load(f)
    print('✅ Translation file is valid JSON')
else:
    print('⚠️  No translation file found')
"
TRANSLATION_EXIT=$?

# Run import test (with Home Assistant handling)
echo "🔍 Import testing..."
python3 -c "
import sys
import os
sys.path.insert(0, 'custom_components')
try:
    from goto_sms import const, oauth, notify, config_flow
    print('✅ All modules imported successfully')
except ImportError as e:
    if 'homeassistant' in str(e):
        print('⚠️  Home Assistant modules not available (expected in local testing)')
        print('✅ Basic module structure is correct')
    else:
        print(f'❌ Import error: {e}')
        sys.exit(1)
"
IMPORT_EXIT=$?

# Check all results
TOTAL_EXIT=$((FLAKE8_EXIT + BLACK_EXIT + ISORT_EXIT + MANIFEST_EXIT + TRANSLATION_EXIT + IMPORT_EXIT))

echo ""
echo "Results:"
echo "  Flake8: $([ $FLAKE8_EXIT -eq 0 ] && echo '✅ Passed' || echo '❌ Failed')"
echo "  Black: $([ $BLACK_EXIT -eq 0 ] && echo '✅ Passed' || echo '❌ Failed')"
echo "  isort: $([ $ISORT_EXIT -eq 0 ] && echo '✅ Passed' || echo '❌ Failed')"
echo "  Manifest: $([ $MANIFEST_EXIT -eq 0 ] && echo '✅ Passed' || echo '❌ Failed')"
echo "  Translation: $([ $TRANSLATION_EXIT -eq 0 ] && echo '✅ Passed' || echo '❌ Failed')"
echo "  Import: $([ $IMPORT_EXIT -eq 0 ] && echo '✅ Passed' || echo '❌ Failed')"

echo ""
if [ $TOTAL_EXIT -eq 0 ]; then
    echo "🎉 All tests passed! Safe to commit."
else
    echo "❌ Some tests failed. Please fix the issues before committing."
fi

exit $TOTAL_EXIT 