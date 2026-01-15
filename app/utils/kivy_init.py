"""
Kivy Initialization Helper
Handles Kivy startup errors gracefully
"""
import os
import sys
import warnings
import logging

logger = logging.getLogger("KivyInit")

# Import capture_exception if available (may not be available during early init)
try:
    from .logger import capture_exception
except ImportError:
    def capture_exception(e, extra_data=None):
        pass  # Fallback if logger not available yet

def suppress_kivy_file_errors():
    """
    Suppress Kivy file-related errors by patching shutil.copytree
    This prevents Permission Denied errors when Kivy tries to copy icons
    """
    try:
        import shutil
        original_copytree = shutil.copytree
        
        def safe_copytree(*args, **kwargs):
            """Wrapper for shutil.copytree that ignores permission errors"""
            try:
                return original_copytree(*args, **kwargs)
            except (PermissionError, OSError) as e:
                # Log but don't crash
                logger.warning(f"Kivy file copy failed (ignored): {e}")
                # Return the destination path as if it succeeded
                return args[1] if len(args) > 1 else kwargs.get('dst', '')
        
        # Monkey-patch shutil.copytree
        shutil.copytree = safe_copytree
        logger.info("Kivy file error suppression enabled")
        
    except Exception as e:
        logger.error(f"Failed to patch shutil: {e}")
        capture_exception(e, extra_data={"context": "kivy_init_patch"})


def init_kivy_environment():
    """
    Initialize Kivy environment variables to prevent file errors
    Must be called BEFORE importing Kivy
    """
    # Prevent Kivy from trying to write log files
    os.environ['KIVY_NO_FILELOG'] = '1'
    os.environ['KIVY_NO_CONSOLELOG'] = '1'
    os.environ['KIVY_LOG_MODE'] = 'PYTHON'
    
    # Suppress warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='kivy')
    
    # Apply shutil patch
    suppress_kivy_file_errors()
    
    logger.info("Kivy environment initialized")
