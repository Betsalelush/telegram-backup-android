"""
Configuration module for Telegram Backup App
Contains all app settings and constants
"""
import os


class Config:
    """Application configuration"""
    
    # Sentry
    SENTRY_DSN = "https://1f490b846ede82cfc3d5f6f5eb23263b@o4510215210598400.ingest.de.sentry.io/4510674676744272"
    SENTRY_TRACES_SAMPLE_RATE = 1.0
    SENTRY_ENVIRONMENT = "production"
    
    # Paths (will be set at runtime)
    BASE_DIR = None
    SESSIONS_DIR = None
    PROGRESS_DIR = None
    ACCOUNTS_FILE = None
    TRANSFERS_FILE = None
    
    # Telegram Rate Limiting
    MAX_MESSAGES_PER_MINUTE = 20
    SMART_DELAY_MIN = 2
    SMART_DELAY_MAX = 8
    
    # Transfer Settings
    DEFAULT_TRANSFER_METHOD = "download_upload"
    MAX_CONCURRENT_TRANSFERS = 5
    
    # Progress Settings
    MAX_PROGRESS_ITEMS = 10000  # Limit progress file size
    PROGRESS_SAVE_INTERVAL = 10  # Save every N messages
    
    # File Types
    SUPPORTED_FILE_TYPES = {
        'text': True,
        'photos': True,
        'videos': True,
        'documents': True,
        'audio': True,
        'voice': True,
        'stickers': True
    }
    
    @classmethod
    def setup(cls, base_dir):
        """
        Setup configuration with base directory
        
        Args:
            base_dir: Base directory for app data
        """
        cls.BASE_DIR = base_dir
        cls.SESSIONS_DIR = os.path.join(base_dir, 'sessions')
        cls.PROGRESS_DIR = os.path.join(base_dir, 'progress')
        cls.DOWNLOADS_DIR = os.path.join(base_dir, 'downloads') # New download dir
        cls.ACCOUNTS_FILE = os.path.join(base_dir, 'accounts.json')
        cls.TRANSFERS_FILE = os.path.join(base_dir, 'transfers.json')
        
        # Create directories
        os.makedirs(cls.SESSIONS_DIR, exist_ok=True)
        os.makedirs(cls.PROGRESS_DIR, exist_ok=True)
        os.makedirs(cls.DOWNLOADS_DIR, exist_ok=True)
    
    @classmethod
    def get_session_path(cls, phone):
        """
        Get session file path for phone number
        
        Args:
            phone: Phone number
            
        Returns:
            str: Path to session file
        """
        # Remove + and spaces from phone
        clean_phone = phone.replace('+', '').replace(' ', '')
        return os.path.join(cls.SESSIONS_DIR, f'session_{clean_phone}')
    
    @classmethod
    def get_progress_path(cls, transfer_id):
        """
        Get progress file path for transfer
        
        Args:
            transfer_id: Transfer ID
            
        Returns:
            str: Path to progress file
        """
        return os.path.join(cls.PROGRESS_DIR, f'{transfer_id}.json')
