"""
Transfer Screen
Configure and run message transfers
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.label import MDLabel
from kivy.properties import NumericProperty

from ..managers.transfer_manager import TransferManager
from ..managers.account_manager import AccountManager
from ..managers.progress_manager import ProgressManager
from ..utils.logger import logger, add_breadcrumb


class TransferScreen(Screen):
    """
    Screen for configuring and running transfers
    
    Features:
    - Select accounts
    - Select source/target channels
    - Select file types
    - Start/stop transfer
    - Show progress
    """
    
    progress_value = NumericProperty(0)
    
    def __init__(self, account_manager: AccountManager,
                 transfer_manager: TransferManager,
                 progress_manager: ProgressManager,
                 **kwargs):
        """
        Initialize Transfer Screen
        
        Args:
            account_manager: AccountManager instance
            transfer_manager: TransferManager instance
            progress_manager: ProgressManager instance
        """
        super().__init__(**kwargs)
        self.account_manager = account_manager
        self.transfer_manager = transfer_manager
        self.progress_manager = progress_manager
        
        self.is_running = False
        
        # Build UI
        self.build_ui()
        
        add_breadcrumb("TransferScreen initialized")
    
    def build_ui(self):
        """Build screen UI"""
        layout = MDBoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(title="New Transfer")
        toolbar.left_action_items = [["arrow-left", lambda x: self.go_back()]]
        layout.add_widget(toolbar)
        
        # Content
        content = MDBoxLayout(
            orientation='vertical',
            padding=20,
            spacing=15
        )
        
        # Source channel
        self.source_field = MDTextField(
            hint_text="Source Channel (ID or Link)",
            mode="rectangle"
        )
        content.add_widget(self.source_field)
        
        # Target channel
        self.target_field = MDTextField(
            hint_text="Target Channel (ID or Link)",
            mode="rectangle"
        )
        content.add_widget(self.target_field)
        
        # Progress bar
        self.progress_bar = MDProgressBar(
            size_hint_y=None,
            height=10
        )
        content.add_widget(self.progress_bar)
        
        # Progress text
        self.progress_label = MDLabel(
            text="Ready",
            halign="center",
            size_hint_y=None,
            height=30
        )
        content.add_widget(self.progress_label)
        
        # Start button
        self.start_btn = MDRaisedButton(
            text="Start Transfer",
            pos_hint={"center_x": 0.5}
        )
        self.start_btn.bind(on_release=self.start_transfer)
        content.add_widget(self.start_btn)
        
        # Stop button
        self.stop_btn = MDFlatButton(
            text="Stop Transfer",
            pos_hint={"center_x": 0.5},
            disabled=True
        )
        self.stop_btn.bind(on_release=self.stop_transfer)
        content.add_widget(self.stop_btn)
        
        layout.add_widget(content)
        self.add_widget(layout)
    
    def start_transfer(self, *args):
        """Start transfer"""
        source = self.source_field.text
        target = self.target_field.text
        
        if not source or not target:
            logger.warning("Missing source or target channel")
            return
        
        # Get connected accounts
        accounts = self.account_manager.get_connected_accounts()
        if not accounts:
            logger.warning("No connected accounts")
            return
        
        # Create transfer
        transfer_id = self.transfer_manager.create_transfer({
            'source': source,
            'target': target,
            'accounts': [acc['id'] for acc in accounts]
        })
        
        logger.info(f"Starting transfer: {transfer_id}")
        add_breadcrumb("Transfer started", {"transfer_id": transfer_id})
        
        # Update UI
        self.is_running = True
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.progress_label.text = "Transfer running..."
        
        # Start transfer (async)
        import asyncio
        asyncio.create_task(self._run_transfer(source, target, accounts))
    
    async def _run_transfer(self, source, target, accounts):
        """
        Run transfer (async)
        
        Args:
            source: Source channel
            target: Target channel
            accounts: List of accounts
        """
        try:
            # Get clients
            clients = [self.account_manager.get_client(acc['id']) for acc in accounts]
            clients = [c for c in clients if c]  # Filter None
            
            if not clients:
                logger.error("No clients available")
                return
            
            # Get entities
            source_entity = await clients[0].get_entity(source)
            target_entity = await clients[0].get_entity(target)
            
            # Get messages
            messages = []
            async for message in clients[0].iter_messages(source_entity):
                messages.append(message)
                if len(messages) >= 100:  # Limit for demo
                    break
            
            logger.info(f"Found {len(messages)} messages to transfer")
            
            # Transfer messages
            stats = await self.transfer_manager.send_messages_batch(
                clients, messages, source_entity, target_entity
            )
            
            logger.info(f"Transfer complete: {stats}")
            self.progress_label.text = f"Complete! Sent: {stats['sent']}, Errors: {stats['errors']}"
            
        except Exception as e:
            logger.error(f"Transfer error: {e}")
            self.progress_label.text = f"Error: {str(e)}"
        
        finally:
            self.is_running = False
            self.start_btn.disabled = False
            self.stop_btn.disabled = True
    
    def stop_transfer(self, *args):
        """Stop transfer"""
        logger.info("Stopping transfer")
        add_breadcrumb("Transfer stopped")
        
        self.is_running = False
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.progress_label.text = "Stopped"
    
    def update_progress(self, current: int, total: int):
        """
        Update progress bar
        
        Args:
            current: Current message count
            total: Total message count
        """
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar.value = percentage
            self.progress_label.text = f"{current}/{total} ({percentage:.1f}%)"
    
    def go_back(self):
        """Go back to action screen"""
        if not self.is_running:
            self.manager.current = 'action'
        else:
            logger.warning("Cannot go back while transfer is running")
