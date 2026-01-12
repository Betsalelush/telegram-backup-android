#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for encryption and storage functionality
Tests new features added per MASTER_PLAN requirements
"""

import os
import sys
import json
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_encryption_manager():
    """Test EncryptionManager basic functionality"""
    print("Testing EncryptionManager...")
    
    try:
        from app.utils.encryption import EncryptionManager, ENCRYPTION_AVAILABLE
        
        if not ENCRYPTION_AVAILABLE:
            print("⚠ Encryption not available (cryptography not installed) - skipping")
            return
        
        # Create temporary directory for test
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Test 1: Initialize with password
            manager = EncryptionManager(password="test_password_123")
            assert manager.enabled, "Encryption should be enabled"
            assert manager.cipher is not None, "Cipher should be initialized"
            
            # Test 2: Encrypt/decrypt string data
            test_data = {"message": "Hello World", "number": 42, "list": [1, 2, 3]}
            encrypted = manager.encrypt(test_data)
            assert encrypted != json.dumps(test_data), "Encrypted data should differ from original"
            
            decrypted = manager.decrypt(encrypted)
            assert decrypted == test_data, "Decrypted data should match original"
            
            # Test 3: Encrypt/decrypt file
            test_file = os.path.join(temp_dir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write("Test file content")
            
            encrypted_file = test_file + '.enc'
            success = manager.encrypt_file(test_file, encrypted_file)
            assert success, "File encryption should succeed"
            assert os.path.exists(encrypted_file), "Encrypted file should exist"
            
            decrypted_file = os.path.join(temp_dir, 'test_decrypted.txt')
            success = manager.decrypt_file(encrypted_file, decrypted_file)
            assert success, "File decryption should succeed"
            
            with open(decrypted_file, 'r') as f:
                content = f.read()
            assert content == "Test file content", "Decrypted content should match"
            
            # Test 4: Hash data
            hash1 = manager.hash_data("test")
            hash2 = manager.hash_data("test")
            hash3 = manager.hash_data("different")
            
            assert hash1 == hash2, "Same input should produce same hash"
            assert hash1 != hash3, "Different input should produce different hash"
            
            print("✓ EncryptionManager tests passed")
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    except ImportError as e:
        print(f"⚠ EncryptionManager not available: {e} - skipping")


def test_storage_manager():
    """Test StorageManager basic functionality"""
    print("Testing StorageManager...")
    
    try:
        from app.utils.storage import StorageManager
        
        # Create temporary directory for test
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Initialize manager
            manager = StorageManager(temp_dir)
            
            # Test 1: Compress/decompress file
            test_file = os.path.join(temp_dir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write("Test content " * 1000)  # Compressible content
            
            compressed = manager.compress_file(test_file)
            assert compressed is not None, "Compression should succeed"
            assert os.path.exists(compressed), "Compressed file should exist"
            assert os.path.getsize(compressed) < os.path.getsize(test_file), "Compressed should be smaller"
            
            decompressed = manager.decompress_file(compressed)
            assert decompressed is not None, "Decompression should succeed"
            
            with open(decompressed, 'r') as f:
                content = f.read()
            assert "Test content" in content, "Decompressed content should match"
            
            # Test 2: Compress/decompress JSON
            test_data = {"key": "value", "numbers": list(range(100))}
            compressed_json = manager.compress_json(test_data)
            assert isinstance(compressed_json, bytes), "Compressed JSON should be bytes"
            
            decompressed_json = manager.decompress_json(compressed_json)
            assert decompressed_json == test_data, "Decompressed JSON should match"
            
            # Test 3: Directory size calculation
            size = manager.get_directory_size(temp_dir)
            assert size > 0, "Directory size should be positive"
            
            # Test 4: Format size
            formatted = manager.format_size(1024)
            assert "KB" in formatted, "Should format as KB"
            
            formatted = manager.format_size(1024 * 1024)
            assert "MB" in formatted, "Should format as MB"
            
            # Test 5: Storage stats
            stats = manager.get_storage_stats()
            assert 'total_size' in stats, "Stats should include total size"
            assert 'total_size_formatted' in stats, "Stats should include formatted size"
            
            # Test 6: Optimize progress files
            progress_dir = os.path.join(temp_dir, 'progress')
            os.makedirs(progress_dir)
            
            # Create test progress file with many IDs
            progress_file = os.path.join(progress_dir, 'test_progress.json')
            progress_data = {
                'transfer_id': 'test',
                'sent_message_ids': list(range(20000)),  # More than max
                'total_sent': 20000
            }
            with open(progress_file, 'w') as f:
                json.dump(progress_data, f)
            
            optimized = manager.optimize_progress_files(progress_dir, max_ids=10000)
            assert optimized == 1, "Should optimize 1 file"
            
            with open(progress_file, 'r') as f:
                optimized_data = json.load(f)
            assert len(optimized_data['sent_message_ids']) == 10000, "Should keep only 10000 IDs"
            
            print("✓ StorageManager tests passed")
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    except ImportError as e:
        print(f"⚠ StorageManager not available: {e} - skipping")


def test_config_encryption_integration():
    """Test that Config works with encryption"""
    print("Testing Config encryption integration...")
    
    try:
        from app.config import Config
        from app.utils.encryption import get_encryption_manager, ENCRYPTION_AVAILABLE
        
        if not ENCRYPTION_AVAILABLE:
            print("⚠ Encryption not available - skipping integration test")
            return
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Setup config
            Config.setup(temp_dir)
            
            # Get encryption manager
            enc_manager = get_encryption_manager()
            assert enc_manager is not None, "Should get encryption manager"
            
            # Test encrypting config data
            test_account = {
                'id': 'test123',
                'api_id': '12345',
                'api_hash': 'secret_hash',
                'phone': '+1234567890'
            }
            
            encrypted = enc_manager.encrypt(test_account)
            decrypted = enc_manager.decrypt(encrypted)
            
            assert decrypted == test_account, "Encrypted account data should match after decryption"
            
            print("✓ Config encryption integration tests passed")
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    except ImportError as e:
        print(f"⚠ Config encryption integration not available: {e} - skipping")


def test_backward_compatibility():
    """Test that encryption handles unencrypted legacy data"""
    print("Testing backward compatibility...")
    
    try:
        from app.utils.encryption import EncryptionManager, ENCRYPTION_AVAILABLE
        
        if not ENCRYPTION_AVAILABLE:
            print("⚠ Encryption not available - skipping compatibility test")
            return
        
        manager = EncryptionManager(password="test")
        
        # Test decrypting plain JSON (legacy format)
        legacy_data = {"key": "value", "number": 123}
        legacy_json = json.dumps(legacy_data)
        
        decrypted = manager.decrypt(legacy_json)
        assert decrypted == legacy_data, "Should handle plain JSON from legacy format"
        
        print("✓ Backward compatibility tests passed")
    
    except ImportError as e:
        print(f"⚠ Backward compatibility test not available: {e} - skipping")


if __name__ == '__main__':
    print("Running encryption and storage tests...\n")
    
    try:
        test_encryption_manager()
        test_storage_manager()
        test_config_encryption_integration()
        test_backward_compatibility()
        
        print("\n✅ All tests completed!")
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
