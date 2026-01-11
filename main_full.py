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
import sentry_sdk

# Sentry - תופס crashes!
sentry_sdk.init(
    dsn="https://1f490b846ede82cfc3d5f6f5eb23263b@o4510215210598400.ingest.de.sentry.io/4510674676744272",
    traces_sample_rate=1.0,
)

# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ⚠️ שים לב: Telethon לא נטען כאן! הוא ייטען רק כשצריך (lazy loading)

KV = '''
MDBoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 10

    MDLabel:
        text: "Telegram Backup"
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
            
            MDLabel:
                text: "Get API credentials from: my.telegram.org"
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Primary"
                font_style: "Caption"
            
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
                hint_text: "Phone Number (+972...)"
                mode: "rectangle"

            MDFillRoundFlatButton:
                text: "Send Verification Code"
                pos_hint: {"center_x": .5}
                on_release: app.send_code()

            MDTextField:
                id: code
                hint_text: "Verification Code"
                mode: "rectangle"
                disabled: True

            MDFillRoundFlatButton:
                id: login_btn
                text: "Login"
                pos_hint: {"center_x": .5}
                disabled: True
                on_release: app.login()

            MDTextField:
                id: source_channel
                hint_text: "Source Channel (ID or Link)"
                mode: "rectangle"

            MDTextField:
                id: target_channel
                hint_text: "Target Channel (ID or Link)"
                mode: "rectangle"

            MDFillRoundFlatButton:
                id: start_btn
                text: "Start Backup"
                pos_hint: {"center_x": .5}
                disabled: True
                on_release: app.start_backup()

            MDLabel:
                id: status_log
                text: "Ready...\\n"
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
        
        # 🆕 שמירת התקדמות
        self.sent_message_ids = set()
        self.last_processed_message_id = 0
        self.consecutive_successes = 0
        
        # תיקון Android: שימוש בתיקיית האפליקציה לקבצי Session
        try:
            from android.storage import app_storage_path
            self.session_dir = app_storage_path()
            logger.info(f"Android: Using directory {self.session_dir}")
        except ImportError:
            # לא Android - שימוש בתיקייה הנוכחית
            self.session_dir = os.getcwd()
            logger.info(f"Desktop: Using directory {self.session_dir}")
        
        # לא טוענים התקדמות כאן - נטען לפי ערוצים ספציפיים
        
        return Builder.load_string(KV)
    
    def get_progress_key(self, source_id, target_id):
        """Create unique key for source→target channel pair"""
        return f"channel_{source_id}_to_{target_id}"
    
    def load_progress(self, source_id, target_id):
        """Load progress for specific channel pair"""
        progress_file = os.path.join(self.session_dir, 'progress.json')
        
        # Load all progress data
        all_progress = {}
        if os.path.exists(progress_file):
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    all_progress = json.load(f)
            except Exception as e:
                logger.error(f"Error loading progress file: {e}")
        
        # Get progress for this specific channel pair
        key = self.get_progress_key(source_id, target_id)
        channel_progress = all_progress.get(key, {})
        
        self.sent_message_ids = set(channel_progress.get('sent_message_ids', []))
        self.last_processed_message_id = channel_progress.get('last_message_id', 0)
        
        if self.sent_message_ids:
            self.log(f"✅ Loaded progress for {key}: {len(self.sent_message_ids)} messages sent")
        else:
            self.log(f"📝 Starting fresh for {key}")
    
    def save_progress(self, source_id, target_id):
        """Save progress for specific channel pair"""
        progress_file = os.path.join(self.session_dir, 'progress.json')
        
        # Load all existing progress
        all_progress = {}
        if os.path.exists(progress_file):
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    all_progress = json.load(f)
            except Exception as e:
                logger.error(f"Error loading progress file: {e}")
        
        # Limit size if too large
        if len(self.sent_message_ids) > 10000:
            temp_list = list(self.sent_message_ids)
            import random
            random.shuffle(temp_list)
            self.sent_message_ids = set(temp_list[:10000])
        
        # Update progress for this channel pair
        key = self.get_progress_key(source_id, target_id)
        all_progress[key] = {
            'sent_message_ids': list(self.sent_message_ids),
            'last_message_id': self.last_processed_message_id
        }
        
        # Save all progress
        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(all_progress, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Progress saved for {key}: {len(self.sent_message_ids)} messages")
        except Exception as e:
            logger.error(f"❌ Error saving progress: {e}")
    
    def smart_delay(self):
        """Smart delay based on consecutive successes"""
        if self.consecutive_successes > 10:
            return random.uniform(1, 2)  # Fast
        elif self.consecutive_successes > 5:
            return random.uniform(2, 4)  # Medium
        else:
            return random.uniform(3, 5)  # Slow
    

    def log(self, message):
        def update_ui(dt):
            current_text = self.root.ids.status_log.text
            self.root.ids.status_log.text = message + "\\n" + current_text
        
        # עדכון ה-UI חייב להתבצע מה-Thread הראשי
        from kivy.clock import Clock
        Clock.schedule_once(update_ui)
        print(message)
        logger.info(message)

    def send_code(self):
        api_id = self.root.ids.api_id.text
        api_hash = self.root.ids.api_hash.text
        phone = self.root.ids.phone.text

        if not api_id or not api_hash or not phone:
            self.log("חסרים פרטים (API ID/HASH/Phone)")
            return
        
        # 🔥 Lazy Loading: טעינת Telethon רק כאן!
        try:
            self.log("טוען Telethon...")
            from telethon import TelegramClient
            self.log("✅ Telethon נטען בהצלחה!")
        except ImportError as e:
            error_msg = f"❌ שגיאה: Telethon לא מותקן - {e}"
            self.log(error_msg)
            sentry_sdk.capture_exception(e)
            return
        except Exception as e:
            error_msg = f"❌ שגיאה בטעינת Telethon: {e}"
            self.log(error_msg)
            sentry_sdk.capture_exception(e)
            return
        
        # שמירת הלוגיקה והלקוח ברמת האפליקציה
        try:
            session_name = f'session_{phone.replace("+", "")}'
            session_path = os.path.join(self.session_dir, session_name)
            self.log(f"יוצר session: {session_path}")
            
            self.client = TelegramClient(session_path, int(api_id), api_hash)
            self.phone = phone
        except Exception as e:
            error_msg = f"שגיאה ביצירת לקוח: {e}"
            self.log(error_msg)
            sentry_sdk.capture_exception(e)
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
                    
                    # שינוי מצב כפתורים דרך Clock
                    from kivy.clock import Clock
                    def enable_fields(dt):
                        self.root.ids.code.disabled = False
                        self.root.ids.login_btn.disabled = False
                    Clock.schedule_once(enable_fields)
                else:
                    self.log("כבר מחובר למשתמש זה!")
                    from kivy.clock import Clock
                    def enable_backup(dt):
                        self.root.ids.start_btn.disabled = False
                    Clock.schedule_once(enable_backup)
            except Exception as e:
                error_msg = f"שגיאה בשליחת קוד: {e}"
                self.log(error_msg)
                sentry_sdk.capture_exception(e)
        
        try:
            loop.run_until_complete(async_send())
        except Exception as e:
            sentry_sdk.capture_exception(e)
        finally:
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
                
                from kivy.clock import Clock
                def enable_backup(dt):
                    self.root.ids.start_btn.disabled = False
                Clock.schedule_once(enable_backup)
            except Exception as e:
                error_msg = f"שגיאה בהתחברות: {e}"
                self.log(error_msg)
                sentry_sdk.capture_exception(e)

        try:
            loop.run_until_complete(async_login())
        except Exception as e:
            sentry_sdk.capture_exception(e)
        finally:
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

                self.log("Starting backup process...")
                
                # המרה למספרים אם צריך
                try:
                    if source.lstrip('-').isdigit(): source = int(source)
                    if target.lstrip('-').isdigit(): target = int(target)
                except: pass

                try:
                     s_entity = await self.client.get_entity(source)
                     t_entity = await self.client.get_entity(target)
                except Exception as e:
                     error_msg = f"Cannot find channels. Make sure you joined them.\nError: {e}"
                     self.log(error_msg)
                     sentry_sdk.capture_exception(e)
                     return

                s_title = getattr(s_entity, 'title', str(source))
                t_title = getattr(t_entity, 'title', str(target))
                s_id = s_entity.id
                t_id = t_entity.id
                
                self.log(f"Transferring from: {s_title}\nTo: {t_title}")
                
                # 🆕 טעינת התקדמות לזוג ערוצים זה
                self.load_progress(s_id, t_id)
                
                # 🆕 שמירת התקדמות + המתנה חכמה
                count = 0
                skipped = 0
                
                async for message in self.client.iter_messages(s_entity, limit=100):
                    if message and message.id:
                        # בדיקה אם כבר שלחנו את ההודעה
                        if message.id in self.sent_message_ids:
                            skipped += 1
                            continue
                        
                        try:
                            # 🔥 הורדה והעלאה ללא קרדיט!
                            if message.media:
                                # יש מדיה - הורד והעלה
                                self.log(f"📥 Downloading media from message {message.id}...")
                                file = await self.client.download_media(message.media, file=bytes)
                                
                                if file:
                                    self.log(f"📤 Uploading to target...")
                                    await self.client.send_file(
                                        t_entity,
                                        file,
                                        caption=message.text if message.text else ''
                                    )
                                else:
                                    self.log(f"⚠️ Failed to download media from message {message.id}")
                                    continue
                            elif message.text:
                                # טקסט בלבד
                                await self.client.send_message(t_entity, message.text)
                            else:
                                # הודעה ריקה - דלג
                                self.log(f"⏩ Skipping empty message {message.id}")
                                continue
                            
                            count += 1
                            self.consecutive_successes += 1
                            
                            # שמירת ההודעה כנשלחה
                            self.sent_message_ids.add(message.id)
                            self.last_processed_message_id = message.id
                            
                            # שמירת התקדמות כל 10 הודעות
                            if count % 10 == 0:
                                self.save_progress(s_id, t_id)
                            
                            # 🎲 המתנה חכמה - אקראית!
                            delay = self.smart_delay()
                            self.log(f"✅ {count} sent, {skipped} skipped. Waiting {delay:.1f}s...")
                            await asyncio.sleep(delay)
                            
                        except errors.FloodWaitError as e:
                            # 🔥 טיפול ב-FloodWait
                            wait_time = e.seconds + random.uniform(2, 5)
                            self.log(f"⏰ FloodWait! Waiting {wait_time:.0f}s...")
                            self.consecutive_successes = 0  # איפוס
                            await asyncio.sleep(wait_time)
                            
                        except Exception as inner_e:
                            self.log(f"❌ Error in message {message.id}: {inner_e}")
                            self.consecutive_successes = 0  # איפוס
                            sentry_sdk.capture_exception(inner_e)
                            await asyncio.sleep(self.smart_delay())
                
                # שמירה סופית
                self.save_progress(s_id, t_id)
                
                self.log(f"🎉 Backup completed!")
                self.log(f"📊 Sent: {count}, Skipped: {skipped}")

            except Exception as e:
                error_msg = f"General backup error: {e}"
                self.log(error_msg)
                sentry_sdk.capture_exception(e)

        try:
            loop.run_until_complete(async_backup())
        except Exception as e:
            sentry_sdk.capture_exception(e)
        finally:
            loop.close()

if __name__ == '__main__':
    try:
        TelegramBackupApp().run()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise
