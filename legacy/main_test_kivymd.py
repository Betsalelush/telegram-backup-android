from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
import sentry_sdk

# Sentry - תופס crashes!
sentry_sdk.init(
    dsn="https://1f490b846ede82cfc3d5f6f5eb23263b@o4510215210598400.ingest.de.sentry.io/4510674676744272",
    traces_sample_rate=1.0,
)

class TestKivyMDApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        box = MDBoxLayout(orientation='vertical', padding=20, spacing=10)
        box.add_widget(MDLabel(
            text='Test KivyMD',
            halign='center',
            font_style='H4'
        ))
        box.add_widget(MDLabel(
            text='If you see this - KivyMD works!',
            halign='center'
        ))
        return box

if __name__ == '__main__':
    try:
        TestKivyMDApp().run()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise
