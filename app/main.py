"""
Main Application Entry Point
Telegram Backup Android App v3.0
"""
import os
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivymd.app import MDApp

from app.config import Config
from app.managers.account_manager import AccountManager
from app.managers.progress_manager import ProgressManager
from app.managers.transfer_manager import TransferManager
from app.screens.accounts_screen import AccountsScreen
from app.screens.action_screen import ActionScreen
from app.screens.transfer_screen import TransferScreen
from app.screens.log_screen import LogScreen
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
        # Set theme
        self.theme_cls.primary_palette = "Lavender"  # Better contrast in Dark
        self.theme_cls.theme_style = "Dark" # Force Dark to match black background
        
        # Bind back button
        Window.bind(on_keyboard=self.on_keyboard)
        
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
        sm.add_widget(LogScreen(name='logs'))
        
        logger.info("App initialized successfully")
        add_breadcrumb("App started")
        
        return sm
    
    def setup_config(self):
        """Setup configuration with base directory"""
        # Use user_data_dir which works on Android (private files) and Desktop
        base_dir = self.user_data_dir
        
        # Ensure directory exists
        if not os.path.exists(base_dir):
            os.makedirs(base_dir, exist_ok=True)
            
        logger.info(f"Using application directory: {base_dir}")
        
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


    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        """Handle hardware key events"""
        if key == 27:  # Back button / Escape
            sm = self.root
            current_screen = sm.current_screen
            
            # If on Action (Home) screen, let system handle it (Minimize/Exit)
            if sm.current == 'action':
                return False
                
            # Check if screen has a 'go_back' method
            if hasattr(current_screen, 'go_back'):
                current_screen.go_back()
                return True
                
            # Fallback: Go to action screen
            sm.current = 'action'
            return True
            
        return False

if __name__ == '__main__':
    TelegramBackupApp().run()
