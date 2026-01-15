"""
Logger utility with Sentry integration
"""
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from ..config import Config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('TelegramBackup')


def init_sentry():
    """Initialize Sentry SDK"""
    try:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
        
        sentry_sdk.init(
            dsn=Config.SENTRY_DSN,
            traces_sample_rate=Config.SENTRY_TRACES_SAMPLE_RATE,
            environment=Config.SENTRY_ENVIRONMENT,
            integrations=[sentry_logging]
        )
        
        logger.info("Sentry initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def add_breadcrumb(message: str, data: dict = None):
    """
    Add breadcrumb to Sentry
    
    Args:
        message: Breadcrumb message
        data: Additional data
    """
    try:
        sentry_sdk.add_breadcrumb(
            message=message,
            data=data or {},
            level='info'
        )
    except Exception as e:
        logger.error(f"Failed to add breadcrumb: {e}")


def capture_message(message: str, level: str = "info", extra: dict = None):
    """
    Send a message to Sentry (visible even without errors)
    
    Args:
        message: Message to send
        level: Severity level (debug, info, warning, error)
        extra: Additional context data
    """
    try:
        with sentry_sdk.push_scope() as scope:
            if extra:
                for key, value in extra.items():
                    scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level=level)
    except Exception as e:
        logger.error(f"Failed to capture message: {e}")


def set_user_context(user_id: str, phone: str = None):
    """
    Set user context in Sentry
    
    Args:
        user_id: User ID
        phone: Phone number
    """
    try:
        sentry_sdk.set_user({
            "id": user_id,
            "phone": phone
        })
    except Exception as e:
        logger.error(f"Failed to set user context: {e}")


def capture_exception(exception: Exception, extra: dict = None):
    """
    Capture exception in Sentry
    
    Args:
        exception: Exception to capture
        extra: Extra context data
    """
    try:
        with sentry_sdk.push_scope() as scope:
            if extra:
                for key, value in extra.items():
                    scope.set_extra(key, value)
            sentry_sdk.capture_exception(exception)
    except Exception as e:
        logger.error(f"Failed to capture exception: {e}")
