# -*- coding: utf-8 -*-
"""
Login Screen - Telegram Authentication
Handles send_code, login, and disconnect functionality
"""

import asyncio
import logging
from kivymd.uix.screen import MDScreen
from app.config import Config
from app.utils.logger import add_breadcrumb, capture_exception

logger = logging.getLogger(__name__)


class LoginScreen(MDScreen):
    """Screen for Telegram login and authentication"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = None
        self.phone_code_hash = None
    
    def send_code(self):
        """Send verification code to phone number"""
        add_breadcrumb('auth', 'Starting send_code', 'info')
        
        api_id = self.ids.api_id.text
        api_hash = self.ids.api_hash.text
        phone = self.ids.phone.text
        
        if not api_id or not api_hash or not phone:
            self.log("Please fill all fields")
            return
        
        # Validate API ID
        try:
            api_id_int = int(api_id)
            if not (-2147483648 <= api_id_int <= 2147483647):
                self.log("ERROR: API ID must be between -2147483648 and 2147483647")
                self.update_status("Invalid API ID", "Error")
                return
        except ValueError:
            self.log("ERROR: API ID must be a number")
            self.update_status("Invalid API ID", "Error")
            return
        
        # Run async
        from kivy.app import App
        app = App.get_running_app()
        app.worker_loop.call_soon_threadsafe(
            asyncio.ensure_future,
            self._send_code_async(api_id_int, api_hash, phone),
            app.worker_loop
        )
    
    async def _send_code_async(self, api_id, api_hash, phone):
        """Async send code implementation"""
        try:
            # Lazy import Telethon
            from telethon import TelegramClient
            
            self.log("Connecting to Telegram...")
            self.update_status("Connecting...", "Secondary")
            
            # Create client
            self.client = TelegramClient('session', api_id, api_hash)
            
            add_breadcrumb('auth', f'Connecting to Telegram for {phone}', 'info')
            await self.client.connect()
            
            # Send code
            self.log("Sending code...")
            result = await self.client.send_code_request(phone)
            self.phone_code_hash = result.phone_code_hash
            
            add_breadcrumb('auth', 'Code sent successfully', 'info')
            self.log("Code sent! Please enter it...")
            self.update_status("Code sent", "Primary")
            
            # Enable login button
            from kivy.clock import Clock
            def enable_login(dt):
                self.ids.login_btn.disabled = False
                self.ids.code.disabled = False
                self.ids.password.disabled = False
            Clock.schedule_once(enable_login)
            
        except Exception as e:
            error_msg = f"ERROR sending code: {e}"
            self.log(error_msg)
            self.update_status("Error sending code", "Error")
            capture_exception(e)
            
            # Re-enable send button on error
            from kivy.clock import Clock
            def enable_send(dt):
                self.ids.send_btn.disabled = False
            Clock.schedule_once(enable_send)
    
    def login(self):
        """Login with verification code"""
        add_breadcrumb('auth', 'Starting login', 'info')
        
        code = self.ids.code.text
        password = self.ids.password.text
        
        if not code:
            self.log("Please enter code")
            return
        
        # Run async
        from kivy.app import App
        app = App.get_running_app()
        app.worker_loop.call_soon_threadsafe(
            asyncio.ensure_future,
            self._login_async(code, password),
            app.worker_loop
        )
    
    async def _login_async(self, code, password):
        """Async login implementation"""
        try:
            self.log("Logging in...")
            self.update_status("Logging in...", "Secondary")
            
            # Try to sign in
            try:
                await self.client.sign_in(code=code)
            except Exception as e:
                # Check if 2FA is needed
                if "SessionPasswordNeededError" in str(type(e).__name__):
                    if not password:
                        self.log("2FA password required!")
                        self.update_status("2FA required", "Error")
                        return
                    
                    self.log("Entering 2FA password...")
                    await self.client.sign_in(password=password)
                else:
                    raise
            
            # Get user info
            me = await self.client.get_me()
            
            add_breadcrumb('auth', f'Login successful: {me.first_name}', 'info')
            self.log(f"Logged in as: {me.first_name}")
            self.update_status("Logged in", "Primary")
            
            # Enable backup controls
            from kivy.clock import Clock
            def enable_backup(dt):
                self.ids.source.disabled = False
                self.ids.target.disabled = False
                self.ids.start_id.disabled = False
                self.ids.start_btn.disabled = False
                self.ids.disconnect_btn.disabled = False
                self.ids.connection_status.text = "Status: Connected"
                self.ids.connection_status.theme_text_color = "Primary"
            Clock.schedule_once(enable_backup)
            
        except Exception as e:
            error_msg = f"ERROR logging in: {e}"
            self.log(error_msg)
            self.update_status("Login failed", "Error")
            capture_exception(e)
    
    def disconnect(self):
        """Disconnect from Telegram"""
        if self.client:
            from kivy.app import App
            app = App.get_running_app()
            app.worker_loop.call_soon_threadsafe(
                asyncio.ensure_future,
                self.client.disconnect(),
                app.worker_loop
            )
            self.log("Disconnected from Telegram")
            self.update_status("Disconnected", "Secondary")
    
    def log(self, message):
        """Add message to log"""
        from kivy.clock import Clock
        def update_log(dt):
            current = self.ids.log.text
            self.ids.log.text = f"{current}\n{message}"
        Clock.schedule_once(update_log)
    
    def update_status(self, text, color):
        """Update status label"""
        from kivy.clock import Clock
        def update(dt):
            self.ids.status.text = text
            self.ids.status.theme_text_color = color
        Clock.schedule_once(update)
