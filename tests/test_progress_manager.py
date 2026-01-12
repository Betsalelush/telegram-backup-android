"""
Basic tests for ProgressManager
"""
import os
import tempfile
import pytest

from app.managers.progress_manager import ProgressManager


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def progress_manager(temp_dir):
    """Create ProgressManager instance"""
    return ProgressManager(temp_dir)


def test_get_progress_key(progress_manager):
    """Test progress key generation"""
    key = progress_manager.get_progress_key("123", "456")
    assert key == "channel_123_to_456"


def test_save_load_progress(progress_manager):
    """Test saving and loading progress"""
    # Save progress
    progress_manager.save_progress(
        "123", "456",
        [1, 2, 3, 4, 5],
        5,
        5, 0
    )
    
    # Load progress
    progress = progress_manager.load_progress("123", "456")
    
    assert progress['sent_message_ids'] == [1, 2, 3, 4, 5]
    assert progress['last_message_id'] == 5
    assert progress['total_sent'] == 5


def test_update_progress(progress_manager):
    """Test updating progress"""
    progress_manager.update_progress("123", "456", 10)
    progress_manager.update_progress("123", "456", 20)
    
    progress = progress_manager.load_progress("123", "456")
    
    assert 10 in progress['sent_message_ids']
    assert 20 in progress['sent_message_ids']
    assert progress['last_message_id'] == 20


def test_clear_progress(progress_manager):
    """Test clearing progress"""
    # Save progress
    progress_manager.save_progress("123", "456", [1, 2, 3], 3, 3, 0)
    
    # Clear
    result = progress_manager.clear_progress("123", "456")
    assert result == True
    
    # Load should return empty
    progress = progress_manager.load_progress("123", "456")
    assert progress['sent_message_ids'] == []
