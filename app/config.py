# -*- coding: utf-8 -*-
"""
Configuration Management
Centralized configuration for the Telegram Backup Android App
"""

import os

class Config:
    """Application configuration"""
    
    # App Info
    APP_NAME = "Telegram Backup"
    APP_VERSION = "3.0.0"
    
    # Sentry Configuration
    SENTRY_DSN = "https://1f490b846ede82cfc3d5f6f5eb23263b@o4510215210598400.ingest.de.sentry.io/4510674676744272"
    SENTRY_TRACES_SAMPLE_RATE = 1.0
    SENTRY_PROFILES_SAMPLE_RATE = 1.0
    SENTRY_MAX_BREADCRUMBS = 100
    
    # Paths (set at runtime)
    BASE_DIR = None
    SESSIONS_DIR = None
    PROGRESS_DIR = None
    ACCOUNTS_FILE = None
    TRANSFERS_FILE = None
    
    # Telegram Settings
    MAX_MESSAGES_PER_MINUTE = 20
    SMART_DELAY_MIN = 2  # seconds
    SMART_DELAY_MAX = 8  # seconds
    CONSECUTIVE_SUCCESSES_THRESHOLD = 20  # for aggressive delay
    
    # Progress Settings
    SAVE_PROGRESS_EVERY = 10  # messages
    MAX_SENT_MESSAGE_IDS = 100000  # keep last N message IDs
    
    # UI Settings
    DEFAULT_THEME = "Light"
    PRIMARY_PALETTE = "Blue"
    
    @classmethod
    def setup(cls, base_dir):
        """
        Setup configuration with base directory
        
        Args:
            base_dir: Base directory for data storage
        """
        cls.BASE_DIR = base_dir
        cls.SESSIONS_DIR = os.path.join(base_dir, 'data', 'sessions')
        cls.PROGRESS_DIR = os.path.join(base_dir, 'data', 'progress')
        cls.ACCOUNTS_FILE = os.path.join(base_dir, 'data', 'accounts.json')
        cls.TRANSFERS_FILE = os.path.join(base_dir, 'data', 'transfers.json')
        
        # Create directories if they don't exist
        os.makedirs(cls.SESSIONS_DIR, exist_ok=True)
        os.makedirs(cls.PROGRESS_DIR, exist_ok=True)
    
    @classmethod
    def get_session_path(cls, phone):
        """
        Get session file path for a phone number
        
        Args:
            phone: Phone number (e.g., "+972123456789")
            
        Returns:
            Full path to session file
        """
        session_name = f'session_{phone.replace("+", "")}'
        return os.path.join(cls.SESSIONS_DIR, session_name)
    
    @classmethod
    def get_progress_path(cls, transfer_id):
        """
        Get progress file path for a transfer
        
        Args:
            transfer_id: Transfer ID
            
        Returns:
            Full path to progress file
        """
        return os.path.join(cls.PROGRESS_DIR, f'{transfer_id}_progress.json')
