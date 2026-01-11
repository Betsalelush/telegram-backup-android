# -*- coding: utf-8 -*-
"""
Account Manager
Manages multiple Telegram accounts, connections, and sessions
Based on tor.py architecture
"""

import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Import will be done at runtime to avoid circular imports
# from telethon import TelegramClient
# from telethon.sessions import StringSession

logger = logging.getLogger(__name__)

class AccountManager:
    """Manages multiple Telegram accounts"""
    
    def __init__(self, accounts_file: str, sessions_dir: str):
        """
        Initialize AccountManager
        
        Args:
            accounts_file: Path to accounts.json
            sessions_dir: Directory for session files
        """
        self.accounts_file = accounts_file
        self.sessions_dir = sessions_dir
        self.accounts = []
        self.clients = {}  # {account_id: TelegramClient}
        
        # Create sessions directory if it doesn't exist
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        # Load existing accounts
        self.load_accounts()
    
    def load_accounts(self):
        """Load accounts from JSON file"""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.accounts = data.get('accounts', [])
                logger.info(f"Loaded {len(self.accounts)} accounts")
            except Exception as e:
                logger.error(f"Error loading accounts: {e}")
                self.accounts = []
        else:
            self.accounts = []
            logger.info("No existing accounts file found")
    
    def save_accounts(self):
        """Save accounts to JSON file"""
        try:
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump({'accounts': self.accounts}, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.accounts)} accounts")
        except Exception as e:
            logger.error(f"Error saving accounts: {e}")
    
    def add_account(self, name: str, api_id: str, api_hash: str, phone: str) -> str:
        """
        Add new account
        
        Args:
            name: Account name (user-friendly)
            api_id: Telegram API ID
            api_hash: Telegram API Hash
            phone: Phone number
            
        Returns:
            Account ID
        """
        import time
        
        account_id = f"acc_{int(time.time() * 1000)}"
        session_path = os.path.join(self.sessions_dir, f'session_{phone.replace("+", "")}')
        
        account = {
            'id': account_id,
            'name': name,
            'api_id': api_id,
            'api_hash': api_hash,
            'phone': phone,
            'session_path': session_path,
            'is_connected': False,
            'created_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat()
        }
        
        self.accounts.append(account)
        self.save_accounts()
        
        logger.info(f"Added account: {name} ({phone})")
        return account_id
    
    def remove_account(self, account_id: str):
        """
        Remove account
        
        Args:
            account_id: Account ID to remove
        """
        # Disconnect if connected
        if account_id in self.clients:
            import asyncio
            asyncio.create_task(self.disconnect_account(account_id))
        
        # Remove from list
        self.accounts = [acc for acc in self.accounts if acc['id'] != account_id]
        self.save_accounts()
        
        logger.info(f"Removed account: {account_id}")
    
    async def connect_account(self, account_id: str) -> bool:
        """
        Connect to Telegram account
        
        Args:
            account_id: Account ID
            
        Returns:
            True if connected successfully
        """
        account = self.get_account(account_id)
        if not account:
            logger.error(f"Account not found: {account_id}")
            return False
        
        try:
            # Lazy import Telethon
            from telethon import TelegramClient
            
            client = TelegramClient(
                account['session_path'],
                int(account['api_id']),
                account['api_hash']
            )
            
            logger.info(f"Connecting to account: {account['name']} ({account['phone']})")
            await client.connect()
            
            if not await client.is_user_authorized():
                logger.warning(f"Account not authorized: {account['name']}")
                await client.disconnect()
                return False
            
            # Get user info
            me = await client.get_me()
            account['is_connected'] = True
            account['last_used'] = datetime.now().isoformat()
            account['user_info'] = {
                'first_name': me.first_name,
                'last_name': me.last_name,
                'username': me.username
            }
            
            self.clients[account_id] = client
            self.save_accounts()
            
            logger.info(f"Connected: {me.first_name} ({account['phone']})")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting account {account_id}: {e}")
            return False
    
    async def disconnect_account(self, account_id: str):
        """
        Disconnect account
        
        Args:
            account_id: Account ID
        """
        if account_id in self.clients:
            try:
                await self.clients[account_id].disconnect()
                del self.clients[account_id]
                logger.info(f"Disconnected account: {account_id}")
            except Exception as e:
                logger.error(f"Error disconnecting {account_id}: {e}")
        
        account = self.get_account(account_id)
        if account:
            account['is_connected'] = False
            self.save_accounts()
    
    def get_account(self, account_id: str) -> Optional[Dict]:
        """
        Get account by ID
        
        Args:
            account_id: Account ID
            
        Returns:
            Account dict or None
        """
        for acc in self.accounts:
            if acc['id'] == account_id:
                return acc
        return None
    
    def get_connected_accounts(self) -> List[Dict]:
        """
        Get list of connected accounts
        
        Returns:
            List of connected account dicts
        """
        return [acc for acc in self.accounts if acc.get('is_connected', False)]
    
    def get_account_clients(self, account_ids: List[str]) -> List:
        """
        Get Telethon clients for specified accounts
        
        Args:
            account_ids: List of account IDs
            
        Returns:
            List of TelegramClient objects
        """
        return [self.clients[acc_id] for acc_id in account_ids if acc_id in self.clients]
    
    def get_all_accounts(self) -> List[Dict]:
        """
        Get all accounts
        
        Returns:
            List of all account dicts
        """
        return self.accounts
