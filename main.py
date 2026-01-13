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
    
    # Define the async entry point
    async def run_app():
        logger.info("Importing main app...")
        try:
            from app.main import TelegramBackupApp
            logger.info("Starting app in ASYNC mode (asyncio.run)...")
            app = TelegramBackupApp()
            await app.async_run(async_lib='asyncio')
        except Exception as e:
            logger.error(f"Error inside async_run: {e}")
            raise e

    try:
        # Run the top-level entry point
        if sys.platform == 'win32':
             # Windows specific policy often needed for Proactor/Selector issues
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
             
        asyncio.run(run_app())
        
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

if __name__ == '__main__':
    main()
