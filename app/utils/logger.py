# -*- coding: utf-8 -*-
"""
Sentry Logger Configuration
Enhanced logging with breadcrumbs and custom tags
"""

import logging
import sys
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from app.config import Config

# Configure UTF-8 encoding for Hebrew support
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Capture ALL logs including DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Sentry configuration with enhanced logging
sentry_logging = LoggingIntegration(
    level=logging.DEBUG,  # Capture DEBUG and above as breadcrumbs
    event_level=logging.WARNING  # Send warnings and errors as events
)

sentry_sdk.init(
    dsn=Config.SENTRY_DSN,
    traces_sample_rate=Config.SENTRY_TRACES_SAMPLE_RATE,
    profiles_sample_rate=Config.SENTRY_PROFILES_SAMPLE_RATE,
    max_breadcrumbs=Config.SENTRY_MAX_BREADCRUMBS,
    integrations=[sentry_logging],
    enable_tracing=True,  # Enable performance monitoring
    # Enable debug mode for development
    debug=False,
    # Attach stack traces to messages
    attach_stacktrace=True,
    # Send default PII (personally identifiable information)
    send_default_pii=False,
)

def add_breadcrumb(category, message, level='info', data=None):
    """
    Add a breadcrumb to Sentry
    
    Args:
        category: Category of the breadcrumb (e.g., 'auth', 'backup', 'ui')
        message: Description of the action
        level: Severity level ('debug', 'info', 'warning', 'error')
        data: Additional data dictionary
    """
    sentry_sdk.add_breadcrumb(
        category=category,
        message=message,
        level=level,
        data=data or {}
    )
    logger.info(f"[{category}] {message}")

def set_user_context(account_id=None, phone=None):
    """
    Set user context in Sentry
    
    Args:
        account_id: Account ID
        phone: Phone number
    """
    sentry_sdk.set_user({
        "id": account_id,
        "phone": phone
    })

def set_transfer_context(transfer_id, source_channel=None, target_channel=None):
    """
    Set transfer context in Sentry
    
    Args:
        transfer_id: Transfer ID
        source_channel: Source channel ID
        target_channel: Target channel ID
    """
    sentry_sdk.set_tag("transfer_id", transfer_id)
    if source_channel:
        sentry_sdk.set_tag("source_channel", source_channel)
    if target_channel:
        sentry_sdk.set_tag("target_channel", target_channel)

def capture_exception(exception, extra_data=None):
    """
    Capture an exception in Sentry
    
    Args:
        exception: The exception to capture
        extra_data: Additional data dictionary
    """
    if extra_data:
        sentry_sdk.set_context("extra", extra_data)
    sentry_sdk.capture_exception(exception)
    logger.error(f"Exception captured: {exception}", exc_info=True)

# Export logger and functions
__all__ = [
    'logger',
    'add_breadcrumb',
    'set_user_context',
    'set_transfer_context',
    'capture_exception'
]
