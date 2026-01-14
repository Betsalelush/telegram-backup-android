"""
Transfer Manager
Manages message transfers between channels
"""
import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import Message, MessageMediaPhoto, MessageMediaDocument

from ..config import Config
from ..utils.logger import logger, add_breadcrumb
from ..utils.helpers import download_media, upload_media
from telethon.tl.types import Message, MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage
import os


class TransferSession:
    """
    Represents a single active transfer session
    """
    def __init__(self, session_id: str, config: Dict):
        self.session_id = session_id
        self.config = config
        self.stats = {
            'total_sent': 0,
            'total_skipped': 0,
            'total_errors': 0,
            'consecutive_successes': 0
        }
        self.is_running = True
        self.start_time = datetime.now()
        self.status = "Initializing..."

    def stop(self):
        self.is_running = False
        self.status = "Stopped"

    def update_stats(self, sent=0, skipped=0, errors=0, success=False):
        self.stats['total_sent'] += sent
        self.stats['total_skipped'] += skipped
        self.stats['total_errors'] += errors
        
        if success:
            self.stats['consecutive_successes'] += 1
        else:
            if errors > 0:
                self.stats['consecutive_successes'] = 0

class TransferManager:
    """
    Manages multiple message transfer sessions
    
    Features:
    - Multiple concurrent sessions
    - Helper class TransferSession
    - Round-robin between multiple accounts
    - Global Rate limiting (20 msg/min per account)
    - FloodWait handling
    """
    
    def __init__(self):
        """Initialize Transfer Manager"""
        # Global Rate Limiting State
        # We need to track rate limits PER CLIENT potentially, or globally if desired.
        # Assuming global safety for now to be safe.
        self.messages_per_minute = 0
        self.minute_start_time = None
        self.max_messages_per_minute = Config.MAX_MESSAGES_PER_MINUTE
        
        # Client FloodWait State (Global)
        self.client_flood_wait = {}  # client_id -> wait_until_time
        
        # Active Sessions
        self.sessions: Dict[str, TransferSession] = {}
        
        add_breadcrumb("TransferManager initialized")
    
    def create_transfer(self, transfer_config: Dict) -> str:
        """Create new transfer session"""
        import uuid
        session_id = f"task_{uuid.uuid4().hex[:8]}"
        session = TransferSession(session_id, transfer_config)
        self.sessions[session_id] = session
        
        logger.info(f"Created session: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[TransferSession]:
        return self.sessions.get(session_id)

    def stop_transfer(self, session_id: str):
        """Stop a specific session"""
        session = self.get_session(session_id)
        if session:
            session.stop()
            logger.info(f"Stopped session {session_id}")

    async def start_mass_transfer(self, session_id: str, clients: List[TelegramClient], status_callback):
        """
        Run a specific transfer session
        """
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return

        try:
            config = session.config
            source = config['source']
            target = config['target']
            start_id = config.get('start_id', 0)
            file_types = config.get('file_types', [])
            
            # 1. Resolve Entities
            status_callback(session_id, "Resolving channels...")
            primary = clients[0]
            
            try:
                source_entity = await self.get_entity_robust(primary, source)
                target_entity = await self.get_entity_robust(primary, target)
            except Exception as e:
                raise Exception(f"Failed to resolve channel ({source} -> {target}): {e}. Make sure the account is a member.")
            
            # 2. Iterate Messages
            status_callback(session_id, f"Scanning from ID {start_id}...")
            
            kwargs = {'reverse': True}
            if start_id > 0:
                kwargs['min_id'] = start_id
            
            batch_size = 20
            batch = []
            
            # Simple round-robin index for this session
            client_index = 0
            
            async for message in primary.iter_messages(source_entity, **kwargs):
                if not session.is_running:
                    status_callback(session_id, "Stopped.")
                    break

                batch.append(message)
                
                if len(batch) >= batch_size:
                    status_callback(session_id, f"Processing batch {message.id}...")
                    
                    # Process batch
                    await self.process_batch(session, clients, batch, source_entity, target_entity, file_types, mode=session.config.get('mode', 'copy'))
                    batch = [] # Clear batch
                    
                    # Update status text
                    s = session.stats
                    status_callback(session_id, f"Running: Sent {s['total_sent']} | Errors {s['total_errors']}")

            # Process remaining
            if batch and session.is_running:
                await self.process_batch(session, clients, batch, source_entity, target_entity, file_types, mode=session.config.get('mode', 'copy'))
            
            if session.is_running:
                session.status = "Completed"
                status_callback(session_id, "Completed Successfully!")
                session.is_running = False
                
        except Exception as e:
            logger.error(f"Session {session_id} error: {e}")
            session.status = f"Error: {str(e)}"
            status_callback(session_id, f"Error: {str(e)}")
            session.is_running = False

    async def process_batch(self, session, clients, messages, source, target, file_types, mode='copy'):
        """Process a batch of messages for a session"""
        
        for message in messages:
            if not session.is_running:
                break
                
            # Filter Logic
            if not self.is_message_allowed(message, file_types):
                session.update_stats(skipped=1)
                continue

            # Get Client
            client = await self.get_next_client(clients)
            if not client:
                session.update_stats(errors=1)
                continue
            
            # Rate Limit (Global)
            await self.check_global_rate_limit()
            
            # Transfer
            try:
                success = await self.transfer_single_message(client, message, source, target, file_types, mode)
                if success:
                    session.update_stats(sent=1, success=True)
                else:
                    session.update_stats(errors=1, success=False)
            except Exception as e:
                logger.error(f"Transfer error: {e}")
                session.update_stats(errors=1, success=False)
            
            # Delay
            await asyncio.sleep(self.calculate_delay(session.stats['consecutive_successes']))

    def is_message_allowed(self, message, file_types):
        """Check if message matches allowed types"""
        if not file_types: return True # All allowed if None
        
        # Text
        if "text" in file_types and message.text and not message.media: return True
        
        # Media
        if message.media:
            if "images" in file_types and message.photo: return True
            if "videos" in file_types and message.video: return True
            if "audio" in file_types and (message.audio or message.voice): return True
            if "documents" in file_types and message.document and not (message.video or message.audio or message.voice or message.photo): return True
            
        return False

    async def transfer_single_message(self, client, message, source, target, file_types: List[str] = None, mode: str = 'copy'):
        """
        Actual transfer logic
        Modes: 'forward', 'copy', 'download_upload'
        """
        try:
            # --- 1. Forward Mode ---
            if mode == 'forward':
                await client.forward_messages(target, message, source)
                return True

            # --- 2. Copy Mode (No Credit) ---
            elif mode == 'copy':
                # Media
                if message.media:
                    # Handle WebPage (Link Previews) separately - treated as text
                    if isinstance(message.media, MessageMediaWebPage):
                        await client.send_message(target, message.text or '')
                        return True

                    # Actual Files
                    file_to_send = message.media
                    if isinstance(message.media, MessageMediaPhoto):
                        file_to_send = message.photo
                    elif isinstance(message.media, MessageMediaDocument):
                        file_to_send = message.document
                    
                    try:
                        await client.send_file(
                            target,
                            file=file_to_send,
                            caption=message.text or ''
                        )
                        return True
                    except TypeError as e:
                         # Fallback for unsupported media types in send_file
                         logger.warning(f"Unsupported media for send_file: {type(message.media)}. Sending text only.")
                         if message.text:
                             await client.send_message(target, message.text)
                             return True
                         return False

                # Text
                elif message.text:
                    await client.send_message(target, message.text)
                    return True

            # --- 3. Download & Upload Mode (Cleanest) ---
            elif mode == 'download_upload':
                if message.media:
                    # Download
                    logger.info("Downloading media for clean upload...")
                    file_bytes = await download_media(client, message)
                    
                    if file_bytes:
                        # Upload
                        await upload_media(client, target, file_bytes, caption=message.text)
                        return True
                    else:
                        logger.warning("Failed to download media")
                        return False
                
                elif message.text:
                    # Text is same as copy
                    await client.send_message(target, message.text)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Transfer error ({mode}): {e}")
            raise e

    async def check_global_rate_limit(self):
        """Global rate limiter implementation"""
        if self.minute_start_time is None:
            self.minute_start_time = datetime.now()
            
        elapsed = (datetime.now() - self.minute_start_time).total_seconds()
        
        if elapsed >= 60:
            self.messages_per_minute = 0
            self.minute_start_time = datetime.now()
            
        if self.messages_per_minute >= self.max_messages_per_minute:
            wait = 60 - elapsed
            if wait > 0:
                logger.warning(f"Global Rate Limit Hit. Waiting {wait:.1f}s")
                await asyncio.sleep(wait)
                self.messages_per_minute = 0
                self.minute_start_time = datetime.now()
        
        self.messages_per_minute += 1

    async def get_next_client(self, clients):
        """Get next available client (FloodWait safe)"""
        # Simple random/round-robin for now
        # Ideally track FloodWait per client_id globally
        import random
        valid_clients = []
        now = datetime.now()
        
        for c in clients:
            cid = id(c)
            # Check FloodWait
            if cid in self.client_flood_wait:
                if now < self.client_flood_wait[cid]:
                    continue # Still waiting
                else:
                    del self.client_flood_wait[cid]
            valid_clients.append(c)
            
        if not valid_clients:
            return None
            
        return random.choice(valid_clients)

    def calculate_delay(self, consecutive_successes):
        """Smart delay"""
        if consecutive_successes > 10:
            return random.uniform(Config.SMART_DELAY_MIN, Config.SMART_DELAY_MIN + 0.5)
        return random.uniform(Config.SMART_DELAY_MIN + 1, Config.SMART_DELAY_MAX)
    async def get_entity_robust(self, client, entity_id):
        """Try to resolve entity, refreshing dialogs if needed"""
        try:
            # First try direct
            if str(entity_id).startswith('-100'):
                # Try as int first if it's a string ID
                try: 
                    return await client.get_entity(int(entity_id))
                except: pass
            
            return await client.get_entity(entity_id)
        except ValueError:
            # Not found in cache, might need to refresh dialogs
            logger.info(f"Entity {entity_id} not found, refreshing dialogs...")
            # We don't get all dialogs as it's expensive, but 'get_dialogs' refreshes cache
            await client.get_dialogs(limit=100) 
            
            # Retry
            if str(entity_id).startswith('-100'):
                try: 
                    return await client.get_entity(int(entity_id))
                except: pass
            return await client.get_entity(entity_id)

    async def get_next_client(self, clients):
        """Get next available client (Round Robin logic is simpler in caller)"""
        # Here we just pick a random one or utilize the passed list logic
        # For now, just return a random one to spread load
        import random
        return random.choice(clients)

    async def check_global_rate_limit(self):
        """Global rate limiting to avoid Bans"""
        now = time.time()
        
        # Reset if minute passed
        if not self.minute_start_time or (now - self.minute_start_time) > 60:
            self.minute_start_time = now
            self.messages_per_minute = 0
            
        # Check limit
        if self.messages_per_minute >= self.max_messages_per_minute:
            wait_time = 60 - (now - self.minute_start_time) + 1
            if wait_time > 0:
                logger.warning(f"Global rate limit hit ({self.messages_per_minute}/min). Waiting {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
                # Reset after wait
                self.minute_start_time = time.time()
                self.messages_per_minute = 0
                
        self.messages_per_minute += 1

    def calculate_delay(self, consecutive_successes):
        """Smart delay based on success streak"""
        # Base delay 2-5 seconds
        base = random.uniform(2, 5)
        
        # If we are on a roll, we can go slightly faster (down to 1.5s)
        # But assume safey first
        if consecutive_successes > 50:
             # Very stable, maybe 1.5 - 3
             return random.uniform(1.5, 3.0)
        
        return base
