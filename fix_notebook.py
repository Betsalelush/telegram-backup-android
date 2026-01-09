import json

# קריאת ה-Notebook
with open(r'E:\app backup\telegram-backup-android\build_apk_colab.ipynb', 'r', encoding='utf-8') as f:
    data = json.load(f)

# תיקון תא 4 (select_version)
cell_4 = data['cells'][4]
cell_4['source'] = [
    'import os\n',
    'import shutil\n',
    '\n',
    '# ⚙️ בחר גרסה כאן:\n',
    'VERSION = "basic"  # שנה ל: "basic", "kivymd", או "full"\n',
    '\n',
    'os.chdir(f\'/content/{REPO_NAME}\')\n',
    '\n',
    '# מיפוי גרסאות\n',
    'version_map = {\n',
    '    "basic": {\n',
    '        "main": "main_test_basic.py",\n',
    '        "requirements": "requirements_basic.txt",\n',
    '        "title": "Test Basic",\n',
    '        "package": "testbasic"\n',
    '    },\n',
    '    "kivymd": {\n',
    '        "main": "main_test_kivymd.py",\n',
    '        "requirements": "requirements_kivymd.txt",\n',
    '        "title": "Test KivyMD",\n',
    '        "package": "testkivymd"\n',
    '    },\n',
    '    "full": {\n',
    '        "main": "main.py",\n',
    '        "requirements": "requirements.txt",\n',
    '        "title": "Telegram Backup",\n',
    '        "package": "telegrambackup"\n',
    '    }\n',
    '}\n',
    '\n',
    'if VERSION not in version_map:\n',
    '    print(f"❌ גרסה לא חוקית: {VERSION}")\n',
    '    print("בחר: basic, kivymd, או full")\n',
    'else:\n',
    '    config = version_map[VERSION]\n',
    '    \n',
    '    # מחיקת buildozer.spec ישן\n',
    '    if os.path.exists(\'buildozer.spec\'):\n',
    '        os.remove(\'buildozer.spec\')\n',
    '    \n',
    '    # העתקת הקבצים הנכונים - תמיד!\n',
    '    print(f"📄 מעתיק {config[\'main\']} -> main.py")\n',
    '    shutil.copy(config["main"], "main.py")\n',
    '    \n',
    '    print(f"📦 מעתיק {config[\'requirements\']} -> requirements.txt")\n',
    '    shutil.copy(config["requirements"], "requirements.txt")\n',
    '    \n',
    '    print(f"\\n✅ נבחרה גרסה: {VERSION}")\n',
    '    print(f"📱 שם אפליקציה: {config[\'title\']}")\n',
    '    \n',
    '    # הצגת תוכן main.py\n',
    '    print(f"\\n📋 תוכן main.py (5 שורות ראשונות):")\n',
    '    !head -5 main.py\n',
    '    \n',
    '    # יצירת buildozer.spec\n',
    '    spec_content = f"""[app]\n',
    'title = {config[\'title\']}\n',
    'package.name = {config[\'package\']}\n',
    'package.domain = org.backup\n',
    'source.dir = .\n',
    'source.include_exts = py,png,jpg,kv,atlas\n',
    'version = 1.0\n',
    '\n',
    'requirements = python3,kivy==2.2.1,sentry-sdk==1.40.0{\',kivymd\' if VERSION in [\'kivymd\', \'full\'] else \'\'}{\',telethon,openssl\' if VERSION == \'full\' else \'\'}\n',
    '\n',
    'orientation = portrait\n',
    'fullscreen = 0\n',
    '\n',
    'android.permissions = INTERNET,ACCESS_NETWORK_STATE\n',
    'android.api = 31\n',
    'android.minapi = 21\n',
    'android.archs = arm64-v8a\n',
    'android.accept_sdk_license = True\n',
    'android.logcat_filters = *:S python:D kivy:D\n',
    '\n',
    '[buildozer]\n',
    'log_level = 2\n',
    'warn_on_root = 0\n',
    '"""\n',
    '    \n',
    '    with open(\'buildozer.spec\', \'w\') as f:\n',
    '        f.write(spec_content)\n',
    '    \n',
    '    print("\\n✅ buildozer.spec נוצר!")'
]

# שמירת ה-Notebook
with open(r'E:\app backup\telegram-backup-android\build_apk_colab.ipynb', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('✅ Notebook תוקן בהצלחה!')
print('📝 השינויים:')
print('  - הוסרתי את התנאי if VERSION != "full"')
print('  - עכשיו תמיד מעתיק את הקבצים הנכונים')
print('  - הוספתי הדפסה של תוכן main.py')
print('  - הוספתי package name ייחודי לכל גרסה')
