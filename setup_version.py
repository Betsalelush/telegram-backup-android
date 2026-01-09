import os
import shutil

# ⚙️ בחר גרסה כאן:
VERSION = "basic"  # שנה ל: "basic", "kivymd", או "full"

# שימוש בנתיב הנוכחי במקום נתיב Colab
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# מיפוי גרסאות
version_map = {
    "basic": {
        "main": "main_test_basic.py",
        "requirements": "requirements_basic.txt",
        "title": "Test Basic",
        "package": "testbasic"
    },
    "kivymd": {
        "main": "main_test_kivymd.py",
        "requirements": "requirements_kivymd.txt",
        "title": "Test KivyMD",
        "package": "testkivymd"
    },
    "full": {
        "main": "main.py",
        "requirements": "requirements.txt",
        "title": "Telegram Backup",
        "package": "telegrambackup"
    }
}

if VERSION not in version_map:
    print(f"❌ גרסה לא חוקית: {VERSION}")
    print("בחר: basic, kivymd, או full")
else:
    config = version_map[VERSION]
    
    # מחיקת buildozer.spec ישן
    if os.path.exists('buildozer.spec'):
        os.remove('buildozer.spec')
        print("🗑️ buildozer.spec ישן נמחק")
    
    # העתקת הקבצים הנכונים
    print(f"📄 מעתיק {config['main']} -> main.py")
    shutil.copy(config["main"], "main.py")
    
    print(f"📦 מעתיק {config['requirements']} -> requirements.txt")
    shutil.copy(config["requirements"], "requirements.txt")
    
    print(f"\n✅ נבחרה גרסה: {VERSION}")
    print(f"📱 שם אפליקציה: {config['title']}")
    
    # הצגת תוכן main.py
    print(f"\n📋 תוכן main.py (5 שורות ראשונות):")
    with open('main.py', 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            print(line.rstrip())
    
    # יצירת buildozer.spec
    spec_content = f"""[app]
title = {config['title']}
package.name = {config['package']}
package.domain = org.backup
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy==2.2.1,sentry-sdk==1.40.0{',kivymd' if VERSION in ['kivymd', 'full'] else ''}{',telethon,openssl' if VERSION == 'full' else ''}

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 31
android.minapi = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
android.logcat_filters = *:S python:D kivy:D

[buildozer]
log_level = 2
warn_on_root = 0
"""
    
    with open('buildozer.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("\n✅ buildozer.spec נוצר!")
    print(f"\n📂 תיקיית עבודה: {os.getcwd()}")
