# -*- coding: utf-8 -*-
"""
Clipboard Utilities
Handles clipboard operations for Android and Desktop
"""

import logging

logger = logging.getLogger(__name__)


def paste_to_field(app, field_id):
    """
    Paste clipboard content to specified field
    
    Args:
        app: App instance
        field_id: ID of the field to paste into
    """
    try:
        # Try Android clipboard
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
                                app.root.ids[field_id].text = str(text)
                                logger.info(f"Pasted to {field_id}")
                            Clock.schedule_once(update_field)
            except Exception as e:
                logger.error(f"ERROR pasting (Android): {e}")
        
        get_clipboard()
        
    except ImportError:
        # Not on Android - try desktop clipboard
        try:
            from kivy.core.clipboard import Clipboard
            text = Clipboard.paste()
            if text:
                app.root.ids[field_id].text = text
                logger.info(f"Pasted to {field_id}")
        except Exception as e:
            logger.error(f"ERROR pasting (Desktop): {e}")
