"""
Log Screen
View live logs from the application
"""
import logging
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.properties import StringProperty

# KivyMD 2.0.0
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.appbar import (
    MDTopAppBar, 
    MDTopAppBarLeadingButtonContainer, 
    MDActionTopAppBarButton, 
    MDTopAppBarTitle,
    MDTopAppBarTrailingButtonContainer
)

from ..utils.logger import logger, add_breadcrumb


class LogScreen(Screen):
    """
    Screen for viewing application logs (MD3)
    """
    log_text = StringProperty("Logs will appear here...\n")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        self.setup_log_handler()
        
    def build_ui(self):
        self.clear_widgets()
        layout = MDBoxLayout(orientation='vertical')
        
        # Toolbar
        self.toolbar = MDTopAppBar(type="small")
        
        leading = MDTopAppBarLeadingButtonContainer()
        back = MDActionTopAppBarButton(icon="arrow-left")
        back.on_release = self.go_back
        leading.add_widget(back)
        self.toolbar.add_widget(leading)
        
        self.toolbar.add_widget(MDTopAppBarTitle(text="Live Logs"))
        
        trailing = MDTopAppBarTrailingButtonContainer()
        trash = MDActionTopAppBarButton(icon="delete")
        trash.on_release = self.clear_logs
        trailing.add_widget(trash)
        self.toolbar.add_widget(trailing)
        
        layout.add_widget(self.toolbar)
        
        # Log view
        self.log_view = TextInput(
            text=self.log_text,
            readonly=True,
            background_color=(0, 0, 0, 1),
            foreground_color=(0, 1, 0, 1),
            font_size="12sp",
        )
        self.bind(log_text=self._update_text)
        layout.add_widget(self.log_view)
        
        self.add_widget(layout)
        
    def setup_log_handler(self):
        class UILogHandler(logging.Handler):
            def __init__(self, screen):
                super().__init__()
                self.screen = screen
                
            def emit(self, record):
                msg = self.format(record)
                Clock.schedule_once(lambda dt: self.screen.append_log(msg))
                
        handler = UILogHandler(self)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
        
    def append_log(self, msg):
        self.log_text += msg + "\n"
        
    def _update_text(self, instance, value):
        if hasattr(self, 'log_view'):
            self.log_view.text = value
            self.log_view.cursor = (0, len(self.log_view.text))

    def clear_logs(self, *args):
        self.log_text = ""
        logger.info("Logs cleared by user")
        
    def go_back(self, *args):
        self.manager.current = 'action'
