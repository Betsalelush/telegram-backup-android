"""
Transfer Screen
Configure and run message transfers
"""
import asyncio
import time
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.core.clipboard import Clipboard

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
    MDListItemSupportingText,
    MDListItemTrailingIcon
)
from kivymd.uix.appbar import (
    MDTopAppBar, 
    MDTopAppBarLeadingButtonContainer, 
    MDActionTopAppBarButton, 
    MDTopAppBarTitle
)
from kivymd.toast import toast

from ..managers.transfer_manager import TransferManager
from ..managers.account_manager import AccountManager
from ..managers.progress_manager import ProgressManager
from ..utils.logger import logger, add_breadcrumb, capture_message


class TransferScreen(Screen):
    """
    Screen for configuring and running transfers (MD3)
    """
    
    def __init__(self, account_manager, transfer_manager, progress_manager, **kwargs):
        super().__init__(**kwargs)
        self.account_manager = account_manager
        self.transfer_manager = transfer_manager
        self.progress_manager = progress_manager
        
        self.account_checks = {} 
        self.type_checks = {} 
        self.tasks_map = {} # Maps session_id -> item widget
        
        self.layout_built = False
        add_breadcrumb("TransferScreen initialized")
    
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
        self.toolbar.add_widget(MDTopAppBarTitle(text="Transfer Dashboard"))
        self.root_box.add_widget(self.toolbar)
        
        # Content Split
        content_split = MDBoxLayout(orientation='vertical', spacing="10dp", padding=0)
        
        # --- TOP CONFIG ---
        top_scroll = MDScrollView(size_hint_y=0.7)
        top_content = MDBoxLayout(orientation='vertical', padding="20dp", spacing="15dp", adaptive_height=True)
        
        # Title
        top_content.add_widget(MDLabel(text="New Task", font_style="Title", role="large", adaptive_height=True))
        
        # Inputs
        self.source_field = self.create_input_with_paste("Source Channel (ID/Link)", "source_field")
        top_content.add_widget(self.source_field)
        
        self.target_field = self.create_input_with_paste("Target Channel (ID/Link)", "target_field")
        top_content.add_widget(self.target_field)
        
        # Options Row
        grid = MDGridLayout(cols=2, spacing="10dp", adaptive_height=True)
        
        # Start ID
        self.start_id_field = MDTextField(
            MDTextFieldHintText(text="Start ID (0=Oldest)"),
            mode="outlined",
        )
        grid.add_widget(self.start_id_field)
        
        # Shortener
        short_btn = MDIconButton(icon="link-variant-plus")
        short_btn.bind(on_release=self.shorten_links)
        grid.add_widget(short_btn)
        
        top_content.add_widget(grid)
        
        # Mode Logic (Radio)
        top_content.add_widget(MDLabel(text="Transfer Mode:", font_style="Label", role="large", adaptive_height=True))
        
        self.mode_group = "transfer_mode"
        modes = [("Forward", "forward"), ("Copy", "copy"), ("Down/Up", "download_upload")]
        self.selected_mode = "copy"
        
        modes_grid = MDGridLayout(cols=3, adaptive_height=True, spacing="5dp")
        for label, val in modes:
            box = MDBoxLayout(adaptive_height=True)
            chk = MDCheckbox(group=self.mode_group, size_hint=(None, None), size=("30dp","30dp"))
            if val == "copy": chk.active = True
            chk.bind(active=lambda inst, act, v=val: self.set_mode(v, act))
            box.add_widget(chk)
            box.add_widget(MDLabel(text=label, font_style="Label", role="medium"))
            modes_grid.add_widget(box)
        top_content.add_widget(modes_grid)

        # Accounts
        top_content.add_widget(MDLabel(text="Select Accounts:", font_style="Label", role="large", adaptive_height=True))
        self.accounts_grid = MDGridLayout(cols=1, adaptive_height=True, spacing="5dp")
        top_content.add_widget(self.accounts_grid)
        
        # Files
        top_content.add_widget(MDLabel(text="File Types:", font_style="Label", role="large", adaptive_height=True))
        files_grid = MDGridLayout(cols=3, adaptive_height=True, spacing="5dp")
        types = ["Images", "Videos", "Audio", "Documents", "Text"]
        for t in types:
            box = MDBoxLayout(adaptive_height=True)
            chk = MDCheckbox(active=True, size_hint=(None, None), size=("30dp","30dp"))
            self.type_checks[t.lower()] = chk
            box.add_widget(chk)
            box.add_widget(MDLabel(text=t, font_style="Label", role="small"))
            files_grid.add_widget(box)
        top_content.add_widget(files_grid)
        
        # Start Button
        start_btn = MDButton(style="filled", pos_hint={"center_x": .5})
        start_btn.add_widget(MDButtonText(text="START NEW TASK"))
        start_btn.bind(on_release=self.start_transfer)
        top_content.add_widget(start_btn)
        
        top_scroll.add_widget(top_content)
        content_split.add_widget(top_scroll)
        
        # --- BOTTOM STATUS ---
        header = MDBoxLayout(adaptive_height=True, padding=["20dp", "5dp"])
        header.add_widget(MDLabel(text="Active Tasks", font_style="Title", role="medium"))
        content_split.add_widget(header)
        
        bottom_scroll = MDScrollView(size_hint_y=0.3)
        self.tasks_list = MDList()
        bottom_scroll.add_widget(self.tasks_list)
        content_split.add_widget(bottom_scroll)
        
        self.root_box.add_widget(content_split)
        self.add_widget(self.root_box)

    def set_mode(self, val, active):
        if active: self.selected_mode = val

    def refresh_accounts(self):
        self.accounts_grid.clear_widgets()
        self.account_checks.clear()
        
        accounts = self.account_manager.get_connected_accounts()
        if not accounts:
            self.accounts_grid.add_widget(MDLabel(text="No connected accounts!", theme_text_color="Error"))
            return

        for acc in accounts:
            box = MDBoxLayout(adaptive_height=True, height="40dp")
            chk = MDCheckbox(active=True, size_hint=(None, None), size=("30dp","30dp"))
            self.account_checks[acc['id']] = chk
            box.add_widget(chk)
            box.add_widget(MDLabel(text=f"{acc['name']} ({acc['phone']})"))
            self.accounts_grid.add_widget(box)

    def create_input_with_paste(self, hint, field_ref_name, **kwargs):
        field = MDTextField(
            MDTextFieldHintText(text=hint),
            mode="outlined",
            **kwargs
        )
        paste_icon = MDTextFieldTrailingIcon(icon="content-paste")
        paste_icon.bind(on_release=lambda x: self.do_paste(field))
        field.add_widget(paste_icon)
        
        setattr(self, field_ref_name, field)
        return field

    def do_paste(self, field):
        """Paste from clipboard with Android support"""
        capture_message("Paste button clicked", level="info")
        try:
            # Try Android clipboard first (for pyjnius)
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                ClipboardManager = autoclass('android.content.ClipboardManager')
                Context = autoclass('android.content.Context')
                
                activity = PythonActivity.mActivity
                clipboard = activity.getSystemService(Context.CLIPBOARD_SERVICE)
                
                if clipboard.hasPrimaryClip():
                    clip = clipboard.getPrimaryClip()
                    if clip.getItemCount() > 0:
                        text = clip.getItemAt(0).getText()
                        if text:
                            field.text = str(text)
                            toast("הודבק!")
                            logger.info("Paste successful (Android clipboard)")
                            return
                logger.warning("Android clipboard empty or no clip")
            except Exception as e:
                # Log the Android clipboard error
                logger.error(f"Android clipboard failed: {e}")
            
            # Kivy clipboard fallback
            text = Clipboard.paste()
            if text:
                field.text = text
                toast("הודבק!")
                logger.info("Paste successful (Kivy clipboard)")
            else:
                toast("אין טקסט בלוח")
                logger.warning("Clipboard is empty")
        except Exception as e:
            logger.error(f"Paste error: {e}")
            toast("ההדבקה נכשלה")

    def shorten_links(self, *args):
        from ..utils.url_shortener import shorten_url
        s = self.source_field.text
        t = self.target_field.text
        
        if s and "http" in s:
            self.source_field.text = shorten_url(s)
            toast("Source shortened")
        if t and "http" in t:
            self.target_field.text = shorten_url(t)
            toast("Target shortened")

    def go_back(self, *args):
        self.manager.current = 'action'

    # --- TRANSFER LOGIC ---
    def start_transfer(self, *args):
        source = self.source_field.text
        target = self.target_field.text
        try:
            start_id = int(self.start_id_field.text) if self.start_id_field.text else 0
        except: start_id = 0
        
        if not source or not target:
            toast("Source and Target required")
            return
            
        selected_accs = [aid for aid, c in self.account_checks.items() if c.active]
        if not selected_accs:
            toast("Select at least one account")
            return
            
        session_id = f"task_{hex(int(time.time()))[2:]}"
        
        # Add UI Item
        self.add_task_item(session_id)
        
        # Run
        asyncio.create_task(self.run_transfer(session_id, selected_accs, source, target, start_id))

    def add_task_item(self, session_id):
        item = MDListItem(type="small")
        headline = MDListItemHeadlineText(text=f"Task: {session_id}")
        supporting = MDListItemSupportingText(text="Initializing...")
        
        item.add_widget(headline)
        item.add_widget(supporting)
        
        self.tasks_list.add_widget(item)
        self.tasks_map[session_id] = supporting

    def update_task_status(self, session_id, text):
        if session_id in self.tasks_map:
            self.tasks_map[session_id].text = text

    async def run_transfer(self, session_id, account_ids, source, target, start_id):
        self.update_task_status(session_id, "Connecting accounts...")
        
        clients = []
        for aid in account_ids:
            client = await self.account_manager.get_client(aid)
            if client: clients.append(client)
            
        if not clients:
            self.update_task_status(session_id, "Failed: No clients")
            return

        # Prepare config
        config = {
            'source': source,
            'target': target,
            'start_id': start_id,
            'file_types': [k for k,v in self.type_checks.items() if v.active]
        }
        
        # Register session
        self.transfer_manager.create_session(session_id, config)
        
        self.update_task_status(session_id, "Starting transfer...")
        
        try:
            await self.transfer_manager.start_mass_transfer(
                session_id, clients, self.update_task_status
            )
            self.update_task_status(session_id, "Completed")
        except Exception as e:
            logger.error(f"Transfer Error: {e}")
            self.update_task_status(session_id, f"Error: {e}")
