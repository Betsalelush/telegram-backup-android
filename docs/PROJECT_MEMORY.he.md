# זיכרון פרויקט - Telegram Backup Android
*מסמך זה הוא המקור היחיד והמעודכן ביותר לכל המידע על הפרויקט.*

**עודכן בתאריך:** 14/01/2026
**גרסה:** 3.1 (Stable Candidate)

---

## 1. 🚦 סטטוס נוכחי
*   **בניית APK:** ✅ הושלמה בהצלחה (לאחר תיקוני תאימות מורכבים ב-`pyjnius` ו-`Cython`).
*   **סנכרון GitHub:** ✅ מלא. כל הקבצים הישנים נמחקו, המבנה נקי.
*   **פונקציונליות:** ✅ עובדת (התחברות, העברה, הורדה, לוגים).
*   **בדיקות:** ממתין לאימות סופי על מכשיר פיזי (Android Arm64).

---

## 2. 📱 תכונות ופונקציונליות (Features)
האפליקציה מאפשרת ניהול וגיבוי של חשבונות טלגרם עם דגש על אוטומציה ונוחות.

### ✨ דברים חדשים בגרסה 3.1:
1.  **מצבי העברה (Transfer Modes):**
    *   **Forward:** העברה רגילה (עם קרדיט למקור).
    *   **Copy:** העתקת תוכן (ללא קרדיט).
    *   **Download & Upload:** הורדה למכשיר והעלאה מחדש (מנתק קשר למקור לחלוטין, איטי יותר אך "נקי").
2.  **ממשק משתמש (UI) משודרג:** התאמה מלאה ל-**KivyMD 2.0.0** עם עיצוב Material You עדכני.
3.  **לוגים חיים:** מסך לוגים ייעודי בתצורת "טרמינל" למעקב אחר פעולות בזמן אמת.
4.  **ניהול מתקדם:** בחירת מזהה הודעה (Message ID) להתחלה, סינון סוגי קבצים.

---

## 3. 🛠️ ארכיטקטורה ומבנה קוד
הפרויקט בנוי בארכיטקטורת **Managers & Screens** כדי להפריד בין הלוגיקה לתצוגה.

### 📂 מבנה התיקיות (מעודכן ונקי)
```text
telegram-backup-android/
├── app/
│   ├── main.py            # נקודת הכניסה לאפליקציה
│   ├── config.py          # הגדרות וקבועים (כולל Sentry DSN)
│   ├── managers/          # לוגיקה עסקית
│   │   ├── account_manager.py  # ניהול Sessions והתחברות
│   │   ├── transfer_manager.py # לוגיקה של העברת הודעות
│   │   └── progress_manager.py # ניהול מד התקדמות
│   ├── screens/           # מסכי ממשק (UI)
│   │   ├── action_screen.py    # תפריט ראשי
│   │   ├── accounts_screen.py  # ניהול חשבונות
│   │   └── transfer_screen.py  # הגדרות והרצת העברה
│   └── utils/             # כלי עזר
│       ├── logger.py           # מערכת לוגים
│       └── helpers.py          # פונקציות עזר כלליות
├── buildozer.spec         # הגדרות בנייה לאנדרואיד
├── requirements_full.txt  # תלויות פייתון מדויקות
└── README.md              # תיעוד למשתמש
```

---

## 4. 🧠 לקחים טכניים ופתרונות (Critical Knowledge)
*סעיף זה קריטי למניעת שגיאות בעתיד - נא לקרוא לפני כל שינוי בקונפיגורציה!*

### 🔧 תיקוני בנייה (Buildozer/Android)
1.  **Cython ו-Pyjnius:** נתקלנו בבעיות תאימות קשות בין גרסאות חדשות.
    *   **הפתרון:** שימוש ב-patch ידני או גרסאות ספציפיות ב-`requirements`. לא לשדרג ספריות אלו ללא בדיקה מעמיקה!
    *   בעיית `long` vs `int` ב-Cython 3 נפתרה על ידי התאמות בקוד המקור או שינמוך גרסאות במקרה הצורך.
2.  **Sentry:** השילוב דורש את הספריות `exceptiongroup`, `asyncgui`, `asynckivy` בקובץ `buildozer.spec` כדי למנוע קריסה בטעינה.
3.  **הרשאות:** חובה לכלול `WRITE_EXTERNAL_STORAGE` ו-`READ_EXTERNAL_STORAGE` כדי שהאפליקציה תוכל לשמור קבצים.

### 🎨 KivyMD 2.0.0 (Master Branch)
אנו משתמשים בגרסת הפיתוח של KivyMD. יש לה שינויים משמעותיים מהגרסה היציבה:
*   **כפתורים:** שימוש ב-`MDButton` (ולא `MDRectangleFlatButton`). עיצוב "Stadium" דורש הגדרת רדיוס ידנית.
*   **סרגל עליון:** `MDTopAppBar` דורש מבנה ספציפי (`LeadingButtonContainer`, `Title`, `TrailingButtonContainer`).
*   **ערכות נושא:** החלפת נושא (Dark/Light) דורשת עדכון ידני של רקע המסכים (`md_bg_color`), זה לא קורה אוטומטית בכל הרכיבים.
*   **לוגים:** בשימוש ב-Kivy רגיל (`TextInput`), יש להשתמש ב-`foreground_color` ולא `text_color` למניעת קריסות.

