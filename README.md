# Telegram Backup - Android App

אפליקציית Android לגיבוי הודעות מטלגרם לערוץ.

## 🚀 בניית APK

יש לך **שתי אופציות** לבניית APK:

### אופציה 1: GitHub Actions (מומלץ! ⚡)

**מהיר, אוטומטי, ללא צורך להישאר בדפדפן**

#### הפעלה ידנית:
1. גש ל-[Actions → Build Android APK](https://github.com/Betsalelush/telegram-backup-android/actions/workflows/build-apk.yml)
2. לחץ **"Run workflow"**
3. בחר גרסה: `crash_test` / `basic` / `kivymd` / `full`
4. המתן ~30-40 דקות
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

**ארכיטקטורה**: arm64-v8a (טלפונים מ-2017+)

## 📱 דרישות

- Python 3.10+
- Kivy 2.2.1
- KivyMD
- Telethon
- OpenSSL

## 📄 תכונות

- גיבוי הודעות מטלגרם
- העברה לערוץ
- ממשק משתמש ידידותי
- תמיכה בקבצים

## 📄 רישיון

MIT License
