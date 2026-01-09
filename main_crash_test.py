from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
import sentry_sdk

# 🔥 Sentry חדש - פרויקט טסט!
sentry_sdk.init(
    dsn="https://a7e9dc2a18c39ecd8925696e027bc7ac@o4510215210598400.ingest.de.sentry.io/4510679475224656",
    traces_sample_rate=1.0,
)

class CrashTestApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Red"
        box = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # כותרת
        box.add_widget(MDLabel(
            text='🧪 Sentry Crash Test',
            halign='center',
            font_style='H4'
        ))
        
        # הסבר
        box.add_widget(MDLabel(
            text='לחץ על הכפתור כדי לגרום לקריסה מכוונת.\\nהשגיאה תישלח ל-Sentry!',
            halign='center',
            theme_text_color='Secondary'
        ))
        
        # כפתור קריסה
        crash_btn = MDFillRoundFlatButton(
            text="💥 Crash Me!",
            pos_hint={"center_x": .5},
            on_release=self.intentional_crash
        )
        box.add_widget(crash_btn)
        
        # הודעת הצלחה
        box.add_widget(MDLabel(
            text='✅ אם אתה רואה את זה - האפליקציה עובדת!\\n✅ Sentry מוכן לתפוס crashes!',
            halign='center',
            theme_text_color='Primary'
        ))
        
        return box
    
    def intentional_crash(self, instance):
        """
        פונקציה שגורמת לקריסה מכוונת.
        Sentry צריך לתפוס את זה ולשלוח דיווח!
        """
        print("🔥 גורם לקריסה מכוונת...")
        
        # קריסה מכוונת - חלוקה באפס
        result = 1 / 0  # ZeroDivisionError
        
        # השורה הזו לעולם לא תתבצע
        print("זה לא אמור להופיע!")

if __name__ == '__main__':
    try:
        CrashTestApp().run()
    except Exception as e:
        # Sentry יתפוס את זה!
        sentry_sdk.capture_exception(e)
        raise
