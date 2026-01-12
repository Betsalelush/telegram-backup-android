# Telegram Backup - Android App v3.0

אפליקציית Android מתקדמת לגיבוי הודעות מטלגרם לערוץ עם תמיכה ב-multi-account וארכיטקטורה מודולרית.

---

## 📊 סטטוס פרויקט

**גרסה נוכחית:** 3.0 (Build #60)  
**התקדמות:** 8/35 משימות (22.9%)  
**עודכן לאחרונה:** 12/01/2026

### ✅ הושלם
- Sentry Integration (DEBUG logging, breadcrumbs)
- Message Skip Handling (deleted, polls, games, service messages)
- Enhanced Logging
- AccountManager & ProgressManager
- Modular Architecture (app/ structure)
- LoginScreen Module

### 🔄 בעבודה
- BackupScreen Module
- TransferManager
- UI Screens

---

## ✨ תכונות

### 🔐 אבטחה ומעקב
- **Sentry Integration** - מעקב real-time אחר שגיאות
- **DEBUG Logging** - breadcrumbs מפורטים לכל פעולה
- **Error Tracking** - כל שגיאה נשלחת ל-Sentry עם context

### 📱 ניהול הודעות חכם
- **Message Skip Handling:**
  - ✅ הודעות מחוקות
  - ✅ Polls (לא נתמך)
  - ✅ Games (לא נתמך)
  - ✅ Service messages
  - ✅ הודעות ריקות
- **Detailed Logging** - סיבת דילוג מפורטת

### 🔄 העברת הודעות
- העברה כרונולוגית (ישן→חדש)
- תמיכה בכל סוגי הקבצים
- Rate limiting חכם
- המשכה אוטומטית
- שמירת התקדמות

### 🎨 ממשק משתמש
- Material Design (KivyMD)
- תמיכה בעברית מלאה
- התראות real-time
- 2FA support

---

## 🏗️ ארכיטקטורה

### מבנה מודולרי (v3.0)

```
telegram-backup-android/
├── app/                          # קוד האפליקציה
│   ├── main.py                  # Entry point (100 שורות)
│   ├── config.py                # הגדרות מרכזיות
│   ├── managers/                # Business Logic
│   │   ├── account_manager.py  # ניהול חשבונות (217 שורות)
│   │   ├── progress_manager.py # מעקב התקדמות (165 שורות)
│   │   └── transfer_manager.py # העברת הודעות
│   ├── screens/                 # UI Screens
│   │   ├── login_screen.py     # Login & Auth (195 שורות)
│   │   ├── backup_screen.py    # Backup UI
│   │   └── settings_screen.py  # Settings
│   ├── utils/                   # Helpers
│   │   └── logger.py           # Sentry logging (79 שורות)
│   └── kv/                      # UI Layouts
│       ├── login.kv
│       └── backup.kv
├── data/                         # נתונים
│   ├── sessions/                # Telegram sessions
│   ├── progress/                # Transfer progress
│   ├── accounts.json            # Multi-account data
│   └── transfers.json           # Transfer history
├── legacy/                       # קבצים ישנים
│   └── main_full.py            # (1,202 שורות - deprecated)
├── .github/workflows/           # CI/CD
│   └── build-apk.yml           # GitHub Actions
└── buildozer.spec              # Android build config
```

### יתרונות המבנה החדש

**לפני (main_full.py):**
- ❌ 1,202 שורות בקובץ אחד
- ❌ קשה לתחזק
- ❌ שגיאות indentation
- ❌ קשה להוסיף פיצ'רים

**אחרי (Modular):**
- ✅ 5+ קבצים קטנים (~100-200 שורות כל אחד)
- ✅ קל לתחזק
- ✅ פחות שגיאות
- ✅ קל להוסיף פיצ'רים
- ✅ Testing מבודד

---

## 🚀 בניית APK

### אופציה 1: GitHub Actions (מומלץ! ⚡)

**מהיר, אוטומטי, ללא צורך להישאר בדפדפן**

#### הפעלה ידנית:
1. [Actions → Build Android APK](https://github.com/Betsalelush/telegram-backup-android/actions/workflows/build-apk.yml)
2. לחץ **"Run workflow"**
3. בחר: `full` (גרסה מלאה)
4. המתן ~10-15 דקות
5. הורד APK מ-**Artifacts**

#### בנייה אוטומטית:
- כל `push` ל-`main*.py` → build אוטומטי
- התראה כש-build מוכן

### אופציה 2: Google Colab

1. פתח [build_apk_colab.ipynb](build_apk_colab.ipynb)
2. הרץ תאים 1→6
3. הורד APK

**זמן:** ~60 דקות  
⚠️ אל תסגור דפדפן!

---

## 📋 תוכנית פיתוח (MASTER_PLAN)

### Phase 0: הכנה ✅
- [x] Sentry Configuration
- [x] Project Cleanup
- [x] Message Skip Handling

### Phase 1: תשתית ✅
- [x] Hebrew Support
- [x] Directory Structure
- [x] Configuration Management

### Phase 2: Account Management (בעבודה)
- [x] AccountManager Class
- [x] LoginScreen Module
- [ ] Accounts Screen UI
- [ ] Login Flow Integration

### Phase 3: Transfer Management (הבא)
- [x] ProgressManager Class
- [ ] TransferManager Class
- [ ] BackupScreen Module
- [ ] Transfer Screen UI

### Phase 4-7: (מתוכנן)
- Multi-account UI
- Settings & Preferences
- Testing & Optimization
- Documentation

**פירוט מלא:** ראה artifacts/MASTER_PLAN.md

---

## 🔧 Refactoring Status

### Phase 1: LoginScreen ✅
**הושלם:** 12/01/2026
- ✅ `app/screens/login_screen.py` (195 שורות)
- ✅ send_code() + login() + disconnect()
- ✅ Breadcrumbs & error handling
- ✅ py_compile verified

### Phase 2: BackupScreen (בעבודה)
**משוער:** ~45 דקות
- [ ] `app/screens/backup_screen.py`
- [ ] start_backup() + stop_backup()
- [ ] Progress tracking
- [ ] UI updates

### Phase 3: TransferManager (הבא)
- [ ] `app/managers/transfer_manager.py`
- [ ] transfer_message()
- [ ] Rate limiting
- [ ] Smart delay

### Phase 4: New Main Entry
- [ ] `app/main.py` (100 שורות)
- [ ] Screen manager
- [ ] Minimal entry point

**פירוט מלא:** ראה artifacts/refactoring_plan.md

---

## 📊 Build History

| Build | Status | Notes |
|-------|--------|-------|
| #60 | 🔄 Running | **FULL FEATURED!** All improvements |
| #59 | ❌ Failed | Syntax errors |
| #57 | ✅ Success | Restored working version |
| #48 | ✅ Success | Last before improvements |

---

## 📋 דרישות

### סביבת פיתוח
- Python 3.10+
- Kivy 2.2.1
- KivyMD
- Telethon
- Sentry SDK

### Android
- **ארכיטקטורה:** arm64-v8a (2017+)
- **API Level:** 21+ (Android 5.0+)

---

## 🔧 הגדרה

### 1. Sentry (אופציונלי)
```python
# sentry_logger.py
sentry_sdk.init(
    dsn="YOUR_DSN_HERE",
    traces_sample_rate=1.0
)
```

### 2. Telegram API
1. קבל credentials מ-[my.telegram.org](https://my.telegram.org)
2. הזן ב-app בהרצה ראשונה

---

## 🎯 תכונות מתוכננות

### קצר טווח (שבוע)
- [ ] BackupScreen Module
- [ ] TransferManager
- [ ] Complete refactoring

### בינוני טווח (חודש)
- [ ] Multi-account UI
- [ ] AccountsScreen
- [ ] TransferScreen
- [ ] Settings Screen

### ארוך טווח (3 חודשים)
- [ ] Media albums support
- [ ] Export/Import settings
- [ ] Scheduled backups
- [ ] Cloud sync

---

## 🐛 דיווח באגים

1. בדוק [Issues](https://github.com/Betsalelush/telegram-backup-android/issues)
2. פתח issue עם:
   - תיאור הבעיה
   - צעדים לשחזור
   - Screenshots
   - Sentry error ID

---

## 📚 מסמכים נוספים

### Artifacts (במחשב המפתח)
- `MASTER_PLAN.md` - תוכנית מפורטת (35 משימות)
- `task.md` - מעקב משימות
- `refactoring_plan.md` - תוכנית refactoring
- `improvements_plan.md` - שיפורים שנוספו
- `project_status_analysis.md` - ניתוח מצב

### GitHub
- `GITHUB_ACTIONS.md` - מדריך CI/CD
- `COLAB_VS_GITHUB.md` - השוואת שיטות build

---

## 📄 רישיון

MIT License

---

## 🙏 תודות

- [Kivy](https://kivy.org/) - Python UI framework
- [KivyMD](https://kivymd.readthedocs.io/) - Material Design
- [Telethon](https://docs.telethon.dev/) - Telegram client
- [Sentry](https://sentry.io/) - Error tracking
- [Buildozer](https://buildozer.readthedocs.io/) - Android packaging

---

## 📞 קשר

**Repository:** [telegram-backup-android](https://github.com/Betsalelush/telegram-backup-android)  
**Issues:** [GitHub Issues](https://github.com/Betsalelush/telegram-backup-android/issues)  
**Sentry:** [bubababa.sentry.io](https://bubababa.sentry.io/issues/)

---

**עודכן:** 12/01/2026 03:07  
**גרסה:** 3.0 (Build #60)  
**סטטוס:** 🔄 Active Development
