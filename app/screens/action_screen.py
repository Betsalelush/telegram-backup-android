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
    - Manage Accounts
    - Transfer Console
    - Live Logs
    """
    
    def __init__(self, **kwargs):
        """Initialize Action Screen"""
        super().__init__(**kwargs)
        self.build_ui()
        add_breadcrumb("ActionScreen initialized")
    
    def build_ui(self):
        """Build screen UI"""
        from kivy.uix.widget import Widget

        # Main layout with centering
        layout = MDBoxLayout(
            orientation='vertical',
            padding=30,
            spacing=40,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            adaptive_height=True
        )

        # Title
        title = MDLabel(
            text="Telegram Backup",
            halign="center",
            font_style="H4",
            theme_text_color="Primary",
            size_hint_y=None,
            height=120
        )
        layout.add_widget(title)
        
        # 3 Main Buttons
        buttons = [
            ("Manage Accounts", "accounts", "account-group"),
            ("Transfer Console", "transfer", "transfer"),
            ("Live Logs", "logs", "console-line"),
        ]
        
        for text, screen, icon in buttons:
            btn = MDRaisedButton(
                text=text,
                size_hint=(0.9, None),
                height=80,
                pos_hint={"center_x": 0.5},
                elevation=3,
                font_size="20sp"
            )
            btn.bind(on_release=lambda x, s=screen: self.navigate_to(s))
            layout.add_widget(btn)

        # Container to center
        container = MDBoxLayout(orientation='vertical')
        container.add_widget(Widget())
        container.add_widget(layout)
        container.add_widget(Widget())

        self.add_widget(container)
    
    def navigate_to(self, screen_name: str):
        """Navigate to screen"""
        logger.info(f"Navigating to: {screen_name}")
        add_breadcrumb("Navigation", {"to": screen_name})
        self.manager.current = screen_name
