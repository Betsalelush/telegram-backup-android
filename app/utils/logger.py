# -*- coding: utf-8 -*-
"""
Logger utility with Sentry integration
Enhanced logging with breadcrumbs and custom tags
Unified Sentry logger - merged from sentry_logger.py
"""
import logging
import sys
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from ..config import Config

# Configure UTF-8 encoding for Hebrew support
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Configure logging
# Show INFO level messages to help with debugging and user feedback
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('TelegramBackup')
logger.setLevel(logging.INFO)  # Show INFO and above


def init_sentry():
    """
    Initialize Sentry SDK with enhanced configuration
    Only initializes if SENTRY_DSN is configured
    """
    try:
        # Check if Sentry DSN is configured
        if not Config.SENTRY_DSN or Config.SENTRY_DSN == "":
            logger.info("Sentry disabled (no DSN configured)")
            return False
        
        # Sentry configuration with enhanced logging
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture INFO and above as breadcrumbs
            event_level=logging.WARNING  # Send warnings and errors as events
        )
        
        sentry_sdk.init(
            dsn=Config.SENTRY_DSN,
            traces_sample_rate=Config.SENTRY_TRACES_SAMPLE_RATE,
            profiles_sample_rate=1.0,  # 100% of profiles
            max_breadcrumbs=100,  # Keep last 100 breadcrumbs
            integrations=[sentry_logging],
            enable_tracing=True,  # Enable performance monitoring
            # Enable debug mode for development
            debug=False,
            # Attach stack traces to messages
            attach_stacktrace=True,
            # Send default PII (personally identifiable information)
            send_default_pii=False,
            environment=Config.SENTRY_ENVIRONMENT
        )
        
        logger.info("Sentry initialized successfully")
        return True
        
    except Exception as e:
        logger.warning(f"Failed to initialize Sentry: {e}")
        return False


def add_breadcrumb(category=None, message=None, level='info', data=None):
    """
    Add a breadcrumb to Sentry (safe - works even if Sentry is disabled)
    
    Args:
        category: Category of the breadcrumb (e.g., 'auth', 'backup', 'ui')
        message: Description of the action
        level: Severity level ('debug', 'info', 'warning', 'error')
        data: Additional data dictionary
    """
    try:
        # Only send if Sentry is initialized
        if not Config.SENTRY_DSN:
            return
            
        # Support both old signature (message only) and new signature (category, message, level, data)
        if category is None and message is not None:
            # Old signature: add_breadcrumb(message, data)
            sentry_sdk.add_breadcrumb(
                message=message,
                data=data or {},
                level=level
            )
        else:
            # New signature: add_breadcrumb(category, message, level, data)
            # Matches sentry_logger.py signature exactly
            sentry_sdk.add_breadcrumb(
                category=category or 'general',
                message=message or '',
                level=level,
                data=data or {}
            )
    except Exception:
        pass  # Silently ignore if Sentry is not initialized


def capture_message(message: str, level: str = "info", extra: dict = None):
    """
    Send a message to Sentry (visible even without errors)
    Safe - works even if Sentry is disabled
    
    Args:
        message: Message to send
        level: Severity level (debug, info, warning, error)
        extra: Additional context data
    """
    try:
        if not Config.SENTRY_DSN:
            return
            
        with sentry_sdk.push_scope() as scope:
            if extra:
                for key, value in extra.items():
                    scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level=level)
    except Exception:
        pass  # Silently ignore if Sentry is not initialized


def set_user_context(account_id=None, phone=None, user_id=None):
    """
    Set user context in Sentry
    Safe - works even if Sentry is disabled
    
    Args:
        account_id: Account ID (matches sentry_logger.py signature)
        phone: Phone number
        user_id: User ID (alternative parameter name for backward compatibility)
    """
    try:
        if not Config.SENTRY_DSN:
            return
            
        # Support both parameter names for backward compatibility
        # Primary signature matches sentry_logger.py: set_user_context(account_id=None, phone=None)
        user_id_value = account_id or user_id
        sentry_sdk.set_user({
            "id": user_id_value,
            "phone": phone
        })
    except Exception:
        pass  # Silently ignore if Sentry is not initialized


def set_transfer_context(transfer_id, source_channel=None, target_channel=None):
    """
    Set transfer context in Sentry
    Safe - works even if Sentry is disabled
    
    Args:
        transfer_id: Transfer ID
        source_channel: Source channel ID
        target_channel: Target channel ID
    """
    try:
        if not Config.SENTRY_DSN:
            return
            
        sentry_sdk.set_tag("transfer_id", transfer_id)
        if source_channel:
            sentry_sdk.set_tag("source_channel", source_channel)
        if target_channel:
            sentry_sdk.set_tag("target_channel", target_channel)
    except Exception:
        pass  # Silently ignore if Sentry is not initialized


def capture_exception(exception, extra_data=None, extra=None):
    """
    Capture an exception in Sentry
    Safe - works even if Sentry is disabled
    
    Args:
        exception: The exception to capture
        extra_data: Additional data dictionary (matches sentry_logger.py signature)
        extra: Extra context data (alternative parameter name for backward compatibility)
    """
    try:
        logger.error(f"Exception: {exception}", exc_info=True)
        
        if not Config.SENTRY_DSN:
            return
            
        # Support both parameter names for backward compatibility
        # Primary signature matches sentry_logger.py: capture_exception(exception, extra_data=None)
        context_data = extra_data or extra
        if context_data:
            sentry_sdk.set_context("extra", context_data)
        sentry_sdk.capture_exception(exception)
    except Exception:
        pass  # Silently ignore if Sentry is not initialized


# Export logger and functions
__all__ = [
    'logger',
    'init_sentry',
    'add_breadcrumb',
    'capture_message',
    'set_user_context',
    'set_transfer_context',
    'capture_exception'
]
