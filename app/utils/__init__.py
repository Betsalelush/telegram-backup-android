"""
Utils package - Helper utilities
"""
# Only import modules that don't have heavy dependencies by default
from app.utils.logger import logger, add_breadcrumb, set_user_context, set_transfer_context, capture_exception

# Optional imports - won't fail if dependencies missing
try:
    from app.utils.clipboard import paste_to_field
except ImportError:
    paste_to_field = None

try:
    from app.utils import helpers
except ImportError:
    helpers = None

try:
    from app.utils.encryption import get_encryption_manager, EncryptionManager
    encryption_available = True
except ImportError:
    encryption_available = False
    get_encryption_manager = None
    EncryptionManager = None

try:
    from app.utils.storage import get_storage_manager, StorageManager
    storage_available = True
except ImportError:
    storage_available = False
    get_storage_manager = None
    StorageManager = None

try:
    from app.utils.performance import get_performance_monitor, get_transfer_tracker, PerformanceMonitor, TransferPerformanceTracker
    performance_available = True
except ImportError:
    performance_available = False
    get_performance_monitor = None
    get_transfer_tracker = None
    PerformanceMonitor = None
    TransferPerformanceTracker = None

__all__ = [
    'logger', 
    'add_breadcrumb', 
    'set_user_context', 
    'set_transfer_context', 
    'capture_exception', 
    'paste_to_field', 
    'helpers',
    'get_encryption_manager',
    'EncryptionManager',
    'encryption_available',
    'get_storage_manager',
    'StorageManager',
    'storage_available',
    'get_performance_monitor',
    'get_transfer_tracker',
    'PerformanceMonitor',
    'TransferPerformanceTracker',
    'performance_available'
]
