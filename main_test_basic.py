from kivy.app import App
from kivy.uix.label import Label
import sentry_sdk

# Sentry - תופס crashes!
sentry_sdk.init(
    dsn="https://1f490b846ede82cfc3d5f6f5eb23263b@o4510215210598400.ingest.de.sentry.io/4510674676744272",
    traces_sample_rate=1.0,
)

class TestBasicApp(App):
    def build(self):
        return Label(
            text='Test Basic\nKivy Only\nIf you see this - Kivy works!',
            font_size='20sp'
        )

if __name__ == '__main__':
    try:
        TestBasicApp().run()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise
