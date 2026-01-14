"""
Action Screen
Main menu for selecting actions
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon, MDIconButton
from kivymd.uix.label import MDLabel
from kivy.uix.widget import Widget
from kivymd.app import MDApp

from ..utils.logger import logger, add_breadcrumb


class ActionScreen(Screen):
    """
    Main action selection screen (KivyMD 2.0.0)
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        add_breadcrumb("ActionScreen initialized")

    def on_enter(self, *args):
        # Ensure background is updated when entering screen
        app = MDApp.get_running_app()
        if hasattr(self, 'root_container'):
             self.root_container.md_bg_color = app.theme_cls.backgroundColor
    
    def build_ui(self):
        """Build screen UI"""
        self.clear_widgets()
        
        # We need a root container that ADAPTS to the theme background
        # By default Screen is transparent?, so Window color shows.
        # But we want explicit control.
        self.root_container = MDBoxLayout(
            orientation='vertical',
            md_bg_color=MDApp.get_running_app().theme_cls.backgroundColor
        )

        # Top Bar for Theme Toggle
        top_bar = MDBoxLayout(adaptive_height=True, padding=["20dp", "20dp"])
        top_bar.add_widget(Widget()) # Push to right
        
        theme_btn = MDIconButton(
            icon="theme-light-dark",
            style="standard",
        )
        theme_btn.bind(on_release=self.toggle_theme)
        top_bar.add_widget(theme_btn)
        
        self.root_container.add_widget(top_bar)
        
        # Spacer
        self.root_container.add_widget(Widget())

        # Main Central Layout
        center_layout = MDBoxLayout(
            orientation='vertical',
            padding="30dp",
            spacing="25dp", # Slightly tighter spacing
            pos_hint={"center_x": 0.5},
            adaptive_height=True
        )

        # Title
        title = MDLabel(
            text="Telegram Backup",
            halign="center",
            font_style="Display",
            role="medium",
            theme_text_color="Primary",
            size_hint_y=None,
            height="120dp"
        )
        center_layout.add_widget(title)
        
        # Buttons
        buttons = [
            ("Manage Accounts", "accounts", "account-group"),
            ("Transfer Console", "transfer", "transfer"),
            ("Download Chat", "download", "download"),
            ("Live Logs", "logs", "console-line"),
        ]
        
        for text, screen, icon in buttons:
            # Stadium Shape (Sausage)
            # Height: 54dp
            # Radius: 27dp (half of height)
            
            btn = MDButton(
                style="filled",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.85, 
                height="54dp",
                radius=[27, 27, 27, 27],
            )
            
            # Content
            if icon:
                btn.add_widget(MDButtonIcon(
                    icon=icon, 
                    pos_hint={"center_y": .5}
                ))
            
            btn.add_widget(MDButtonText(
                text=text, 
                pos_hint={"center_y": .5},
                font_style="Label", # Using Label instead of Title for better fit
                role="large",
            ))
            
            btn.bind(on_release=lambda x, s=screen: self.navigate_to(s))
            center_layout.add_widget(btn)

        self.root_container.add_widget(center_layout)
        
        # Spacer
        self.root_container.add_widget(Widget())

        self.add_widget(self.root_container)
        
        # Bind theme change to update background manually if needed
        app = MDApp.get_running_app()
        app.bind(theme_cls=self.update_bg)

    def update_bg(self, instance, value):
        # Triggered when theme_style changes
        # But we need to listen specifically to theme_style property change?
        # Usually binding to theme_cls is redundant if using kivymd widgets correctly.
        # But let's force update color.
        if hasattr(self, 'root_container'):
            self.root_container.md_bg_color = instance.theme_cls.backgroundColor

    def toggle_theme(self, instance):
        """Switch between Light and Dark mode"""
        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Dark":
            # Switch to Light
            app.theme_cls.theme_style = "Light"
            app.theme_cls.primary_palette = "Olive" # Something High Contrast? Or Gray
            # User wants black buttons.
            # In Light mode, Primary color fills the button.
            # If we want black buttons, we need a dark palette.
            # But "Black" isn't a palette. "Gray" or "Neutral"?
            # Let's stick with "Gray" or similar dark tone.
        else:
            # Switch to Dark
            app.theme_cls.theme_style = "Dark"
            # User wants White buttons?
            # In Dark mode, Primary color fills.
            # If we want White buttons, we need "White" (not possible).
            # "Lavender" is close to white-ish.
            app.theme_cls.primary_palette = "Lavender"
            
        # Force background update explicitly
        self.root_container.md_bg_color = app.theme_cls.backgroundColor
    
    def navigate_to(self, screen_name: str):
        logger.info(f"Navigating to: {screen_name}")
        add_breadcrumb("Navigation", {"to": screen_name})
        self.manager.current = screen_name
