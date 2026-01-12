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
from telethon.tl.types import Message

from ..config import Config
from ..utils.logger import logger, add_breadcrumb


class TransferManager:
    """
    Manages message transfers
    
    Features:
    - Multiple transfer methods (forward, send_message, download/upload)
    - Round-robin between multiple accounts
    - Rate limiting (20 msg/min)
    - Smart delay based on success rate
    - FloodWait handling per account
    """
    
    def __init__(self):
        """Initialize Transfer Manager"""
        # Rate limiting
        self.messages_per_minute = 0
        self.minute_start_time = None
        self.max_messages_per_minute = Config.MAX_MESSAGES_PER_MINUTE
        
        # Smart delay
        self.consecutive_successes = 0
        
        # Round-robin
        self.current_client_index = 0
        self.client_flood_wait = {}  # client_id -> wait_until_time
        
        # Statistics
        self.total_sent = 0
        self.total_skipped = 0
        self.total_errors = 0
        self.start_time = None
        
        add_breadcrumb("TransferManager initialized")
    
    async def transfer_message(self, client: TelegramClient, message: Message,
                              source_entity, target_entity, 
                              method: str = "forward") -> bool:
        """
        Transfer single message using specified method
        
        Args:
            client: Telegram client
            message: Message to transfer
            source_entity: Source channel entity
            target_entity: Target channel entity
            method: Transfer method (forward/send_message/download_upload)
            
        Returns:
            bool: True if transferred successfully
        """
        try:
            if method == "forward":
                # Forward with credit
                await client.forward_messages(
                    target_entity,
                    message,
                    source_entity
                )
                
            elif method == "send_message":
                # Send without credit
                await client.send_message(
                    target_entity,
                    message=message
                )
                
            elif method == "download_upload":
                # Download and upload (no credit)
                if message.media:
                    # Download media
                    file = await client.download_media(message.media, file=bytes)
                    
                    if file:
                        # Upload to target
                        await client.send_file(
                            target_entity,
                            file,
                            caption=message.text if message.text else ''
                        )
                    else:
                        raise Exception("Failed to download media")
                elif message.text:
                    # Text only
                    await client.send_message(target_entity, message.text)
            
            self.consecutive_successes += 1
            self.total_sent += 1
            return True
            
        except Exception as e:
            logger.error(f"Error transferring message {message.id}: {e}")
            self.consecutive_successes = 0
            self.total_errors += 1
            return False
    
    async def check_rate_limit(self):
        """
        Check and manage rate limits (20 messages/minute)
        
        Waits if limit is reached
        """
        if self.minute_start_time is None:
            self.minute_start_time = datetime.now()
        
        # Check if minute passed
        elapsed = datetime.now() - self.minute_start_time
        if elapsed.total_seconds() >= 60:
            # Reset counter
            self.messages_per_minute = 0
            self.minute_start_time = datetime.now()
            logger.info(f"Rate limit reset: 0/{self.max_messages_per_minute} messages this minute")
        
        # Check if limit reached
        if self.messages_per_minute >= self.max_messages_per_minute:
            wait_time = 60 - elapsed.total_seconds()
            if wait_time > 0:
                logger.warning(f"Rate limit reached! Waiting {int(wait_time)}s...")
                add_breadcrumb("Rate limit hit", {"wait_time": int(wait_time)})
                await asyncio.sleep(wait_time)
                # Reset after waiting
                self.messages_per_minute = 0
                self.minute_start_time = datetime.now()
        
        # Increment counter
        self.messages_per_minute += 1
    
    def smart_delay(self) -> float:
        """
        Calculate smart delay based on consecutive successes
        
        Returns:
            float: Delay in seconds
        """
        if self.consecutive_successes > 10:
            # Fast mode
            delay = random.uniform(Config.SMART_DELAY_MIN, Config.SMART_DELAY_MIN + 1)
        elif self.consecutive_successes > 5:
            # Medium mode
            delay = random.uniform(Config.SMART_DELAY_MIN + 1, Config.SMART_DELAY_MAX - 2)
        else:
            # Slow mode (after errors)
            delay = random.uniform(Config.SMART_DELAY_MAX - 2, Config.SMART_DELAY_MAX)
        
        return delay
    
    async def send_messages_batch(self, clients: List[TelegramClient], 
                                  messages: List[Message],
                                  source_entity, target_entity,
                                  method: str = "forward") -> Dict:
        """
        Send batch of messages using round-robin between clients
        
        Args:
            clients: List of Telegram clients
            messages: List of messages to send
            source_entity: Source channel entity
            target_entity: Target channel entity
            method: Transfer method
            
        Returns:
            Dict: Statistics (sent, skipped, errors)
        """
        stats = {
            'sent': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for message in messages:
            # Get next available client
            client = await self.get_next_client(clients)
            
            if not client:
                logger.error("No available clients!")
                stats['errors'] += 1
                continue
            
            # Check rate limit
            await self.check_rate_limit()
            
            # Transfer message
            success = await self.transfer_message(
                client, message, source_entity, target_entity, method
            )
            
            if success:
                stats['sent'] += 1
            else:
                stats['errors'] += 1
            
            # Smart delay
            delay = self.smart_delay()
            await asyncio.sleep(delay)
        
        add_breadcrumb("Batch sent", stats)
        return stats
    
    async def get_next_client(self, clients: List[TelegramClient]) -> Optional[TelegramClient]:
        """
        Get next available client (round-robin with FloodWait check)
        
        Args:
            clients: List of available clients
            
        Returns:
            Optional[TelegramClient]: Next client or None if all in FloodWait
        """
        if not clients:
            return None
        
        # Try all clients
        attempts = 0
        while attempts < len(clients):
            # Get next client (round-robin)
            client = clients[self.current_client_index]
            client_id = id(client)
            
            # Move to next for next time
            self.current_client_index = (self.current_client_index + 1) % len(clients)
            
            # Check if in FloodWait
            if client_id in self.client_flood_wait:
                wait_until = self.client_flood_wait[client_id]
                if datetime.now() < wait_until:
                    # Still in FloodWait, try next
                    attempts += 1
                    continue
                else:
                    # FloodWait expired, remove
                    del self.client_flood_wait[client_id]
            
            # Client is available
            return client
        
        # All clients in FloodWait
        logger.warning("All clients in FloodWait!")
        return None
    
    async def handle_flood_wait_for_client(self, client: TelegramClient, 
                                          wait_seconds: int):
        """
        Handle FloodWait for specific client
        
        Args:
            client: Telegram client
            wait_seconds: Seconds to wait
        """
        client_id = id(client)
        wait_until = datetime.now() + timedelta(seconds=wait_seconds)
        
        self.client_flood_wait[client_id] = wait_until
        
        logger.warning(f"Client {client_id} in FloodWait for {wait_seconds}s until {wait_until}")
        add_breadcrumb("FloodWait", {
            "client_id": client_id,
            "wait_seconds": wait_seconds
        })
    
    def get_stats(self) -> Dict:
        """
        Get transfer statistics
        
        Returns:
            Dict: Statistics
        """
        elapsed = 0
        speed = 0
        
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            if elapsed > 0:
                speed = self.total_sent / elapsed
        
        return {
            'total_sent': self.total_sent,
            'total_skipped': self.total_skipped,
            'total_errors': self.total_errors,
            'elapsed_seconds': elapsed,
            'messages_per_second': speed,
            'consecutive_successes': self.consecutive_successes
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.total_sent = 0
        self.total_skipped = 0
        self.total_errors = 0
        self.consecutive_successes = 0
        self.start_time = datetime.now()
        
        add_breadcrumb("Stats reset")
    
    def create_transfer(self, transfer_config: Dict) -> str:
        """
        Create new transfer task
        
        Args:
            transfer_config: Transfer configuration
            
        Returns:
            str: Transfer ID
        """
        import uuid
        transfer_id = f"transfer_{uuid.uuid4().hex[:12]}"
        
        # Reset stats for new transfer
        self.reset_stats()
        
        logger.info(f"Created transfer: {transfer_id}")
        add_breadcrumb("Transfer created", {"transfer_id": transfer_id})
        
        return transfer_id
