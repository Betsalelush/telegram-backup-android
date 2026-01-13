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
from kivy.uix.widget import Widget

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
        
    def build_ui(self):
        """Build screen UI with Task Dashboard - Robust Layout"""
        from kivymd.uix.selectioncontrol import MDCheckbox
        from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.gridlayout import MDGridLayout
        from kivymd.uix.list import MDList
        
        # 1. Root Vertical Box
        # We use a standard vertical box, adding widgets in order.
        # This is the most reliable way in Kivy to stack things Top-to-Bottom.
        root_box = MDBoxLayout(orientation='vertical', spacing=0)
        
        # Toolbar (Top)
        toolbar = MDTopAppBar(title="Transfer Dashboard", elevation=4)
        toolbar.left_action_items = [["arrow-left", lambda x: self.go_back()]]
        root_box.add_widget(toolbar)
        
        # Content Area containing Split View (Top Config, Bottom Status)
        # We put this in a BoxLayout to manage the share (60% / 40%)
        content_split = MDBoxLayout(orientation='vertical', spacing=10, padding=0)
        
        # --- TOP SECTION: CONFIG (Weight 7) ---
        top_scroll = MDScrollView(size_hint_y=0.7)
        top_content = MDBoxLayout(orientation='vertical', padding=20, spacing=15, adaptive_height=True)
        
        # Title
        top_content.add_widget(MDLabel(text="New Task", font_style="H6", theme_text_color="Primary", adaptive_height=True))
        
        # Fields
        self.source_field = MDTextField(hint_text="Source Channel (ID or Link)", mode="rectangle")
        top_content.add_widget(self.source_field)
        
        self.target_field = MDTextField(hint_text="Target Channel (ID or Link)", mode="rectangle")
        top_content.add_widget(self.target_field)
        
        # Options Row
        grid = MDGridLayout(cols=2, spacing=10, adaptive_height=True)
        self.start_id_field = MDTextField(hint_text="Start ID (0=Oldest)", text="0", input_filter="int", mode="rectangle")
        grid.add_widget(self.start_id_field)
        top_content.add_widget(grid)
        
        # Accounts Header
        top_content.add_widget(MDLabel(text="Select Accounts:", font_style="Subtitle2", adaptive_height=True))
        self.accounts_grid = MDGridLayout(cols=1, adaptive_height=True, spacing=5)
        top_content.add_widget(self.accounts_grid)
        
        # File Types Header
        top_content.add_widget(MDLabel(text="File Types:", font_style="Subtitle2", adaptive_height=True))
        types_layout = MDGridLayout(cols=3, adaptive_height=True, spacing=5)
        file_types = ["Images", "Videos", "Audio", "Documents", "Text"]
        for ftype in file_types:
            box = MDBoxLayout(adaptive_height=True)
            chk = MDCheckbox(active=True, size_hint=(None, None), size=("30dp", "30dp"))
            self.type_checks[ftype.lower()] = chk
            box.add_widget(chk)
            box.add_widget(MDLabel(text=ftype, font_style="Caption", adaptive_height=True, pos_hint={"center_y": .5}))
            types_layout.add_widget(box)
        top_content.add_widget(types_layout)
        
        # Spacer
        top_content.add_widget(Widget(size_hint_y=None, height="10dp"))
        
        # Start Button (Centered)
        self.start_btn = MDRaisedButton(
            text="🚀 START NEW TASK", 
            size_hint_x=0.9, 
            pos_hint={"center_x": 0.5},
            md_bg_color=(0, 0.7, 0, 1)
        )
        self.start_btn.bind(on_release=self.start_transfer)
        top_content.add_widget(self.start_btn)
        
        top_scroll.add_widget(top_content)
        content_split.add_widget(top_scroll)
        
        # --- BOTTOM SECTION: LIST (Weight 3) ---
        header_box = MDBoxLayout(adaptive_height=True, padding=[20, 5], md_bg_color=(0.95,0.95,0.95,1))
        header_box.add_widget(MDLabel(text="Active Tasks", font_style="Subtitle1", bold=True))
        content_split.add_widget(header_box)
        
        bottom_scroll = MDScrollView(size_hint_y=0.3)
        self.tasks_list = MDList()
        bottom_scroll.add_widget(self.tasks_list)
        content_split.add_widget(bottom_scroll)
        
        # Add content split to root
        root_box.add_widget(content_split)
        
        self.add_widget(root_box)

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
