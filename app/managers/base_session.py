"""
Base Session
Abstract base class for Transfer and Download sessions
De-duplicates session management logic
"""
from datetime import datetime
from typing import Dict, Any, Optional

class BaseSession:
    """
    Base class for any active session (transfer, download, etc.)
    """
    def __init__(self, session_id: str, config: Optional[Dict[str, Any]] = None):
        self.session_id = session_id
        self.config = config or {}
        
        # Common status flags
        self.is_running = True
        self.start_time = datetime.now()
        self.status = "Initializing..."
        
        # Base stats (can be extended by subclasses)
        self.stats = {
            'total_processed': 0,
            'total_errors': 0,
            'total_skipped': 0
        }

    def stop(self):
        """Stop the session"""
        self.is_running = False
        self.status = "Stopped"

    def update_status(self, new_status: str):
        """Update textual status"""
        self.status = new_status

    def to_dict(self):
        """Serialize mostly for debugging/logging"""
        return {
            'session_id': self.session_id,
            'status': self.status,
            'is_running': self.is_running,
            'start_time': self.start_time.isoformat(),
            'stats': self.stats
        }
