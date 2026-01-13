import sys
import os
import asyncio
from unittest.mock import MagicMock

# הוספת התיקייה הנוכחית ל-path
sys.path.append(os.getcwd())

async def test_new_features():
    print("--- Test New Features ---")
    
    # 1. בדיקת ייבוא ספריות חדשות
    print("\n1. Library Check:")
    try:
        import qrcode
        print("[OK] qrcode imported successfully")
    except ImportError as e:
        print(f"[FAIL] Failed to import qrcode: {e}")
        
    try:
        import pyshorteners
        print("[OK] pyshorteners imported successfully")
    except ImportError as e:
        print(f"[FAIL] Failed to import pyshorteners: {e}")

    # 2. בדיקת URL Shortener
    print("\n2. URL Shortener Check:")
    try:
        from app.utils.url_shortener import shorten_url
        print("[OK] url_shortener module imported")
        # בדיקה אמיתית דורשת רשת, נסתפק בבדיקת קיום הפונקציה
        if callable(shorten_url):
             print("[OK] shorten_url is callable")
    except Exception as e:
        print(f"[FAIL] URL Shortener check failed: {e}")

    # 3. בדיקת AccountManager QR
    print("\n3. AccountManager QR Check:")
    try:
        from app.managers.account_manager import AccountManager
        am = AccountManager('temp_accounts.json', 'temp_sessions')
        if hasattr(am, 'start_qr_auth'):
            print("[OK] start_qr_auth method exists in AccountManager")
        else:
            print("[FAIL] start_qr_auth missing from AccountManager")
    except Exception as e:
        print(f"[FAIL] AccountManager check failed: {e}")

    # 4. בדיקת TransferManager Copy Logic
    print("\n4. TransferManager Copy Logic Check:")
    try:
        from app.managers.transfer_manager import TransferManager
        tm = TransferManager()
        
        # Test transfer_single_message signature
        import inspect
        sig = inspect.signature(tm.transfer_single_message)
        if 'file_types' in sig.parameters:
             print("[OK] transfer_single_message signature updated correctly")
        else:
             print("[FAIL] transfer_single_message signature incorrect")

    except Exception as e:
        print(f"[FAIL] TransferManager check failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_new_features())
