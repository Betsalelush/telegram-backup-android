"""
Action Screen
Main menu for selecting actions
"""
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon, MDIconButton, MDFabButton
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
    
    def build_ui(self):
        """Build screen UI"""
        self.clear_widgets()

        # Main layout with centering
        layout = MDBoxLayout(
            orientation='vertical',
            padding="30dp",
            spacing="30dp",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            adaptive_height=True
        )

        # Theme Toggle (Top Right)
        theme_btn = MDIconButton(
            icon="theme-light-dark",
            style="standard",
            pos_hint={"right": 0.95, "top": 0.95},
        )
        theme_btn.bind(on_release=self.toggle_theme)
        # We need to add this to the root container, not the centered layout

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
        
        # 4 Main Buttons
        buttons = [
            ("Manage Accounts", "accounts", "account-group"),
            ("Transfer Console", "transfer", "transfer"),
            ("Download Chat", "download", "download"),
            ("Live Logs", "logs", "console-line"),
        ]
        
        for text, screen, icon in buttons:
            btn = MDButton(
                style="filled", 
                # In MD 2.0.0 'filled' uses primary color background.
                # To get rectangular:
                radius=[4, 4, 4, 4], 
                pos_hint={"center_x": 0.5},
                size_hint_x=0.7, 
                height="64dp"
            )
            # Center content in button
            # Note: MD3 buttons auto-handle contrast if using standard styles.
            # But user reported confusion.
            # In Dark Mode: Primary color (Lavender) usually has black text.
            # User wants White text on Black? Or just standard contrast?
            # "When Dark: Buttons should be White on Black? Or lavender"
            # It seems user sees Lavender circle with text outside.
            # MDButton behaves like a container.
            
            # Let's try 'outlined' style for high contrast or stay 'filled' but ensure radius is small.
            # User wants: "Rectangular, not round".
            
            # Center content in button
            
            if icon:
                btn.add_widget(MDButtonIcon(icon=icon, pos_hint={"center_y": .5}))
            
            btn.add_widget(MDButtonText(text=text, pos_hint={"center_y": .5}))
            
            btn.bind(on_release=lambda x, s=screen: self.navigate_to(s))
            layout.add_widget(btn)

        # Container to center
        container = MDBoxLayout(orientation='vertical')
        
        # Top Bar for Theme Toggle
        top_bar = MDBoxLayout(adaptive_height=True, padding=[20, 20])
        top_bar.add_widget(Widget()) # Push to right
        top_bar.add_widget(theme_btn)
        
        container.add_widget(top_bar)
        container.add_widget(Widget())
        container.add_widget(layout)
        container.add_widget(Widget())

        self.add_widget(container)

    def toggle_theme(self, instance):
        """Switch between Light and Dark mode"""
        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Dark":
            app.theme_cls.theme_style = "Light"
            app.theme_cls.primary_palette = "White" # White background? No, palette defines accent.
            # Let's try keeping palette neutral or high contrast to black.
            app.theme_cls.primary_palette = "Gray" 
        else:
            app.theme_cls.theme_style = "Dark"
            app.theme_cls.primary_palette = "Lavender" 
    
    def navigate_to(self, screen_name: str):
        logger.info(f"Navigating to: {screen_name}")
        add_breadcrumb("Navigation", {"to": screen_name})
        self.manager.current = screen_name
