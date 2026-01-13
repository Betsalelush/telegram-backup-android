"""
Main entry point for the application
Imports from app package
"""
import sys
import logging
import traceback
import time

# Configure basic logging first as fallback
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Launcher")

# Initialize Sentry immediately to capture startup/import errors
try:
    import sentry_logger
    logger.info("Sentry logger imported successfully")
    sentry_logger.add_breadcrumb('system', 'Main entry point started')
except Exception as e:
    logger.error(f"CRITICAL: Failed to import sentry_logger: {e}")
    traceback.print_exc()

def main():
    try:
        logger.info("Importing main app...")
        from app.main import TelegramBackupApp
        
        logger.info("Starting app...")
        TelegramBackupApp().run()
        
    except ImportError as e:
        logger.error(f"Import Error during startup: {e}")
        traceback.print_exc()
        # Try to report to Sentry if available
        if 'sentry_logger' in sys.modules:
            try:
                import sentry_logger
                sentry_logger.capture_exception(e, {"context": "startup_import_error"})
                # Give Sentry a moment to send
                time.sleep(2)
            except:
                pass
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Runtime Error during startup: {e}")
        traceback.print_exc()
        # Try to report to Sentry if available
        if 'sentry_logger' in sys.modules:
            try:
                import sentry_logger
                sentry_logger.capture_exception(e, {"context": "startup_runtime_error"})
                # Give Sentry a moment to send
                time.sleep(2)
            except:
                pass
        raise

if __name__ == '__main__':
    main()
