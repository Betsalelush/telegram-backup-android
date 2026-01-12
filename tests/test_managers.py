#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for managers functionality
Tests AccountManager and ProgressManager without external dependencies
"""

import os
import sys
import json
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.managers.account_manager import AccountManager
from app.managers.progress_manager import ProgressManager


def test_account_manager():
    """Test AccountManager basic functionality"""
    print("Testing AccountManager...")
    
    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp()
    
    try:
        accounts_file = os.path.join(temp_dir, 'accounts.json')
        sessions_dir = os.path.join(temp_dir, 'sessions')
        
        # Initialize manager
        manager = AccountManager(accounts_file, sessions_dir)
        
        # Test 1: Initial state
        assert len(manager.accounts) == 0, "Initial accounts list should be empty"
        assert os.path.isdir(sessions_dir), "Sessions directory should be created"
        
        # Test 2: Add account
        account_id = manager.add_account(
            name="Test Account",
            api_id="12345",
            api_hash="test_hash",
            phone="+972123456789"
        )
        
        assert account_id is not None, "Account ID should be returned"
        assert len(manager.accounts) == 1, "Should have one account"
        
        # Test 3: Get account
        account = manager.get_account(account_id)
        assert account is not None, "Account should be retrievable"
        assert account['name'] == "Test Account", "Account name should match"
        assert account['phone'] == "+972123456789", "Phone should match"
        
        # Test 4: Save and reload
        manager.save_accounts()
        assert os.path.isfile(accounts_file), "Accounts file should be created"
        
        manager2 = AccountManager(accounts_file, sessions_dir)
        assert len(manager2.accounts) == 1, "Reloaded manager should have one account"
        
        # Test 5: Get all accounts
        all_accounts = manager.get_all_accounts()
        assert len(all_accounts) == 1, "Should return one account"
        
        # Test 6: Remove account
        manager.remove_account(account_id)
        assert len(manager.accounts) == 0, "Should have no accounts after removal"
        
        print("✓ AccountManager tests passed")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_progress_manager():
    """Test ProgressManager basic functionality"""
    print("Testing ProgressManager...")
    
    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp()
    
    try:
        progress_dir = temp_dir
        
        # Initialize manager
        manager = ProgressManager(progress_dir)
        
        # Test 1: Load non-existent progress
        transfer_id = "test_transfer_123"
        progress = manager.load_progress(transfer_id)
        
        assert progress['transfer_id'] == transfer_id, "Transfer ID should match"
        assert progress['total_sent'] == 0, "Initial sent count should be 0"
        assert len(progress['sent_message_ids']) == 0, "Initial message IDs should be empty"
        
        # Test 2: Update progress
        manager.update_progress(transfer_id, 101, success=True)
        manager.update_progress(transfer_id, 102, success=True)
        manager.update_progress(transfer_id, 103, success=False)
        
        # Test 3: Load updated progress
        progress = manager.load_progress(transfer_id)
        assert progress['total_sent'] == 2, "Should have 2 sent messages"
        assert progress['total_skipped'] == 1, "Should have 1 skipped message"
        assert progress['last_message_id'] == 102, "Last message ID should be 102"
        
        # Test 4: Get sent message IDs
        sent_ids = manager.get_sent_message_ids(transfer_id)
        assert 101 in sent_ids, "Message 101 should be in sent IDs"
        assert 102 in sent_ids, "Message 102 should be in sent IDs"
        assert 103 not in sent_ids, "Message 103 should not be in sent IDs (was skipped)"
        
        # Test 5: Get last message ID
        last_id = manager.get_last_message_id(transfer_id)
        assert last_id == 102, "Last message ID should be 102"
        
        # Test 6: Delete progress
        progress_path = manager.get_progress_path(transfer_id)
        assert os.path.isfile(progress_path), "Progress file should exist"
        
        manager.delete_progress(transfer_id)
        assert not os.path.isfile(progress_path), "Progress file should be deleted"
        
        print("✓ ProgressManager tests passed")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_config_integration():
    """Test that Config paths work with managers"""
    print("Testing Config integration...")
    
    from app.config import Config
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Setup config
        Config.setup(temp_dir)
        
        # Test that directories are created
        assert os.path.isdir(Config.SESSIONS_DIR), "Sessions dir should be created"
        assert os.path.isdir(Config.PROGRESS_DIR), "Progress dir should be created"
        
        # Test that files can be created
        assert Config.ACCOUNTS_FILE is not None, "Accounts file path should be set"
        assert Config.TRANSFERS_FILE is not None, "Transfers file path should be set"
        
        # Test session path generation
        session_path = Config.get_session_path("+972123456789")
        assert "972123456789" in session_path, "Session path should contain phone without +"
        
        # Test progress path generation
        progress_path = Config.get_progress_path("transfer_123")
        assert "transfer_123_progress.json" in progress_path, "Progress path should contain transfer ID"
        
        print("✓ Config integration tests passed")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    print("Running manager tests...\n")
    
    try:
        test_account_manager()
        test_progress_manager()
        test_config_integration()
        
        print("\n✅ All manager tests passed!")
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
