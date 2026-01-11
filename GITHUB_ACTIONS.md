# 🚀 בניית APK עם GitHub Actions

## למה GitHub Actions?

- ✅ **לא צריך להישאר בדפדפן** - הבנייה רצה ברקע
- ✅ **אוטומציה מלאה** - push = בנייה אוטומטית
- ✅ **לוגים מלאים** - כל הלוגים נשמרים
- ✅ **מהיר יותר** - 30-40 דקות (במקום שעה ב-Colab)
- ✅ **אין timeout** - GitHub Actions לא מנתק

## איך להשתמש?

### אופציה 1: הפעלה ידנית (מומלץ)

1. **גש ל-GitHub**:
   [Actions → Build Android APK](https://github.com/Betsalelush/telegram-backup-android/actions/workflows/build-apk.yml)

2. **לחץ על "Run workflow"**

3. **בחר גרסה**:
   - `crash_test` - 🧪 טסט Sentry (מהיר! ~10 דקות)
   - `basic` - Kivy בלבד
   - `kivymd` - Kivy + KivyMD
   - `full` - הגרסה המלאה עם Telethon

4. **לחץ "Run workflow"** (הכפתור הירוק)

5. **המתן לסיום** - תקבל ✅ כשמוכן

6. **הורד את ה-APK**:
   - לחץ על הריצה (run)
   - גלול למטה ל-"Artifacts"
   - לחץ על `apk-[version]-[hash]` להורדה

### אופציה 2: בנייה אוטומטית

כל פעם ש**אתה עושה push** לקבצים הבאים, הבנייה תתחיל אוטומטית:
- `main*.py`
- `requirements*.txt`
- `.github/workflows/build-apk.yml`

הגרסה שתיבנה: `crash_test` (ברירת מחדל)

## 📊 מעקב אחר הבנייה

1. **גש ל-Actions** בגיטהאב
2. **לחץ על הריצה האחרונה**
3. **לחץ על "build"** כדי לראות את הלוגים
4. **עקוב בזמן אמת** - תראה כל שלב

## 🐛 איתור קריסות

### שלב 1: בנה crash_test
```bash
# הפעל ידנית עם version = crash_test
```

- התקן במכשיר
- לחץ "💥 Crash Me!"
- בדוק ב-[Sentry](https://bubababa.sentry.io/projects/test-crash-android/)
- **אם רואה את השגיאה ב-Sentry** = ✅ Sentry עובד!

### שלב 2: בנה full
```bash
# הפעל ידנית עם version = full
```

- התקן במכשיר
- נסה לפתוח
- **אם קורסת**:
  1. גש ל-[Sentry](https://bubababa.sentry.io)
  2. תראה את השגיאה המדויקת
  3. קרא את ה-stack trace
  4. תקן את הבעיה
  5. push ל-GitHub
  6. בנייה אוטומטית מחדש!

## 🔧 תיקון בעיות

### הבנייה נכשלה?

1. **גש ל-Actions**
2. **לחץ על הריצה הכושלת**
3. **לחץ על "build"**
4. **קרא את הלוגים** - תראה בדיוק איפה נכשל
5. **תקן ו-push מחדש**

### APK לא עובד?

1. **בדוק ב-Sentry** - יש שם stack trace מלא
2. **קרא את הלוגים** של הבנייה
3. **תקן את הבעיה**
4. **push ל-GitHub** - בנייה אוטומטית!

## 📝 גרסאות זמינות

| גרסה | תיאור | זמן בנייה | קבצים |
|------|-------|-----------|-------|
| `crash_test` | טסט Sentry עם כפתור קריסה | ~10 דקות | `main_crash_test.py` + `requirements_crash_test.txt` |
| `basic` | Kivy בלבד | ~15 דקות | `main_test_basic.py` + `requirements_basic.txt` |
| `kivymd` | Kivy + KivyMD | ~20 דקות | `main_test_kivymd.py` + `requirements_kivymd.txt` |
| `full` | הגרסה המלאה + Telethon | ~30-40 דקות | `main_full.py` + `requirements_full.txt` |

## 🎯 המלצה

1. **התחל עם `crash_test`** - וודא ש-Sentry עובד
2. **אחר כך `full`** - בנה את הגרסה המלאה
3. **אם קורסת** - בדוק ב-Sentry ותקן
4. **push התיקון** - בנייה אוטומטית מחדש

---

**זמן חיסכון**: במקום להישאר בדפדפן שעה - עשה push ולך לישון! 😴
