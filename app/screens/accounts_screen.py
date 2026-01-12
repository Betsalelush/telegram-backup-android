"""
Accounts Screen
Manage Telegram accounts
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.properties import ObjectProperty

from ..managers.account_manager import AccountManager
from ..utils.logger import logger, add_breadcrumb


class AccountsScreen(Screen):
    """
    Screen for managing accounts
    
    Features:
    - List all accounts
    - Add new account
    - Remove account
    - Connect/disconnect
    """
    
    def __init__(self, account_manager: AccountManager, **kwargs):
        """
        Initialize Accounts Screen
        
        Args:
            account_manager: AccountManager instance
        """
        super().__init__(**kwargs)
        self.account_manager = account_manager
        self.dialog = None
        
        # Build UI
        self.build_ui()
        
        add_breadcrumb("AccountsScreen initialized")
    
    def build_ui(self):
        """Build screen UI"""
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.toolbar import MDTopAppBar
        from kivymd.uix.floatingactionbutton import MDFloatingActionButton
        
        layout = MDBoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(title="Accounts")
        toolbar.left_action_items = [["arrow-left", lambda x: self.go_back()]]
        layout.add_widget(toolbar)
        
        # Accounts list
        self.accounts_list = MDList()
        layout.add_widget(self.accounts_list)
        
        # Add button
        add_btn = MDFloatingActionButton(
            icon="plus",
            pos_hint={"center_x": 0.9, "center_y": 0.1}
        )
        add_btn.bind(on_release=self.show_add_dialog)
        layout.add_widget(add_btn)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Called when screen is entered"""
        self.load_accounts_list()
    
    def load_accounts_list(self):
        """Load and display accounts list"""
        self.accounts_list.clear_widgets()
        
        accounts = self.account_manager.get_all_accounts()
        
        for account in accounts:
            item = TwoLineAvatarIconListItem(
                text=account['name'],
                secondary_text=account['phone'],
            )
            
            # Add connect/disconnect button
            if account['is_connected']:
                item.add_widget(
                    MDFlatButton(
                        text="Disconnect",
                        on_release=lambda x, acc_id=account['id']: self.on_account_action(acc_id, 'disconnect')
                    )
                )
            else:
                item.add_widget(
                    MDRaisedButton(
                        text="Connect",
                        on_release=lambda x, acc_id=account['id']: self.on_account_action(acc_id, 'connect')
                    )
                )
            
            # Add delete button
            item.add_widget(
                MDFlatButton(
                    text="Delete",
                    on_release=lambda x, acc_id=account['id']: self.on_account_action(acc_id, 'delete')
                )
            )
            
            self.accounts_list.add_widget(item)
        
        logger.info(f"Loaded {len(accounts)} accounts to UI")
        add_breadcrumb("Accounts list loaded", {"count": len(accounts)})
    
    def show_add_dialog(self, *args):
        """Show dialog to add new account"""
        if not self.dialog:
            content = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
            
            self.name_field = MDTextField(hint_text="Account Name")
            self.api_id_field = MDTextField(hint_text="API ID")
            self.api_hash_field = MDTextField(hint_text="API Hash")
            self.phone_field = MDTextField(hint_text="Phone Number")
            
            content.add_widget(self.name_field)
            content.add_widget(self.api_id_field)
            content.add_widget(self.api_hash_field)
            content.add_widget(self.phone_field)
            
            self.dialog = MDDialog(
                title="Add Account",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="ADD",
                        on_release=self.add_account
                    ),
                ],
            )
        
        self.dialog.open()
    
    def add_account(self, *args):
        """Add new account"""
        name = self.name_field.text
        api_id = self.api_id_field.text
        api_hash = self.api_hash_field.text
        phone = self.phone_field.text
        
        if not all([name, api_id, api_hash, phone]):
            logger.warning("Missing account details")
            return
        
        # Add account
        account_id = self.account_manager.add_account(name, api_id, api_hash, phone)
        
        logger.info(f"Added account: {account_id}")
        add_breadcrumb("Account added via UI", {"account_id": account_id})
        
        # Close dialog and refresh list
        self.dialog.dismiss()
        self.load_accounts_list()
    
    def on_account_action(self, account_id: str, action: str):
        """
        Handle account actions
        
        Args:
            account_id: Account ID
            action: Action (connect/disconnect/delete)
        """
        if action == 'connect':
            # Connect account (async)
            import asyncio
            asyncio.create_task(self.account_manager.connect_account(account_id))
            logger.info(f"Connecting account: {account_id}")
            
        elif action == 'disconnect':
            # Disconnect account (async)
            import asyncio
            asyncio.create_task(self.account_manager.disconnect_account(account_id))
            logger.info(f"Disconnecting account: {account_id}")
            
        elif action == 'delete':
            # Delete account
            self.account_manager.remove_account(account_id)
            logger.info(f"Deleted account: {account_id}")
        
        # Refresh list
        self.load_accounts_list()
    
    def go_back(self):
        """Go back to previous screen"""
        self.manager.current = 'action'
