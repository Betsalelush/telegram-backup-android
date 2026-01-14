"""
Action Screen
Main menu for selecting actions
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.label import MDLabel
from kivy.uix.widget import Widget

from ..utils.logger import logger, add_breadcrumb


class ActionScreen(Screen):
    """
    Main action selection screen (KivyMD 2.0.0)
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        add_breadcrumb("ActionScreen initialized")
    
    def build_ui(self):
        """Build screen UI"""
        self.clear_widgets()

        # Main layout with centering
        layout = MDBoxLayout(
            orientation='vertical',
            padding="30dp",
            spacing="40dp",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            adaptive_height=True
        )

        # Title
        title = MDLabel(
            text="Telegram Backup",
            halign="center",
            font_style="Display", # H4 is DisplaySmall/Medium in MD3
            role="medium",
            theme_text_color="Primary",
            size_hint_y=None,
            height="120dp"
        )
        layout.add_widget(title)
        
        # 3 Main Buttons
        buttons = [
            ("Manage Accounts", "accounts", "account-group"),
            ("Transfer Console", "transfer", "transfer"),
            ("Live Logs", "logs", "console-line"),
        ]
        
        for text, screen, icon in buttons:
            btn = MDButton(
                style="filled",
                pos_hint={"center_x": 0.5},
            )
            # MDButton in 2.0.0 uses sizing differently.
            # To set fixed width, use size_hint_x=None + width
            # But let's use adaptive
            
            if icon:
                btn.add_widget(MDButtonIcon(icon=icon))
            
            btn.add_widget(MDButtonText(text=text))
            
            btn.bind(on_release=lambda x, s=screen: self.navigate_to(s))
            layout.add_widget(btn)

        # Container to center
        container = MDBoxLayout(orientation='vertical')
        container.add_widget(Widget())
        container.add_widget(layout)
        container.add_widget(Widget())

        self.add_widget(container)
    
    def navigate_to(self, screen_name: str):
        logger.info(f"Navigating to: {screen_name}")
        add_breadcrumb("Navigation", {"to": screen_name})
        self.manager.current = screen_name
