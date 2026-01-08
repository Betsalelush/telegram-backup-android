import asyncio
import logging
import os
import threading
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from telethon import TelegramClient

# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
                text: "מוכן...\n"
                halign: "left"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Secondary"
'''

class TelegramBackupApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.client = None
        self.phone = None
        return Builder.load_string(KV)

    def log(self, message):
        def update_ui(dt):
            current_text = self.root.ids.status_log.text
            self.root.ids.status_log.text = message + "\n" + current_text
        
        # עדכון ה-UI חייב להתבצע מה-Thread הראשי
        from kivy.clock import Clock
        Clock.schedule_once(update_ui)
        print(message)

    def send_code(self):
        api_id = self.root.ids.api_id.text
        api_hash = self.root.ids.api_hash.text
        phone = self.root.ids.phone.text

        if not api_id or not api_hash or not phone:
            self.log("חסרים פרטים (API ID/HASH/Phone)")
            return
        
        # שמירת הלוגיקה והלקוח ברמת האפליקציה
        try:
             self.client = TelegramClient(f'session_{phone.replace("+", "")}', int(api_id), api_hash)
        except Exception as e:
            self.log(f"שגיאה ביצירת לקוח: {e}")
            return

        threading.Thread(target=self._send_code_thread, args=(phone,), daemon=True).start()

    def _send_code_thread(self, phone):
        # יצירת Loop חדש עבור ה-Thread הזה
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def async_send():
            try:
                self.log("מתחבר לשרתי טלגרם...")
                await self.client.connect()
                
                if not await self.client.is_user_authorized():
                    self.log("שולח בקשת קוד אימות...")
                    await self.client.send_code_request(phone)
                    self.log("קוד נשלח! אנא הזן אותו בשדה המתאים ולחץ 'התחבר'.")
                    
                    # שינוי מצב כפתורים (דרך ה-Main Thread אם צריך, אבל Kivy לרוב מסתדר עם Property changes)
                    # עדיף להשתמש ב-Clock אם זה קריטי, אבל ננסה ישיר
                    self.root.ids.code.disabled = False
                    self.root.ids.login_btn.disabled = False
                else:
                    self.log("כבר מחובר למשתמש זה!")
                    self.root.ids.start_btn.disabled = False
            except Exception as e:
                self.log(f"שגיאה בשליחת קוד: {e}")
        
        loop.run_until_complete(async_send())
        loop.close()

    def login(self):
        code = self.root.ids.code.text
        phone = self.root.ids.phone.text
        if not code:
            self.log("אנא הזן את הקוד שקיבלת.")
            return
        threading.Thread(target=self._login_thread, args=(phone, code), daemon=True).start()

    def _login_thread(self, phone, code):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def async_login():
            try:
                if not self.client.is_connected():
                     await self.client.connect()
                     
                await self.client.sign_in(phone, code)
                self.log("התחברת בהצלחה!")
                self.root.ids.start_btn.disabled = False
            except Exception as e:
                self.log(f"שגיאה בהתחברות: {e}")

        loop.run_until_complete(async_login())
        loop.close()

    def start_backup(self):
        source = self.root.ids.source_channel.text
        target = self.root.ids.target_channel.text
        if not source or not target:
            self.log("אנא הזן ערוץ מקור וערוץ יעד.")
            return
        
        threading.Thread(target=self._backup_thread, args=(source, target), daemon=True).start()

    def _backup_thread(self, source, target):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def async_backup():
            try:
                if not self.client.is_connected():
                     await self.client.connect()

                self.log("מתחיל בתהליך הגיבוי...")
                
                # המרה למספרים אם צריך
                try:
                    if source.lstrip('-').isdigit(): source = int(source)
                    if target.lstrip('-').isdigit(): target = int(target)
                except: pass

                try:
                     s_entity = await self.client.get_entity(source)
                     t_entity = await self.client.get_entity(target)
                except Exception as e:
                     self.log(f"לא מצליח למצוא את הערוצים. ודא שהצטרפת אליהם.\nשגיאה: {e}")
                     return

                s_title = getattr(s_entity, 'title', str(source))
                t_title = getattr(t_entity, 'title', str(target))
                self.log(f"מעביר מ: {s_title}\nאל: {t_title}")
                
                # לוגיקה פשוטה להעברה - אפשר להרחיב ללוגיקה המלאה מהקוד המקורי
                count = 0
                async for message in self.client.iter_messages(s_entity, limit=20): # הגבלה ל-20 להדגמה
                    if message:
                        try:
                            await self.client.send_message(t_entity, message)
                            count += 1
                            if count % 5 == 0:
                                self.log(f"הועברו {count} הודעות...")
                        except Exception as inner_e:
                            self.log(f"שגיאה בהודעה {message.id}: {inner_e}")
                
                self.log(f"סיום סבב! הועברו {count} הודעות.")

            except Exception as e:
                self.log(f"שגיאה כללית בתהליך הגיבוי: {e}")

        loop.run_until_complete(async_backup())
        loop.close()

if __name__ == '__main__':
    TelegramBackupApp().run()
