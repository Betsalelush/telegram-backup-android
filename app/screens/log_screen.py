"""
Log Screen
View live logs from the application
"""
import logging
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDFloatingActionButton
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.properties import StringProperty

from ..utils.logger import logger, add_breadcrumb


class LogScreen(Screen):
    """
    Screen for viewing application logs
    """
    log_text = StringProperty("Logs will appear here...\n")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
        # Setup log handler to redirect to specific text widget or variable
        # For now, we'll just read from a global buffer or simplistic approach
        # Ideally, we should add a custom Handler to the root logger
        self.setup_log_handler()
        
    def build_ui(self):
        """Build screen UI"""
        layout = MDBoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(title="Live Logs")
        toolbar.left_action_items = [["arrow-left", lambda x: self.go_back()]]
        toolbar.right_action_items = [["delete", lambda x: self.clear_logs()]]
        layout.add_widget(toolbar)
        
        # Log view (using TextInput as readonly for selectable text)
        self.log_view = TextInput(
            text=self.log_text,
            readonly=True,
            background_color=(0, 0, 0, 1),
            foreground_color=(0, 1, 0, 1),  # Green text
            font_size="12sp",
            font_name="RobotoMono-Regular" if "RobotoMono-Regular" in self.get_font_list() else "Roboto"
        )
        self.bind(log_text=self._update_text)
        layout.add_widget(self.log_view)
        
        self.add_widget(layout)
        
    def setup_log_handler(self):
        """Add a handler to capture logs"""
        class UILogHandler(logging.Handler):
            def __init__(self, screen):
                super().__init__()
                self.screen = screen
                
            def emit(self, record):
                msg = self.format(record)
                # Update on main thread
                Clock.schedule_once(lambda dt: self.screen.append_log(msg))
                
        handler = UILogHandler(self)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
        
    def append_log(self, msg):
        """Append log message"""
        self.log_text += msg + "\n"
        
    def _update_text(self, instance, value):
        """Update actual widget text"""
        if hasattr(self, 'log_view'):
            self.log_view.text = value
            # Auto scroll to bottom (simple approach)
            self.log_view.cursor = (0, len(self.log_view.text))

    def clear_logs(self):
        """Clear logs"""
        self.log_text = ""
        logger.info("Logs cleared by user")
        
    def go_back(self):
        """Go back"""
        self.manager.current = 'action'
        
    def get_font_list(self):
        """Get available fonts (helper)"""
        from kivy.core.text import LabelBase
        return LabelBase.get_system_fonts_dir()
