# -*- coding: utf-8 -*-
"""
Storage Optimization Module
Provides compression and storage management features
Implements storage optimization (MASTER_PLAN Objective 3)
"""

import os
import json
import gzip
import shutil
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class StorageManager:
    """
    Manages storage optimization including compression and cleanup
    """
    
    def __init__(self, base_dir: str):
        """
        Initialize storage manager
        
        Args:
            base_dir: Base directory for storage management
        """
        self.base_dir = base_dir
    
    def compress_file(self, file_path: str, remove_original: bool = False) -> Optional[str]:
        """
        Compress a file using gzip
        
        Args:
            file_path: Path to file to compress
            remove_original: Whether to remove original file after compression
            
        Returns:
            Path to compressed file or None on error
        """
        compressed_path = file_path + '.gz'
        
        try:
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb', compresslevel=6) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            original_size = os.path.getsize(file_path)
            compressed_size = os.path.getsize(compressed_path)
            ratio = (1 - compressed_size / original_size) * 100
            
            logger.info(f"Compressed {file_path}: {original_size} -> {compressed_size} bytes ({ratio:.1f}% reduction)")
            
            if remove_original:
                os.remove(file_path)
                logger.info(f"Removed original file: {file_path}")
            
            return compressed_path
        except Exception as e:
            logger.error(f"Compression failed for {file_path}: {e}")
            if os.path.exists(compressed_path):
                os.remove(compressed_path)
            return None
    
    def decompress_file(self, compressed_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Decompress a gzip file
        
        Args:
            compressed_path: Path to compressed file
            output_path: Path for decompressed file (defaults to compressed_path without .gz)
            
        Returns:
            Path to decompressed file or None on error
        """
        if output_path is None:
            output_path = compressed_path.rstrip('.gz')
        
        try:
            with gzip.open(compressed_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            logger.info(f"Decompressed {compressed_path} -> {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Decompression failed for {compressed_path}: {e}")
            return None
    
    def compress_json(self, data: Any) -> bytes:
        """
        Compress JSON data to bytes
        
        Args:
            data: Data to serialize and compress
            
        Returns:
            Compressed bytes
        """
        json_str = json.dumps(data, ensure_ascii=False)
        return gzip.compress(json_str.encode('utf-8'))
    
    def decompress_json(self, compressed_data: bytes) -> Any:
        """
        Decompress JSON data from bytes
        
        Args:
            compressed_data: Compressed bytes
            
        Returns:
            Deserialized data
        """
        json_str = gzip.decompress(compressed_data).decode('utf-8')
        return json.loads(json_str)
    
    def get_directory_size(self, directory: str) -> int:
        """
        Calculate total size of directory
        
        Args:
            directory: Directory path
            
        Returns:
            Size in bytes
        """
        total_size = 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception as e:
            logger.error(f"Error calculating directory size for {directory}: {e}")
        
        return total_size
    
    def format_size(self, size_bytes: int) -> str:
        """
        Format byte size to human-readable string
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def cleanup_old_files(self, directory: str, days: int = 30) -> int:
        """
        Remove files older than specified days
        
        Args:
            directory: Directory to clean
            days: Age threshold in days
            
        Returns:
            Number of files removed
        """
        removed_count = 0
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    
                    if os.path.exists(filepath):
                        mtime = os.path.getmtime(filepath)
                        
                        if mtime < cutoff_time:
                            os.remove(filepath)
                            removed_count += 1
                            logger.info(f"Removed old file: {filepath}")
        except Exception as e:
            logger.error(f"Error during cleanup of {directory}: {e}")
        
        return removed_count
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Dictionary with storage stats
        """
        stats = {
            'base_dir': self.base_dir,
            'total_size': 0,
            'total_size_formatted': '0 B',
            'subdirs': {}
        }
        
        if not os.path.exists(self.base_dir):
            return stats
        
        # Calculate total size
        total_size = self.get_directory_size(self.base_dir)
        stats['total_size'] = total_size
        stats['total_size_formatted'] = self.format_size(total_size)
        
        # Calculate size per subdirectory
        try:
            for item in os.listdir(self.base_dir):
                item_path = os.path.join(self.base_dir, item)
                
                if os.path.isdir(item_path):
                    dir_size = self.get_directory_size(item_path)
                    stats['subdirs'][item] = {
                        'size': dir_size,
                        'size_formatted': self.format_size(dir_size)
                    }
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
        
        return stats
    
    def optimize_progress_files(self, progress_dir: str, max_ids: int = 10000) -> int:
        """
        Optimize progress files by limiting stored message IDs
        
        Args:
            progress_dir: Directory containing progress files
            max_ids: Maximum number of message IDs to keep
            
        Returns:
            Number of files optimized
        """
        optimized_count = 0
        
        try:
            for filename in os.listdir(progress_dir):
                if not filename.endswith('_progress.json'):
                    continue
                
                filepath = os.path.join(progress_dir, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        progress = json.load(f)
                    
                    sent_ids = progress.get('sent_message_ids', [])
                    
                    if len(sent_ids) > max_ids:
                        # Keep only most recent message IDs
                        progress['sent_message_ids'] = sent_ids[-max_ids:]
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(progress, f, ensure_ascii=False, indent=2)
                        
                        optimized_count += 1
                        logger.info(f"Optimized {filename}: {len(sent_ids)} -> {max_ids} IDs")
                except Exception as e:
                    logger.error(f"Error optimizing {filename}: {e}")
        except Exception as e:
            logger.error(f"Error accessing progress directory {progress_dir}: {e}")
        
        return optimized_count
    
    def create_backup(self, source_dir: str, backup_path: str) -> bool:
        """
        Create compressed backup of directory
        
        Args:
            source_dir: Directory to backup
            backup_path: Path for backup file (will add .tar.gz)
            
        Returns:
            True if successful
        """
        try:
            import tarfile
            
            if not backup_path.endswith('.tar.gz'):
                backup_path += '.tar.gz'
            
            with tarfile.open(backup_path, 'w:gz') as tar:
                tar.add(source_dir, arcname=os.path.basename(source_dir))
            
            size = os.path.getsize(backup_path)
            logger.info(f"Created backup: {backup_path} ({self.format_size(size)})")
            return True
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return False
    
    def restore_backup(self, backup_path: str, restore_dir: str) -> bool:
        """
        Restore from compressed backup
        
        Args:
            backup_path: Path to backup file
            restore_dir: Directory to restore to
            
        Returns:
            True if successful
        """
        try:
            import tarfile
            
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(path=restore_dir)
            
            logger.info(f"Restored backup from {backup_path} to {restore_dir}")
            return True
        except Exception as e:
            logger.error(f"Backup restore failed: {e}")
            return False


# Global instance
_default_storage_manager = None

def get_storage_manager(base_dir: Optional[str] = None) -> StorageManager:
    """
    Get default storage manager instance
    
    Args:
        base_dir: Base directory (uses current if None)
        
    Returns:
        StorageManager instance
    """
    global _default_storage_manager
    
    if _default_storage_manager is None or base_dir is not None:
        if base_dir is None:
            base_dir = os.getcwd()
        _default_storage_manager = StorageManager(base_dir)
    
    return _default_storage_manager
