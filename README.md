# 📱 Telegram Backup Android - v3.0

אפליקציית אנדרואיד מודרנית להעברת הודעות בין ערוצי טלגרם עם תמיכה בריבוי חשבונות.

[![Build Status](https://github.com/Betsalelush/telegram-backup-android/workflows/Build%20Android%20APK/badge.svg)](https://github.com/Betsalelush/telegram-backup-android/actions)

---

## ✨ תכונות עיקריות

### 🎯 ניהול חשבונות
- ✅ **Multi-Account Support** - תמיכה בריבוי חשבונות טלגרם
- ✅ **Round-Robin Distribution** - חלוקת הודעות בין חשבונות
- ✅ **Session Management** - שמירת התחברות בין הרצות

### 📤 העברת הודעות
- ✅ **3 שיטות העברה:**
  - Forward - העברה ישירה (מהיר)
  - Send Message - שליחת הודעה חדשה
  - Download & Upload - הורדה והעלאה (לערוצים פרטיים)
- ✅ **Smart Rate Limiting** - מניעת חסימה (20 הודעות/דקה)
- ✅ **FloodWait Handling** - טיפול אוטומטי בהגבלות טלגרם
- ✅ **Progress Tracking** - שמירת התקדמות והמשך מנקודת עצירה

### 🔧 תכונות נוספות
- ✅ **File Type Filtering** - בחירת סוגי קבצים (תמונות, וידאו, מסמכים)
- ✅ **Channel Link Parsing** - תמיכה בכל סוגי הקישורים (t.me/c/, @username)
- ✅ **Sentry Integration** - תיעוד שגיאות אוטומטי
- ✅ **Performance Monitoring** - מעקב ביצועים

---

## 📋 55 פונקציות באפליקציה

### AccountManager (10 פונקציות)
```python
1. __init__()                  # אתחול מנהל חשבונות
2. load_accounts()             # טעינת חשבונות מJSON
3. save_accounts()             # שמירת חשבונות לJSON
4. add_account()               # הוספת חשבון חדש
5. remove_account()            # מחיקת חשבון
6. connect_account()           # התחברות לטלגרם (async)
7. disconnect_account()        # ניתוק מטלגרם (async)
8. get_account()               # קבלת חשבון לפי ID
9. get_connected_accounts()    # רשימת חשבונות מחוברים
10. get_client()               # קבלת Telegram client
```

### ProgressManager (8 פונקציות)
```python
1. __init__()                  # אתחול מנהל התקדמות
2. get_progress_key()          # יצירת מפתח ייחודי
3. load_progress()             # טעינת התקדמות מקובץ
4. save_progress()             # שמירת התקדמות לקובץ
5. get_all_progress()          # כל ההתקדמויות
6. clear_progress()            # ניקוי התקדמות
7. update_progress()           # עדכון התקדמות
8. cleanup_old_progress()      # ניקוי קבצים ישנים
```

### TransferManager (12 פונקציות)
```python
1. __init__()                        # אתחול מנהל העברות
2. transfer_message()                # העברת הודעה (3 שיטות)
3. check_rate_limit()                # בדיקת מגבלת קצב
4. smart_delay()                     # השהיה חכמה
5. send_messages_batch()             # שליחת אצווה עם round-robin
6. get_next_client()                 # בחירת חשבון הבא
7. handle_flood_wait_for_client()    # טיפול ב-FloodWait
8. get_stats()                       # קבלת סטטיסטיקות
9. reset_stats()                     # איפוס סטטיסטיקות
10. create_transfer()                # יצירת העברה חדשה
```

### Logger (4 פונקציות)
```python
1. init_sentry()           # אתחול Sentry
2. add_breadcrumb()        # הוספת breadcrumb
3. set_user_context()      # הגדרת context משתמש
4. capture_exception()     # תפיסת שגיאה
```

### Helpers (8 פונקציות)
```python
1. list_available_chats()   # רשימת ערוצים זמינים
2. parse_channel_link()     # פענוח קישור ערוץ
3. get_channel_variations() # וריאציות של ID
4. choose_file_types()      # בחירת סוגי קבצים
5. filter_by_file_type()    # סינון לפי סוג קובץ
6. download_media()         # הורדת מדיה
7. upload_media()           # העלאת מדיה
```

### Screens (17 פונקציות)
```python
# AccountsScreen (7)
1. __init__()              # אתחול
2. build_ui()              # בניית ממשק
3. on_enter()              # כניסה למסך
4. load_accounts_list()    # טעינת רשימה
5. show_add_dialog()       # דיאלוג הוספה
6. add_account()           # הוספת חשבון
7. on_account_action()     # פעולות על חשבון

# ActionScreen (3)
1. __init__()              # אתחול
2. build_ui()              # בניית ממשק
3. navigate_to()           # ניווט

# TransferScreen (7)
1. __init__()              # אתחול
2. build_ui()              # בניית ממשק
3. start_transfer()        # התחלת העברה
4. _run_transfer()         # הרצת העברה (async)
5. stop_transfer()         # עצירת העברה
6. update_progress()       # עדכון התקדמות
7. go_back()               # חזרה
```

**סה"כ:** 55+ פונקציות!

---

## 📁 מבנה הפרויקט

```
telegram-backup-android/
├── app/                          # קוד האפליקציה
│   ├── __init__.py              # אתחול חבילה
│   ├── config.py                # הגדרות (Sentry, Rate Limits, Paths)
│   ├── main.py                  # Entry point - TelegramBackupApp
│   │
│   ├── managers/                # מנהלי לוגיקה עסקית
│   │   ├── __init__.py
│   │   ├── account_manager.py  # ניהול חשבונות (10 פונקציות)
│   │   ├── progress_manager.py # ניהול התקדמות (8 פונקציות)
│   │   └── transfer_manager.py # ניהול העברות (12 פונקציות)
│   │
│   ├── screens/                 # מסכי UI
│   │   ├── __init__.py
│   │   ├── accounts_screen.py  # מסך ניהול חשבונות (7 פונקציות)
│   │   ├── action_screen.py    # תפריט ראשי (3 פונקציות)
│   │   └── transfer_screen.py  # מסך העברות (7 פונקציות)
│   │
│   └── utils/                   # כלים עזר
│       ├── __init__.py
│       ├── logger.py           # Sentry logger (4 פונקציות)
│       └── helpers.py          # פונקציות עזר (8 פונקציות)
│
├── tests/                       # בדיקות
│   ├── __init__.py
│   ├── test_account_manager.py
│   └── test_progress_manager.py
│
├── .github/workflows/           # GitHub Actions
│   └── build-apk.yml           # Workflow משופר עם cache
│
├── main.py                      # Entry point ראשי
├── buildozer.spec              # הגדרות build
├── requirements_full.txt       # תלויות (גרסאות קבועות)
├── sentry_logger.py            # Sentry logger נוסף
├── README.md                   # המסמך הזה
├── BUILD_ERRORS.md             # תיעוד שגיאות build
└── MASTER_PLAN.md              # תוכנית אב
```

---

## 🚀 איך משתמשים באפליקציה

### 1️⃣ הוספת חשבון
1. פתח את האפליקציה
2. לחץ על "Manage Accounts"
3. לחץ על כפתור ➕
4. הזן:
   - שם חשבון
   - API ID (מ-my.telegram.org)
   - API Hash (מ-my.telegram.org)
   - מספר טלפון
5. לחץ "ADD"
6. לחץ "Connect" להתחברות

### 2️⃣ התחלת העברה
1. חזור לתפריט הראשי
2. לחץ על "New Transfer"
3. הזן:
   - **Source Channel:** ערוץ מקור (ID או קישור)
   - **Target Channel:** ערוץ יעד (ID או קישור)
4. לחץ "Start Transfer"
5. האפליקציה תתחיל להעביר הודעות

### 3️⃣ מעקב אחרי התקדמות
- תראה progress bar עם אחוזים
- מספר הודעות שנשלחו / סה"כ
- אפשר לעצור בכל רגע ולהמשיך מאוחר יותר

### 4️⃣ סוגי קישורים נתמכים
```
✅ t.me/username
✅ t.me/c/123456789
✅ @username
✅ -100123456789 (ID ישיר)
```

---

## 🔧 התקנה ופיתוח

### דרישות
- Python 3.11+
- Buildozer (לבניית APK)
- Telegram API credentials (מ-my.telegram.org)

### התקנת תלויות
```bash
pip install -r requirements_full.txt
```

### הרצה מקומית (Desktop)
```bash
python main.py
```

### בניית APK
```bash
buildozer android debug
```

### GitHub Actions
הפרויקט כולל workflow אוטומטי:
- Push ל-master → בנייה אוטומטית
- Cache מלא (pip, buildozer, SDK/NDK)
- זמן build: 45 דקות (ראשון) → 5-10 דקות (עם cache)
- APK זמין ב-Actions artifacts

---

## ⚙️ הגדרות

### Sentry (מוגדר!)
```python
# app/config.py
SENTRY_DSN = "https://..."  # מוגדר ופעיל
SENTRY_TRACES_SAMPLE_RATE = 1.0
SENTRY_ENVIRONMENT = "production"
```

### Rate Limiting
```python
# app/config.py
MAX_MESSAGES_PER_MINUTE = 20  # מספר הודעות מקסימלי
SMART_DELAY_MIN = 2           # השהיה מינימלית (שניות)
SMART_DELAY_MAX = 8           # השהיה מקסימלית (שניות)
```

### שיטות העברה
```python
# app/config.py
DEFAULT_TRANSFER_METHOD = "download_upload"
# אפשרויות: "forward", "send_message", "download_upload"
```

---

## 📊 סטטיסטיקות

- **קבצי Python:** 18
- **פונקציות:** 55+
- **מסכים:** 3
- **בדיקות:** 9
- **שורות קוד:** ~2,000

---

## 🧪 בדיקות

הרצת בדיקות:
```bash
pytest tests/ -v
```

בדיקות זמינות:
- `test_account_manager.py` - בדיקות ניהול חשבונות
- `test_progress_manager.py` - בדיקות התקדמות

---

## 🔍 Sentry Integration

האפליקציה שולחת ל-Sentry:
- ✅ כל השגיאות (exceptions)
- ✅ 100 breadcrumbs אחרונים (מה קרה לפני)
- ✅ Logs (WARNING ומעלה)
- ✅ User context (מי קיבל שגיאה)
- ✅ Performance data (מהירות, זמנים)

---

## ⚠️ הערות חשובות

1. **API Credentials:** צריך להשיג API ID ו-API Hash מ-[my.telegram.org](https://my.telegram.org)
2. **Rate Limits:** טלגרם מגביל 20 הודעות לדקה - האפליקציה מטפלת בזה אוטומטית
3. **FloodWait:** במקרה של חסימה זמנית, האפליקציה ממתינה אוטומטית
4. **Progress:** ההתקדמות נשמרת אוטומטית - אפשר להמשיך מאותו מקום
5. **Round-Robin:** ההודעות מתחלקות אוטומטית בין כל החשבונות המחוברים

---

## 🤝 תרומה

1. Fork the project
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 רישיון

MIT License

---

## 👨‍💻 מפתחים

- **גרסה:** 3.0.0
- **תאריך עדכון:** 12/01/2026
- **סטטוס:** ✅ מוכן לשימוש

---

## 🔗 קישורים

- [Telegram API Documentation](https://core.telegram.org/api)
- [Telethon Documentation](https://docs.telethon.dev/)
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [KivyMD Documentation](https://kivymd.readthedocs.io/)
- [Sentry](https://sentry.io)

---

**נבנה עם ❤️ בעברית**
