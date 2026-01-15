"""
Download Manager
Handles downloading channels to local disk with strict rate limiting.
"""
import os
import asyncio
import random
import time
from datetime import datetime
from typing import Dict, List, Optional
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import telethon.utils

from app.config import Config
from app.utils.logger import logger

from .base_session import BaseSession

class DownloadSession(BaseSession):
    """Helper for tracking download session state"""
    def __init__(self, session_id):
        super().__init__(session_id)
        self.stats.update({
            'total_downloaded': 0
        })

class DownloadManager:
    """
    Manages downloads from Telegram channels to local storage.
    Includes rate limiting and file type filtering.
    """
    def __init__(self):
        self.sessions: Dict[str, DownloadSession] = {}
        self.base_download_path = Config.DOWNLOADS_DIR if Config.DOWNLOADS_DIR else "downloads"
        os.makedirs(self.base_download_path, exist_ok=True)

    def create_session(self, session_id: str):
        """Initialize a new download session"""
        self.sessions[session_id] = DownloadSession(session_id)
        logger.info(f"Created download session: {session_id}")

    def get_session(self, session_id: str) -> Optional[DownloadSession]:
        return self.sessions.get(session_id)

    async def download_channel(self, session_id: str, client: TelegramClient, source, file_types: Dict, status_callback):
        """
        Main download loop
        """
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return

        try:
            # 1. Resolve Entity
            status_callback("Resolving channel...")
            entity = await self._get_entity_robust(client, source)
            if not entity:
                status_callback("Error: Could not find channel")
                return

            # 2. Iterate
            status_callback("Scanning messages...")
            
            # Create channel-specific folder
            channel_name = telethon.utils.get_display_name(entity)
            safe_name = "".join([c for c in channel_name if c.isalnum() or c in (' ', '-', '_')]).strip()
            save_path = os.path.join(self.base_download_path, f"{safe_name}_{session_id}")
            os.makedirs(save_path, exist_ok=True)
            
            count = 0
            async for message in client.iter_messages(entity, reverse=True): # Oldest to newest
                if not session.is_running:
                    status_callback("Stopped by user")
                    break

                # Filter
                if not self._should_download(message, file_types):
                    session.total_skipped += 1
                    continue

                # Download
                try:
                    status_callback(f"Downloading msg {message.id}...")
                    
                    # Text
                    if message.text and file_types.get('text') and not message.media:
                         with open(os.path.join(save_path, f"msg_{message.id}.txt"), "w", encoding='utf-8') as f:
                             f.write(message.text)
                         session.total_downloaded += 1
                    
                    # Media
                    elif message.media:
                        filename = f"{message.id}"
                        path = await client.download_media(message, file=os.path.join(save_path, filename))
                        if path:
                            session.total_downloaded += 1
                        else:
                            session.total_errors += 1
                            
                    # Rate Limit
                    await asyncio.sleep(random.uniform(1.0, 3.0))
                    
                except Exception as e:
                    logger.error(f"Download error msg {message.id}: {e}")
                    session.total_errors += 1
                
                count += 1
                if count % 5 == 0:
                    status_callback(f"Downloaded: {session.total_downloaded} | Errors: {session.total_errors}")

            status_callback(f"Complete! Saved to {safe_name}_{session_id}")
            
        except Exception as e:
            logger.error(f"Download fatal error: {e}")
            status_callback(f"Error: {e}")
            
    def _should_download(self, message, file_types):
        """Check if message matches selected file types"""
        # Fix: If text is allowed and message is text-only, return True (Logic fixed form User Request)
        if message.text and file_types.get('text') and not message.media:
            return True 

        if not message.media:
            return False

        if isinstance(message.media, MessageMediaPhoto):
            return file_types.get('images', False)
        
        if isinstance(message.media, MessageMediaDocument):
            # Check for video mime type or generic doc
            is_video = False
            if hasattr(message.media, 'document'):
                # Try simple mime check first if available
                if hasattr(message.media.document, 'mime_type') and 'video' in message.media.document.mime_type:
                    is_video = True
                else:
                    # Attribute check fallback
                    for attr in message.media.document.attributes:
                         if hasattr(attr, 'duration'): 
                             is_video = True
                             break
            
            if is_video:
                return file_types.get('videos', False)
            else:
                return file_types.get('documents', False)
                
        return False

    async def _get_entity_robust(self, client, source):
        try:
            if source.isdigit() or (source.startswith('-') and source[1:].isdigit()):
                source = int(source)
            return await client.get_entity(source)
        except ValueError:
             # Refresh cache
            await client.get_dialogs(limit=50)
            try:
                return await client.get_entity(source)
            except Exception:
                return None
        except Exception as e:
            logger.error(f"Entity Resolve Error: {e}")
            return None
