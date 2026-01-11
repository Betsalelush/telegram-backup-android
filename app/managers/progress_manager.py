# -*- coding: utf-8 -*-
"""
Progress Manager
Manages transfer progress tracking and persistence
Based on tor.py architecture
"""

import json
import os
import logging
from typing import Dict, Set, Optional

logger = logging.getLogger(__name__)

class ProgressManager:
    """Manages transfer progress"""
    
    def __init__(self, progress_dir: str):
        """
        Initialize ProgressManager
        
        Args:
            progress_dir: Directory for progress files
        """
        self.progress_dir = progress_dir
        
        # Create progress directory if it doesn't exist
        os.makedirs(self.progress_dir, exist_ok=True)
    
    def get_progress_path(self, transfer_id: str) -> str:
        """
        Get progress file path for a transfer
        
        Args:
            transfer_id: Transfer ID
            
        Returns:
            Full path to progress file
        """
        return os.path.join(self.progress_dir, f'{transfer_id}_progress.json')
    
    def load_progress(self, transfer_id: str) -> Dict:
        """
        Load progress for a transfer
        
        Args:
            transfer_id: Transfer ID
            
        Returns:
            Progress dict with sent_message_ids, last_message_id, etc.
        """
        progress_path = self.get_progress_path(transfer_id)
        
        if os.path.exists(progress_path):
            try:
                with open(progress_path, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                logger.info(f"Loaded progress for {transfer_id}: {progress.get('total_sent', 0)} messages")
                return progress
            except Exception as e:
                logger.error(f"Error loading progress for {transfer_id}: {e}")
                return self._create_empty_progress(transfer_id)
        else:
            return self._create_empty_progress(transfer_id)
    
    def save_progress(self, transfer_id: str, progress: Dict):
        """
        Save progress for a transfer
        
        Args:
            transfer_id: Transfer ID
            progress: Progress dict
        """
        progress_path = self.get_progress_path(transfer_id)
        
        try:
            # Update timestamp
            from datetime import datetime
            progress['last_updated'] = datetime.now().isoformat()
            
            with open(progress_path, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Saved progress for {transfer_id}")
        except Exception as e:
            logger.error(f"Error saving progress for {transfer_id}: {e}")
    
    def update_progress(self, transfer_id: str, message_id: int, success: bool = True):
        """
        Update progress with a new message
        
        Args:
            transfer_id: Transfer ID
            message_id: Message ID
            success: Whether message was sent successfully
        """
        progress = self.load_progress(transfer_id)
        
        if success:
            progress['sent_message_ids'].append(message_id)
            progress['last_message_id'] = message_id
            progress['total_sent'] += 1
        else:
            progress['total_skipped'] += 1
        
        self.save_progress(transfer_id, progress)
    
    def get_sent_message_ids(self, transfer_id: str) -> Set[int]:
        """
        Get set of sent message IDs
        
        Args:
            transfer_id: Transfer ID
            
        Returns:
            Set of message IDs
        """
        progress = self.load_progress(transfer_id)
        return set(progress.get('sent_message_ids', []))
    
    def get_last_message_id(self, transfer_id: str) -> int:
        """
        Get last processed message ID
        
        Args:
            transfer_id: Transfer ID
            
        Returns:
            Last message ID or 0
        """
        progress = self.load_progress(transfer_id)
        return progress.get('last_message_id', 0)
    
    def _create_empty_progress(self, transfer_id: str) -> Dict:
        """
        Create empty progress dict
        
        Args:
            transfer_id: Transfer ID
            
        Returns:
            Empty progress dict
        """
        from datetime import datetime
        return {
            'transfer_id': transfer_id,
            'sent_message_ids': [],
            'last_message_id': 0,
            'total_sent': 0,
            'total_skipped': 0,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
    
    def delete_progress(self, transfer_id: str):
        """
        Delete progress file
        
        Args:
            transfer_id: Transfer ID
        """
        progress_path = self.get_progress_path(transfer_id)
        
        if os.path.exists(progress_path):
            try:
                os.remove(progress_path)
                logger.info(f"Deleted progress for {transfer_id}")
            except Exception as e:
                logger.error(f"Error deleting progress for {transfer_id}: {e}")
