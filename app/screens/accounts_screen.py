"""
Accounts Screen
Manage Telegram accounts
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDFloatingActionButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
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
        """Build screen UI with robust positioning"""
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.toolbar import MDTopAppBar
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.floatlayout import MDFloatLayout
        
        # 1. Root Layout (MDFloatLayout)
        # We use FloatLayout to force the Toolbar to the top regardless of other widgets
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Accounts", 
            elevation=4, 
            pos_hint={"top": 1},
            specific_text_color=(1, 1, 1, 1)
        )
        toolbar.left_action_items = [["arrow-left", lambda x: self.go_back()]]
        self.add_widget(toolbar)
        
        # ScrollView (Below Toolbar)
        # Assuming Toolbar is approx 64dp
        scroll = MDScrollView(
            pos_hint={"top": 1, "bottom": 0},
            size_hint=(1, 1)
        )
        # We use padding to push content below the fixed Toolbar
        scroll.padding = [0, "64dp", 0, 0] 
        # Actually better: Use a BoxLayout below the toolbar? 
        # Let's try explicit relative sizes
        
        # Improved Layout strategy:
        # A main box that fills the screen.
        main_box = MDBoxLayout(orientation='vertical')
        
        # We need to re-add the toolbar to the box to ensure it pushes content down?
        # No, the user said "buttons at bottom".
        # Let's stick to FloatLayout but make the ScrollView start BELOW the toolbar.
        
        self.add_widget(main_box)
        # Re-doing the add:
        
    def build_ui(self):
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.toolbar import MDTopAppBar
        from kivymd.uix.scrollview import MDScrollView
        
        # Clear existing
        self.clear_widgets()
        
        # 1. Root Vertical Box - this is the standard way.
        root_box = MDBoxLayout(orientation='vertical', spacing=0)
        
        # Toolbar (First item = Top)
        toolbar = MDTopAppBar(title="Accounts", elevation=4)
        toolbar.left_action_items = [["arrow-left", lambda x: self.go_back()]]
        root_box.add_widget(toolbar)
        
        # Content (Fills remaining space)
        scroll = MDScrollView()
        self.accounts_list = MDList()
        scroll.add_widget(self.accounts_list)
        root_box.add_widget(scroll)
        
        self.add_widget(root_box)
        
        # FAB (Floating absolute)
        add_btn = MDFloatingActionButton(
            icon="plus",
            pos_hint={"right": 0.9, "bottom": 0.05}
        )
        add_btn.bind(on_release=self.show_add_dialog)
        self.add_widget(add_btn)

    def show_add_dialog(self, *args):
        """Show custom dialog to add new account"""
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
            
        content = MDBoxLayout(
            orientation='vertical', 
            spacing="12dp", 
            padding="2dp",
            adaptive_height=True,
            size_hint_y=None
        )
        
        # Fields
        self.name_field = MDTextField(hint_text="Account Name", mode="rectangle")
        self.api_id_field = MDTextField(hint_text="API ID (Optional)", mode="rectangle")
        self.api_hash_field = MDTextField(hint_text="API Hash (Optional)", mode="rectangle")
        self.phone_field = MDTextField(hint_text="Phone Number (+972...)", mode="rectangle")
        
        content.add_widget(self.name_field)
        content.add_widget(self.phone_field)
        content.add_widget(self.api_id_field)
        content.add_widget(self.api_hash_field)
        
        # Buttons are handled by the Dialog container usually, but let's be explicit
        self.dialog = MDDialog(
            title="Add New Account",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ADD ACCOUNT",
                    on_release=self.add_account_callback
                ),
            ],
        )
        self.dialog.open()
        
    def add_account_callback(self, *args):
        """Callback to extract data and add account"""
        try:
            name = self.name_field.text
            phone = self.phone_field.text
            api_id = self.api_id_field.text
            api_hash = self.api_hash_field.text
            
            logger.info(f"Attempting to add account: name={name}, phone={phone}")
            
            if not name or not phone:
                from kivymd.toast import toast
                toast("Name and Phone are required!")
                return
            
            # Logic to add account
            acc_id = self.account_manager.add_account(name, api_id, api_hash, phone)
            
            if acc_id:
                logger.info(f"Account added successfully: {acc_id}")
                self.dialog.dismiss()
                self.load_accounts_list()
            else:
                logger.error("Failed to add account (Manager returned None)")
                
        except Exception as e:
            logger.error(f"Error in add_account_callback: {e}")
            import traceback
            traceback.print_exc()
    
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
