# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures
"""
import os
import sys
import pytest
import tempfile
import shutil
from unittest.mock import MagicMock

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config import Config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_config(temp_dir):
    """Setup mock configuration with temporary directories"""
    Config.setup(temp_dir)
    return Config


@pytest.fixture
def mock_telegram_client():
    """Create a mock Telegram client"""
    client = MagicMock()
    client.is_connected.return_value = True
    client.get_me.return_value = MagicMock(
        id=123456,
        phone='+972123456789',
        first_name='Test',
        last_name='User'
    )
    return client


@pytest.fixture
def sample_account():
    """Sample account data for testing"""
    return {
        'id': 'test_account_1',
        'phone': '+972123456789',
        'api_id': '12345',
        'api_hash': 'abcdef123456',
        'created_at': '2026-01-12T00:00:00',
        'last_used': '2026-01-12T00:00:00'
    }


@pytest.fixture
def sample_transfer():
    """Sample transfer data for testing"""
    return {
        'id': 'transfer_123',
        'account_id': 'test_account_1',
        'source_channel': 'source_channel_id',
        'target_channel': 'target_channel_id',
        'start_message_id': 1,
        'last_sent_id': 50,
        'total_sent': 50,
        'status': 'in_progress',
        'created_at': '2026-01-12T00:00:00',
        'updated_at': '2026-01-12T00:00:00'
    }
