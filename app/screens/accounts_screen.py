"""
Accounts Screen
Manage Telegram accounts
"""
import asyncio
import urllib.parse
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.core.clipboard import Clipboard
from kivy.uix.image import AsyncImage

# KivyMD 2.0.0 Imports
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    MDList,
    MDListItem, 
    MDListItemHeadlineText, 
    MDListItemSupportingText, 
    MDListItemLeadingIcon, 
    MDListItemTrailingIcon
)
from kivymd.uix.dialog import (
    MDDialog, 
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogContentContainer,
    MDDialogButtonContainer
)
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton, MDFabButton
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldTrailingIcon
from kivymd.uix.appbar import (
    MDTopAppBar, 
    MDTopAppBarLeadingButtonContainer, 
    MDActionTopAppBarButton, 
    MDTopAppBarTitle, 
    MDTopAppBarTrailingButtonContainer
)
from kivymd.toast import toast

from ..managers.account_manager import AccountManager
from ..utils.logger import logger, add_breadcrumb


class AccountsScreen(Screen):
    """
    Screen for managing accounts (KivyMD 2.0.0 Update)
    """
    
    def __init__(self, account_manager: AccountManager, **kwargs):
        super().__init__(**kwargs)
        self.account_manager = account_manager
        self.dialog = None
        self.auth_dialog = None
        self.settings_dialog = None
        self.options_dialog = None
        self.qr_dialog = None
        
        self.build_ui()
        add_breadcrumb("AccountsScreen initialized")
    
    def on_enter(self):
        # Update background on enter
        app = MDApp.get_running_app()
        if hasattr(self, 'root_box'):
            self.root_box.md_bg_color = app.theme_cls.backgroundColor
            
        self.load_accounts_list()

    def build_ui(self):
        self.clear_widgets()
        app = MDApp.get_running_app()
        
        # Root Layout
        self.root_box = MDBoxLayout(
            orientation='vertical', 
            spacing=0,
            md_bg_color=app.theme_cls.backgroundColor
        )
        
        # Toolbar (MD3)
        self.toolbar = MDTopAppBar(type="small")
        
        # Leading (Back)
        leading_container = MDTopAppBarLeadingButtonContainer()
        back_btn = MDActionTopAppBarButton(icon="arrow-left")
        back_btn.on_release = self.go_back
        leading_container.add_widget(back_btn)
        self.toolbar.add_widget(leading_container)
        
        # Title
        self.toolbar.add_widget(MDTopAppBarTitle(text="Accounts"))
        
        # Trailing (Settings)
        trailing_container = MDTopAppBarTrailingButtonContainer()
        cog_btn = MDActionTopAppBarButton(icon="cog")
        cog_btn.on_release = self.show_global_settings
        trailing_container.add_widget(cog_btn)
        self.toolbar.add_widget(trailing_container)
        
        root_box = self.root_box # Alias for legacy code usage below if needed, but we use self.root_box
        
        self.root_box.add_widget(self.toolbar)
        
        # Content
        scroll = MDScrollView()
        self.accounts_list = MDList()
        scroll.add_widget(self.accounts_list)
        self.root_box.add_widget(scroll)
        
        # FAB (Bottom Right)
        # In MD3, FAB often goes in a FloatLayout or Overlay, 
        # but pure MDBoxLayout cuts it off.
        # Let's just put it at bottom of the box for now or use FloatLayout wrapper if needed.
        # But for list screens, standard is usually FAB over list.
        # Since we use simple layout, let's inject FAB into a FloatLayout wrapper?
        # Actually, simpler: Let's refactor root to Float, add Box(Toolbar, List), then FAB.
        
        # Re-doing Layout structure for FAB support
        # We need to re-assign self.root_box to be the INNER box, and allow FAB on top.
        # BUT current code added root_box to self.
        
        self.add_widget(self.root_box)
        
        # Add FAB
        fab = MDFabButton(
            icon="plus",
            style="standard",
            pos_hint={"right": .95, "bottom": .05},
        )
        fab.bind(on_release=self.show_add_account_dialog)
        self.add_widget(fab)
        



    def go_back(self, *args):
        self.manager.current = 'action'

    def create_input_with_paste(self, hint, field_ref_name, **kwargs):
        """Helper to create MDTextField with paste support"""
        field = MDTextField(
            MDTextFieldHintText(text=hint),
            mode="outlined",
            **kwargs
        )
        
        # Trailing paste icon
        paste_icon = MDTextFieldTrailingIcon(icon="content-paste")
        paste_icon.bind(on_release=lambda x: self.do_paste(field))
        field.add_widget(paste_icon)
        
        setattr(self, field_ref_name, field)
        return field

    def do_paste(self, field):
        """Paste from clipboard with Android support"""
        try:
            # Try Android clipboard first
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
                            return
            except:
                pass
            
            # Kivy clipboard fallback
            text = Clipboard.paste()
            if text:
                field.text = text
                toast("הודבק!")
            else:
                toast("אין טקסט בלוח")
        except Exception as e:
            logger.error(f"Paste error: {e}")
            toast("ההדבקה נכשלה")

    # --- LIST LOADING ---
    def load_accounts_list(self):
        self.accounts_list.clear_widgets()
        accounts = self.account_manager.get_all_accounts()
        
        if not accounts:
            self.accounts_list.add_widget(
                MDLabel(
                    text="No accounts found",
                    halign="center",
                    theme_text_color="Hint",
                    size_hint_y=None,
                    height="100dp"
                )
            )
            return

        for acc in accounts:
            is_connected = acc.get('authorized', False)
            status_text = "Connected" if is_connected else "Not Connected"
            
            item = MDListItem(
                type="small",
                pos_hint={"center_x": .5, "center_y": .5}
            )
            
            # Leading
            leading = MDListItemLeadingIcon(
                icon="account-check" if is_connected else "account-alert",
            )
            item.add_widget(leading)
            
            # Headline
            phone = f"+{acc.get('phone','?')}"
            headline = MDListItemHeadlineText(
                text=f"{acc.get('name', 'User')} ({phone})"
            )
            item.add_widget(headline)
            
            # Supporting
            supporting = MDListItemSupportingText(
                text=f"{status_text} • ID: {acc.get('id', 'N/A')}"
            )
            item.add_widget(supporting)
            
            # Trailing Action
            trailing = MDListItemTrailingIcon(icon="dots-vertical")
            trailing.bind(on_release=lambda x, a=acc: self.show_account_options(a))
            item.add_widget(trailing)
            
            self.accounts_list.add_widget(item)

    # --- DIALOGS (MD3) ---

    def show_add_account_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()
        
        # Fields
        self.name_field = self.create_input_with_paste("Account Name", "name_field")
        self.phone_field = self.create_input_with_paste("Phone Number (+972...)", "phone_field", input_filter="int")
        self.api_id_field = self.create_input_with_paste("API ID (Optional)", "api_id_field")
        self.api_hash_field = self.create_input_with_paste("API Hash (Optional)", "api_hash_field")

        self.dialog = MDDialog()
        self.dialog.add_widget(MDDialogHeadlineText(text="Add New Account"))
        
        content = MDDialogContentContainer(orientation="vertical", spacing="10dp")
        content.add_widget(self.name_field)
        content.add_widget(self.phone_field)
        content.add_widget(self.api_id_field)
        content.add_widget(self.api_hash_field)
        
        if self.account_manager.global_api_id:
            content.add_widget(MDLabel(
                text="* Using Global API credentials", 
                theme_text_color="Hint", font_style="Caption"
            ))
            
        self.dialog.add_widget(content)
        
        buttons = MDDialogButtonContainer()
        btn_cancel = MDButton(style="text")
        btn_cancel.add_widget(MDButtonText(text="CANCEL"))
        btn_cancel.bind(on_release=lambda x: self.dialog.dismiss())
        
        btn_add = MDButton(style="text")
        btn_add.add_widget(MDButtonText(text="ADD"))
        btn_add.bind(on_release=self.add_account_callback)
        
        buttons.add_widget(btn_cancel)
        buttons.add_widget(btn_add)
        self.dialog.add_widget(buttons)
        
        self.dialog.open()

    def add_account_callback(self, *args):
        try:
            name = self.name_field.text
            phone = self.phone_field.text
            api_id = self.api_id_field.text
            api_hash = self.api_hash_field.text
            
            if not name or not phone:
                toast("Name and Phone are required!")
                return
            
            acc_id = self.account_manager.add_account(
                name=name, phone=phone, api_id=api_id, api_hash=api_hash
            )
            
            if acc_id:
                toast("Account added!")
                self.dialog.dismiss()
                self.load_accounts_list()
                asyncio.create_task(self._handle_manual_login(acc_id))
            else:
                toast("Failed to add account")
                
        except Exception as e:
            logger.error(f"Add account error: {e}")
            toast(f"Error: {e}")

    def show_global_settings(self, *args):
        self.g_api_id_field = self.create_input_with_paste("Global API ID", "g_api_id_field")
        self.g_api_hash_field = self.create_input_with_paste("Global API Hash", "g_api_hash_field")
        
        self.g_api_id_field.text = self.account_manager.global_api_id or ""
        self.g_api_hash_field.text = self.account_manager.global_api_hash or ""

        self.settings_dialog = MDDialog()
        self.settings_dialog.add_widget(MDDialogHeadlineText(text="Global API Settings"))
        
        content = MDDialogContentContainer(orientation="vertical", spacing="10dp")
        content.add_widget(self.g_api_id_field)
        content.add_widget(self.g_api_hash_field)
        
        self.settings_dialog.add_widget(content)
        
        buttons = MDDialogButtonContainer()
        btn_cancel = MDButton(style="text")
        btn_cancel.add_widget(MDButtonText(text="CANCEL"))
        btn_cancel.bind(on_release=lambda x: self.settings_dialog.dismiss())
        
        btn_save = MDButton(style="text")
        btn_save.add_widget(MDButtonText(text="SAVE"))
        btn_save.bind(on_release=self.save_global_settings_callback)
        
        buttons.add_widget(btn_cancel)
        buttons.add_widget(btn_save)
        self.settings_dialog.add_widget(buttons)
        
        self.settings_dialog.open()

    def save_global_settings_callback(self, *args):
        api_id = self.g_api_id_field.text
        api_hash = self.g_api_hash_field.text
        self.account_manager.save_global_settings(api_id, api_hash)
        self.settings_dialog.dismiss()
        toast("Settings Saved")

    def show_account_options(self, account):
        acc_id = account['id']
        
        self.options_dialog = MDDialog()
        self.options_dialog.add_widget(MDDialogHeadlineText(text=f"Account: {account.get('name')}"))
        
        content = MDDialogContentContainer(orientation="vertical", spacing="10dp")
        
        # Buttons
        # SMS
        btn_sms = MDButton(style="filled", pos_hint={"center_x": .5})
        btn_sms.add_widget(MDButtonText(text="CONNECT VIA SMS"))
        btn_sms.bind(on_release=lambda x: self.deferred_dialog_action(acc_id, 'manual_connect'))
        content.add_widget(btn_sms)
        
        # QR
        btn_qr = MDButton(style="filled", pos_hint={"center_x": .5})
        btn_qr.add_widget(MDButtonText(text="CONNECT VIA QR"))
        btn_qr.bind(on_release=lambda x: self.deferred_dialog_action(acc_id, 'qr_connect'))
        content.add_widget(btn_qr)
        
        # REMOVE
        btn_del = MDButton(style="text", pos_hint={"center_x": .5})
        btn_del.add_widget(MDButtonText(text="REMOVE FROM APP", theme_text_color="Error"))
        btn_del.bind(on_release=lambda x: self.deferred_dialog_action(acc_id, 'delete'))
        content.add_widget(btn_del)
        
        self.options_dialog.add_widget(content)
        self.options_dialog.open()

    def deferred_dialog_action(self, account_id, action):
        if self.options_dialog:
            self.options_dialog.dismiss()
        
        if action == 'manual_connect':
            asyncio.create_task(self._handle_manual_login(account_id))
        elif action == 'qr_connect':
            asyncio.create_task(self._process_qr(account_id))
        elif action == 'delete':
            self.account_manager.remove_account(account_id)
            self.load_accounts_list()
            toast("Account Removed")

    # --- LOGIN LOGIC ---

    async def _handle_manual_login(self, account_id):
        success = await self.account_manager.connect_account(account_id)
        if success:
            toast("Connected!")
            self.load_accounts_list()
            return
            
        # Start SMS
        try:
            toast("Requesting SMS...")
            res = await self.account_manager.send_login_code(account_id)
            self.phone_code_hash = res.phone_code_hash
            self.show_auth_dialog(account_id, "Enter SMS Code", mode="code")
        except Exception as e:
            toast(f"Error: {e}")

    def show_auth_dialog(self, account_id, title, mode="code"):
        self.auth_input = self.create_input_with_paste(title, "auth_input")
        if mode == "password":
            self.auth_input.password = True
            
        self.auth_dialog = MDDialog()
        self.auth_dialog.add_widget(MDDialogHeadlineText(text=title))
        
        content = MDDialogContentContainer(orientation="vertical", spacing="10dp")
        content.add_widget(self.auth_input)
        self.auth_dialog.add_widget(content)
        
        buttons = MDDialogButtonContainer()
        btn_cancel = MDButton(style="text")
        btn_cancel.add_widget(MDButtonText(text="CANCEL"))
        btn_cancel.bind(on_release=lambda x: self.auth_dialog.dismiss())
        
        btn_sub = MDButton(style="text")
        btn_sub.add_widget(MDButtonText(text="SUBMIT"))
        btn_sub.bind(on_release=lambda x: self._submit_auth(account_id, mode))
        
        buttons.add_widget(btn_cancel)
        buttons.add_widget(btn_sub)
        self.auth_dialog.add_widget(buttons)
        self.auth_dialog.open()

    def _submit_auth(self, account_id, mode):
        val = self.auth_input.text
        self.auth_dialog.dismiss()
        
        if mode == "code":
            asyncio.create_task(self._finish_login(account_id, val))
        else:
            asyncio.create_task(self._finish_login(account_id, None, password=val))

    async def _finish_login(self, account_id, code, password=None):
        try:
            res = await self.account_manager.sign_in(
                account_id, 
                getattr(self, 'phone_code_hash', None), 
                code, 
                password=password
            )
            
            if res == "PASSWORD_NEEDED":
                self.show_auth_dialog(account_id, "Enter 2FA Password", mode="password")
            else:
                toast("Login Successful!")
                self.load_accounts_list()
        except Exception as e:
            toast(f"Login failed: {e}")

    async def _process_qr(self, account_id):
        toast("Generating QR...")
        try:
            qr_login, client = await self.account_manager.start_qr_auth(account_id)
            if not qr_login:
                toast("Failed to start QR")
                return
            
            url = qr_login.url
            encoded_url = urllib.parse.quote(url)
            qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={encoded_url}"
            
            self.qr_dialog = MDDialog()
            self.qr_dialog.add_widget(MDDialogHeadlineText(text="Scan QR Code"))
            
            content = MDDialogContentContainer(orientation="vertical", size_hint_y=None, height="350dp")
            img = AsyncImage(source=qr_api_url, size_hint=(1, 1))
            content.add_widget(img)
            content.add_widget(MDLabel(text="Scan with Telegram Mobile App", halign="center"))
            self.qr_dialog.add_widget(content)
            
            buttons = MDDialogButtonContainer()
            btn_close = MDButton(style="text")
            btn_close.add_widget(MDButtonText(text="CLOSE"))
            btn_close.bind(on_release=lambda x: self.close_qr_dialog())
            buttons.add_widget(btn_close)
            self.qr_dialog.add_widget(buttons)
            
            self.qr_dialog.open()
            
            # Wait loop
            user = await qr_login.wait()
            self.close_qr_dialog()
            toast(f"Welcome {user.first_name}!")
            await self.account_manager.connect_account(account_id)
            self.load_accounts_list()
            
        except Exception as e:
            logger.error(f"QR Error: {e}")
            toast(f"QR Error: {e}")
            self.close_qr_dialog()

    def close_qr_dialog(self):
        if self.qr_dialog:
            self.qr_dialog.dismiss()
            self.qr_dialog = None
