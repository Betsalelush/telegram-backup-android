# Telegram Backup - Android App v3.0

אפליקציית Android מתקדמת לגיבוי הודעות מטלגרם לערוץ עם תמיכה ב-multi-account.

---

## 📊 סטטוס פרויקט

**גרסה נוכחית:** 3.0 (Build #60 Running, Build #61 Queued)  
**התקדמות:** 11/35 משימות (31.4%)  
**עודכן לאחרונה:** 12/01/2026 03:25

### ⚠️ מצב Refactoring

**סטטוס:** 🔄 בתהליך (חלקי)

**מה הושלם:**
- ✅ יצירת מודולים חדשים (LoginScreen, BackupScreen, TransferManager)
- ✅ העברת לוגיקה למודולים
- ✅ main.py חדש (120 שורות)

**מה חסר:**
- ❌ KV files (UI layouts)
- ❌ חיבור UI למודולים
- ❌ Helper functions במודולים
- ❌ בדיקות integration

**הקובץ הפעיל:** `main_full.py` (1,202 שורות) - **כל הפונקציות שמורות!**

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

### מבנה נוכחי (Hybrid)

```
telegram-backup-android/
├── main_full.py                 # 🔴 ACTIVE - כל הפונקציות (1,202 שורות)
├── app/                         # 🟡 IN PROGRESS - מודולים חדשים
│   ├── main.py                 # Entry point חדש (120 שורות)
│   ├── config.py               # הגדרות (85 שורות)
│   ├── managers/
│   │   ├── account_manager.py  # ✅ (217 שורות)
│   │   ├── progress_manager.py # ✅ (165 שורות)
│   │   └── transfer_manager.py # ✅ (173 שורות)
│   ├── screens/
│   │   ├── login_screen.py     # ⚠️ לוגיקה בלבד (195 שורות)
│   │   └── backup_screen.py    # ⚠️ לוגיקה בלבד (370 שורות)
│   └── utils/
│       └── logger.py           # ✅ (79 שורות)
├── data/
│   ├── sessions/               # Telegram sessions
│   └── progress/               # Transfer progress
└── .github/workflows/
    └── build-apk.yml          # CI/CD
```

### מה חסר למודולים:

```
app/
├── kv/                    # ❌ צריך ליצור
│   ├── login.kv          # UI for LoginScreen
│   └── backup.kv         # UI for BackupScreen
├── utils/                 # ⚠️ חלקי
│   ├── clipboard.py      # ❌ paste_to_field()
│   └── helpers.py        # ❌ update_progress(), etc.
└── screens/               # ⚠️ חסר UI
    ├── login_screen.py   # יש לוגיקה, חסר KV
    └── backup_screen.py  # יש לוגיקה, חסר KV
```

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

**Build #60:** 🔄 Running - עם main_full.py (כל הפונקציות!)  
**Build #61:** ⏳ Queued - עם app/main.py (ארכיטקטורה חדשה)

---

## 📋 תוכנית פיתוח

### Phase 0-1: הכנה ותשתית ✅
- [x] Sentry Configuration
- [x] Project Cleanup
- [x] Directory Structure
- [x] Configuration Management

### Phase 2: Refactoring (בתהליך) 🔄
- [x] LoginScreen Module (לוגיקה)
- [x] BackupScreen Module (לוגיקה)
- [x] TransferManager Module
- [x] New Main Entry Point
- [ ] KV Files (UI)
- [ ] Helper Functions
- [ ] Integration Testing

### Phase 3-7: (מתוכנן)
- [ ] Multi-account UI
- [ ] Settings & Preferences
- [ ] Testing & Optimization
- [ ] Documentation

---

## 🔧 מצב נוכחי

### ✅ מה עובד (main_full.py):
- Login flow (send_code, login, 2FA)
- Backup functions
- Progress tracking
- Rate limiting
- Message skip handling
- Sentry logging
- **כל הפונקציות!**

### 🔄 מה בתהליך (app/):
- מודולים עם לוגיקה
- ללא UI (KV files)
- לא מחובר למסכים
- צריך השלמה

---

## 📊 Build History

| Build | Status | Version | Notes |
|-------|--------|---------|-------|
| #61 | ⏳ Queued | app/main.py | ארכיטקטורה חדשה (חלקי) |
| #60 | 🔄 Running | main_full.py | **כל הפונקציות!** |
| #59 | ❌ Failed | - | Syntax errors |
| #57 | ✅ Success | main_full.py | Restored version |

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

## ⚠️ הערות חשובות

### Refactoring Status:
1. **main_full.py עדיין פעיל** - כל הפונקציות שמורות
2. **המודולים החדשים** - יש לוגיקה אבל לא UI
3. **Build #60** - משתמש ב-main_full.py (מומלץ!)
4. **Build #61** - ינסה app/main.py (עלול להיכשל)

### המלצה:
- **להשתמש ב-Build #60** (main_full.py) - עובד!
- **להמשיך Refactoring** בהדרגה
- **לא למחוק main_full.py** עד שהמודולים מוכנים

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

### Artifacts
- `MASTER_PLAN.md` - תוכנית מפורטת
- `task.md` - מעקב משימות
- `refactoring_verification.md` - אימות Refactoring

---

## 📄 רישיון

MIT License

---

**עודכן:** 12/01/2026 03:25  
**גרסה:** 3.0  
**סטטוס:** 🔄 Refactoring In Progress  
**Build פעיל:** #60 (main_full.py)
