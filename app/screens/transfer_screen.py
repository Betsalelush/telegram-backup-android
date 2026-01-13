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
    - Select accounts (Multi-select)
    - Source/Target channels
    - Start Message ID
    - File Types selection
    - Start/stop transfer
    - Show progress
    """
    
    progress_value = NumericProperty(0)
    
    def __init__(self, account_manager, transfer_manager, progress_manager, **kwargs):
        super().__init__(**kwargs)
        self.account_manager = account_manager
        self.transfer_manager = transfer_manager
        self.progress_manager = progress_manager
        
        self.account_checks = {} 
        self.type_checks = {} 
        
        self.build_ui()
        add_breadcrumb("TransferScreen initialized")
    
    def on_enter(self):
        self.refresh_accounts()

    def build_ui(self):
        """Build screen UI with Task Dashboard"""
        from kivymd.uix.selectioncontrol import MDCheckbox
        from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.gridlayout import MDGridLayout
        from kivymd.uix.list import MDList
        
        layout = MDBoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(title="Transfer Dashboard")
        toolbar.left_action_items = [["arrow-left", lambda x: self.go_back()]]
        layout.add_widget(toolbar)
        
        # Split Screen: Top = Config, Bottom = Active Tasks
        
        # --- Top Section: New Task Config (Scrollable) ---
        top_scroll = MDScrollView(size_hint_y=0.6)
        content = MDBoxLayout(orientation='vertical', padding=20, spacing=15, adaptive_height=True)
        
        # 1. Channels
        content.add_widget(MDLabel(text="New Task", font_style="H6", theme_text_color="Primary"))
        
        self.source_field = MDTextField(hint_text="Source Channel (ID or Link)", mode="rectangle")
        content.add_widget(self.source_field)
        
        self.target_field = MDTextField(hint_text="Target Channel (ID or Link)", mode="rectangle")
        content.add_widget(self.target_field)
        
        # 2. Options
        grid = MDGridLayout(cols=2, spacing=10, adaptive_height=True)
        self.start_id_field = MDTextField(hint_text="Start ID (0=Oldest)", text="0", input_filter="int", mode="rectangle")
        grid.add_widget(self.start_id_field)
        content.add_widget(grid)
        
        # 3. Accounts & types (Simplified for height)
        self.accounts_grid = MDGridLayout(cols=1, adaptive_height=True, spacing=5)
        content.add_widget(MDLabel(text="Select Accounts:", font_style="Subtitle2"))
        content.add_widget(self.accounts_grid)
        
        # 4. File Types
        types_layout = MDGridLayout(cols=3, adaptive_height=True, spacing=5)
        file_types = ["Images", "Videos", "Audio", "Documents", "Text"]
        for ftype in file_types:
            box = MDBoxLayout(adaptive_height=True)
            chk = MDCheckbox(active=True, size_hint=(None, None), size=("30dp", "30dp"))
            self.type_checks[ftype.lower()] = chk
            box.add_widget(chk)
            box.add_widget(MDLabel(text=ftype, font_style="Caption"))
            types_layout.add_widget(box)
        content.add_widget(types_layout)
        
        # Start Button
        self.start_btn = MDRaisedButton(text="🚀 START NEW TASK", size_hint_x=1, md_bg_color=(0, 0.7, 0, 1))
        self.start_btn.bind(on_release=self.start_transfer)
        content.add_widget(self.start_btn)
        
        top_scroll.add_widget(content)
        layout.add_widget(top_scroll)
        
        # --- Bottom Section: Active Tasks List ---
        layout.add_widget(MDLabel(text="  Active Tasks", size_hint_y=None, height=30, md_bg_color=(0.9,0.9,0.9,1)))
        
        bottom_scroll = MDScrollView(size_hint_y=0.4)
        self.tasks_list = MDList()
        bottom_scroll.add_widget(self.tasks_list)
        layout.add_widget(bottom_scroll)
        
        self.add_widget(layout)

    def refresh_accounts(self):
        """Refresh account list checkboxes"""
        from kivymd.uix.selectioncontrol import MDCheckbox
        self.accounts_grid.clear_widgets()
        self.account_checks.clear()
        
        accounts = self.account_manager.get_connected_accounts()
        if not accounts:
            self.accounts_grid.add_widget(MDLabel(text="No accounts!", theme_text_color="Error"))
            return

        for acc in accounts:
            box = MDBoxLayout(adaptive_height=True, height="40dp")
            chk = MDCheckbox(active=True, size_hint=(None, None), size=("30dp", "30dp"))
            self.account_checks[acc['id']] = chk
            box.add_widget(chk)
            box.add_widget(MDLabel(text=f"{acc['name']}"))
            self.accounts_grid.add_widget(box)

    def start_transfer(self, *args):
        """Start transfer logic"""
        source = self.source_field.text
        target = self.target_field.text
        start_id = int(self.start_id_field.text or 0)
        
        if not source or not target:
            return # TODO: Toast
            
        selected_accounts = [aid for aid, chk in self.account_checks.items() if chk.active]
        if not selected_accounts: return
        
        selected_types = [t for t, chk in self.type_checks.items() if chk.active]

        config = {
            'source': source,
            'target': target,
            'accounts': selected_accounts,
            'start_id': start_id,
            'file_types': selected_types
        }
        
        # Create Session in Manager
        session_id = self.transfer_manager.create_transfer(config)
        
        # Add to List UI
        self.add_task_to_list(session_id, source, target)
        
        # Start Async
        self.source_field.text = "" # Clear form
        import asyncio
        asyncio.create_task(self._run_transfer(session_id, config))

    def add_task_to_list(self, session_id, source, target):
        from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
        
        item = TwoLineAvatarIconListItem(
            text=f"Task: {source} -> {target}",
            secondary_text="Initializing...",
            id=session_id
        )
        icon = IconLeftWidget(icon="transfer")
        item.add_widget(icon)
        
        # Stop Button
        # Note: Ideally needs better binding, simplified here
        # right_icon = IconRightWidget(icon="stop", on_release=lambda x: self.stop_task(session_id, item))
        # item.add_widget(right_icon)
        
        self.tasks_list.add_widget(item)

    async def _run_transfer(self, session_id, config):
        """Async runner"""
        try:
            # Get only selected clients
            clients = []
            for acc_id in config['accounts']:
                client = self.account_manager.get_client(acc_id)
                if client: clients.append(client)
            
            # Start Manager Logic
            await self.transfer_manager.start_mass_transfer(
                session_id,
                clients, 
                self.update_task_status
            )
            
        except Exception as e:
            logger.error(f"Transfer failed: {e}")
            self.update_task_status(session_id, f"Error: {e}")

    def update_task_status(self, session_id, text):
        """Find the list item and update text"""
        # Linear search for now (simple)
        for child in self.tasks_list.children:
            if getattr(child, 'id', None) == session_id:
                child.secondary_text = text
                if "Completed" in text or "Error" in text:
                    child.tertiary_text = "Done" # If ThreeLine
                break

    def stop_transfer(self, *args):
        pass # Per task now

    def go_back(self):
        self.manager.current = 'action'
