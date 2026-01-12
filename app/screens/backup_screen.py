# -*- coding: utf-8 -*-
"""
Backup Screen - Message Transfer and Backup
Handles backup process, progress tracking, and message transfer
"""

import asyncio
import time
import logging
import os
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from app.config import Config
from app.managers import ProgressManager
from app.utils.logger import add_breadcrumb, capture_exception
from app.utils import helpers

logger = logging.getLogger(__name__)

# Load KV file
kv_file = os.path.join(os.path.dirname(__file__), '../kv/backup.kv')
Builder.load_file(kv_file)


class BackupScreen(MDScreen):
    """Screen for backup and message transfer operations"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = None
        self.backup_running = False
        self.progress_manager = ProgressManager(Config.PROGRESS_DIR)
        
        # Progress tracking
        self.total_messages = 0
        self.processed_messages = 0
        self.start_time = None
        self.sent_message_ids = set()
        self.last_processed_message_id = 0
        
        # Rate limiting
        self.messages_per_minute = 0
        self.max_messages_per_minute = Config.MAX_MESSAGES_PER_MINUTE
        self.consecutive_successes = 0
    
    def start_backup(self):
        """Start backup process"""
        add_breadcrumb('backup', 'Starting backup', 'info')
        
        source = self.ids.source.text
        target = self.ids.target.text
        
        if not source or not target:
            self.log("Please enter source and target channels")
            return
        
        # Get start message ID
        try:
            start_id = int(self.ids.start_message_id.text or "0")
        except ValueError:
            start_id = 0
        
        # Get file types
        file_types = {
            'text': self.ids.cb_text.active,
            'photos': self.ids.cb_photos.active,
            'videos': self.ids.cb_videos.active,
            'documents': self.ids.cb_documents.active
        }
        
        self.log(f"Settings: Start ID={start_id}, Types={file_types}")
        
        # Run async
        from kivy.app import App
        app = App.get_running_app()
        app.worker_loop.call_soon_threadsafe(
            asyncio.ensure_future,
            self._start_backup_async(source, target, start_id, file_types),
            app.worker_loop
        )
    
    async def _start_backup_async(self, source, target, start_id, file_types):
        """Async backup implementation"""
        try:
            # Lazy import Telethon
            from telethon import errors
            
            if not self.client.is_connected():
                await self.client.connect()
            
            self.log("Starting backup process...")
            
            # Convert to entities
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
                capture_exception(e)
                return
            
            s_title = getattr(s_entity, 'title', str(source))
            t_title = getattr(t_entity, 'title', str(target))
            s_id = s_entity.id
            t_id = t_entity.id
            
            self.log(f"Transferring from: {s_title} to {t_title}")
            
            # Load progress
            progress_data = self.progress_manager.load_progress(s_id, t_id)
            if progress_data:
                self.sent_message_ids = set(progress_data.get('sent_ids', []))
                self.last_processed_message_id = progress_data.get('last_id', 0)
                self.log(f"Loaded progress: {len(self.sent_message_ids)} messages already sent")
            
            # Get transfer method
            transfer_method = self.get_transfer_method()
            self.log(f"Transfer method: {transfer_method}")
            
            # Count total messages
            self.total_messages = await self.get_total_messages(s_entity)
            self.processed_messages = 0
            self.start_time = time.time()
            self.backup_running = True
            
            self.log(f"Total messages in channel: {self.total_messages}")
            self.update_status("Starting backup...", "Primary")
            
            add_breadcrumb('backup', f'Starting transfer: {s_title} → {t_title}', 'info', {
                'source_id': s_id,
                'target_id': t_id,
                'total_messages': self.total_messages
            })
            
            # Enable stop button
            from kivy.clock import Clock
            def enable_stop(dt):
                self.ids.stop_btn.disabled = False
                self.ids.start_btn.disabled = True
            Clock.schedule_once(enable_stop)
            
            # Transfer messages
            count = 0
            skipped = 0
            
            # Chronological order (old→new)
            offset_id = start_id if start_id > 0 else 0
            if offset_id > 0:
                self.log(f"Starting from message ID: {offset_id}, going forward (old→new)")
            
            async for message in self.client.iter_messages(s_entity, limit=None, reverse=True, offset_id=offset_id):
                # Check if stopped
                if not self.backup_running:
                    self.log("Backup stopped")
                    break
                
                # Handle deleted or None messages
                if not message:
                    add_breadcrumb('backup', 'Skipped: Deleted or None message', 'warning')
                    self.log("Skipped: Deleted or empty message slot")
                    skipped += 1
                    continue
                
                if not message.id:
                    add_breadcrumb('backup', 'Skipped: Message without ID', 'warning')
                    self.log("Skipped: Message without ID")
                    skipped += 1
                    continue
                
                # Check if already sent
                if message.id in self.sent_message_ids:
                    skipped += 1
                    continue
                
                # Check for unsupported message types
                skip_reason = None
                
                if hasattr(message, 'poll') and message.poll:
                    skip_reason = "Poll (not supported)"
                elif hasattr(message, 'game') and message.game:
                    skip_reason = "Game (not supported)"
                elif hasattr(message, 'action') and message.action:
                    skip_reason = f"Service message: {type(message.action).__name__}"
                elif not message.text and not message.media:
                    skip_reason = "Empty message (no content)"
                
                if skip_reason:
                    add_breadcrumb('backup', f'Message {message.id} skipped: {skip_reason}', 'info', {
                        'message_id': message.id,
                        'reason': skip_reason
                    })
                    self.log(f"Skipped message {message.id}: {skip_reason}")
                    skipped += 1
                    continue
                
                # File type filtering
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
                    should_send = True
                    message_type = "other"
                
                if not should_send:
                    add_breadcrumb('backup', f'Message {message.id} filtered: {message_type} not selected', 'info', {
                        'message_id': message.id,
                        'type': message_type
                    })
                    self.log(f"Skipping {message_type} message {message.id} (filtered by user settings)")
                    skipped += 1
                    continue
                
                try:
                    # Rate limiting
                    await self.check_rate_limit()
                    
                    # Transfer message
                    await self.transfer_message(message, s_entity, t_entity, transfer_method)
                    
                    count += 1
                    self.consecutive_successes += 1
                    self.messages_per_minute += 1
                    self.processed_messages += 1
                    self.update_progress()
                    
                    self.log(f"Rate: {self.messages_per_minute}/{self.max_messages_per_minute} messages this minute")
                    
                    # Mark as sent
                    self.sent_message_ids.add(message.id)
                    self.last_processed_message_id = message.id
                    
                    # Save progress every 10 messages
                    if count % 10 == 0:
                        self.progress_manager.save_progress(s_id, t_id, {
                            'sent_ids': list(self.sent_message_ids),
                            'last_id': self.last_processed_message_id,
                            'total_sent': count,
                            'total_skipped': skipped
                        })
                    
                    # Smart delay
                    delay = self.smart_delay()
                    self.log(f"{count} sent, {skipped} skipped. Waiting {delay:.1f}s...")
                    await asyncio.sleep(delay)
                
                except errors.FloodWaitError as e:
                    wait_time = e.seconds + random.uniform(2, 5)
                    self.log(f"FloodWait! Waiting {wait_time:.0f}s...")
                    self.consecutive_successes = 0
                    await asyncio.sleep(wait_time)
                
                except Exception as inner_e:
                    self.log(f"Error in message {message.id}: {inner_e}")
                    self.consecutive_successes = 0
                    capture_exception(inner_e)
                    await asyncio.sleep(self.smart_delay())
            
            # Final save
            self.progress_manager.save_progress(s_id, t_id, {
                'sent_ids': list(self.sent_message_ids),
                'last_id': self.last_processed_message_id,
                'total_sent': count,
                'total_skipped': skipped
            })
            
            # Update completion status
            if self.backup_running:
                self.update_status("Completed", "Primary")
                self.log(f"Backup completed! Sent: {count}, Skipped: {skipped}")
            else:
                self.update_status("Stopped by user", "Error")
        
        except Exception as e:
            error_msg = f"Backup error: {e}"
            self.log(error_msg)
            self.update_status("Error", "Error")
            capture_exception(e)
        
        finally:
            self.backup_running = False
            from kivy.clock import Clock
            def update_ui(dt):
                self.ids.stop_btn.disabled = True
                self.ids.start_btn.disabled = False
            Clock.schedule_once(update_ui)
    
    def stop_backup(self):
        """Stop backup process"""
        self.backup_running = False
        self.log("Stopping backup...")
        self.update_status("Stopping...", "Secondary")
    
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
    
    # Helper methods (to be implemented or imported from TransferManager)
    def get_transfer_method(self):
        """Get selected transfer method"""
        return "forward"  # Default
    
    async def get_total_messages(self, entity):
        """Get total message count"""
        try:
            dialogs = await self.client.get_dialogs()
            for dialog in dialogs:
                if dialog.entity.id == entity.id:
                    return dialog.message.id
        except:
            pass
        return 0
    
    def update_progress(self):
        """Update progress UI"""
        if self.total_messages > 0:
            progress = (self.processed_messages / self.total_messages) * 100
            elapsed = time.time() - self.start_time
            # Update UI with progress
    
    async def check_rate_limit(self):
        """Check and enforce rate limiting"""
        # To be moved to TransferManager
        pass
    
    def smart_delay(self):
        """Calculate smart delay based on success rate"""
        # To be moved to TransferManager
        import random
        if self.consecutive_successes > 10:
            return random.uniform(1.0, 2.0)
        elif self.consecutive_successes > 5:
            return random.uniform(2.0, 3.0)
        else:
            return random.uniform(3.0, 5.0)
    
    async def transfer_message(self, message, source, target, method):
        """Transfer a single message"""
        # To be moved to TransferManager
        if method == "forward":
            await self.client.forward_messages(target, message)
        elif method == "copy":
            await self.client.send_message(target, message.text or message.message)
