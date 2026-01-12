"""
Basic tests for AccountManager
"""
import os
import json
import tempfile
import pytest

from app.managers.account_manager import AccountManager


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def account_manager(temp_dir):
    """Create AccountManager instance"""
    accounts_file = os.path.join(temp_dir, 'accounts.json')
    sessions_dir = os.path.join(temp_dir, 'sessions')
    return AccountManager(accounts_file, sessions_dir)


def test_add_account(account_manager):
    """Test adding account"""
    account_id = account_manager.add_account(
        "Test Account",
        "12345",
        "abcdef",
        "+972123456789"
    )
    
    assert account_id is not None
    assert account_id.startswith("acc_")
    assert len(account_manager.accounts) == 1


def test_save_load_accounts(account_manager):
    """Test saving and loading accounts"""
    # Add account
    account_id = account_manager.add_account(
        "Test",
        "123",
        "abc",
        "+972111"
    )
    
    # Save
    assert account_manager.save_accounts() == True
    
    # Create new manager and load
    new_manager = AccountManager(
        account_manager.accounts_file,
        account_manager.sessions_dir
    )
    
    assert len(new_manager.accounts) == 1
    assert new_manager.accounts[0]['id'] == account_id


def test_remove_account(account_manager):
    """Test removing account"""
    account_id = account_manager.add_account(
        "Test",
        "123",
        "abc",
        "+972111"
    )
    
    assert len(account_manager.accounts) == 1
    
    account_manager.remove_account(account_id)
    
    assert len(account_manager.accounts) == 0


def test_get_account(account_manager):
    """Test getting account by ID"""
    account_id = account_manager.add_account(
        "Test",
        "123",
        "abc",
        "+972111"
    )
    
    account = account_manager.get_account(account_id)
    
    assert account is not None
    assert account['id'] == account_id
    assert account['name'] == "Test"
