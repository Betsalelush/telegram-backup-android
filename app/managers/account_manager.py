"""
Account Manager
Manages multiple Telegram accounts
"""
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from telethon import TelegramClient
from telethon.sessions import MemorySession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

from ..config import Config
from ..utils.logger import logger, add_breadcrumb


class AccountManager:
    """
    Manages Telegram accounts
    
    Features:
    - Add/remove accounts
    - Connect/disconnect accounts
    - Save/load from JSON
    - Track connection status
    """
    
    def __init__(self, accounts_file: str, sessions_dir: str):
        """
        Initialize Account Manager
        
        Args:
            accounts_file: Path to accounts JSON file
            sessions_dir: Directory for session files
        """
        self.accounts_file = accounts_file
        self.sessions_dir = sessions_dir
        self.accounts = []
        self.clients = {}  # account_id -> TelegramClient
        
        # Load existing accounts
        self.load_accounts()
        
        # New: Global credentials
        self.global_api_id = ""
        self.global_api_hash = ""
        self._load_global_settings()
        
        add_breadcrumb("AccountManager initialized", {"accounts_count": len(self.accounts)})
    
    def _load_global_settings(self):
        """Internal: Load global settings from JSON if exists"""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.global_api_id = data.get('global_api_id', "")
                    self.global_api_hash = data.get('global_api_hash', "")
            except: pass

    def save_global_settings(self, api_id: str, api_hash: str):
        """Save global API credentials"""
        self.global_api_id = api_id
        self.global_api_hash = api_hash
        
        # We need to save to file
        try:
            data = {}
            if os.path.exists(self.accounts_file):
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            data['global_api_id'] = api_id
            data['global_api_hash'] = api_hash
            
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save global settings: {e}")
    
    def load_accounts(self):
        """
        Load accounts from JSON file
        
        Returns:
            List[Dict]: List of accounts
        """
        if not os.path.exists(self.accounts_file):
            logger.info("No accounts file found, starting fresh")
            self.accounts = []
            return self.accounts
        
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.accounts = data.get('accounts', [])
            
            logger.info(f"Loaded {len(self.accounts)} accounts")
            add_breadcrumb("Accounts loaded", {"count": len(self.accounts)})
            return self.accounts
            
        except Exception as e:
            logger.error(f"Error loading accounts: {e}")
            self.accounts = []
            return self.accounts
    
    def save_accounts(self):
        """
        Save accounts to JSON file
        
        Returns:
            bool: True if saved successfully
        """
        try:
            data = {
                'accounts': self.accounts,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved {len(self.accounts)} accounts")
            add_breadcrumb("Accounts saved", {"count": len(self.accounts)})
            return True
            
        except Exception as e:
            logger.error(f"Error saving accounts: {e}")
            return False
    
    def add_account(self, name: str, phone: str, api_id: str = None, api_hash: str = None) -> str:
        """
        Add a new account to the manager
        """
        account_id = f"acc_{uuid.uuid4().hex[:12]}"
        
        # Use provided or global if empty
        final_api_id = api_id if api_id and api_id.strip() else self.global_api_id
        final_api_hash = api_hash if api_hash and api_hash.strip() else self.global_api_hash
        
        # Fallback to public if everything is empty
        if not final_api_id: final_api_id = "21568473"
        if not final_api_hash: final_api_hash = "cc39659b867c26ae67f40cfdca8705f1"

        # Create account object
        account = {
            'id': account_id,
            'name': name,
            'api_id': final_api_id,
            'api_hash': final_api_hash,
            'phone': phone,
            'session_path': Config.get_session_path(phone),
            'is_connected': False,
            'created_at': datetime.now().isoformat(),
            'last_used': None
        }
        
        self.accounts.append(account)
        self.save_accounts()
        
        logger.info(f"Added account: {name} ({phone})")
        add_breadcrumb("Account added", {"account_id": account_id, "phone": phone})
        
        return account_id
    
    def remove_account(self, account_id: str):
        """
        Remove account
        
        Args:
            account_id: Account ID to remove
            
        Returns:
            bool: True if removed successfully
        """
        # Find account
        account = self.get_account(account_id)
        if not account:
            logger.warning(f"Account not found: {account_id}")
            return False
        
        # Disconnect if connected
        if account_id in self.clients:
            self.disconnect_account(account_id)
        
        # Remove from list
        self.accounts = [acc for acc in self.accounts if acc['id'] != account_id]
        self.save_accounts()
        
        logger.info(f"Removed account: {account_id}")
        add_breadcrumb("Account removed", {"account_id": account_id})
        
        return True
    
    async def connect_account(self, account_id: str) -> bool:
        """
        Connect to Telegram account
        
        Args:
            account_id: Account ID
            
        Returns:
            bool: True if connected successfully
        """
        account = self.get_account(account_id)
        if not account:
            logger.error(f"Account not found: {account_id}")
            return False
        
        try:
            # Create client
            client = TelegramClient(
                MemorySession(),
                int(account['api_id']),
                account['api_hash']
            )
            
            # Connect
            await client.connect()
            
            # Check if authorized
            if not await client.is_user_authorized():
                logger.warning(f"Account not authorized: {account_id}")
                # We don't disconnect here because we might want to sign in
                self.clients[account_id] = client
                return False
            
            # Store client
            self.clients[account_id] = client
            
            # Update account status
            account['is_connected'] = True
            account['authorized'] = True # Explicit flag
            account['last_used'] = datetime.now().isoformat()
            self.save_accounts()
            
            logger.info(f"Connected account: {account['name']}")
            add_breadcrumb("Account connected", {"account_id": account_id})
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting account {account_id}: {e}")
            return False

    async def send_login_code(self, account_id: str):
        """Send login code to phone"""
        account = self.get_account(account_id)
        if not account: return None
        
        try:
            client = self.clients.get(account_id)
            if not client or not client.is_connected():
                client = TelegramClient(
                    MemorySession(),
                    int(account['api_id']),
                    account['api_hash']
                )
                await client.connect()
                self.clients[account_id] = client
            
            return await client.send_code_request(account['phone'])
        except Exception as e:
            logger.error(f"Error sending code: {e}")
            raise e

    async def sign_in(self, account_id: str, phone_code_hash: str, code: str, password: str = None):
        """Finish sign in"""
        account = self.get_account(account_id)
        client = self.clients.get(account_id)
        
        if not client: return None
        
        try:
            if password:
                user = await client.sign_in(account['phone'], code, password=password)
            else:
                try:
                    user = await client.sign_in(account['phone'], code, phone_code_hash=phone_code_hash)
                except SessionPasswordNeededError:
                    return "PASSWORD_NEEDED"
            
            # Success
            account['is_connected'] = True
            account['authorized'] = True
            self.save_accounts()
            return user
            
        except Exception as e:
            logger.error(f"Sign in error: {e}")
            raise e

    async def start_qr_auth(self, account_id: str):
        """
        Start QR authentication for account
        
        Args:
            account_id: Account ID
            
        Returns:
            Tuple[qr_login, TelegramClient]: QR login object and client
        """
        account = self.get_account(account_id)
        if not account:
            logger.error(f"Account not found: {account_id}")
            return None, None
            
        try:
            # Create client
            client = TelegramClient(
                MemorySession(),
                int(account['api_id']),
                account['api_hash']
            )
            
            await client.connect()
            
            if await client.is_user_authorized():
                logger.info(f"Account {account_id} already authorized")
                return None, client
                
            qr_login = await client.qr_login()
            return qr_login, client
            
        except Exception as e:
            logger.error(f"Error starting QR auth for {account_id}: {e}")
            return None, None
    
    async def disconnect_account(self, account_id: str):
        """
        Disconnect from Telegram account
        
        Args:
            account_id: Account ID
        """
        if account_id not in self.clients:
            logger.warning(f"Account not connected: {account_id}")
            return
        
        try:
            client = self.clients[account_id]
            await client.disconnect()
            del self.clients[account_id]
            
            # Update account status
            account = self.get_account(account_id)
            if account:
                account['is_connected'] = False
                self.save_accounts()
            
            logger.info(f"Disconnected account: {account_id}")
            add_breadcrumb("Account disconnected", {"account_id": account_id})
            
        except Exception as e:
            logger.error(f"Error disconnecting account {account_id}: {e}")
    
    def get_account(self, account_id: str) -> Optional[Dict]:
        """
        Get account by ID
        
        Args:
            account_id: Account ID
            
        Returns:
            Optional[Dict]: Account data or None
        """
        for account in self.accounts:
            if account['id'] == account_id:
                return account
        return None
    
    def get_connected_accounts(self) -> List[Dict]:
        """
        Get list of connected accounts
        
        Returns:
            List[Dict]: Connected accounts
        """
        return [acc for acc in self.accounts if acc['is_connected']]
    
    def get_all_accounts(self) -> List[Dict]:
        """
        Get all accounts
        
        Returns:
            List[Dict]: All accounts
        """
        return self.accounts
    
    def get_client(self, account_id: str) -> Optional[TelegramClient]:
        """
        Get Telegram client for account
        
        Args:
            account_id: Account ID
            
        Returns:
            Optional[TelegramClient]: Client or None
        """
        return self.clients.get(account_id)
