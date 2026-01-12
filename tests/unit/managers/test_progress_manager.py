# -*- coding: utf-8 -*-
"""
Unit tests for ProgressManager
"""
import os
import json
import pytest
from app.managers.progress_manager import ProgressManager


class TestProgressManager:
    """Test ProgressManager class"""
    
    def test_init_creates_directory(self, temp_dir):
        """Test that ProgressManager creates progress directory"""
        progress_dir = os.path.join(temp_dir, 'progress')
        
        manager = ProgressManager(progress_dir)
        
        assert os.path.exists(progress_dir)
        assert manager.progress_dir == progress_dir
    
    def test_load_progress_no_file(self, temp_dir):
        """Test loading progress when file doesn't exist returns empty progress"""
        progress_dir = os.path.join(temp_dir, 'progress')
        
        manager = ProgressManager(progress_dir)
        progress = manager.load_progress('transfer_123')
        
        # Should return empty progress, not None
        assert progress is not None
        assert progress['transfer_id'] == 'transfer_123'
        assert progress['total_sent'] == 0
        assert progress['sent_message_ids'] == []
    
    def test_save_and_load_progress(self, temp_dir):
        """Test saving and loading progress"""
        progress_dir = os.path.join(temp_dir, 'progress')
        
        manager = ProgressManager(progress_dir)
        
        # Create progress dict
        progress_data = {
            'transfer_id': 'transfer_123',
            'sent_message_ids': [1, 2, 3, 4, 5],
            'last_message_id': 5,
            'total_sent': 5,
            'total_skipped': 0
        }
        
        # Save progress
        manager.save_progress('transfer_123', progress_data)
        
        # Load progress
        loaded = manager.load_progress('transfer_123')
        
        assert loaded is not None
        assert loaded['last_message_id'] == 5
        assert loaded['total_sent'] == 5
        assert len(loaded['sent_message_ids']) == 5
    
    def test_update_progress(self, temp_dir):
        """Test updating progress with new messages"""
        progress_dir = os.path.join(temp_dir, 'progress')
        
        manager = ProgressManager(progress_dir)
        
        # Update with successful message
        manager.update_progress('transfer_123', 1, success=True)
        manager.update_progress('transfer_123', 2, success=True)
        
        # Load and verify
        progress = manager.load_progress('transfer_123')
        
        assert progress['last_message_id'] == 2
        assert progress['total_sent'] == 2
        assert 1 in progress['sent_message_ids']
        assert 2 in progress['sent_message_ids']
    
    def test_update_progress_skip(self, temp_dir):
        """Test updating progress with skipped messages"""
        progress_dir = os.path.join(temp_dir, 'progress')
        
        manager = ProgressManager(progress_dir)
        
        # Update with skipped message
        manager.update_progress('transfer_123', 1, success=False)
        
        # Load and verify
        progress = manager.load_progress('transfer_123')
        
        assert progress['total_skipped'] == 1
        assert progress['total_sent'] == 0
    
    def test_delete_progress(self, temp_dir):
        """Test deleting progress"""
        progress_dir = os.path.join(temp_dir, 'progress')
        
        manager = ProgressManager(progress_dir)
        
        # Create progress
        progress_data = {
            'transfer_id': 'transfer_123',
            'sent_message_ids': [1, 2, 3],
            'last_message_id': 3,
            'total_sent': 3,
            'total_skipped': 0
        }
        manager.save_progress('transfer_123', progress_data)
        
        # Verify it exists
        progress_path = manager.get_progress_path('transfer_123')
        assert os.path.exists(progress_path)
        
        # Delete progress
        manager.delete_progress('transfer_123')
        
        # Verify it's deleted
        assert not os.path.exists(progress_path)
    
    def test_get_progress_path(self, temp_dir):
        """Test getting progress file path"""
        progress_dir = os.path.join(temp_dir, 'progress')
        
        manager = ProgressManager(progress_dir)
        
        transfer_id = 'transfer_123'
        path = manager.get_progress_path(transfer_id)
        
        expected = os.path.join(progress_dir, f'{transfer_id}_progress.json')
        assert path == expected
    
    def test_get_sent_message_ids(self, temp_dir):
        """Test getting sent message IDs as a set"""
        progress_dir = os.path.join(temp_dir, 'progress')
        
        manager = ProgressManager(progress_dir)
        
        # Add some messages
        manager.update_progress('transfer_123', 1, success=True)
        manager.update_progress('transfer_123', 2, success=True)
        manager.update_progress('transfer_123', 3, success=True)
        
        # Get sent IDs
        sent_ids = manager.get_sent_message_ids('transfer_123')
        
        assert isinstance(sent_ids, set)
        assert len(sent_ids) == 3
        assert 1 in sent_ids
        assert 2 in sent_ids
        assert 3 in sent_ids
    
    def test_get_last_message_id(self, temp_dir):
        """Test getting last message ID"""
        progress_dir = os.path.join(temp_dir, 'progress')
        
        manager = ProgressManager(progress_dir)
        
        # Initially should be 0
        last_id = manager.get_last_message_id('transfer_123')
        assert last_id == 0
        
        # Add messages
        manager.update_progress('transfer_123', 5, success=True)
        manager.update_progress('transfer_123', 10, success=True)
        
        # Should return the last one
        last_id = manager.get_last_message_id('transfer_123')
        assert last_id == 10

