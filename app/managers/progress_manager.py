"""
Progress Manager
Manages transfer progress tracking
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from ..config import Config
from ..utils.logger import logger, add_breadcrumb, capture_exception


class ProgressManager:
    """
    Manages transfer progress
    
    Features:
    - Save/load progress per transfer
    - Track sent message IDs
    - Resume from last position
    - Cleanup old progress
    """
    
    def __init__(self, progress_dir: str):
        """
        Initialize Progress Manager
        
        Args:
            progress_dir: Directory for progress files
        """
        self.progress_dir = progress_dir
        os.makedirs(progress_dir, exist_ok=True)
        
        add_breadcrumb("ProgressManager initialized")
    
    def get_progress_key(self, source_id: str, target_id: str) -> str:
        """
        Create unique key for source→target channel pair
        
        Args:
            source_id: Source channel ID
            target_id: Target channel ID
            
        Returns:
            str: Unique progress key
        """
        return f"channel_{source_id}_to_{target_id}"
    
    def load_progress(self, source_id: str, target_id: str) -> Dict:
        """
        Load progress for specific channel pair
        
        Args:
            source_id: Source channel ID
            target_id: Target channel ID
            
        Returns:
            Dict: Progress data with sent_message_ids and last_message_id
        """
        key = self.get_progress_key(source_id, target_id)
        progress_file = os.path.join(self.progress_dir, f'{key}.json')
        
        if not os.path.exists(progress_file):
            logger.info(f"No progress found for {key}, starting fresh")
            return {
                'sent_message_ids': [],
                'last_message_id': 0,
                'total_sent': 0,
                'total_skipped': 0,
                'last_updated': None
            }
        
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
            
            logger.info(f"Loaded progress for {key}: {progress['total_sent']} messages sent")
            add_breadcrumb("Progress loaded", {
                "key": key,
                "total_sent": progress['total_sent']
            })
            
            return progress
            
        except Exception as e:
            logger.error(f"Error loading progress for {key}: {e}")
            capture_exception(e, extra_data={"key": key, "source_id": source_id, "target_id": target_id, "context": "load_progress"})
            return {
                'sent_message_ids': [],
                'last_message_id': 0,
                'total_sent': 0,
                'total_skipped': 0,
                'last_updated': None
            }
    
    def save_progress(self, source_id: str, target_id: str, 
                     sent_message_ids: List[int], last_message_id: int,
                     total_sent: int = 0, total_skipped: int = 0):
        """
        Save progress for specific channel pair
        
        Args:
            source_id: Source channel ID
            target_id: Target channel ID
            sent_message_ids: List of sent message IDs
            last_message_id: Last processed message ID
            total_sent: Total messages sent
            total_skipped: Total messages skipped
            
        Returns:
            bool: True if saved successfully
        """
        key = self.get_progress_key(source_id, target_id)
        progress_file = os.path.join(self.progress_dir, f'{key}.json')
        
        try:
            # Limit size if too large
            if len(sent_message_ids) > Config.MAX_PROGRESS_ITEMS:
                logger.warning(f"Progress too large ({len(sent_message_ids)} items), trimming to {Config.MAX_PROGRESS_ITEMS}")
                # Keep most recent items
                sent_message_ids = sent_message_ids[-Config.MAX_PROGRESS_ITEMS:]
            
            progress = {
                'sent_message_ids': sent_message_ids,
                'last_message_id': last_message_id,
                'total_sent': total_sent,
                'total_skipped': total_skipped,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved progress for {key}: {total_sent} sent, {total_skipped} skipped")
            add_breadcrumb("Progress saved", {
                "key": key,
                "total_sent": total_sent,
                "total_skipped": total_skipped
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving progress for {key}: {e}")
            capture_exception(e, extra_data={"key": key, "source_id": source_id, "target_id": target_id, "total_sent": total_sent, "context": "save_progress"})
            return False
    
    def get_all_progress(self) -> Dict[str, Dict]:
        """
        Get all progress files
        
        Returns:
            Dict[str, Dict]: Dictionary of all progress data
        """
        all_progress = {}
        
        try:
            for filename in os.listdir(self.progress_dir):
                if filename.endswith('.json'):
                    key = filename[:-5]  # Remove .json
                    filepath = os.path.join(self.progress_dir, filename)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            all_progress[key] = json.load(f)
                    except Exception as e:
                        logger.error(f"Error loading {filename}: {e}")
                        capture_exception(e, extra_data={"filename": filename, "context": "get_all_progress"})
            
            logger.info(f"Loaded {len(all_progress)} progress files")
            return all_progress
            
        except Exception as e:
            logger.error(f"Error getting all progress: {e}")
            capture_exception(e, extra_data={"context": "get_all_progress"})
            return {}
    
    def clear_progress(self, source_id: str, target_id: str) -> bool:
        """
        Clear progress for specific channel pair
        
        Args:
            source_id: Source channel ID
            target_id: Target channel ID
            
        Returns:
            bool: True if cleared successfully
        """
        key = self.get_progress_key(source_id, target_id)
        progress_file = os.path.join(self.progress_dir, f'{key}.json')
        
        try:
            if os.path.exists(progress_file):
                os.remove(progress_file)
                logger.info(f"Cleared progress for {key}")
                add_breadcrumb("Progress cleared", {"key": key})
                return True
            else:
                logger.warning(f"No progress file to clear for {key}")
                return False
                
        except Exception as e:
            logger.error(f"Error clearing progress for {key}: {e}")
            capture_exception(e, extra_data={"key": key, "source_id": source_id, "target_id": target_id, "context": "clear_progress"})
            return False
    
    def update_progress(self, source_id: str, target_id: str, message_id: int):
        """
        Update progress with new message
        
        Args:
            source_id: Source channel ID
            target_id: Target channel ID
            message_id: Message ID that was sent
        """
        # Load current progress
        progress = self.load_progress(source_id, target_id)
        
        # Update
        if message_id not in progress['sent_message_ids']:
            progress['sent_message_ids'].append(message_id)
            progress['total_sent'] += 1
        
        if message_id > progress['last_message_id']:
            progress['last_message_id'] = message_id
        
        # Save
        self.save_progress(
            source_id, target_id,
            progress['sent_message_ids'],
            progress['last_message_id'],
            progress['total_sent'],
            progress['total_skipped']
        )
    
    def cleanup_old_progress(self, days: int = 30) -> int:
        """
        Cleanup progress files older than specified days
        
        Args:
            days: Number of days to keep
            
        Returns:
            int: Number of files deleted
        """
        deleted = 0
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        try:
            for filename in os.listdir(self.progress_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.progress_dir, filename)
                    
                    # Check file age
                    if os.path.getmtime(filepath) < cutoff:
                        os.remove(filepath)
                        deleted += 1
                        logger.info(f"Deleted old progress file: {filename}")
            
            if deleted > 0:
                add_breadcrumb("Old progress cleaned", {"deleted": deleted})
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error cleaning old progress: {e}")
            capture_exception(e, extra_data={"days": days, "context": "cleanup_old_progress"})
            return 0
