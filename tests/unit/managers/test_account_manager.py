# -*- coding: utf-8 -*-
"""
Unit tests for AccountManager
"""
import os
import json
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.managers.account_manager import AccountManager


class TestAccountManager:
    """Test AccountManager class"""
    
    def test_init_creates_directories(self, temp_dir):
        """Test that AccountManager creates necessary directories"""
        accounts_file = os.path.join(temp_dir, 'accounts.json')
        sessions_dir = os.path.join(temp_dir, 'sessions')
        
        manager = AccountManager(accounts_file, sessions_dir)
        
        assert os.path.exists(sessions_dir)
        assert manager.accounts_file == accounts_file
        assert manager.sessions_dir == sessions_dir
        assert manager.accounts == []
    
    def test_load_accounts_empty_file(self, temp_dir):
        """Test loading accounts when file doesn't exist"""
        accounts_file = os.path.join(temp_dir, 'accounts.json')
        sessions_dir = os.path.join(temp_dir, 'sessions')
        
        manager = AccountManager(accounts_file, sessions_dir)
        
        assert manager.accounts == []
    
    def test_load_accounts_with_data(self, temp_dir, sample_account):
        """Test loading accounts from existing file"""
        accounts_file = os.path.join(temp_dir, 'accounts.json')
        sessions_dir = os.path.join(temp_dir, 'sessions')
        
        # Create accounts file with sample data
        with open(accounts_file, 'w', encoding='utf-8') as f:
            json.dump({'accounts': [sample_account]}, f)
        
        manager = AccountManager(accounts_file, sessions_dir)
        
        assert len(manager.accounts) == 1
        assert manager.accounts[0]['phone'] == sample_account['phone']
    
    def test_save_accounts(self, temp_dir, sample_account):
        """Test saving accounts to file"""
        accounts_file = os.path.join(temp_dir, 'accounts.json')
        sessions_dir = os.path.join(temp_dir, 'sessions')
        
        manager = AccountManager(accounts_file, sessions_dir)
        manager.accounts = [sample_account]
        manager.save_accounts()
        
        # Verify file was created and contains data
        assert os.path.exists(accounts_file)
        with open(accounts_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'accounts' in data
        assert len(data['accounts']) == 1
        assert data['accounts'][0]['phone'] == sample_account['phone']
    
    def test_add_account(self, temp_dir, sample_account):
        """Test adding a new account"""
        accounts_file = os.path.join(temp_dir, 'accounts.json')
        sessions_dir = os.path.join(temp_dir, 'sessions')
        
        manager = AccountManager(accounts_file, sessions_dir)
        
        # Add account
        account_id = manager.add_account(
            phone=sample_account['phone'],
            api_id=sample_account['api_id'],
            api_hash=sample_account['api_hash']
        )
        
        assert account_id is not None
        assert len(manager.accounts) == 1
        assert manager.accounts[0]['phone'] == sample_account['phone']
    
    def test_get_account(self, temp_dir, sample_account):
        """Test getting an account by ID"""
        accounts_file = os.path.join(temp_dir, 'accounts.json')
        sessions_dir = os.path.join(temp_dir, 'sessions')
        
        manager = AccountManager(accounts_file, sessions_dir)
        manager.accounts = [sample_account]
        
        account = manager.get_account(sample_account['id'])
        
        assert account is not None
        assert account['phone'] == sample_account['phone']
    
    def test_get_account_not_found(self, temp_dir):
        """Test getting a non-existent account"""
        accounts_file = os.path.join(temp_dir, 'accounts.json')
        sessions_dir = os.path.join(temp_dir, 'sessions')
        
        manager = AccountManager(accounts_file, sessions_dir)
        
        account = manager.get_account('non_existent_id')
        
        assert account is None
    
    def test_remove_account(self, temp_dir, sample_account):
        """Test removing an account"""
        accounts_file = os.path.join(temp_dir, 'accounts.json')
        sessions_dir = os.path.join(temp_dir, 'sessions')
        
        manager = AccountManager(accounts_file, sessions_dir)
        manager.accounts = [sample_account]
        
        result = manager.remove_account(sample_account['id'])
        
        assert result is True
        assert len(manager.accounts) == 0
    
    def test_get_connected_accounts(self, temp_dir, sample_account, mock_telegram_client):
        """Test getting connected accounts"""
        accounts_file = os.path.join(temp_dir, 'accounts.json')
        sessions_dir = os.path.join(temp_dir, 'sessions')
        
        manager = AccountManager(accounts_file, sessions_dir)
        manager.accounts = [sample_account]
        manager.clients[sample_account['id']] = mock_telegram_client
        
        connected = manager.get_connected_accounts()
        
        assert len(connected) == 1
        assert connected[0]['id'] == sample_account['id']
