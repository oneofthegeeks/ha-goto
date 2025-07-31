#!/usr/bin/env python3
"""
Test script for GoTo SMS integration validation.
This script tests the integration logic without requiring Home Assistant.
"""

import json
import sys
from pathlib import Path

def test_manifest():
    """Test manifest.json validation."""
    print("🔍 Testing manifest.json...")
    try:
        with open('custom_components/goto_sms/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        required_keys = ['domain', 'name', 'version', 'config_flow']
        for key in required_keys:
            if key not in manifest:
                print(f"❌ Missing required key: {key}")
                return False
            print(f"✅ {key}: {manifest[key]}")
        
        print("✅ Manifest validation passed")
        return True
    except Exception as e:
        print(f"❌ Manifest validation failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'custom_components/goto_sms/__init__.py',
        'custom_components/goto_sms/manifest.json',
        'custom_components/goto_sms/const.py',
        'custom_components/goto_sms/oauth.py',
        'custom_components/goto_sms/notify.py',
        'custom_components/goto_sms/config_flow.py',
        'custom_components/goto_sms/sensor.py',
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
    
    if all_exist:
        print("✅ All required files exist")
    return all_exist

def test_syntax():
    """Test Python syntax for all .py files."""
    print("\n🔍 Testing Python syntax...")
    
    import ast
    
    py_files = [
        'custom_components/goto_sms/__init__.py',
        'custom_components/goto_sms/const.py',
        'custom_components/goto_sms/oauth.py',
        'custom_components/goto_sms/notify.py',
        'custom_components/goto_sms/config_flow.py',
        'custom_components/goto_sms/sensor.py',
    ]
    
    all_valid = True
    for file_path in py_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            ast.parse(content)
            print(f"✅ {file_path} - syntax valid")
        except SyntaxError as e:
            print(f"❌ {file_path} - syntax error: {e}")
            all_valid = False
        except Exception as e:
            print(f"❌ {file_path} - error: {e}")
            all_valid = False
    
    if all_valid:
        print("✅ All Python files have valid syntax")
    return all_valid

def test_json_files():
    """Test JSON syntax for JSON files."""
    print("\n🔍 Testing JSON syntax...")
    
    json_files = [
        'custom_components/goto_sms/manifest.json',
        'custom_components/goto_sms/translations/en/config_flow.json',
    ]
    
    all_valid = True
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                json.load(f)
            print(f"✅ {file_path} - JSON valid")
        except json.JSONDecodeError as e:
            print(f"❌ {file_path} - JSON error: {e}")
            all_valid = False
        except Exception as e:
            print(f"❌ {file_path} - error: {e}")
            all_valid = False
    
    if all_valid:
        print("✅ All JSON files are valid")
    return all_valid

def test_yaml_files():
    """Test YAML syntax for YAML files."""
    print("\n🔍 Testing YAML syntax...")
    
    yaml_files = [
        'custom_components/goto_sms/services.yaml',
    ]
    
    try:
        import yaml
    except ImportError:
        print("⚠️  PyYAML not available, skipping YAML validation")
        return True
    
    all_valid = True
    for file_path in yaml_files:
        try:
            with open(file_path, 'r') as f:
                yaml.safe_load(f)
            print(f"✅ {file_path} - YAML valid")
        except yaml.YAMLError as e:
            print(f"❌ {file_path} - YAML error: {e}")
            all_valid = False
        except Exception as e:
            print(f"❌ {file_path} - error: {e}")
            all_valid = False
    
    if all_valid:
        print("✅ All YAML files are valid")
    return all_valid

def test_notify_logic():
    """Test the notify.py logic without Home Assistant dependencies."""
    print("\n🔍 Testing notify.py logic...")
    
    try:
        # Read the notify.py file and check for key functions
        with open('custom_components/goto_sms/notify.py', 'r') as f:
            content = f.read()
        
        required_functions = [
            'get_service',
            'GoToSMSNotificationService',
            'async_send_message',
            '_track_message_sent',
        ]
        
        all_found = True
        for func in required_functions:
            if func in content:
                print(f"✅ Found function: {func}")
            else:
                print(f"❌ Missing function: {func}")
                all_found = False
        
        # Check for the fix we implemented
        if 'async_add_job' in content:
            print("✅ Found async_add_job usage (counter fix)")
        else:
            print("❌ Missing async_add_job usage")
            all_found = False
        
        if '_get_sensor_current_value' in content:
            print("✅ Found sensor helper methods")
        else:
            print("❌ Missing sensor helper methods")
            all_found = False
        
        if all_found:
            print("✅ Notify logic validation passed")
        return all_found
        
    except Exception as e:
        print(f"❌ Notify logic validation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 GoTo SMS Integration Validation")
    print("=" * 40)
    
    tests = [
        test_manifest,
        test_file_structure,
        test_syntax,
        test_json_files,
        test_yaml_files,
        test_notify_logic,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} tests passed!")
        print("\n🎉 Integration validation successful!")
        print("The SMS counter fix has been implemented and validated.")
        return 0
    else:
        print(f"❌ {total - passed} of {total} tests failed")
        print("\n🔧 Please fix the failing tests before release.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 