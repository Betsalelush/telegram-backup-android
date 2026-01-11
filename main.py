# -*- coding: utf-8 -*-
"""
Telegram Backup Android App v3.0
Main application entry point with multi-account support
"""

import asyncio
import os
import sys

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager

# Import configuration
from app.config import Config
from app.utils.logger import logger, add_breadcrumb

# KivyMD Layout
KV = '''
ScreenManager:
    id: screen_manager
    
    Screen:
        name: 'main'
        
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(10)
            
            MDLabel:
                text: "Telegram Backup v3.0"
                halign: "center"
                font_style: "H4"
                size_hint_y: None
                height: self.texture_size[1]
            
            MDLabel:
                text: "Multi-Account Support"
                halign: "center"
                font_style: "H6"
                size_hint_y: None
                height: self.texture_size[1]
            
            Widget:
                size_hint_y: 0.3
            
            MDFillRoundFlatButton:
                text: "Manage Accounts"
                pos_hint: {"center_x": .5}
                size_hint_x: 0.8
                on_release: app.show_accounts_screen()
            
            MDFillRoundFlatButton:
                text: "New Transfer"
                pos_hint: {"center_x": .5}
                size_hint_x: 0.8
                on_release: app.show_transfer_screen()
            
            MDFillRoundFlatButton:
                text: "Settings"
                pos_hint: {"center_x": .5}
                size_hint_x: 0.8
                on_release: app.show_settings()
            
            Widget:
                size_hint_y: 0.3
            
            MDLabel:
                text: "Status: Ready"
                id: status_label
                halign: "center"
                size_hint_y: None
                height: "30dp"
'''

class TelegramBackupApp(MDApp):
    """Main application class"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.account_manager = None
        self.progress_manager = None
        self.transfer_manager = None
    
    def build(self):
        """Build the application"""
        # Set theme
        self.theme_cls.primary_palette = Config.PRIMARY_PALETTE
        self.theme_cls.theme_style = Config.DEFAULT_THEME
        
        # Setup configuration
        self.setup_config()
        
        # Initialize managers
        self.init_managers()
        
        # Add breadcrumb
        add_breadcrumb('app', 'Application started', 'info')
        logger.info("Telegram Backup App v3.0 started")
        
        return Builder.load_string(KV)
    
    def setup_config(self):
        """Setup configuration and paths"""
        try:
            # Try Android storage
            from android.storage import app_storage_path
            base_dir = app_storage_path()
            logger.info(f"Android: Using directory {base_dir}")
        except ImportError:
            # Desktop - use current directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
            logger.info(f"Desktop: Using directory {base_dir}")
        
        # Setup config
        Config.setup(base_dir)
        add_breadcrumb('config', f'Configuration setup: {base_dir}', 'info')
    
    def init_managers(self):
        """Initialize all managers"""
        from app.managers import AccountManager, ProgressManager
        
        self.account_manager = AccountManager(
            Config.ACCOUNTS_FILE,
            Config.SESSIONS_DIR
        )
        
        self.progress_manager = ProgressManager(
            Config.PROGRESS_DIR
        )
        
        add_breadcrumb('managers', 'Managers initialized', 'info')
        logger.info("Managers initialized successfully")
    
    def show_accounts_screen(self):
        """Show accounts management screen"""
        add_breadcrumb('navigation', 'Navigate to accounts screen', 'info')
        logger.info("TODO: Show accounts screen")
        # TODO: Implement accounts screen
    
    def show_transfer_screen(self):
        """Show transfer screen"""
        add_breadcrumb('navigation', 'Navigate to transfer screen', 'info')
        logger.info("TODO: Show transfer screen")
        # TODO: Implement transfer screen
    
    def show_settings(self):
        """Show settings screen"""
        add_breadcrumb('navigation', 'Navigate to settings', 'info')
        logger.info("TODO: Show settings")
        # TODO: Implement settings
    
    def on_stop(self):
        """Called when app is closing"""
        add_breadcrumb('app', 'Application stopping', 'info')
        logger.info("Application stopped")
        
        # Disconnect all accounts
        if self.account_manager:
            for account in self.account_manager.get_connected_accounts():
                try:
                    asyncio.create_task(
                        self.account_manager.disconnect_account(account['id'])
                    )
                except Exception as e:
                    logger.error(f"Error disconnecting account: {e}")

if __name__ == '__main__':
    TelegramBackupApp().run()
