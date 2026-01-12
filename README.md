# Telegram Backup - Android App

אפליקציית Android לגיבוי הודעות מטלגרם לערוץ עם תמיכה ב-multi-account.

## ✨ תכונות

### 🔐 אבטחה ומעקב
- **Sentry Integration** - מעקב אחר שגיאות ו-crashes בזמן אמת
- **DEBUG Logging** - breadcrumbs מפורטים לכל פעולה
- **Error Tracking** - כל שגיאה נשלחת ל-Sentry עם context מלא

### 📱 ניהול הודעות חכם
- **Message Skip Handling** - דילוג אוטומטי על:
  - הודעות מחוקות
  - Polls (לא נתמך)
  - Games (לא נתמך)
  - Service messages (משתמש הצטרף וכו')
  - הודעות ריקות
- **Detailed Logging** - סיבת דילוג מפורטת לכל הודעה

### 🔄 העברת הודעות
- העברה כרונולוגית (ישן→חדש)
- תמיכה בכל סוגי הקבצים (תמונות, וידאו, מסמכים)
- Rate limiting חכם
- המשכה אוטומטית אחרי הפסקה
- שמירת התקדמות

### 🎨 ממשק משתמש
- ממשק Material Design (KivyMD)
- תמיכה בעברית מלאה
- התראות סטטוס בזמן אמת
- 2FA support

### 🏗️ ארכיטקטורה מודולרית (חדש!)
```
app/
├── main.py              # Entry point
├── config.py            # הגדרות מרכזיות
├── managers/
│   ├── account_manager.py    # ניהול חשבונות
│   ├── progress_manager.py   # מעקב התקדמות
│   └── transfer_manager.py   # העברת הודעות
├── screens/             # מסכי UI
├── utils/
│   └── logger.py        # Sentry logging
└── kv/                  # UI layouts
```

---

## 🚀 בניית APK

יש לך **שתי אופציות** לבניית APK:

### אופציה 1: GitHub Actions (מומלץ! ⚡)

**מהיר, אוטומטי, ללא צורך להישאר בדפדפן**

#### הפעלה ידנית:
1. גש ל-[Actions → Build Android APK](https://github.com/Betsalelush/telegram-backup-android/actions/workflows/build-apk.yml)
2. לחץ **"Run workflow"**
3. בחר גרסה: `crash_test` / `basic` / `kivymd` / `full`
4. המתן ~10-15 דקות
5. הורד את ה-APK מ-**Artifacts**

#### בנייה אוטומטית:
- כל `push` לקבצים `main*.py` או `requirements*.txt` יפעיל בנייה אוטומטית
- תקבל התראה כש-build מוכן

📖 **מדריך מפורט**: [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md)

---

### אופציה 2: Google Colab (חלופה)

**שליטה מלאה, טוב לדיבאג**

1. פתח את [build_apk_colab.ipynb](build_apk_colab.ipynb) ב-Google Colab
2. הרץ את כל התאים לפי הסדר (1→6)
3. הורד את ה-APK

**זמן בנייה**: ~60 דקות  
⚠️ **חשוב**: אל תסגור את הדפדפן במהלך הבנייה!

---

### 🤔 לא בטוח איזו אופציה לבחור?

קרא את [COLAB_VS_GITHUB.md](COLAB_VS_GITHUB.md) - השוואה מפורטת בין שתי השיטות

**TL;DR**: GitHub Actions מהיר יותר וקל יותר. Colab טוב כגיבוי או לדיבאג.

---

## 📋 דרישות

### סביבת פיתוח:
- Python 3.10+
- Kivy 2.2.1
- KivyMD
- Telethon
- Sentry SDK

### Android:
- **ארכיטקטורה**: arm64-v8a (טלפונים מ-2017+)
- **Android API**: 21+ (Android 5.0+)

---

## 🔧 הגדרה

### 1. Sentry (אופציונלי)
אם רוצה מעקב אחר שגיאות:
1. צור חשבון ב-[Sentry.io](https://sentry.io)
2. קבל DSN
3. עדכן ב-`sentry_logger.py`

### 2. Telegram API
1. קבל API credentials מ-[my.telegram.org](https://my.telegram.org)
2. הזן ב-app בעת הרצה ראשונה

---

## 📊 מבנה הפרויקט

```
telegram-backup-android/
├── app/                    # קוד האפליקציה
│   ├── main.py            # Entry point
│   ├── config.py          # הגדרות
│   ├── managers/          # Business logic
│   ├── screens/           # UI screens
│   ├── utils/             # Helpers
│   └── kv/                # UI layouts
├── data/                   # נתונים
│   ├── sessions/          # Telegram sessions
│   └── progress/          # Transfer progress
├── legacy/                 # קבצים ישנים
├── .github/workflows/      # GitHub Actions
└── buildozer.spec         # Android build config
```

---

## 🎯 תכונות מתוכננות

- [ ] Multi-account support מלא
- [ ] UI מודרני עם Material Design 3
- [ ] תמיכה ב-media albums
- [ ] Export/Import של הגדרות
- [ ] Scheduled backups
- [ ] Cloud sync

ראה [MASTER_PLAN.md](https://github.com/Betsalelush/telegram-backup-android/blob/master/.gemini/antigravity/brain/56c5c8b6-c38e-49fd-bb59-884423db661c/MASTER_PLAN.md) לתוכנית מפורטת.

---

## 🐛 דיווח על באגים

אם מצאת באג:
1. בדוק ב-[Issues](https://github.com/Betsalelush/telegram-backup-android/issues)
2. פתח issue חדש עם:
   - תיאור הבעיה
   - צעדים לשחזור
   - Screenshots (אם רלוונטי)
   - Sentry error ID (אם יש)

---

## 📄 רישיון

MIT License

---

## 🙏 תודות

- [Kivy](https://kivy.org/) - Python UI framework
- [KivyMD](https://kivymd.readthedocs.io/) - Material Design components
- [Telethon](https://docs.telethon.dev/) - Telegram client library
- [Sentry](https://sentry.io/) - Error tracking
- [Buildozer](https://buildozer.readthedocs.io/) - Android packaging

---

**עודכן לאחרונה**: 12/01/2026  
**גרסה**: 3.0 (Build #60)
