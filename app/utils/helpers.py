# -*- coding: utf-8 -*-
"""
Helper Functions
UI update and utility functions
"""

import time
import logging
from kivy.clock import Clock

logger = logging.getLogger(__name__)


def log_message(screen, message):
    """
    Add message to log
    
    Args:
        screen: Screen instance with log widget
        message: Message to log
    """
    def update_log(dt):
        current = screen.ids.log.text
        screen.ids.log.text = f"{current}\n{message}"
    
    Clock.schedule_once(update_log)
    logger.info(message)


def update_status(screen, text, color="Primary"):
    """
    Update status label
    
    Args:
        screen: Screen instance with status widget
        text: Status text
        color: Theme color ("Primary", "Secondary", "Error")
    """
    def update(dt):
        screen.ids.status.text = text
        screen.ids.status.theme_text_color = color
    
    Clock.schedule_once(update)


def update_progress(screen, processed, total, start_time):
    """
    Update progress bar and stats
    
    Args:
        screen: Screen instance with progress_bar widget
        processed: Number of messages processed
        total: Total messages
        start_time: Start time (timestamp)
    """
    def update(dt):
        if total > 0:
            progress = (processed / total) * 100
            screen.ids.progress_bar.value = progress
            
            # Calculate stats
            elapsed = time.time() - start_time
            if elapsed > 0:
                rate = processed / elapsed
                remaining = (total - processed) / rate if rate > 0 else 0
                
                stats = f"Progress: {processed}/{total} ({progress:.1f}%) - "
                stats += f"Rate: {rate:.1f} msg/s - "
                stats += f"ETA: {remaining/60:.1f} min"
                
                update_status(screen, stats, "Primary")
    
    Clock.schedule_once(update)


def get_transfer_method(screen):
    """
    Get selected transfer method
    
    Args:
        screen: Screen instance
        
    Returns:
        str: Transfer method ("forward" or "copy")
    """
    # Default to forward
    # Can be extended to read from UI selection
    return "forward"


def enable_ui_elements(screen, element_ids, enabled=True):
    """
    Enable/disable multiple UI elements
    
    Args:
        screen: Screen instance
        element_ids: List of element IDs
        enabled: True to enable, False to disable
    """
    def update(dt):
        for element_id in element_ids:
            if element_id in screen.ids:
                screen.ids[element_id].disabled = not enabled
    
    Clock.schedule_once(update)
