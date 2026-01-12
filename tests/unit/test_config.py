# -*- coding: utf-8 -*-
"""
Unit tests for Config module
"""
import os
import pytest
from app.config import Config


class TestConfig:
    """Test Config class"""
    
    def test_config_defaults(self):
        """Test that default config values are set correctly"""
        assert Config.APP_NAME == "Telegram Backup"
        assert Config.APP_VERSION == "3.0.0"
        assert Config.MAX_MESSAGES_PER_MINUTE == 20
        assert Config.SAVE_PROGRESS_EVERY == 10
        assert Config.DEFAULT_THEME == "Light"
        assert Config.PRIMARY_PALETTE == "Blue"
    
    def test_config_setup(self, temp_dir):
        """Test config setup with base directory"""
        Config.setup(temp_dir)
        
        assert Config.BASE_DIR == temp_dir
        assert Config.SESSIONS_DIR == os.path.join(temp_dir, 'data', 'sessions')
        assert Config.PROGRESS_DIR == os.path.join(temp_dir, 'data', 'progress')
        assert Config.ACCOUNTS_FILE == os.path.join(temp_dir, 'data', 'accounts.json')
        assert Config.TRANSFERS_FILE == os.path.join(temp_dir, 'data', 'transfers.json')
        
        # Check directories were created
        assert os.path.exists(Config.SESSIONS_DIR)
        assert os.path.exists(Config.PROGRESS_DIR)
    
    def test_get_session_path(self, temp_dir):
        """Test session path generation"""
        Config.setup(temp_dir)
        
        phone = "+972123456789"
        session_path = Config.get_session_path(phone)
        
        expected_path = os.path.join(
            Config.SESSIONS_DIR,
            'session_972123456789'
        )
        assert session_path == expected_path
    
    def test_get_progress_path(self, temp_dir):
        """Test progress path generation"""
        Config.setup(temp_dir)
        
        transfer_id = 'transfer_123'
        progress_path = Config.get_progress_path(transfer_id)
        
        expected_path = os.path.join(
            Config.PROGRESS_DIR,
            'transfer_123_progress.json'
        )
        assert progress_path == expected_path
    
    def test_sentry_config(self):
        """Test Sentry configuration values"""
        assert Config.SENTRY_DSN.startswith('https://')
        assert Config.SENTRY_TRACES_SAMPLE_RATE == 1.0
        assert Config.SENTRY_PROFILES_SAMPLE_RATE == 1.0
        assert Config.SENTRY_MAX_BREADCRUMBS == 100
