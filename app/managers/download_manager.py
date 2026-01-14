"""
Download Manager
Handles downloading channels to local disk with strict rate limiting.
"""
import os
import asyncio
import random
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import telethon.utils

from app.config import Config
from app.utils.logger import logger

class DownloadManager:
    # ... (rest of class)
    
    # ...
    
    def _should_download(self, message, file_types):
        """Check if message matches selected file types"""
        if message.text and file_types.get('text') and not message.media:
            return False 

        if not message.media:
            return False

        if isinstance(message.media, MessageMediaPhoto):
            return file_types.get('images', False)
        
        if isinstance(message.media, MessageMediaDocument):
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
