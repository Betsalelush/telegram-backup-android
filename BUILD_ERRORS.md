# 🐛 תיעוד שגיאות Build - Telegram Backup Android

**עודכן:** 12/01/2026  
**גרסה:** 3.0.0

---

## 📊 סיכום

**סה"כ בניות:** 80  
**בניות מוצלחות:** 0  
**בניות נכשלות:** 80  
**שגיאה עיקרית:** pyjnius - טיפוס `long` לא נתמך ב-Python 3

---

## ❌ שגיאה עיקרית: pyjnius 'long' Type

### הבעיה
```
jnius/jnius_conversion.pxi:544:12: undeclared name not builtin: long
```

**סיבה:**  
- `pyjnius 1.5.0` משתמש בטיפוס `long` שהוסר ב-Python 3
- צריך להחליף `long` ל-`int`

### ניסיונות תיקון (כולם נכשלו)

#### ניסיון 1: sed על קובץ אחד
```bash
sed -i 's/long/int/g' jnius_utils.pxi
```
**תוצאה:** ❌ לא מספיק - יש קבצים נוספים

#### ניסיון 2: sed על שני קבצים
```bash
sed -i 's/long/int/g' jnius_utils.pxi jnius_conversion.pxi
```
**תוצאה:** ❌ לא תפס את כל המופעים

#### ניסיון 3: sed גלובלי
```bash
find jnius -type f \( -name "*.pxi" -o -name "*.pyx" \) -exec sed -i 's/\blong\b/int/g' {} +
```
**תוצאה:** ❌ שבר C types (`ctypedef long`)

#### ניסיון 4: sed ספציפי
```bash
sed -i \
  -e 's/isinstance(\([^,]*\), long)/isinstance(\1, int)/g' \
  -e 's/, long)/, int)/g' \
  -e 's/(long)/(int)/g' \
  -e 's/\[long\]/[int]/g'
```
**תוצאה:** ❌ עדיין לא תפס את כל המופעים

---

## 🔍 שגיאות נוספות שתוקנו

### 1. Cython Language Level
**שגיאה:**
```
Cython language level not set
```

**תיקון:**
```yaml
export CYTHON_LANGUAGE_LEVEL=3
```
**סטטוס:** ✅ תוקן

### 2. APK לא נמצא
**שגיאה:**
```
Error: No files found with the provided path: bin/*.apk
```

**תיקון:**
```yaml
path: |
  bin/*.apk
  .buildozer/android/platform/build-*/dists/*/bin/*.apk
  **/*.apk
```
**סטטוס:** ✅ תוקן

### 3. pip download - קובץ wheel במקום source
**שגיאה:**
```
tar: Cannot open: No such file or directory
```

**תיקון:**
```bash
pip download pyjnius==1.5.0 --no-deps --dest /tmp --no-binary :all:
```
**סטטוס:** ✅ תוקן

### 4. cd: too many arguments
**שגיאה:**
```
cd: too many arguments
```

**תיקון:**
```bash
extracted_dir=$(find . -maxdepth 1 -type d -name 'pyjnius-*' | head -n 1)
cd "$extracted_dir"
```
**סטטוס:** ✅ תוקן

---

## 💡 פתרונות אפשריים

### אופציה 1: גרסה חדשה של pyjnius
```bash
pip install pyjnius>=1.6.0
```
**סטטוס:** לא נבדק

### אופציה 2: Fork מתוקן
```bash
pip install git+https://github.com/user/pyjnius-python3-fix.git
```
**סטטוס:** לא נבדק

### אופציה 3: Patch מקיף יותר
- לזהות את כל המופעים של `long`
- להחליף רק במקומות הנכונים
- לא לשבור C types

**סטטוס:** בתהליך

---

## 📈 היסטוריית בניות

| בנייה | תאריך | שגיאה | ניסיון תיקון |
|-------|-------|-------|--------------|
| #1-5 | 11/01 | Cython | - |
| #6 | 11/01 | APK לא נמצא | Cython ✅ |
| #7-76 | 11/01 | שונות | ניסיונות שונים |
| #77 | 12/01 | jnius_conversion.pxi | sed קובץ אחד |
| #78 | 12/01 | שורה 544 | sed שני קבצים |
| #79 | 12/01 | Syntax error ctypedef | sed גלובלי |
| #80 | 12/01 | שורה 544 שוב | sed ספציפי |

---

## 🎯 מסקנות

1. **pyjnius 1.5.0 לא תומך ב-Python 3** - זו הבעיה המרכזית
2. **sed לא מספיק** - צריך פתרון יותר מתוחכם
3. **צריך גרסה חדשה** - או fork מתוקן

---

## 📝 הערות

- כל השגיאות מתועדות ב-GitHub Actions logs
- ניסיונות התיקון נשמרים ב-git history
- הקוד עצמו תקין - הבעיה רק ב-build

---

**סטטוס נוכחי:** ⚠️ ממתין לפתרון לבעיית pyjnius
