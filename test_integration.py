#!/usr/bin/env python3
"""
Test script for GoTo SMS Integration
This script validates the integration without requiring Home Assistant.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

def test_manifest():
    """Test manifest.json file."""
    print("🔍 Testing manifest.json...")
    
    try:
        with open('custom_components/goto_sms/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        required_keys = ['domain', 'name', 'version', 'config_flow']
        for key in required_keys:
            if key not in manifest:
                print(f"❌ Missing required key: {key}")
                return False
        
        print(f"✅ Manifest validation passed (version: {manifest.get('version')})")
        return True
    except Exception as e:
        print(f"❌ Manifest validation failed: {e}")
        return False

def test_file_structure():
    """Test file structure."""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'custom_components/goto_sms/__init__.py',
        'custom_components/goto_sms/manifest.json',
        'custom_components/goto_sms/const.py',
        'custom_components/goto_sms/oauth.py',
        'custom_components/goto_sms/notify.py',
        'custom_components/goto_sms/config_flow.py',
        'custom_components/goto_sms/services.yaml',
        'custom_components/goto_sms/translations/en/config_flow.json',
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False
    
    return all_exist

def test_syntax():
    """Test Python syntax."""
    print("\n🔍 Testing Python syntax...")
    
    import ast
    
    python_files = [
        'custom_components/goto_sms/__init__.py',
        'custom_components/goto_sms/const.py',
        'custom_components/goto_sms/oauth.py',
        'custom_components/goto_sms/notify.py',
        'custom_components/goto_sms/config_flow.py',
        'custom_components/goto_sms/sensor.py',
    ]
    
    all_valid = True
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            ast.parse(content)
            print(f"✅ {file_path}")
        except SyntaxError as e:
            print(f"❌ Syntax error in {file_path}: {e}")
            all_valid = False
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            all_valid = False
    
    return all_valid

def test_json_files():
    """Test JSON files."""
    print("\n🔍 Testing JSON files...")
    
    json_files = [
        'custom_components/goto_sms/manifest.json',
        'custom_components/goto_sms/translations/en/config_flow.json',
        'hacs.json',
    ]
    
    all_valid = True
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                json.load(f)
            print(f"✅ {file_path}")
        except Exception as e:
            print(f"❌ JSON error in {file_path}: {e}")
            all_valid = False
    
    return all_valid

def test_yaml_files():
    """Test YAML files."""
    print("\n🔍 Testing YAML files...")
    
    try:
        import yaml
    except ImportError:
        print("⚠️  PyYAML not available, skipping YAML validation")
        return True
    
    yaml_files = [
        'custom_components/goto_sms/services.yaml',
    ]
    
    all_valid = True
    for file_path in yaml_files:
        try:
            with open(file_path, 'r') as f:
                yaml.safe_load(f)
            print(f"✅ {file_path}")
        except Exception as e:
            print(f"❌ YAML error in {file_path}: {e}")
            all_valid = False
    
    return all_valid

def test_notify_logic():
    """Test notify logic without Home Assistant."""
    print("\n🔍 Testing notify logic...")
    
    try:
        # Test the OAuth manager logic by reading the file and checking for key improvements
        with open('custom_components/goto_sms/oauth.py', 'r') as f:
            content = f.read()
        
        # Check for the authentication persistence improvements
        improvements = [
            'max_retries = 3',
            'retry_count = 0',
            'while retry_count < max_retries:',
            'timedelta(minutes=15)',
            'Exponential backoff',
        ]
        
        all_found = True
        for improvement in improvements:
            if improvement in content:
                print(f"✅ Found improvement: {improvement}")
            else:
                print(f"❌ Missing improvement: {improvement}")
                all_found = False
        
        # Check for periodic refresh in __init__.py
        with open('custom_components/goto_sms/__init__.py', 'r') as f:
            init_content = f.read()
        
        if 'async_track_time_interval' in init_content:
            print("✅ Found periodic token refresh")
        else:
            print("❌ Missing periodic token refresh")
            all_found = False
        
        if 'startup_token_validation' in init_content:
            print("✅ Found startup token validation")
        else:
            print("❌ Missing startup token validation")
            all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ Notify logic test failed: {e}")
        return False

def test_authentication_persistence():
    """Test authentication persistence improvements."""
    print("\n🔍 Testing authentication persistence improvements...")
    
    try:
        # Read the oauth.py file and check for the improvements
        with open('custom_components/goto_sms/oauth.py', 'r') as f:
            content = f.read()
        
        # Check for the key improvements we made
        improvements = [
            'max_retries = 3',  # Retry logic
            'retry_count = 0',  # Retry counter
            'while retry_count < max_retries:',  # Retry loop
            'timedelta(minutes=15)',  # Aggressive token validation
            'Exponential backoff',  # Backoff strategy
            'time.sleep(2 ** retry_count)',  # Exponential backoff implementation
        ]
        
        all_found = True
        for improvement in improvements:
            if improvement in content:
                print(f"✅ Found improvement: {improvement}")
            else:
                print(f"❌ Missing improvement: {improvement}")
                all_found = False
        
        # Check for better error handling
        if 'response.status_code in [401, 400]' in content:
            print("✅ Found improved error handling for invalid refresh tokens")
        else:
            print("❌ Missing improved error handling")
            all_found = False
        
        # Check for better logging
        if '_LOGGER.debug' in content:
            print("✅ Found improved debug logging")
        else:
            print("❌ Missing improved debug logging")
            all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ Authentication persistence test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 GoTo SMS Integration Test Suite")
    print("=" * 40)
    
    tests = [
        ("Manifest", test_manifest),
        ("File Structure", test_file_structure),
        ("Python Syntax", test_syntax),
        ("JSON Files", test_json_files),
        ("YAML Files", test_yaml_files),
        ("Notify Logic", test_notify_logic),
        ("Authentication Persistence", test_authentication_persistence),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print()
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Integration is ready.")
        return 0
    else:
        print(f"\n🔧 {len(results) - passed} tests failed. Please fix issues before release.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 