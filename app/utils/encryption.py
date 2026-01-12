# -*- coding: utf-8 -*-
"""
Encryption Module
Provides encryption/decryption for sensitive data storage
Implements modern encryption for data security (MASTER_PLAN Objective 4)
"""

import os
import json
import base64
import hashlib
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    logger.warning("cryptography not available - encryption disabled")


class EncryptionManager:
    """
    Manages encryption/decryption of sensitive data
    Uses Fernet (symmetric encryption) with key derivation
    """
    
    def __init__(self, password: Optional[str] = None):
        """
        Initialize encryption manager
        
        Args:
            password: Master password for encryption. If None, uses device-based key
        """
        self.enabled = ENCRYPTION_AVAILABLE
        self.cipher = None
        
        if self.enabled:
            self._setup_cipher(password)
    
    def _setup_cipher(self, password: Optional[str] = None):
        """Setup encryption cipher with key derivation"""
        try:
            if password:
                # Derive key from password
                key = self._derive_key(password)
            else:
                # Use device-based key (stored in config)
                key = self._get_or_create_device_key()
            
            self.cipher = Fernet(key)
            logger.info("Encryption initialized successfully")
        except Exception as e:
            logger.error(f"Failed to setup encryption: {e}")
            self.enabled = False
    
    def _derive_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation (generated if None)
            
        Returns:
            Base64-encoded Fernet key
        """
        if salt is None:
            salt = b'telegram_backup_salt_v1'  # Static salt for consistency
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _get_or_create_device_key(self) -> bytes:
        """
        Get or create device-specific encryption key
        
        Returns:
            Fernet encryption key
        """
        key_file = os.path.join(os.path.expanduser('~'), '.telegram_backup_key')
        
        if os.path.exists(key_file):
            try:
                with open(key_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Failed to read key file: {e}")
        
        # Generate new key
        key = Fernet.generate_key()
        
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions (Unix-like systems)
            if hasattr(os, 'chmod'):
                os.chmod(key_file, 0o600)
        except Exception as e:
            logger.warning(f"Failed to save key file: {e}")
        
        return key
    
    def encrypt(self, data: Any) -> str:
        """
        Encrypt data
        
        Args:
            data: Data to encrypt (will be JSON serialized)
            
        Returns:
            Encrypted string (base64 encoded)
        """
        if not self.enabled or self.cipher is None:
            # Return JSON without encryption if not available
            return json.dumps(data, ensure_ascii=False)
        
        try:
            # Serialize to JSON
            json_data = json.dumps(data, ensure_ascii=False)
            
            # Encrypt
            encrypted = self.cipher.encrypt(json_data.encode('utf-8'))
            
            # Return base64 encoded string
            return base64.b64encode(encrypted).decode('ascii')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            # Fallback to unencrypted
            return json.dumps(data, ensure_ascii=False)
    
    def decrypt(self, encrypted_data: str) -> Any:
        """
        Decrypt data
        
        Args:
            encrypted_data: Encrypted string (base64 encoded)
            
        Returns:
            Decrypted data (JSON deserialized)
        """
        if not self.enabled or self.cipher is None:
            # Try to parse as JSON without decryption
            try:
                return json.loads(encrypted_data)
            except:
                return encrypted_data
        
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('ascii'))
            
            # Decrypt
            decrypted = self.cipher.decrypt(encrypted_bytes)
            
            # Parse JSON
            return json.loads(decrypted.decode('utf-8'))
        except Exception as e:
            # Might be unencrypted data from older version
            logger.debug(f"Decryption failed, trying as plain JSON: {e}")
            try:
                return json.loads(encrypted_data)
            except:
                logger.error(f"Failed to decrypt or parse data: {e}")
                return None
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> bool:
        """
        Encrypt a file
        
        Args:
            file_path: Path to file to encrypt
            output_path: Path for encrypted file (defaults to file_path + '.enc')
            
        Returns:
            True if successful
        """
        if not self.enabled or self.cipher is None:
            logger.warning("Encryption not available")
            return False
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            encrypted = self.cipher.encrypt(data)
            
            if output_path is None:
                output_path = file_path + '.enc'
            
            with open(output_path, 'wb') as f:
                f.write(encrypted)
            
            logger.info(f"File encrypted: {file_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            return False
    
    def decrypt_file(self, encrypted_path: str, output_path: Optional[str] = None) -> bool:
        """
        Decrypt a file
        
        Args:
            encrypted_path: Path to encrypted file
            output_path: Path for decrypted file (defaults to encrypted_path without '.enc')
            
        Returns:
            True if successful
        """
        if not self.enabled or self.cipher is None:
            logger.warning("Encryption not available")
            return False
        
        try:
            with open(encrypted_path, 'rb') as f:
                encrypted = f.read()
            
            decrypted = self.cipher.decrypt(encrypted)
            
            if output_path is None:
                output_path = encrypted_path.rstrip('.enc')
            
            with open(output_path, 'wb') as f:
                f.write(decrypted)
            
            logger.info(f"File decrypted: {encrypted_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            return False
    
    def hash_data(self, data: str) -> str:
        """
        Create SHA256 hash of data (for verification, not encryption)
        
        Args:
            data: Data to hash
            
        Returns:
            Hex string of hash
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def is_available() -> bool:
        """Check if encryption is available"""
        return ENCRYPTION_AVAILABLE


# Global instance (initialized without password by default)
_default_encryption_manager = None

def get_encryption_manager(password: Optional[str] = None) -> EncryptionManager:
    """
    Get default encryption manager instance
    
    Args:
        password: Optional password for encryption
        
    Returns:
        EncryptionManager instance
    """
    global _default_encryption_manager
    
    if _default_encryption_manager is None or password is not None:
        _default_encryption_manager = EncryptionManager(password)
    
    return _default_encryption_manager
