import asyncio
import threading
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from telethon import TelegramClient
import sentry_sdk

# Sentry - תופס crashes!
sentry_sdk.init(
    dsn="https://1f490b846ede82cfc3d5f6f5eb23263b@o4510215210598400.ingest.de.sentry.io/4510674676744272",
    traces_sample_rate=1.0,
)

KV = '''
MDBoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 10

    MDLabel:
        text: "גיבוי טלגרם"
        halign: "center"
        font_style: "H5"
        size_hint_y: None
        height: self.texture_size[1]

    MDScrollView:
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: 15
            padding: 10
            
            MDTextField:
                id: api_id
                hint_text: "API ID"
                mode: "rectangle"

            MDTextField:
                id: api_hash
                hint_text: "API HASH"
                mode: "rectangle"

            MDTextField:
                id: phone
                hint_text: "מספר טלפון (+972...)"
                mode: "rectangle"

            MDFillRoundFlatButton:
                text: "שלח קוד אימות"
                pos_hint: {"center_x": .5}
                on_release: app.send_code()

            MDTextField:
                id: code
                hint_text: "קוד אימות"
                mode: "rectangle"
                disabled: True

            MDFillRoundFlatButton:
                id: login_btn
                text: "התחבר"
                pos_hint: {"center_x": .5}
                disabled: True
                on_release: app.login()

            MDTextField:
                id: source_channel
                hint_text: "ערוץ מקור (ID או Link)"
                mode: "rectangle"

            MDTextField:
                id: target_channel
                hint_text: "ערוץ יעד (ID או Link)"
                mode: "rectangle"

            MDFillRoundFlatButton:
                id: start_btn
                text: "התחל גיבוי"
                pos_hint: {"center_x": .5}
                disabled: True
                on_release: app.start_backup()

            MDLabel:
                id: status_log
                text: "מוכן...\\n"
                halign: "left"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Secondary"
'''

class TelegramBackupApp(MDApp):
    def build(self):
        try:
            self.theme_cls.primary_palette = "Blue"
            self.theme_cls.theme_style = "Light"
            self.client = None
            self.phone = None
            return Builder.load_string(KV)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise

    def log(self, message):
        def update_ui(dt):
            try:
                current_text = self.root.ids.status_log.text
                self.root.ids.status_log.text = message + "\\n" + current_text
            except Exception as e:
                sentry_sdk.capture_exception(e)
        
        from kivy.clock import Clock
        Clock.schedule_once(update_ui)

    def send_code(self):
        try:
            api_id = self.root.ids.api_id.text
            api_hash = self.root.ids.api_hash.text
            phone = self.root.ids.phone.text

            if not api_id or not api_hash or not phone:
                self.log("חסרים פרטים")
                return
            
            self.client = TelegramClient(f'session_{phone.replace("+", "")}', int(api_id), api_hash)
            self.phone = phone
            
            threading.Thread(target=self._send_code_thread, args=(phone,), daemon=True).start()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            self.log(f"שגיאה: {e}")

    def _send_code_thread(self, phone):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def async_send():
                try:
                    self.log("מתחבר...")
                    await self.client.connect()
                    
                    if not await self.client.is_user_authorized():
                        await self.client.send_code_request(phone)
                        self.log("קוד נשלח!")
                        
                        from kivy.clock import Clock
                        def enable_fields(dt):
                            self.root.ids.code.disabled = False
                            self.root.ids.login_btn.disabled = False
                        Clock.schedule_once(enable_fields)
                    else:
                        self.log("כבר מחובר!")
                        from kivy.clock import Clock
                        def enable_backup(dt):
                            self.root.ids.start_btn.disabled = False
                        Clock.schedule_once(enable_backup)
                except Exception as e:
                    sentry_sdk.capture_exception(e)
                    self.log(f"שגיאה: {e}")
            
            loop.run_until_complete(async_send())
            loop.close()
        except Exception as e:
            sentry_sdk.capture_exception(e)

    def login(self):
        try:
            code = self.root.ids.code.text
            phone = self.root.ids.phone.text
            if not code:
                self.log("הזן קוד")
                return
            threading.Thread(target=self._login_thread, args=(phone, code), daemon=True).start()
        except Exception as e:
            sentry_sdk.capture_exception(e)

    def _login_thread(self, phone, code):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def async_login():
                try:
                    if not self.client.is_connected():
                        await self.client.connect()
                    
                    await self.client.sign_in(phone, code)
                    self.log("התחברת!")
                    
                    from kivy.clock import Clock
                    def enable_backup(dt):
                        self.root.ids.start_btn.disabled = False
                    Clock.schedule_once(enable_backup)
                except Exception as e:
                    sentry_sdk.capture_exception(e)
                    self.log(f"שגיאה: {e}")

            loop.run_until_complete(async_login())
            loop.close()
        except Exception as e:
            sentry_sdk.capture_exception(e)

    def start_backup(self):
        try:
            source = self.root.ids.source_channel.text
            target = self.root.ids.target_channel.text
            if not source or not target:
                self.log("הזן ערוצים")
                return
            threading.Thread(target=self._backup_thread, args=(source, target), daemon=True).start()
        except Exception as e:
            sentry_sdk.capture_exception(e)

    def _backup_thread(self, source, target):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def async_backup():
                try:
                    if not self.client.is_connected():
                        await self.client.connect()

                    self.log("מתחיל גיבוי...")
                    
                    try:
                        if source.lstrip('-').isdigit(): source = int(source)
                        if target.lstrip('-').isdigit(): target = int(target)
                    except: pass

                    s_entity = await self.client.get_entity(source)
                    t_entity = await self.client.get_entity(target)
                    
                    s_title = getattr(s_entity, 'title', str(source))
                    t_title = getattr(t_entity, 'title', str(target))
                    self.log(f"מ: {s_title} → {t_title}")
                    
                    count = 0
                    async for message in self.client.iter_messages(s_entity, limit=20):
                        if message:
                            try:
                                await self.client.send_message(t_entity, message)
                                count += 1
                                if count % 5 == 0:
                                    self.log(f"{count} הודעות")
                            except Exception as inner_e:
                                sentry_sdk.capture_exception(inner_e)
                    
                    self.log(f"סיום! {count} הודעות")
                except Exception as e:
                    sentry_sdk.capture_exception(e)
                    self.log(f"שגיאה: {e}")

            loop.run_until_complete(async_backup())
            loop.close()
        except Exception as e:
            sentry_sdk.capture_exception(e)

if __name__ == '__main__':
    try:
        TelegramBackupApp().run()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise
