# הגדרת Sentry

## סקירה כללית
האפליקציה משולבת עם Sentry לתיעוד שגיאות אוטומטי. יש להגדיר שני דברים:

1. **DSN** - לשליחת שגיאות מהאפליקציה ל-Sentry
2. **Auth Token** - לבדיקת שגיאות דרך API (לסקריפטים)

## הגדרת DSN (Data Source Name)

DSN נדרש כדי שהאפליקציה תשלח שגיאות ל-Sentry.

### איך להשיג DSN:
1. היכנס ל-[Sentry.io](https://sentry.io)
2. בחר את הארגון שלך
3. לך ל-Settings → Projects → בחר את הפרויקט שלך
4. לך ל-Client Keys (DSN)
5. העתק את ה-DSN (נראה כך: `https://<key>@<org>.ingest.sentry.io/<project>`)

### הגדרת DSN:

**Windows (PowerShell):**
```powershell
$env:SENTRY_DSN="https://<your-key>@<org>.ingest.sentry.io/<project>"
```

**Linux/Mac:**
```bash
export SENTRY_DSN="https://<your-key>@<org>.ingest.sentry.io/<project>"
```

**Android (Buildozer):**
הוסף ל-`buildozer.spec`:
```ini
[app]
android.env.SENTRY_DSN = https://<your-key>@<org>.ingest.sentry.io/<project>
```

## הגדרת Auth Token

Auth Token נדרש לסקריפטים כמו `check_sentry_logs.py` שמביאים מידע על שגיאות דרך API.

### איך להשיג Auth Token:
1. היכנס ל-[Sentry.io](https://sentry.io)
2. לך ל-Settings → Account → Auth Tokens
3. צור token חדש עם הרשאות: `project:read`, `org:read`
4. העתק את ה-token

### הגדרת Auth Token:

**Windows (PowerShell):**
```powershell
$env:SENTRY_AUTH_TOKEN="51147bc0eec811f0b99a065cb2cd158a"
```

**Linux/Mac:**
```bash
export SENTRY_AUTH_TOKEN="51147bc0eec811f0b99a065cb2cd158a"
```

## בדיקת הגדרות

לאחר הגדרת ה-DSN וה-Auth Token, תוכל לבדוק שהכל עובד:

1. **בדיקת DSN** - הרץ את האפליקציה ושגיאה תישלח ל-Sentry
2. **בדיקת Auth Token** - הרץ:
   ```bash
   python check_sentry_logs.py
   ```

## הערות חשובות

- **DSN** ו-**Auth Token** הם שני דברים שונים:
  - DSN = לשליחת שגיאות מהאפליקציה
  - Auth Token = לקריאת מידע על שגיאות דרך API
  
- ה-DSN לא צריך להיות ב-`.gitignore` כי הוא לא רגיש (רק מפתח ציבורי)
- ה-Auth Token רגיש - אל תחלוק אותו!

## הגדרות נוספות

ניתן להגדיר גם:
- `SENTRY_SAMPLE_RATE` - אחוז ה-traces לשליחה (ברירת מחדל: 1.0 = 100%)
- `APP_ENV` - סביבת הפעלה (production/staging/development)
