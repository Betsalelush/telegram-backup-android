#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic structure validation test
Tests that the directory structure and imports work correctly
"""

import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_directory_structure():
    """Test that all required directories exist"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    required_dirs = [
        'app',
        'app/managers',
        'app/screens',
        'app/utils',
        'sessions',
        'progress',
        'docs',
        'tests',
        'debug_tools'
    ]
    
    for dir_path in required_dirs:
        full_path = os.path.join(base_dir, dir_path)
        assert os.path.isdir(full_path), f"Directory {dir_path} does not exist"
    
    print("- All required directories exist")


def test_config_import():
    """Test that Config module imports correctly"""
    try:
        from app.config import Config
        
        # Verify key configuration values
        assert hasattr(Config, 'SMART_DELAY_MIN'), "Config missing SMART_DELAY_MIN"
        assert hasattr(Config, 'SMART_DELAY_MAX'), "Config missing SMART_DELAY_MAX"
        assert hasattr(Config, 'setup'), "Config missing setup method"
        assert hasattr(Config, 'MAX_MESSAGES_PER_MINUTE'), "Config missing MAX_MESSAGES_PER_MINUTE"
        
        print("- Config module imports correctly")
        
    except ImportError as e:
        raise AssertionError(f"Failed to import Config: {e}")


def test_managers_structure():
    """Test that managers package structure is correct"""
    # This will fail if dependencies are missing, but structure can be verified
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    manager_files = [
        'app/managers/__init__.py',
        'app/managers/account_manager.py',
        'app/managers/progress_manager.py',
        'app/managers/transfer_manager.py'
    ]
    
    for file_path in manager_files:
        full_path = os.path.join(base_dir, file_path)
        assert os.path.isfile(full_path), f"Manager file {file_path} does not exist"
        
        # Verify it's valid Python syntax
        import py_compile
        try:
            py_compile.compile(full_path, doraise=True)
        except py_compile.PyCompileError as e:
            raise AssertionError(f"Syntax error in {file_path}: {e}")
    
    print("- All manager files have valid Python syntax")


if __name__ == '__main__':
    print("Running structure validation tests...\n")
    
    try:
        test_directory_structure()
        test_config_import()
        test_managers_structure()
        
        print("\nSUCCESS: All tests passed! Project structure is valid.")
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)
