#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Runner - Runs all tests with proper dependency handling
"""

import sys
import os
import subprocess

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_and_install_dependencies():
    """Check and install required test dependencies"""
    print("Checking dependencies...")
    
    required = {
        'sentry-sdk': 'sentry_sdk',
        'cryptography': 'cryptography'
    }
    
    missing = []
    for package, import_name in required.items():
        try:
            __import__(import_name)
            print(f"  ✓ {package} installed")
        except ImportError:
            print(f"  ✗ {package} missing")
            missing.append(package)
    
    if missing:
        print(f"\nInstalling missing dependencies: {', '.join(missing)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--quiet'
            ] + missing)
            print("✓ Dependencies installed")
        except subprocess.CalledProcessError:
            print("⚠ Warning: Could not install all dependencies")
            print("  Some tests may be skipped")
    
    print()

def run_test(test_file):
    """Run a single test file"""
    test_name = os.path.basename(test_file).replace('test_', '').replace('.py', '')
    print(f"{'='*60}")
    print(f"Running: {test_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {test_name} - PASSED\n")
            return True
        else:
            print(f"❌ {test_name} - FAILED\n")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"⏱️ {test_name} - TIMEOUT\n")
        return False
    except Exception as e:
        print(f"💥 {test_name} - ERROR: {e}\n")
        return False

def main():
    """Main test runner"""
    print("="*60)
    print("Telegram Backup Android - Test Suite")
    print("="*60)
    print()
    
    # Install dependencies
    check_and_install_dependencies()
    
    # Find all test files
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = [
        os.path.join(tests_dir, f)
        for f in os.listdir(tests_dir)
        if f.startswith('test_') and f.endswith('.py')
    ]
    test_files.sort()
    
    if not test_files:
        print("No test files found!")
        return 1
    
    print(f"Found {len(test_files)} test file(s):\n")
    for tf in test_files:
        print(f"  • {os.path.basename(tf)}")
    print()
    
    # Run all tests
    results = {}
    for test_file in test_files:
        test_name = os.path.basename(test_file)
        results[test_name] = run_test(test_file)
    
    # Summary
    print("="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r)
    failed = len(results) - passed
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status:12} - {test_name}")
    
    print()
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
