"""
Helper utilities for channels, file types, and media
"""
import re
from typing import List, Dict, Optional
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat

from .logger import logger, add_breadcrumb


async def list_available_chats(client: TelegramClient) -> List[Dict]:
    """
    List all available chats/channels
    
    Args:
        client: Telegram client
        
    Returns:
        List[Dict]: List of chats with id, title, username
    """
    chats = []
    
    try:
        async for dialog in client.iter_dialogs():
            chat_info = {
                'id': dialog.id,
                'title': dialog.title,
                'username': getattr(dialog.entity, 'username', None),
                'type': 'channel' if isinstance(dialog.entity, Channel) else 'chat'
            }
            chats.append(chat_info)
        
        logger.info(f"Found {len(chats)} chats")
        add_breadcrumb("Chats listed", {"count": len(chats)})
        
        return chats
        
    except Exception as e:
        logger.error(f"Error listing chats: {e}")
        return []


def parse_channel_link(link: str) -> Optional[str]:
    """
    Parse channel link and extract ID or username
    
    Supports:
    - t.me/username
    - t.me/c/123456789
    - @username
    - -100123456789 (direct ID)
    
    Args:
        link: Channel link or ID
        
    Returns:
        Optional[str]: Channel identifier or None
    """
    if not link:
        return None
    
    link = link.strip()
    
    # Direct ID (starts with - or digit)
    if link.startswith('-') or link.isdigit():
        return link
    
    # @username
    if link.startswith('@'):
        return link[1:]
    
    # t.me/username
    username_match = re.match(r'(?:https?://)?t\.me/([a-zA-Z0-9_]+)', link)
    if username_match:
        return username_match.group(1)
    
    # t.me/c/123456789
    private_match = re.match(r'(?:https?://)?t\.me/c/(\d+)', link)
    if private_match:
        # Convert to full ID format
        return f"-100{private_match.group(1)}"
    
    logger.warning(f"Could not parse channel link: {link}")
    return None


def get_channel_variations(channel_id: str) -> List[str]:
    """
    Get different variations of channel ID
    
    Args:
        channel_id: Channel ID
        
    Returns:
        List[str]: List of ID variations
    """
    variations = [channel_id]
    
    # If starts with -100, add without it
    if channel_id.startswith('-100'):
        variations.append(channel_id[4:])
    
    # If numeric, add with -100
    elif channel_id.isdigit():
        variations.append(f"-100{channel_id}")
    
    return variations


def choose_file_types(selected: Dict[str, bool] = None) -> Dict[str, bool]:
    """
    Choose which file types to transfer
    
    Args:
        selected: Dictionary of file type selections
        
    Returns:
        Dict[str, bool]: File type selections
    """
    from ..config import Config
    
    if selected is None:
        # Default: all types
        return Config.SUPPORTED_FILE_TYPES.copy()
    
    # Validate selections
    valid_types = {}
    for file_type, enabled in selected.items():
        if file_type in Config.SUPPORTED_FILE_TYPES:
            valid_types[file_type] = enabled
    
    return valid_types


def filter_by_file_type(message, file_types: Dict[str, bool]) -> bool:
    """
    Check if message matches selected file types
    
    Args:
        message: Telegram message
        file_types: Dictionary of enabled file types
        
    Returns:
        bool: True if message should be transferred
    """
    # Text messages
    if message.text and not message.media:
        return file_types.get('text', True)
    
    # Media messages
    if message.media:
        media_type = type(message.media).__name__
        
        if 'Photo' in media_type:
            return file_types.get('photos', True)
        elif 'Video' in media_type or 'Document' in media_type:
            # Check if it's a video
            if hasattr(message.media, 'document'):
                mime = getattr(message.media.document, 'mime_type', '')
                if 'video' in mime:
                    return file_types.get('videos', True)
            return file_types.get('documents', True)
        elif 'Audio' in media_type:
            return file_types.get('audio', True)
        elif 'Voice' in media_type:
            return file_types.get('voice', True)
        elif 'Sticker' in media_type:
            return file_types.get('stickers', True)
    
    # Default: transfer
    return True


async def download_media(client: TelegramClient, message, 
                        file_path: str = None) -> Optional[bytes]:
    """
    Download media from message
    
    Args:
        client: Telegram client
        message: Message with media
        file_path: Optional file path to save
        
    Returns:
        Optional[bytes]: Downloaded file bytes or None
    """
    try:
        if not message.media:
            logger.warning("Message has no media")
            return None
        
        # Download
        if file_path:
            await client.download_media(message.media, file=file_path)
            logger.info(f"Downloaded media to {file_path}")
            return None
        else:
            file_bytes = await client.download_media(message.media, file=bytes)
            logger.info(f"Downloaded media ({len(file_bytes)} bytes)")
            return file_bytes
            
    except Exception as e:
        logger.error(f"Error downloading media: {e}")
        return None


async def upload_media(client: TelegramClient, target_entity,
                      file_data, caption: str = None):
    """
    Upload media to channel
    
    Args:
        client: Telegram client
        target_entity: Target channel
        file_data: File bytes or path
        caption: Optional caption
        
    Returns:
        bool: True if uploaded successfully
    """
    try:
        await client.send_file(
            target_entity,
            file_data,
            caption=caption or ''
        )
        
        logger.info("Uploaded media successfully")
        add_breadcrumb("Media uploaded")
        return True
        
    except Exception as e:
        logger.error(f"Error uploading media: {e}")
        return False
