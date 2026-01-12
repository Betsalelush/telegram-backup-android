# -*- coding: utf-8 -*-
"""
Telegram Backup Android App v3.0
Main application entry point with modular architecture
"""

import asyncio
import os
import sys
import threading
import logging

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager

# Import configuration
from app.config import Config
from app.utils.logger import logger, add_breadcrumb
from app.screens.login_screen import LoginScreen
from app.screens.backup_screen import BackupScreen

# KivyMD Layout (minimal - screens have their own KV)
KV = '''
ScreenManager:
    id: screen_manager
    
    LoginScreen:
        name: 'login'
    
    BackupScreen:
        name: 'backup'
'''


class TelegramBackupApp(MDApp):
    """Main application class with modular architecture"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.worker_thread = None
        self.worker_loop = None
    
    def build(self):
        """Build the application"""
        # Set theme
        self.theme_cls.primary_palette = Config.PRIMARY_PALETTE
        self.theme_cls.theme_style = Config.DEFAULT_THEME
        
        # Setup configuration
        self.setup_config()
        
        # Setup worker thread for async operations
        self.setup_worker_thread()
        
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
    
    def setup_worker_thread(self):
        """Setup persistent worker thread for async operations"""
        def worker():
            """Worker thread with persistent event loop"""
            self.worker_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.worker_loop)
            self.worker_loop.run_forever()
        
        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()
        
        add_breadcrumb('worker', 'Worker thread started', 'info')
        logger.info("Worker thread initialized")
    
    def run_in_worker(self, coro):
        """
        Run coroutine in worker thread
        
        Args:
            coro: Coroutine to run
        """
        if self.worker_loop:
            asyncio.run_coroutine_threadsafe(coro, self.worker_loop)
    
    def on_stop(self):
        """Called when app is closing"""
        add_breadcrumb('app', 'Application stopping', 'info')
        logger.info("Application stopped")
        
        # Stop worker loop
        if self.worker_loop:
            self.worker_loop.call_soon_threadsafe(self.worker_loop.stop)


if __name__ == '__main__':
    TelegramBackupApp().run()
