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
    import asyncio
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        logger.info("Importing main app...")
        from app.main import TelegramBackupApp
        
        logger.info("Starting app in ASYNC mode...")
        app = TelegramBackupApp()
        
        # Use simple run for now if async_run causes issues with KivyMD 1.2.0 compatibility
        # But Telethon NEEDS async.
        # Kivy 2.2.0+ supports async_run properly.
        # Let's try to run the async loop
        
        loop.run_until_complete(app.async_run(async_lib='asyncio'))
        
    except ImportError as e:
        logger.error(f"Import Error during startup: {e}")
        traceback.print_exc()
        # Try to report to Sentry
        if 'sentry_logger' in sys.modules:
            try:
                import sentry_logger
                sentry_logger.capture_exception(e, {"context": "startup_import_error"})
                time.sleep(2)
            except: pass
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Runtime Error during startup: {e}")
        traceback.print_exc()
        if 'sentry_logger' in sys.modules:
            try:
                import sentry_logger
                sentry_logger.capture_exception(e, {"context": "startup_runtime_error"})
                time.sleep(2)
            except: pass
        raise
    finally:
        loop.close()

if __name__ == '__main__':
    main()
