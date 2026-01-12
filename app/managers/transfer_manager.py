# -*- coding: utf-8 -*-
"""
Transfer Manager - Message Transfer and Rate Limiting
Handles message transfer, rate limiting, and smart delays
"""

import asyncio
import random
import time
import logging
from app.config import Config
from app.utils.logger import add_breadcrumb, capture_exception

logger = logging.getLogger(__name__)


class TransferManager:
    """Manages message transfer operations with rate limiting"""
    
    def __init__(self):
        # Rate limiting
        self.messages_per_minute = 0
        self.max_messages_per_minute = Config.MAX_MESSAGES_PER_MINUTE
        self.last_minute_start = time.time()
        self.consecutive_successes = 0
        
        # Delays
        self.min_delay = Config.SMART_DELAY_MIN
        self.max_delay = Config.SMART_DELAY_MAX
    
    async def transfer_message(self, client, message, source_entity, target_entity, method="forward"):
        """
        Transfer a single message from source to target
        
        Args:
            client: TelegramClient instance
            message: Message object to transfer
            source_entity: Source channel/chat entity
            target_entity: Target channel/chat entity
            method: Transfer method ("forward" or "copy")
        """
        try:
            if method == "forward":
                # Forward message
                await client.forward_messages(
                    entity=target_entity,
                    messages=message,
                    from_peer=source_entity
                )
                add_breadcrumb('transfer', f'Forwarded message {message.id}', 'info')
            
            elif method == "copy":
                # Copy message (send as new)
                if message.text:
                    await client.send_message(
                        entity=target_entity,
                        message=message.text
                    )
                elif message.media:
                    await client.send_file(
                        entity=target_entity,
                        file=message.media,
                        caption=message.message or ""
                    )
                add_breadcrumb('transfer', f'Copied message {message.id}', 'info')
            
            else:
                raise ValueError(f"Unknown transfer method: {method}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error transferring message {message.id}: {e}")
            capture_exception(e)
            raise
    
    async def check_rate_limit(self):
        """
        Check and enforce rate limiting
        Waits if rate limit is exceeded
        """
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.last_minute_start >= 60:
            add_breadcrumb('rate_limit', f'Minute reset: {self.messages_per_minute} messages sent', 'info')
            self.messages_per_minute = 0
            self.last_minute_start = current_time
        
        # Wait if limit exceeded
        if self.messages_per_minute >= self.max_messages_per_minute:
            wait_time = 60 - (current_time - self.last_minute_start)
            if wait_time > 0:
                add_breadcrumb('rate_limit', f'Rate limit reached, waiting {wait_time:.1f}s', 'warning')
                logger.warning(f"Rate limit reached. Waiting {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
                
                # Reset after wait
                self.messages_per_minute = 0
                self.last_minute_start = time.time()
    
    def smart_delay(self):
        """
        Calculate smart delay based on consecutive successes
        More successes = shorter delay (but still random)
        
        Returns:
            float: Delay in seconds
        """
        if self.consecutive_successes > 20:
            # Very successful - minimal delay
            delay = random.uniform(0.5, 1.5)
        elif self.consecutive_successes > 10:
            # Quite successful - short delay
            delay = random.uniform(1.0, 2.0)
        elif self.consecutive_successes > 5:
            # Moderately successful - medium delay
            delay = random.uniform(2.0, 3.0)
        else:
            # Few successes or just started - longer delay
            delay = random.uniform(3.0, 5.0)
        
        # Ensure within configured bounds
        delay = max(self.min_delay, min(delay, self.max_delay))
        
        add_breadcrumb('delay', f'Smart delay: {delay:.1f}s (successes: {self.consecutive_successes})', 'debug')
        return delay
    
    def reset_success_counter(self):
        """Reset consecutive success counter (call on error)"""
        self.consecutive_successes = 0
    
    def increment_success_counter(self):
        """Increment consecutive success counter"""
        self.consecutive_successes += 1
    
    def increment_message_counter(self):
        """Increment messages per minute counter"""
        self.messages_per_minute += 1
    
    def get_stats(self):
        """
        Get current transfer statistics
        
        Returns:
            dict: Statistics including rate and success count
        """
        return {
            'messages_per_minute': self.messages_per_minute,
            'max_messages_per_minute': self.max_messages_per_minute,
            'consecutive_successes': self.consecutive_successes,
            'current_delay_range': self.get_current_delay_range()
        }
    
    def get_current_delay_range(self):
        """Get current delay range based on success count"""
        if self.consecutive_successes > 20:
            return (0.5, 1.5)
        elif self.consecutive_successes > 10:
            return (1.0, 2.0)
        elif self.consecutive_successes > 5:
            return (2.0, 3.0)
        else:
            return (3.0, 5.0)
