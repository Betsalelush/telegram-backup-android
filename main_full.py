import asyncio
import json
import logging
import os
import queue
import random
import threading
import time
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
import sentry_sdk

# Sentry - תופס crashes!
sentry_sdk.init(
    dsn="https://1f490b846ede82cfc3d5f6f5eb23263b@o4510215210598400.ingest.de.sentry.io/4510674676744272",
    traces_sample_rate=1.0,
)

# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ⚠️ שים לב: Telethon לא נטען כאן! הוא ייטען רק כשצריך (lazy loading)

KV = '''
MDBoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 10

    MDLabel:
        text: "Telegram Backup"
        halign: "center"
        font_style: "H5"
        size_hint_y: None
        height: self.texture_size[1]

    MDScrollView:
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: 15
            padding: 10
            
            MDLabel:
                text: "Get API credentials from: my.telegram.org"
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Primary"
                font_style: "Caption"
            
            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "56dp"
                spacing: 5
                
                MDTextField:
                    id: api_id
                    hint_text: "API ID"
                    mode: "rectangle"
                
                MDIconButton:
                    icon: "content-paste"
                    size_hint: None, None
                    size: "48dp", "48dp"
                    pos_hint: {"center_y": .5}
                    on_release: app.paste_to_field('api_id')

            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "56dp"
                spacing: 5
                
                MDTextField:
                    id: api_hash
                    hint_text: "API HASH"
                    mode: "rectangle"
                
                MDIconButton:
                    icon: "content-paste"
                    size_hint: None, None
                    size: "48dp", "48dp"
                    pos_hint: {"center_y": .5}
                    on_release: app.paste_to_field('api_hash')

            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "56dp"
                spacing: 5
                
                MDTextField:
                    id: phone
                    hint_text: "Phone Number (+972...)"
                    mode: "rectangle"
                
                MDIconButton:
                    icon: "content-paste"
                    size_hint: None, None
                    size: "48dp", "48dp"
                    pos_hint: {"center_y": .5}
                    on_release: app.paste_to_field('phone')

            MDFillRoundFlatButton:
                id: send_code_btn
                text: "Send Verification Code"
                pos_hint: {"center_x": .5}
                on_release: app.send_code()

            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "56dp"
                spacing: 5
                
                MDTextField:
                    id: code
                    hint_text: "Verification Code"
                    mode: "rectangle"
                    disabled: True
                
                MDIconButton:
                    icon: "content-paste"
                    size_hint: None, None
                    size: "48dp", "48dp"
                    pos_hint: {"center_y": .5}
                    on_release: app.paste_to_field('code')
            
            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "56dp"
                spacing: 5
                
                MDTextField:
                    id: two_fa_password
                    hint_text: "2FA Password (if enabled)"
                    mode: "rectangle"
                    password: True
                    disabled: True
                
                MDIconButton:
                    icon: "content-paste"
                    size_hint: None, None
                    size: "48dp", "48dp"
                    pos_hint: {"center_y": .5}
                    on_release: app.paste_to_field('two_fa_password')

            MDFillRoundFlatButton:
                id: login_btn
                text: "Login"
                pos_hint: {"center_x": .5}
                disabled: True
                on_release: app.login()
            
            MDLabel:
                id: connection_status
                text: "Status: Not connected"
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Error"

            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "56dp"
                spacing: 5
                
                MDTextField:
                    id: source_channel
                    hint_text: "Source Channel (ID or Link)"
                    mode: "rectangle"
                
                MDIconButton:
                    icon: "content-paste"
                    size_hint: None, None
                    size: "48dp", "48dp"
                    pos_hint: {"center_y": .5}
                    on_release: app.paste_to_field('source_channel')

            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "56dp"
                spacing: 5
                
                MDTextField:
                    id: target_channel
                    hint_text: "Target Channel (ID or Link)"
                    mode: "rectangle"
                
                MDIconButton:
                    icon: "content-paste"
                    size_hint: None, None
                    size: "48dp", "48dp"
                    pos_hint: {"center_y": .5}
                    on_release: app.paste_to_field('target_channel')
            
            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "56dp"
                spacing: 5
                
                MDTextField:
                    id: start_message_id
                    hint_text: "Start from Message ID (optional, 0 = from beginning)"
                    mode: "rectangle"
                    text: "0"
                
                MDIconButton:
                    icon: "content-paste"
                    size_hint: None, None
                    size: "48dp", "48dp"
                    pos_hint: {"center_y": .5}
                    on_release: app.paste_to_field('start_message_id')
            
            
            MDLabel:
                text: "Select message types to transfer:"
                halign: "left"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Primary"
            
            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "48dp"
                spacing: 10
                
                MDCheckbox:
                    id: cb_text
                    size_hint: None, None
                    size: "48dp", "48dp"
                    active: True
                
                MDLabel:
                    text: "Text"
                    size_hint_y: None
                    height: "48dp"
            
            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "48dp"
                spacing: 10
                
                MDCheckbox:
                    id: cb_photos
                    size_hint: None, None
                    size: "48dp", "48dp"
                    active: True
                
                MDLabel:
                    text: "Photos"
                    size_hint_y: None
                    height: "48dp"
            
            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "48dp"
                spacing: 10
                
                MDCheckbox:
                    id: cb_videos
                    size_hint: None, None
                    size: "48dp", "48dp"
                    active: True
                
                MDLabel:
                    text: "Videos"
                    size_hint_y: None
                    height: "48dp"
            
            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "40dp"
                spacing: 10
                
                MDCheckbox:
                    id: cb_documents
                    size_hint: None, None
                    size: "48dp", "48dp"
                    active: True
                
                MDLabel:
                    text: "Documents (All Files)"
                    size_hint_y: None
                    height: "48dp"
            
            MDSeparator:
                height: "1dp"
            
            MDLabel:
                text: "Transfer Method:"
                halign: "left"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Primary"
                font_style: "Subtitle1"
            
            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "40dp"
                spacing: 10
                
                MDCheckbox:
                    id: method_download_upload
                    group: "transfer_method"
                    size_hint: None, None
                    size: "48dp", "48dp"
                    active: True
                
                MDLabel:
                    text: "Download & Upload (No Credit)"
                    size_hint_y: None
                    height: "40dp"
            
            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "40dp"
                spacing: 10
                
                MDCheckbox:
                    id: method_send_message
                    group: "transfer_method"
                    size_hint: None, None
                    size: "48dp", "48dp"
                
                MDLabel:
                    text: "Send Message (No Credit)"
                    size_hint_y: None
                    height: "40dp"
            
            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: "40dp"
                spacing: 10
                
                MDCheckbox:
                    id: method_forward
                    group: "transfer_method"
                    size_hint: None, None
                    size: "48dp", "48dp"
                
                MDLabel:
                    text: "Forward (With Credit)"
                    size_hint_y: None
                    height: "40dp"

            MDFillRoundFlatButton:
                id: start_btn
                text: "Start Backup"
                pos_hint: {"center_x": .5}
                disabled: True
                on_release: app.start_backup()
            
            MDFillRoundFlatButton:
                id: stop_btn
                text: "Stop Backup"
                pos_hint: {"center_x": .5}
                disabled: True
                md_bg_color: 0.8, 0.2, 0.2, 1
                on_release: app.stop_backup()
            
            MDSeparator:
                height: "1dp"
            
            MDLabel:
                text: "Progress"
                halign: "left"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Primary"
                font_style: "Subtitle1"
            
            MDProgressBar:
                id: progress_bar
                size_hint_y: None
                height: "10dp"
                value: 0
                max: 100
            
            MDLabel:
                id: progress_text
                text: "Progress: 0/0 messages (0%)"
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Primary"
            
            MDLabel:
                id: speed_text
                text: "Speed: 0 msg/s | ETA: --:--"
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Primary"
            
            MDLabel:
                id: current_status
                text: "Status: Ready"
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Primary"
            
            MDSeparator:
                height: "1dp"
            
            MDLabel:
                text: "Log"
                halign: "left"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Primary"
                font_style: "Subtitle1"

            MDLabel:
                id: status_log
                text: "Ready...\\n"
                halign: "left"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Secondary"
'''

class TelegramBackupApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.client = None
        self.phone = None
        self.needs_2fa = False  # Track if we're in 2FA mode
        
        # Worker thread with persistent event loop
        self.worker_loop = None
        self.worker_thread = None
        self.task_queue = queue.Queue()
        self._start_worker_thread()
        
        # שמירת התקדמות
        self.sent_message_ids = set()
        self.last_processed_message_id = 0
        self.consecutive_successes = 0
        
        # מונה הודעות לדקה (מניעת חסימה)
        self.messages_per_minute = 0
        self.max_messages_per_minute = 20
        self.minute_start_time = None
        
        # מעקב התקדמות (גרסה 2.4)
        self.total_messages = 0
        self.processed_messages = 0
        self.start_time = None
        self.messages_per_second = 0
        self.backup_running = False
        
        # תיקון Android: שימוש בתיקיית האפליקציה לקבצי Session
        try:
            from android.storage import app_storage_path
            self.session_dir = app_storage_path()
            logger.info(f"Android: Using directory {self.session_dir}")
        except ImportError:
            # לא Android - שימוש בתיקייה הנוכחית
            self.session_dir = os.getcwd()
            logger.info(f"Desktop: Using directory {self.session_dir}")
        
        # לא טוענים התקדמות כאן - נטען לפי ערוצים ספציפיים
        
        return Builder.load_string(KV)
    
    def _start_worker_thread(self):
        """Start persistent worker thread with event loop"""
        def worker():
            self.worker_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.worker_loop)
            
            async def process_tasks():
                while True:
                    try:
                        task = await asyncio.get_event_loop().run_in_executor(None, self.task_queue.get, True, 0.1)
                        if task is None:  # Shutdown signal
                            break
                        await task()
                    except queue.Empty:
                        continue
                    except Exception as e:
                        logger.error(f"Worker task error: {e}")
                        sentry_sdk.capture_exception(e)
            
            try:
                self.worker_loop.run_until_complete(process_tasks())
            finally:
                self.worker_loop.close()
        
        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()
    
    def run_in_worker(self, coro):
        """Schedule coroutine to run in worker thread's event loop"""
        future = asyncio.run_coroutine_threadsafe(coro, self.worker_loop)
        return future
    
    def get_progress_key(self, source_id, target_id):
        """Create unique key for source→target channel pair"""
        return f"channel_{source_id}_to_{target_id}"
    
    def load_progress(self, source_id, target_id):
        """Load progress for specific channel pair"""
        progress_file = os.path.join(self.session_dir, 'progress.json')
        
        # Load all progress data
        all_progress = {}
        if os.path.exists(progress_file):
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    all_progress = json.load(f)
            except Exception as e:
                logger.error(f"Error loading progress file: {e}")
        
        # Get progress for this specific channel pair
        key = self.get_progress_key(source_id, target_id)
        channel_progress = all_progress.get(key, {})
        
        self.sent_message_ids = set(channel_progress.get('sent_message_ids', []))
        self.last_processed_message_id = channel_progress.get('last_message_id', 0)
        
        if self.sent_message_ids:
            self.log(f"Loaded progress for {key}: {len(self.sent_message_ids)} messages sent")
        else:
            self.log(f"Starting fresh for {key}")
    
    def save_progress(self, source_id, target_id):
        """Save progress for specific channel pair"""
        progress_file = os.path.join(self.session_dir, 'progress.json')
        
        # Load all existing progress
        all_progress = {}
        if os.path.exists(progress_file):
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    all_progress = json.load(f)
            except Exception as e:
                logger.error(f"Error loading progress file: {e}")
        
        # Limit size if too large
        if len(self.sent_message_ids) > 10000:
            temp_list = list(self.sent_message_ids)
            import random
            random.shuffle(temp_list)
            self.sent_message_ids = set(temp_list[:10000])
        
        # Update progress for this channel pair
        key = self.get_progress_key(source_id, target_id)
        all_progress[key] = {
            'sent_message_ids': list(self.sent_message_ids),
            'last_message_id': self.last_processed_message_id
        }
        
        # Save all progress
        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(all_progress, f, ensure_ascii=False, indent=2)
            logger.info(f"Progress saved for {key}: {len(self.sent_message_ids)} messages")
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
    
    async def check_rate_limit(self):
        """Check and manage rate limits (20 messages/minute)"""
        from datetime import datetime, timedelta
        
        if self.minute_start_time is None:
            self.minute_start_time = datetime.now()
        
        # בדוק אם עברה דקה
        elapsed = datetime.now() - self.minute_start_time
        if elapsed.total_seconds() >= 60:
            # איפוס מונה
            self.messages_per_minute = 0
            self.minute_start_time = datetime.now()
            self.log(f"Rate limit reset: 0/{self.max_messages_per_minute} messages this minute")
        
        # בדוק אם עברנו את הגבול
        if self.messages_per_minute >= self.max_messages_per_minute:
            wait_time = 60 - elapsed.total_seconds()
            if wait_time > 0:
                self.log(f"Rate limit reached! Waiting {int(wait_time)}s...")
                await asyncio.sleep(wait_time)
                # איפוס אחרי המתנה
                self.messages_per_minute = 0
                self.minute_start_time = datetime.now()
    
    def smart_delay(self):
        """Smart delay based on consecutive successes"""
        if self.consecutive_successes > 10:
            return random.uniform(1, 2)  # Fast
        elif self.consecutive_successes > 5:
            return random.uniform(2, 4)  # Medium
        else:
            return random.uniform(3, 5)  # Slow
    
    async def get_total_messages(self, entity):
        """Get total message count in channel"""
        try:
            # Use get_messages with limit=0 to get count
            messages = await self.client.get_messages(entity, limit=0)
            return messages.total
        except Exception as e:
            logger.error(f"Error getting total messages: {e}")
            return 0
    
    def update_progress(self):
        """Update progress bar and labels"""
        def update_ui(dt):
            if self.total_messages > 0:
                percentage = (self.processed_messages / self.total_messages) * 100
                self.root.ids.progress_bar.value = percentage
                
                # Update progress text
                progress_text = f"Progress: {self.processed_messages}/{self.total_messages} messages ({percentage:.1f}%)"
                self.root.ids.progress_text.text = progress_text
                
                # Calculate speed and ETA
                if self.start_time:
                    elapsed = time.time() - self.start_time
                    if elapsed > 0:
                        self.messages_per_second = self.processed_messages / elapsed
                        remaining = self.total_messages - self.processed_messages
                        eta_seconds = remaining / self.messages_per_second if self.messages_per_second > 0 else 0
                        eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
                        
                        speed_text = f"Speed: {self.messages_per_second:.2f} msg/s | ETA: {eta_str}"
                        self.root.ids.speed_text.text = speed_text
        
        from kivy.clock import Clock
        Clock.schedule_once(update_ui)
    
    def update_status(self, status, color="Primary"):
        """Update current status label"""
        def update_ui(dt):
            self.root.ids.current_status.text = f"Status: {status}"
            self.root.ids.current_status.theme_text_color = color
        
        from kivy.clock import Clock
        Clock.schedule_once(update_ui)
    
    def get_transfer_method(self):
        """Get selected transfer method"""
        if self.root.ids.method_download_upload.active:
            return "download_upload"
        elif self.root.ids.method_send_message.active:
            return "send_message"
        elif self.root.ids.method_forward.active:
            return "forward"
        return "download_upload"  # default
    

    
    def stop_backup(self):
        """Stop the backup process"""
        self.backup_running = False
        self.log("Backup stopped by user")
        self.update_status("Stopped", "Error")
        
        def update_ui(dt):
            self.root.ids.stop_btn.disabled = True
            self.root.ids.start_btn.disabled = False
        
        from kivy.clock import Clock
        Clock.schedule_once(update_ui)
    
    async def transfer_message(self, message, source_entity, target_entity, method):
        """Transfer message using selected method"""
        
        if method == "download_upload":
            # Current implementation - download and upload
            if message.media:
                self.update_status("Downloading media...", "Custom")
                file = await self.client.download_media(message.media, file=bytes)
                
                if file:
                    self.update_status("Uploading to target...", "Custom")
                    await self.client.send_file(
                        target_entity,
                        file,
                        caption=message.text if message.text else ''
                    )
                else:
                    raise Exception("Failed to download media")
            elif message.text:
                await self.client.send_message(target_entity, message.text)
        
        elif method == "send_message":
            # Forward without credit using send_message
            self.update_status("Sending message...", "Custom")
            await self.client.send_message(
                target_entity,
                message=message
            )
        
        elif method == "forward":
            # Forward with credit
            self.update_status("Forwarding with credit...", "Custom")
            await self.client.forward_messages(
                target_entity,
                message,
                source_entity
            )

    
    def paste_to_field(self, field_id):
        """Paste clipboard content to specified field"""
        try:
            # Try to get clipboard content (Android)
            from android.runnable import run_on_ui_thread
            from jnius import autoclass
            
            @run_on_ui_thread
            def get_clipboard():
                try:
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    activity = PythonActivity.mActivity
                    clipboard = activity.getSystemService(activity.CLIPBOARD_SERVICE)
                    
                    if clipboard.hasPrimaryClip():
                        clip = clipboard.getPrimaryClip()
                        if clip.getItemCount() > 0:
                            text = clip.getItemAt(0).getText()
                            if text:
                                # Update field on main thread
                                from kivy.clock import Clock
                                def update_field(dt):
                                    self.root.ids[field_id].text = str(text)
                                    self.log(f"Pasted to {field_id}")
                                Clock.schedule_once(update_field)
                except Exception as e:
                    self.log(f"ERROR pasting: {e}")
            
            get_clipboard()
        except ImportError:
            # Not on Android - try desktop clipboard
            try:
                from kivy.core.clipboard import Clipboard
                text = Clipboard.paste()
                if text:
                    self.root.ids[field_id].text = text
                    self.log(f"Pasted to {field_id}")
            except Exception as e:
                self.log(f"ERROR pasting: {e}")

    def log(self, message):
        def update_ui(dt):
            current_text = self.root.ids.status_log.text
            self.root.ids.status_log.text = message + "\\n" + current_text
        
        # עדכון ה-UI חייב להתבצע מה-Thread הראשי
        from kivy.clock import Clock
        Clock.schedule_once(update_ui)
        print(message)
        logger.info(message)

    def send_code(self):
        api_id = self.root.ids.api_id.text
        api_hash = self.root.ids.api_hash.text
        phone = self.root.ids.phone.text

        if not api_id or not api_hash or not phone:
            self.log("ERROR: Missing details (API ID/HASH/Phone)")
            return
        
        # Show visual feedback
        self.log("Sending verification code...")
        self.update_status("Sending code...", "Custom")
        
        # Disable send button to prevent double-click
        from kivy.clock import Clock
        def disable_send_btn(dt):
            self.root.ids.send_code_btn.disabled = True
        Clock.schedule_once(disable_send_btn)
        
        # Lazy Loading: Load Telethon only here!
        try:
            self.log("Loading Telethon...")
            from telethon import TelegramClient
            from telethon.errors import SessionPasswordNeededError
            self.log("Telethon loaded successfully!")
        except ImportError as e:
            self.log(f"ERROR: Telethon not installed - {e}")
            self.update_status("Error loading Telethon", "Error")
            sentry_sdk.capture_exception(e)
            return
        except Exception as e:
            error_msg = f"Error loading Telethon: {e}"
            self.log(error_msg)
            sentry_sdk.capture_exception(e)
            return
        
        # Validate and convert API ID
        try:
            api_id_int = int(api_id)
            # Check if API ID is within valid range (32-bit signed integer)
            if api_id_int < -2147483648 or api_id_int > 2147483647:
                self.log("ERROR: API ID is too large. Please check your API ID from my.telegram.org")
                self.update_status("Invalid API ID", "Error")
                return
        except ValueError:
            self.log("ERROR: API ID must be a number")
            self.update_status("Invalid API ID", "Error")
            return
        
        # Save client info
        try:
            session_name = f'session_{phone.replace("+", "")}'
            session_path = os.path.join(self.session_dir, session_name)
            self.log(f"Creating session: {session_path}")
            
            self.client = TelegramClient(session_path, api_id_int, api_hash)
            self.phone = phone
        except Exception as e:
            error_msg = f"Error creating client: {e}"
            self.log(error_msg)
            sentry_sdk.capture_exception(e)
            return

        # Use worker thread instead of creating new thread
        async def async_send():
            try:
                self.log("Connecting to Telegram servers...")
                self.update_status("Connecting...", "Custom")
                await self.client.connect()
                
                if not await self.client.is_user_authorized():
                    self.log("Requesting verification code...")
                    self.update_status("Requesting code...", "Custom")
                    await self.client.send_code_request(phone)
                    self.log("Code sent! Please enter it in the field below and click 'Login'.")
                    self.update_status("Code sent successfully!", "Primary")
                    
                    # Enable code field and login button
                    from kivy.clock import Clock
                    def enable_fields(dt):
                        self.root.ids.code.disabled = False
                        self.root.ids.login_btn.disabled = False
                    Clock.schedule_once(enable_fields)
                else:
                    self.log("Already logged in!")
                    self.update_status("Already logged in", "Primary")
                    from kivy.clock import Clock
                    def enable_backup(dt):
                        self.root.ids.start_btn.disabled = False
                        self.root.ids.connection_status.text = "Status: Connected"
                        self.root.ids.connection_status.theme_text_color = "Primary"
                    Clock.schedule_once(enable_backup)
            except Exception as e:
                error_msg = f"ERROR sending code: {e}"
                self.log(error_msg)
                self.update_status("Error sending code", "Error")
                sentry_sdk.capture_exception(e)
                
                # Re-enable send button on error
                from kivy.clock import Clock
                def enable_send_btn(dt):
                    self.root.ids.send_code_btn.disabled = False
                Clock.schedule_once(enable_send_btn)
        
        # Run in worker thread's event loop
        self.run_in_worker(async_send())

    def login(self):
        code = self.root.ids.code.text
        password = self.root.ids.two_fa_password.text
        phone = self.root.ids.phone.text
        
        if not code and not self.needs_2fa:
            self.log("ERROR: Please enter the code you received.")
            return
        
        if self.needs_2fa and not password:
            self.log("ERROR: Please enter your 2FA password.")
            return
        
        self.log("Logging in...")
        self.update_status("Logging in...", "Custom")
        
        # Use worker thread instead of creating new thread
        async def async_login():
            try:
                # Import here to have access in this scope
                from telethon.errors import SessionPasswordNeededError
                
                if not self.client.is_connected():
                     await self.client.connect()
                
                if self.needs_2fa:
                    # Sign in with 2FA password
                    await self.client.sign_in(password=password)
                    self.log("Logged in successfully with 2FA!")
                else:
                    # Normal sign in with code
                    await self.client.sign_in(phone, code)
                    self.log("Logged in successfully!")
                
                self.update_status("Logged in successfully", "Primary")
                
                from kivy.clock import Clock
                def enable_backup(dt):
                    self.root.ids.start_btn.disabled = False
                    # Update connection status
                    self.root.ids.connection_status.text = "Status: Connected"
                    self.root.ids.connection_status.theme_text_color = "Primary"
                Clock.schedule_once(enable_backup)
                
            except SessionPasswordNeededError:
                # 2FA is required!
                self.log("Two-steps verification is enabled and a password is required (caused by SignInRequest)")
                self.log("Please enter your 2FA password in the field below and click 'Login'.")
                self.update_status("2FA password required", "Custom")
                
                # Enable 2FA password field
                from kivy.clock import Clock
                def enable_2fa_field(dt):
                    self.root.ids.two_fa_password.disabled = False
                    self.needs_2fa = True
                Clock.schedule_once(enable_2fa_field)
                
            except Exception as e:
                error_msg = f"ERROR logging in: {e}"
                self.log(error_msg)
                self.update_status("Login error", "Error")
                sentry_sdk.capture_exception(e)
        
        # Run in worker thread's event loop
        self.run_in_worker(async_login())

    def start_backup(self):
        source = self.root.ids.source_channel.text
        target = self.root.ids.target_channel.text
        if not source or not target:
            self.log("Please enter source and target channels.")
            return
        
        # קריאת הגדרות מה-UI
        try:
            start_id = int(self.root.ids.start_message_id.text or "0")
        except ValueError:
            start_id = 0
        
        # קריאת checkboxes
        file_types = {
            'text': self.root.ids.cb_text.active,
            'photos': self.root.ids.cb_photos.active,
            'videos': self.root.ids.cb_videos.active,
            'documents': self.root.ids.cb_documents.active
        }
        
        self.log(f"Settings: Start ID={start_id}, Types={file_types}")
        
        threading.Thread(target=self._backup_thread, args=(source, target, start_id, file_types), daemon=True).start()

    def _backup_thread(self, source, target, start_id, file_types):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def async_backup():
            try:
                if not self.client.is_connected():
                     await self.client.connect()

                self.log("Starting backup process...")
                
                # Convert to integers if needed (use new variables to avoid UnboundLocalError)
                source_entity = source
                target_entity = target
                try:
                    if str(source).lstrip('-').isdigit(): 
                        source_entity = int(source)
                    if str(target).lstrip('-').isdigit(): 
                        target_entity = int(target)
                except: 
                    pass

                try:
                     s_entity = await self.client.get_entity(source_entity)
                     t_entity = await self.client.get_entity(target_entity)
                except Exception as e:
                     error_msg = f"Cannot find channels. Make sure you joined them.\nError: {e}"
                     self.log(error_msg)
                     sentry_sdk.capture_exception(e)
                     return

                s_title = getattr(s_entity, 'title', str(source))
                t_title = getattr(t_entity, 'title', str(target))
                s_id = s_entity.id
                t_id = t_entity.id
                
                self.log(f"Transferring from: {s_title} to {t_title}")
                
                # טעינת התקדמות לזוג ערוצים זה
                self.load_progress(s_id, t_id)
                
                # קבלת שיטת העברה
                transfer_method = self.get_transfer_method()
                self.log(f"Transfer method: {transfer_method}")
                
                # ספירת סך ההודעות בערוץ
                self.total_messages = await self.get_total_messages(s_entity)
                self.processed_messages = 0
                self.start_time = time.time()
                self.backup_running = True
                
                self.log(f"Total messages in channel: {self.total_messages}")
                self.update_status("Starting backup...", "Primary")
                
                # הפעלת כפתור Stop
                from kivy.clock import Clock
                def enable_stop(dt):
                    self.root.ids.stop_btn.disabled = False
                    self.root.ids.start_btn.disabled = True
                Clock.schedule_once(enable_stop)
                
                # שמירת התקדמות + המתנה חכמה
                count = 0
                skipped = 0
                
                # שימוש ב-start_id אם צוין
                offset_id = start_id if start_id > 0 else 0
                if offset_id > 0:
                    self.log(f"Starting from message ID: {offset_id}")
                
                async for message in self.client.iter_messages(s_entity, limit=None, offset_id=offset_id):
                    # בדיקה אם המשתמש עצר את הגיבוי
                    if not self.backup_running:
                        self.log("Backup stopped")
                        break
                    
                    if message and message.id:
                        # בדיקה אם כבר שלחנו את ההודעה
                        if message.id in self.sent_message_ids:
                            skipped += 1
                            continue
                        
                        # סינון סוגי קבצים
                        should_send = False
                        message_type = None
                        
                        if message.text and not message.media:
                            should_send = file_types.get('text', True)
                            message_type = "text"
                        elif message.photo:
                            should_send = file_types.get('photos', True)
                            message_type = "photo"
                        elif message.video:
                            should_send = file_types.get('videos', True)
                            message_type = "video"
                        elif message.document:
                            should_send = file_types.get('documents', True)
                            message_type = "document"
                        else:
                            # סוגים אחרים (audio, voice, etc.)
                            should_send = True
                            message_type = "other"
                        
                        if not should_send:
                            self.log(f"Skipping {message_type} message {message.id} (filtered)")
                            skipped += 1
                            continue
                        
                        try:
                            # בדיקת הגבלת קצב לפני שליחה
                            await self.check_rate_limit()
                            
                            # העברת הודעה לפי השיטה הנבחרת
                            await self.transfer_message(message, s_entity, t_entity, transfer_method)
                            
                            count += 1
                            self.consecutive_successes += 1
                            
                            # עדכון מונה הודעות לדקה
                            self.messages_per_minute += 1
                            
                            # עדכון התקדמות
                            self.processed_messages += 1
                            self.update_progress()
                            
                            self.log(f"Rate: {self.messages_per_minute}/{self.max_messages_per_minute} messages this minute")
                            
                            # שמירת ההודעה כנשלחה
                            self.sent_message_ids.add(message.id)
                            self.last_processed_message_id = message.id
                            
                            # שמירת התקדמות כל 10 הודעות
                            if count % 10 == 0:
                                self.save_progress(s_id, t_id)
                            
                            # Smart delay - random!
                            delay = self.smart_delay()
                            self.log(f"{count} sent, {skipped} skipped. Waiting {delay:.1f}s...")
                            await asyncio.sleep(delay)
                            
                        except errors.FloodWaitError as e:
                            # Handle FloodWait
                            wait_time = e.seconds + random.uniform(2, 5)
                            self.log(f"FloodWait! Waiting {wait_time:.0f}s...")
                            self.consecutive_successes = 0  # Reset
                            await asyncio.sleep(wait_time)
                            
                        except Exception as inner_e:
                            self.log(f"Error in message {message.id}: {inner_e}")
                            self.consecutive_successes = 0  # Reset
                            sentry_sdk.capture_exception(inner_e)
                            await asyncio.sleep(self.smart_delay())
                
                # Final save
                self.save_progress(s_id, t_id)
                
                # Update completion status
                if self.backup_running:
                    self.update_status("Completed", "Primary")
                    self.log(f"Backup completed!")
                    self.log(f"Sent: {count}, Skipped: {skipped}")
                else:
                    self.update_status("Stopped by user", "Error")
                
                # החזרת כפתורים למצב רגיל
                from kivy.clock import Clock
                def reset_buttons(dt):
                    self.root.ids.stop_btn.disabled = True
                    self.root.ids.start_btn.disabled = False
                Clock.schedule_once(reset_buttons)

            except Exception as e:
                error_msg = f"General backup error: {e}"
                self.log(error_msg)
                sentry_sdk.capture_exception(e)

        try:
            loop.run_until_complete(async_backup())
        except Exception as e:
            sentry_sdk.capture_exception(e)
        finally:
            loop.close()

if __name__ == '__main__':
    try:
        TelegramBackupApp().run()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise
