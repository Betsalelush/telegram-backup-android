"""
Action Screen
Main menu for selecting actions
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel

from ..utils.logger import logger, add_breadcrumb


class ActionScreen(Screen):
    """
    Main action selection screen
    
    Features:
    - New transfer
    - Active transfers
    - Manage accounts
    - Settings
    """
    
    def __init__(self, **kwargs):
        """Initialize Action Screen"""
        super().__init__(**kwargs)
        
        # Build UI
        self.build_ui()
        
        add_breadcrumb("ActionScreen initialized")
    
    def build_ui(self):
        """Build screen UI"""
        layout = MDBoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20
        )
        
        # Title
        title = MDLabel(
            text="Telegram Backup",
            halign="center",
            font_style="H4",
            size_hint_y=None,
            height=100
        )
        layout.add_widget(title)
        
        # Buttons
        buttons = [
            ("New Transfer", "transfer"),
            ("Manage Accounts", "accounts"),
            ("Settings", "settings"),
        ]
        
        for text, screen in buttons:
            btn = MDRaisedButton(
                text=text,
                size_hint=(0.8, None),
                height=60,
                pos_hint={"center_x": 0.5}
            )
            btn.bind(on_release=lambda x, s=screen: self.navigate_to(s))
            layout.add_widget(btn)
        
        self.add_widget(layout)
    
    def navigate_to(self, screen_name: str):
        """
        Navigate to screen
        
        Args:
            screen_name: Screen name
        """
        logger.info(f"Navigating to: {screen_name}")
        add_breadcrumb("Navigation", {"to": screen_name})
        
        self.manager.current = screen_name
