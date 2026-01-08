import asyncio
import logging
import os
import sys
import threading
import traceback
from datetime import datetime
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from telethon import TelegramClient

# ייבוא Android - בצורה נכונה!
ANDROID = False
try:
    from jnius import autoclass
    from android.runnable import run_on_ui_thread
    Environment = autoclass('android.os.Environment')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    ANDROID = True
except ImportError:
    pass

# הגדרת מערכת logging מתקדמת
class AndroidLogger:
    def __init__(self):
        self.log_file = None
        self.setup_logging()
    
    def setup_logging(self):
        """הגדרת logging לקובץ ול-console"""
        try:
            # קביעת תיקיית logs
            if ANDROID:
                try:
                    # שימוש ב-Environment.getExternalStorageDirectory()
                    storage_dir = Environment.getExternalStorageDirectory().getAbsolutePath()
                    log_dir = os.path.join(storage_dir, 'Download', 'TelegramBackup_Logs')
                except Exception as e:
                    # fallback
                    log_dir = '/sdcard/Download/TelegramBackup_Logs'
            else:
                log_dir = os.path.expanduser('~/TelegramBackup_Logs')
            
            os.makedirs(log_dir, exist_ok=True)
            
            # שם קובץ לוג עם תאריך ושעה
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.log_file = os.path.join(log_dir, f'app_log_{timestamp}.txt')
            
            # הגדרת logging
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                handlers=[
                    logging.FileHandler(self.log_file, encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
            
            self.logger = logging.getLogger('TelegramBackup')
            self.logger.info(f"=== אפליקציה התחילה ===")
            self.logger.info(f"קובץ לוג: {self.log_file}")
            self.logger.info(f"גרסת Python: {sys.version}")
            self.logger.info(f"Android: {ANDROID}")
            
        except Exception as e:
            print(f"שגיאה בהגדרת logging: {e}")
            traceback.print_exc()
    
    def log_exception(self, exc_type, exc_value, exc_traceback):
        """רישום חריגות לא מטופלות"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        self.logger.critical("חריגה לא מטופלת!", exc_info=(exc_type, exc_value, exc_traceback))
        
    def get_log_path(self):
        return self.log_file

# יצירת logger גלובלי
app_logger = AndroidLogger()
logger = app_logger.logger

# הגדרת exception handler גלובלי
sys.excepthook = app_logger.log_exception

# בקשת הרשאות Android - בצורה נכונה!
if ANDROID:
    try:
        logger.info("מבקש הרשאות Android...")
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.INTERNET,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE
        ])
        logger.info("הרשאות התקבלו")
    except Exception as e:
        logger.warning(f"לא הצלחנו לבקש הרשאות (זה תקין בגרסאות ישנות): {e}")

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
            
            MDLabel:
                id: log_path_label
                text: ""
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: "Hint"
                font_size: "10sp"
'''

class TelegramBackupApp(MDApp):
    def build(self):
        try:
            logger.info("מתחיל build של האפליקציה")
            self.theme_cls.primary_palette = "Blue"
            self.theme_cls.theme_style = "Light"
            self.client = None
            self.phone = None
            
            # הגדרת תיקיית עבודה
            try:
                if ANDROID:
                    storage_dir = Environment.getExternalStorageDirectory().getAbsolutePath()
                    self.session_dir = os.path.join(storage_dir, 'TelegramBackup')
                else:
                    self.session_dir = os.path.expanduser('~/TelegramBackup')
                
                os.makedirs(self.session_dir, exist_ok=True)
                logger.info(f"תיקיית עבודה: {self.session_dir}")
            except Exception as e:
                logger.error(f"שגיאה ביצירת תיקיית עבודה: {e}")
                self.session_dir = self.user_data_dir
                logger.info(f"משתמש בתיקייה פנימית: {self.session_dir}")
            
            root = Builder.load_string(KV)
            
            # הצגת מיקום קובץ הלוג
            log_path = app_logger.get_log_path()
            if log_path:
                root.ids.log_path_label.text = f"לוג: {log_path}"
            
            logger.info("build הושלם בהצלחה")
            return root
            
        except Exception as e:
            logger.critical(f"שגיאה קריטית ב-build: {e}", exc_info=True)
            raise

    def log(self, message):
        """רישום הודעה ל-UI ול-logger"""
        logger.info(message)
        
        def update_ui(dt):
            try:
                current_text = self.root.ids.status_log.text
                self.root.ids.status_log.text = message + "\\n" + current_text
            except Exception as e:
                logger.error(f"שגיאה בעדכון UI: {e}")
        
        from kivy.clock import Clock
        Clock.schedule_once(update_ui)

    def send_code(self):
        try:
            logger.info("=== send_code נקרא ===")
            api_id = self.root.ids.api_id.text
            api_hash = self.root.ids.api_hash.text
            phone = self.root.ids.phone.text

            logger.debug(f"API ID: {api_id[:4]}... (מוסתר)")
            logger.debug(f"Phone: {phone}")

            if not api_id or not api_hash or not phone:
                self.log("חסרים פרטים (API ID/HASH/Phone)")
                logger.warning("חסרים פרטים")
                return
            
            session_file = os.path.join(self.session_dir, f'session_{phone.replace("+", "")}')
            logger.info(f"יוצר client עם session: {session_file}")
            
            self.client = TelegramClient(session_file, int(api_id), api_hash)
            self.phone = phone
            self.log(f"Client נוצר. Session: {os.path.basename(session_file)}")
            
            threading.Thread(target=self._send_code_thread, args=(phone,), daemon=True).start()
            logger.info("Thread לשליחת קוד הופעל")
            
        except Exception as e:
            logger.error(f"שגיאה ב-send_code: {e}", exc_info=True)
            self.log(f"שגיאה: {e}")

    def _send_code_thread(self, phone):
        try:
            logger.info("=== _send_code_thread התחיל ===")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def async_send():
                try:
                    self.log("מתחבר לטלגרם...")
                    logger.info("מתחבר ל-Telegram")
                    await self.client.connect()
                    logger.info("חיבור הצליח")
                    
                    if not await self.client.is_user_authorized():
                        logger.info("משתמש לא מורשה, שולח קוד")
                        await self.client.send_code_request(phone)
                        self.log("קוד נשלח! הזן אותו ולחץ 'התחבר'.")
                        logger.info("קוד נשלח בהצלחה")
                        
                        from kivy.clock import Clock
                        def enable_fields(dt):
                            self.root.ids.code.disabled = False
                            self.root.ids.login_btn.disabled = False
                        Clock.schedule_once(enable_fields)
                    else:
                        logger.info("משתמש כבר מורשה")
                        self.log("כבר מחובר!")
                        from kivy.clock import Clock
                        def enable_backup(dt):
                            self.root.ids.start_btn.disabled = False
                        Clock.schedule_once(enable_backup)
                        
                except Exception as e:
                    logger.error(f"שגיאה ב-async_send: {e}", exc_info=True)
                    self.log(f"שגיאה: {e}")
            
            loop.run_until_complete(async_send())
            logger.info("async_send הושלם")
            
        except Exception as e:
            logger.error(f"שגיאה ב-_send_code_thread: {e}", exc_info=True)
            self.log(f"שגיאה: {e}")
        finally:
            loop.close()
            logger.info("_send_code_thread הסתיים")

    def login(self):
        try:
            logger.info("=== login נקרא ===")
            code = self.root.ids.code.text
            phone = self.root.ids.phone.text
            
            if not code:
                self.log("הזן את הקוד")
                logger.warning("קוד חסר")
                return
                
            logger.info(f"מנסה להתחבר עם קוד: {code[:2]}...")
            threading.Thread(target=self._login_thread, args=(phone, code), daemon=True).start()
            
        except Exception as e:
            logger.error(f"שגיאה ב-login: {e}", exc_info=True)
            self.log(f"שגיאה: {e}")

    def _login_thread(self, phone, code):
        try:
            logger.info("=== _login_thread התחיל ===")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def async_login():
                try:
                    if not self.client.is_connected():
                        logger.info("מתחבר מחדש...")
                        await self.client.connect()
                    
                    logger.info("מבצע sign_in")
                    await self.client.sign_in(phone, code)
                    self.log("התחברת בהצלחה!")
                    logger.info("התחברות הצליחה")
                    
                    from kivy.clock import Clock
                    def enable_backup(dt):
                        self.root.ids.start_btn.disabled = False
                    Clock.schedule_once(enable_backup)
                    
                except Exception as e:
                    logger.error(f"שגיאה ב-async_login: {e}", exc_info=True)
                    self.log(f"שגיאה: {e}")

            loop.run_until_complete(async_login())
            
        except Exception as e:
            logger.error(f"שגיאה ב-_login_thread: {e}", exc_info=True)
            self.log(f"שגיאה: {e}")
        finally:
            loop.close()
            logger.info("_login_thread הסתיים")

    def start_backup(self):
        try:
            logger.info("=== start_backup נקרא ===")
            source = self.root.ids.source_channel.text
            target = self.root.ids.target_channel.text
            
            logger.info(f"מקור: {source}, יעד: {target}")
            
            if not source or not target:
                self.log("הזן ערוץ מקור ויעד")
                logger.warning("ערוצים חסרים")
                return
            
            threading.Thread(target=self._backup_thread, args=(source, target), daemon=True).start()
            logger.info("Thread גיבוי הופעל")
            
        except Exception as e:
            logger.error(f"שגיאה ב-start_backup: {e}", exc_info=True)
            self.log(f"שגיאה: {e}")

    def _backup_thread(self, source, target):
        try:
            logger.info("=== _backup_thread התחיל ===")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def async_backup():
                try:
                    if not self.client.is_connected():
                        logger.info("מתחבר מחדש...")
                        await self.client.connect()

                    self.log("מתחיל גיבוי...")
                    logger.info("מתחיל תהליך גיבוי")
                    
                    try:
                        if source.lstrip('-').isdigit(): source = int(source)
                        if target.lstrip('-').isdigit(): target = int(target)
                    except: pass

                    logger.info(f"מחפש ערוצים: {source}, {target}")
                    s_entity = await self.client.get_entity(source)
                    t_entity = await self.client.get_entity(target)
                    
                    s_title = getattr(s_entity, 'title', str(source))
                    t_title = getattr(t_entity, 'title', str(target))
                    logger.info(f"נמצאו: {s_title} -> {t_title}")
                    self.log(f"מ: {s_title} → {t_title}")
                    
                    count = 0
                    async for message in self.client.iter_messages(s_entity, limit=20):
                        if message:
                            try:
                                await self.client.send_message(t_entity, message)
                                count += 1
                                if count % 5 == 0:
                                    self.log(f"הועברו {count} הודעות")
                                    logger.info(f"הועברו {count} הודעות")
                            except Exception as inner_e:
                                logger.error(f"שגיאה בהודעה {message.id}: {inner_e}")
                    
                    self.log(f"סיום! {count} הודעות")
                    logger.info(f"גיבוי הושלם: {count} הודעות")

                except Exception as e:
                    logger.error(f"שגיאה ב-async_backup: {e}", exc_info=True)
                    self.log(f"שגיאה: {e}")

            loop.run_until_complete(async_backup())
            
        except Exception as e:
            logger.error(f"שגיאה ב-_backup_thread: {e}", exc_info=True)
            self.log(f"שגיאה: {e}")
        finally:
            loop.close()
            logger.info("_backup_thread הסתיים")

    def on_pause(self):
        logger.info("=== on_pause נקרא ===")
        return True

    def on_resume(self):
        logger.info("=== on_resume נקרא ===")
        pass
    
    def on_stop(self):
        logger.info("=== on_stop נקרא - אפליקציה נסגרת ===")

if __name__ == '__main__':
    try:
        logger.info("=== מפעיל אפליקציה ===")
        TelegramBackupApp().run()
    except Exception as e:
        logger.critical(f"שגיאה קריטית בהפעלת אפליקציה: {e}", exc_info=True)
        raise
