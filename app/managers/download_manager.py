"""
Download Manager
Handles downloading channels to local disk with strict rate limiting.
"""
import os
import asyncio
import random
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, MessageMediaVideo
import telethon.utils

from app.config import Config
from app.utils.logger import logger

class DownloadManager:
    """
    Manages secure downloading of chats to local storage.
    Enforces rate limits to avoid bans.
    """
    
    def __init__(self):
        self.active_downloads = {} # session_id -> bool (is_running)

    def create_session(self, session_id):
        self.active_downloads[session_id] = True

    def stop_session(self, session_id):
        if session_id in self.active_downloads:
            self.active_downloads[session_id] = False

    async def download_channel(self, session_id, client: TelegramClient, source, file_types, callback):
        """
        Download channel content to local disk.
        
        Args:
            session_id: Unique task ID
            client: Authenticated Telethon client
            source: Source channel (ID or Link)
            file_types: Dict of enabled file types (images, videos, etc.)
            callback: Async function(text) to update UI
        """
        try:
            entity = await self._get_entity_robust(client, source)
            if not entity:
                await callback("Error: Cannot find source channel")
                return

            chat_title = telethon.utils.get_display_name(entity)
            safe_title = "".join([c for c in chat_title if c.isalnum() or c in (' ', '-', '_')]).strip()
            download_path = os.path.join(Config.DOWNLOADS_DIR, safe_title)
            os.makedirs(download_path, exist_ok=True)

            total_messages = 0
            downloaded_count = 0
            
            await callback(f"Scanning: {chat_title}...")
            
            # Use reverse=True so we start from oldest if needed, or just iterate. 
            # Usually backup implies newest first or oldest first. 
            # Let's iterate normally (newest to oldest) but we serve robust backup.
            
            async for message in client.iter_messages(entity):
                if not self.active_downloads.get(session_id, False):
                    await callback("Stopped by user")
                    break

                total_messages += 1
                
                # Filter by type
                if not self._should_download(message, file_types):
                    continue
                
                # Download
                try:
                    fname = f"{message.id}"
                    if message.file and message.file.name:
                        fname += f"_{message.file.name}"
                    
                    # Log
                    await callback(f"Downloading Msg {message.id}...")
                    
                    path = await client.download_media(message, file=os.path.join(download_path, str(message.id)))
                    
                    if path:
                        downloaded_count += 1
                        await callback(f"Saved: {os.path.basename(path)}")
                    
                    # RATE LIMITING (CRITICAL)
                    # Sleep 2-5 seconds between media downloads
                    delay = random.uniform(2.5, 5.5)
                    await asyncio.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"Failed to download message {message.id}: {e}")
                    # Continue even if one fails
            
            await callback(f"Finished! Saved {downloaded_count} files in 'downloads/{safe_title}'")
            
        except Exception as e:
            logger.error(f"Download Session Error: {e}")
            await callback(f"Critical Error: {e}")
            import traceback
            traceback.print_exc()

    def _should_download(self, message, file_types):
        """Check if message matches selected file types"""
        if message.text and file_types.get('text') and not message.media:
            # We don't really 'download' text yet, maybe save to a text file?
            # For now, skip text-only if we are focused on media, 
            # unless we implement text export.
            # Let's assume user wants FILES.
            return False 

        if not message.media:
            return False

        if isinstance(message.media, MessageMediaPhoto):
            return file_types.get('images', False)
        
        if isinstance(message.media, (MessageMediaVideo, MessageMediaDocument)):
            # Check for video mime type or generic doc
            is_video = False
            if hasattr(message.media, 'document'):
                for attr in message.media.document.attributes:
                    if hasattr(attr, 'duration'): # simple video check
                        is_video = True
            
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
            except:
                return None
        except Exception as e:
            logger.error(f"Entity Resolve Error: {e}")
            return None
