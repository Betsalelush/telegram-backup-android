# 📱 Telegram Backup Android - v3.0

אפליקציית אנדרואיד מודרנית להעברת הודעות בין ערוצי טלגרם עם תמיכה בריבוי חשבונות.

---

## ✨ תכונות

### 🎯 תכונות עיקריות
- ✅ **Multi-Account Support** - תמיכה בריבוי חשבונות טלגרם
- ✅ **Round-Robin Distribution** - חלוקת הודעות בין חשבונות
- ✅ **Smart Rate Limiting** - מניעת חסימה (20 הודעות/דקה)
- ✅ **FloodWait Handling** - טיפול אוטומטי בהגבלות טלגרם
- ✅ **Progress Tracking** - שמירת התקדמות והמשך מנקודת עצירה
- ✅ **3 Transfer Methods** - Forward / Send Message / Download & Upload

### 📱 ממשק משתמש
- ✅ **3 מסכים** - חשבונות, פעולות, העברות
- ✅ **ניהול חשבונות** - הוספה, מחיקה, התחברות
- ✅ **תצוגת התקדמות** - מעקב בזמן אמת
- ✅ **Sentry Integration** - תיעוד שגיאות

### 🔧 תכונות טכניות
- ✅ **ארכיטקטורה מודולרית** - קוד מאורגן ונקי
- ✅ **Async Operations** - ביצועים מהירים
- ✅ **Session Management** - שמירת התחברות
- ✅ **File Type Filtering** - בחירת סוגי קבצים

---

## 📁 מבנה הפרויקט

```
telegram-backup-android/
├── app/                      # קוד האפליקציה
│   ├── config.py            # הגדרות
│   ├── main.py              # Entry point
│   ├── managers/            # מנהלי לוגיקה
│   │   ├── account_manager.py
│   │   ├── progress_manager.py
│   │   └── transfer_manager.py
│   ├── screens/             # מסכי UI
│   │   ├── accounts_screen.py
│   │   ├── action_screen.py
│   │   └── transfer_screen.py
│   └── utils/               # כלים עזר
│       ├── logger.py
│       └── helpers.py
├── tests/                   # בדיקות
├── .github/workflows/       # GitHub Actions
├── main.py                  # Entry point ראשי
├── buildozer.spec          # הגדרות build
├── requirements_full.txt   # תלויות
└── README.md               # המסמך הזה
```

---

## 🚀 התקנה

### דרישות
- Python 3.8+
- Buildozer (לבניית APK)
- Telegram API credentials (מ-my.telegram.org)

### התקנת תלויות
```bash
pip install -r requirements_full.txt
```

---

## 📖 שימוש

### הרצה מקומית (Desktop)
```bash
python main.py
```

### בניית APK
```bash
buildozer android debug
```

### GitHub Actions
הפרויקט כולל workflow אוטומטי לבניית APK:
- Push ל-master → בנייה אוטומטית
- APK זמין ב-Actions artifacts

---

## 🎨 מסכים

### 1. מסך חשבונות
- הצגת רשימת חשבונות
- הוספת חשבון חדש
- מחיקת חשבון
- התחברות/ניתוק

### 2. מסך פעולות
- תפריט ראשי
- ניווט למסכים

### 3. מסך העברות
- בחירת ערוצים
- בחירת חשבונות
- התחלה/עצירה
- תצוגת התקדמות

---

## 🔧 הגדרות

### Sentry (אופציונלי)
ערוך את `app/config.py`:
```python
SENTRY_DSN = "your-sentry-dsn-here"
```

### Rate Limiting
ניתן לשנות ב-`app/config.py`:
```python
MAX_MESSAGES_PER_MINUTE = 20  # מספר הודעות מקסימלי לדקה
SMART_DELAY_MIN = 2           # השהיה מינימלית (שניות)
SMART_DELAY_MAX = 8           # השהיה מקסימלית (שניות)
```

---

## 📊 סטטיסטיקות

- **קבצי Python:** 18
- **פונקציות:** 55
- **מסכים:** 3
- **בדיקות:** 9
- **שורות קוד:** ~2,000

---

## 🧪 בדיקות

הרצת בדיקות:
```bash
pytest tests/
```

בדיקות זמינות:
- `test_account_manager.py` - בדיקות ניהול חשבונות
- `test_progress_manager.py` - בדיקות התקדמות

---

## 📝 תיעוד נוסף

- **תוכנית_עבודה_מלאה.md** - תוכנית פיתוח מפורטת
- **MASTER_PLAN.md** - ארכיטקטורה ותכנון
- **BUILD_ERRORS.md** - תיעוד שגיאות build

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

---

## ⚠️ הערות חשובות

1. **API Credentials:** צריך להשיג API ID ו-API Hash מ-my.telegram.org
2. **Rate Limits:** טלגרם מגביל 20 הודעות לדקה - האפליקציה מטפלת בזה אוטומטית
3. **FloodWait:** במקרה של חסימה זמנית, האפליקציה ממתינה אוטומטית
4. **Progress:** ההתקדמות נשמרת אוטומטית - אפשר להמשיך מאותו מקום

---

**נבנה עם ❤️ בעברית**
