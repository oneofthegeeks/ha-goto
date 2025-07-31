#!/usr/bin/env python3
"""
Release Checklist for GoTo SMS Integration
This script helps ensure all steps are completed before a release.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def check_version_consistency():
    """Check that version is consistent across files."""
    print("🔍 Checking version consistency...")
    
    try:
        # Check manifest.json
        with open('custom_components/goto_sms/manifest.json', 'r') as f:
            manifest = json.load(f)
        manifest_version = manifest.get('version')
        print(f"✅ manifest.json version: {manifest_version}")
        
        # Check CHANGELOG.md for version
        with open('CHANGELOG.md', 'r') as f:
            changelog = f.read()
        
        if f"## [{manifest_version}]" in changelog:
            print(f"✅ CHANGELOG.md has entry for version {manifest_version}")
        else:
            print(f"❌ CHANGELOG.md missing entry for version {manifest_version}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Version consistency check failed: {e}")
        return False

def check_documentation():
    """Check that documentation is up to date."""
    print("\n🔍 Checking documentation...")
    
    required_docs = [
        'README.md',
        'CHANGELOG.md',
        'INSTALL.md',
        'SMS_TRACKING.md',
        'CONTRIBUTING.md',
    ]
    
    all_exist = True
    for doc in required_docs:
        if Path(doc).exists():
            print(f"✅ {doc}")
        else:
            print(f"❌ Missing: {doc}")
            all_exist = False
    
    return all_exist

def check_scripts():
    """Check that installation scripts exist and are executable."""
    print("\n🔍 Checking installation scripts...")
    
    scripts = [
        'install.sh',
        'update.sh',
    ]
    
    all_good = True
    for script in scripts:
        script_path = Path(script)
        if script_path.exists():
            print(f"✅ {script} exists")
            if script_path.stat().st_mode & 0o111:  # Check if executable
                print(f"✅ {script} is executable")
            else:
                print(f"⚠️  {script} is not executable")
        else:
            print(f"❌ Missing: {script}")
            all_good = False
    
    return all_good

def check_ci_cd():
    """Check that CI/CD files exist."""
    print("\n🔍 Checking CI/CD configuration...")
    
    ci_files = [
        '.github/workflows/test.yml',
        'hacs.json',
    ]
    
    all_exist = True
    for file_path in ci_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False
    
    return all_exist

def check_code_quality():
    """Check code quality tools configuration."""
    print("\n🔍 Checking code quality configuration...")
    
    quality_files = [
        'pyproject.toml',
        '.gitignore',
    ]
    
    all_exist = True
    for file_path in quality_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False
    
    return all_exist

def generate_release_notes():
    """Generate a summary of changes for release notes."""
    print("\n📝 Release Notes Summary:")
    print("=" * 40)
    
    try:
        with open('CHANGELOG.md', 'r') as f:
            changelog = f.read()
        
        # Find the latest version entry
        lines = changelog.split('\n')
        latest_version = None
        latest_changes = []
        
        for i, line in enumerate(lines):
            if line.startswith('## [') and '] - ' in line:
                if latest_version is None:
                    latest_version = line
                    # Collect changes until next version
                    for j in range(i + 1, len(lines)):
                        if lines[j].startswith('## ['):
                            break
                        if lines[j].strip():
                            latest_changes.append(lines[j])
                    break
        
        if latest_version:
            print(f"Latest version: {latest_version}")
            print("\nKey changes:")
            for change in latest_changes[:10]:  # Show first 10 changes
                if change.strip() and not change.startswith('#'):
                    print(f"  {change}")
        else:
            print("❌ Could not find latest version in CHANGELOG.md")
            
    except Exception as e:
        print(f"❌ Error generating release notes: {e}")

def main():
    """Run the release checklist."""
    print("🚀 GoTo SMS Integration Release Checklist")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        ("Version Consistency", check_version_consistency),
        ("Documentation", check_documentation),
        ("Installation Scripts", check_scripts),
        ("CI/CD Configuration", check_ci_cd),
        ("Code Quality Tools", check_code_quality),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Release Checklist Results:")
    print()
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} checks")
    
    if passed == len(results):
        print("\n🎉 All checks passed! Ready for release.")
        print("\nNext steps:")
        print("1. Run: python test_integration.py")
        print("2. Test the integration in a Home Assistant environment")
        print("3. Create a GitHub release")
        print("4. Update HACS if applicable")
        generate_release_notes()
        return 0
    else:
        print(f"\n🔧 {len(results) - passed} checks failed. Please fix before release.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 