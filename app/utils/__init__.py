"""
Utils package - Helper utilities
"""
from app.utils.logger import logger, add_breadcrumb, set_user_context, set_transfer_context, capture_exception
from app.utils.clipboard import paste_to_field
from app.utils import helpers

# Optional imports - won't fail if dependencies missing
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
    'storage_available'
]
