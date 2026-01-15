"""
Download Screen
Configure and run channel downloads
"""
import asyncio
import time
from kivy.uix.screenmanager import Screen


# KivyMD 2.0.0
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldTrailingIcon
from kivymd.uix.list import (
    MDList, 
    MDListItem, 
    MDListItemHeadlineText, 
    MDListItemSupportingText
)
from kivymd.uix.appbar import (
    MDTopAppBar, 
    MDTopAppBarLeadingButtonContainer, 
    MDActionTopAppBarButton, 
    MDTopAppBarTitle
)
from kivymd.toast import toast

from ..managers.download_manager import DownloadManager
from ..utils.logger import logger, add_breadcrumb, capture_message, capture_exception


class DownloadScreen(Screen):
    """
    Screen for downloading content to device
    """
    
    def __init__(self, account_manager, **kwargs):
        super().__init__(**kwargs)
        self.account_manager = account_manager
        self.download_manager = DownloadManager()
        self.checks = {}
        self.tasks_map = {}
        self.layout_built = False
        add_breadcrumb("DownloadScreen initialized")
    
    def on_enter(self):
        if not self.layout_built:
            self.build_ui()
            self.layout_built = True
        
        # Ensure theme background
        app = MDApp.get_running_app()
        if hasattr(self, 'root_box'):
            self.root_box.md_bg_color = app.theme_cls.backgroundColor
            
        self.refresh_accounts()

    def build_ui(self):
        self.clear_widgets()
        app = MDApp.get_running_app()
        
        self.root_box = MDBoxLayout(
            orientation='vertical', 
            spacing=0,
            md_bg_color=app.theme_cls.backgroundColor
        )
        
        # Toolbar
        self.toolbar = MDTopAppBar(type="small")
        leading = MDTopAppBarLeadingButtonContainer()
        back = MDActionTopAppBarButton(icon="arrow-left")
        back.on_release = self.go_back
        leading.add_widget(back)
        self.toolbar.add_widget(leading)
        self.toolbar.add_widget(MDTopAppBarTitle(text="Download Manager"))
        self.root_box.add_widget(self.toolbar)
        
        # Content Split
        content_split = MDBoxLayout(orientation='vertical', spacing="10dp", padding=0)
        
        # --- TOP CONFIG ---
        top_scroll = MDScrollView(size_hint_y=0.7)
        top_content = MDBoxLayout(orientation='vertical', padding="20dp", spacing="15dp", adaptive_height=True)
        
        top_content.add_widget(MDLabel(text="Select Channel/Chat", font_style="Title", role="large", adaptive_height=True))
        
        # Account Selector
        self.account_spinner_box = MDBoxLayout(orientation='vertical', adaptive_height=True, spacing="5dp")
        top_content.add_widget(self.account_spinner_box)
        
        # Source Field
        self.source_field = self.create_input_with_paste("Source Channel (Link/ID)", "source_field")
        top_content.add_widget(self.source_field)
        
        # File Types
        top_content.add_widget(MDLabel(text="File Types:", font_style="Label", role="large", adaptive_height=True))
        files_grid = MDGridLayout(cols=2, adaptive_height=True, spacing="5dp")
        types = ["Images", "Videos", "Documents", "Audio"] # Text not supported yet
        for t in types:
            box = MDBoxLayout(adaptive_height=True)
            chk = MDCheckbox(active=True, size_hint=(None, None), size=("30dp","30dp"))
            self.checks[t.lower()] = chk
            box.add_widget(chk)
            box.add_widget(MDLabel(text=t))
            files_grid.add_widget(box)
        top_content.add_widget(files_grid)
        
        # Warning
        top_content.add_widget(MDLabel(
            text="* Downloads are rate-limited (Slow Mode) to prevent bans.",
            theme_text_color="Error",
            font_style="Body",
            role="small"
        ))
        
        # Start Button
        start_btn = MDButton(style="filled", pos_hint={"center_x": .5})
        start_btn.add_widget(MDButtonText(text="START DOWNLOAD (SAFE MODE)"))
        start_btn.bind(on_release=self.start_download)
        top_content.add_widget(start_btn)
        
        top_scroll.add_widget(top_content)
        content_split.add_widget(top_scroll)
        
        # --- BOTTOM LOGS ---
        header = MDBoxLayout(adaptive_height=True, padding=["20dp", "5dp"])
        header.add_widget(MDLabel(text="Active Downloads", font_style="Title", role="medium"))
        content_split.add_widget(header)
        
        bottom_scroll = MDScrollView(size_hint_y=0.3)
        self.tasks_list = MDList()
        bottom_scroll.add_widget(self.tasks_list)
        content_split.add_widget(bottom_scroll)
        
        self.root_box.add_widget(content_split)
        self.add_widget(self.root_box)

    def refresh_accounts(self):
        # Implementing a simple radio list for account selection
        self.account_spinner_box.clear_widgets()
        self.account_spinner_box.add_widget(MDLabel(text="Select Download Account:", font_style="Label", role="medium"))
        
        accounts = self.account_manager.get_connected_accounts()
        if not accounts:
            self.account_spinner_box.add_widget(MDLabel(text="No connected accounts!", theme_text_color="Error"))
            self.account_radios = {}
            return

        self.account_radios = {}
        for acc in accounts:
            box = MDBoxLayout(adaptive_height=True, height="40dp")
            chk = MDCheckbox(group="dl_account", size_hint=(None, None), size=("30dp","30dp"))
            if not self.account_radios: chk.active = True # Select first
            
            self.account_radios[acc['id']] = chk
            box.add_widget(chk)
            box.add_widget(MDLabel(text=f"{acc['name']} ({acc['phone']})"))
            self.account_spinner_box.add_widget(box)

    def create_input_with_paste(self, hint, field_ref_name, **kwargs):
        # Using standard field without paste button
        field = MDTextField(
            MDTextFieldHintText(text=hint),
            mode="outlined",
            **kwargs
        )
        setattr(self, field_ref_name, field)
        return field



    def go_back(self, *args):
        self.manager.current = 'action'

    def start_download(self, *args):
        source = self.source_field.text
        if not source:
            toast("Source required")
            return
            
        # Get selected account
        acc_id = None
        for aid, chk in self.account_radios.items():
            if chk.active:
                acc_id = aid
                break
        
        if not acc_id:
            toast("Select an account")
            return
            
        session_id = f"dl_{hex(int(time.time()))[2:]}"
        self.add_task_item(session_id)
        
        asyncio.create_task(self.run_download(session_id, acc_id, source))

    def add_task_item(self, session_id):
        item = MDListItem()
        headline = MDListItemHeadlineText(text=f"Task: {session_id}")
        supporting = MDListItemSupportingText(text="Initializing...")
        
        item.add_widget(headline)
        item.add_widget(supporting)
        self.tasks_list.add_widget(item)
        self.tasks_map[session_id] = supporting

    def update_status(self, text):
        # Since we run inside a task context for specific session, we need to pass session_id or partial
        pass # Handled by wrapper below

    async def run_download(self, session_id, account_id, source):
        # Wrapper to pass to manager
        async def ui_callback(text):
            if session_id in self.tasks_map:
                self.tasks_map[session_id].text = text
        
        try:
            await ui_callback("Connecting...")
            client = self.account_manager.get_client(account_id)
            
            if not client:
                await ui_callback("Failed to connect client")
                return
                
            file_types = {k: v.active for k,v in self.checks.items()}
            
            self.download_manager.create_session(session_id)
            
            await self.download_manager.download_channel(
                session_id, 
                client, 
                source, 
                file_types, 
                ui_callback
            )
        except Exception as e:
            logger.error(f"Download screen error: {e}")
            capture_exception(e, extra_data={"session_id": session_id, "account_id": account_id, "source": source, "context": "download_screen_run"})
            if session_id in self.tasks_map:
                self.tasks_map[session_id].text = f"Error: {e}"