### 🐞 באגים ידועים שנפתרו
*   **Widget Parent Error:** שגיאה נפוצה ב-Kivy כשמנסים להוסיף כפתור שכבר קיים. נפתר על ידי בדיקת `if not parent` או ניקוי ה-Layout לפני הוספה מחדש.
*   **Paste Binding:** בעיה בכפתורי "הדבק". חובה להשתמש ב-`lambda x, f=field: ...` כדי לשמור על הקשר (Scope) הנכון בלולאות.

---

## 5. 🚀 תהליך בנייה ופריסה (CI/CD)

### GitHub Actions - בנייה אוטומטית
האפליקציה נבנית אוטומטית באמצעות GitHub Actions.

**קובץ Workflow:** `.github/workflows/build-apk.yml`

#### טריגרים:
- ✅ **Push ל-master** - כל push מפעיל בנייה אוטומטית
- ✅ **הפעלה ידנית** - דרך GitHub UI (`workflow_dispatch`)

#### תהליך הבנייה:
1. 📥 משיכת קוד מ-Repository
2. 🐳 הרצת Buildozer ב-Docker Container (Kivy Official Image)
3. 🔨 בנייה של APK (Android Debug)
4. 📤 העלאת APK כ-Artifact (שמור 30 יום)
5. 📋 במקרה של כשלון - העלאת לוג הבנייה

#### הורדת APK:
1. לך ל-**GitHub Actions** tab
2. בחר את ה-Run האחרון
3. גלול ל-**Artifacts** → הורד `telegram-backup-v3.0-apk`

---

## 6. 🔧 כלי ניפוי באגים (Debug Tools)

התיקייה `debug_tools/` מכילה **19 סקריפטים** לניפוי ובדיקת שגיאות.

⚠️ **אזהרת אבטחה:** הקבצים מכילים **API Tokens** (GitHub, Sentry) ולכן התיקייה ב-`.gitignore`.

### 🔴 כלי Sentry (5 סקריפטים):
- `check_sentry_logs.py` - בדיקה בסיסית של שגיאות
- `fetch_sentry_comprehensive.py` - ניתוח מקיף ומפורט
- `fetch_sentry_debug.py` - דיבוג issues ספציפיים
- `fetch_sentry_trace.py` - משיכת stack traces
- `fetch_sentry_trace_v2.py` - גרסה משודרגת

### 🟢 כלי GitHub (4 סקריפטים):
- `check_artifacts_api.py` - בדיקת APK artifacts
- `check_github_logs.py` - לוגים מ-GitHub Actions
- `debug_gh_api.py` - דיבוג workflows
- `fetch_gh_logs.py` - משיכת לוגים מפורטת

### 🔵 כלי נוספים:
- `test_app_integrity.py` - בדיקת תקינות קבצים
- `verify_changes.py` - אימות שינויים
- `syntax_check.py` - בדיקת תחביר Python

**שימוש:** הרץ את הסקריפט הרלוונטי כשצריך לבדוק שגיאות או סטטוס בנייה.

---

## 7. 📦 תהליך עדכון גרסה

כאשר מוכנים לשחרר גרסה חדשה:

### שלב 1: עדכון מספר גרסה
עדכן ב-**3 מקומות**:
1. `buildozer.spec` → שדה `version`
2. `.github/workflows/build-apk.yml` → שם ה-Artifact
3. `docs/PROJECT_MEMORY.he.md` → גרסה נוכחית (בראש)

### שלב 2: Commit ו-Push
```bash
git add .
git commit -m "Release v3.2: [תיאור השינויים]"
git push origin master
```

### שלב 3: בנייה אוטומטית
- GitHub Actions יבנה את ה-APK אוטומטית
- זמן בנייה: ~5-10 דקות (עם cache)

### שלב 4: הורדה ובדיקה
- הורד את ה-APK מ-Artifacts
- התקן על מכשיר פיזי
- בדוק פונקציונליות

---

## 8. 📝 משימות להמשך (Todo)
1.  [ ] **בדיקה פיזית:** התקנת ה-APK על מכשיר אנדרואיד אמיתי ואימות כל הפיצ'רים (במיוחד הרשאות כתיבה לאחסון).
2.  [ ] **בדיקת ביצועים:** העברת כמות גדולה של הודעות (1000+) לבדיקת יציבות זיכרון.
3.  [ ] **QR Login:** שיפור הממשק להצגת קוד ה-QR (כרגע מודפס ללוג או מוצג בסיסי).

---
*מסמך זה מחליף את כל קבצי הזיכרון והסטטוס הקודמים.*
