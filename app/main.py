"""
Main Application Entry Point
Telegram Backup Android App v3.0
"""
import os
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from app.config import Config
from app.managers.account_manager import AccountManager
from app.managers.progress_manager import ProgressManager
from app.managers.transfer_manager import TransferManager
from app.screens.accounts_screen import AccountsScreen
from app.screens.action_screen import ActionScreen
from app.screens.transfer_screen import TransferScreen
from app.utils.logger import logger, init_sentry, add_breadcrumb


class TelegramBackupApp(MDApp):
    """
    Main Application Class
    
    Features:
    - Multi-screen navigation
    - Account management
    - Transfer management
    - Progress tracking
    - Sentry integration
    """
    
    def build(self):
        """Build application"""
        # Set theme
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # Setup configuration
        self.setup_config()
        
        # Initialize Sentry
        init_sentry()
        
        # Initialize managers
        self.account_manager = AccountManager(
            Config.ACCOUNTS_FILE,
            Config.SESSIONS_DIR
        )
        
        self.progress_manager = ProgressManager(
            Config.PROGRESS_DIR
        )
        
        self.transfer_manager = TransferManager()
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(ActionScreen(name='action'))
        sm.add_widget(AccountsScreen(
            self.account_manager,
            name='accounts'
        ))
        sm.add_widget(TransferScreen(
            self.account_manager,
            self.transfer_manager,
            self.progress_manager,
            name='transfer'
        ))
        
        logger.info("App initialized successfully")
        add_breadcrumb("App started")
        
        return sm
    
    def setup_config(self):
        """Setup configuration with base directory"""
        try:
            # Try Android storage
            from android.storage import app_storage_path
            base_dir = app_storage_path()
            logger.info(f"Android: Using directory {base_dir}")
        except ImportError:
            # Desktop - use current directory
            base_dir = os.getcwd()
            logger.info(f"Desktop: Using directory {base_dir}")
        
        # Setup config
        Config.setup(base_dir)
        
        add_breadcrumb("Config setup", {"base_dir": base_dir})
    
    def on_start(self):
        """Called when app starts"""
        logger.info("App started")
        add_breadcrumb("App on_start")
    
    def on_stop(self):
        """Called when app stops"""
        logger.info("App stopped")
        add_breadcrumb("App on_stop")
        
        # Disconnect all accounts
        import asyncio
        for account in self.account_manager.get_connected_accounts():
            asyncio.create_task(
                self.account_manager.disconnect_account(account['id'])
            )


if __name__ == '__main__':
    TelegramBackupApp().run()
