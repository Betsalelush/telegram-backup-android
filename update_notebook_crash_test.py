import json

# קריאת ה-notebook
with open('build_apk_colab.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# מציאת תא בחירת הגרסה (id: select_version)
for i, cell in enumerate(notebook['cells']):
    if cell.get('metadata', {}).get('id') == 'select_version':
        print(f"מצאתי את תא בחירת הגרסה במיקום {i}")
        
        # עדכון התוכן להוסיף crash_test
        cell['source'] = [
            "import os\n",
            "import shutil\n",
            "\n",
            "# ⚙️ בחר גרסה כאן:\n",
            "VERSION = \"crash_test\"  # שנה ל: \"crash_test\", \"basic\", \"kivymd\", או \"full\"\n",
            "\n",
            "os.chdir(f'/content/{REPO_NAME}')\n",
            "\n",
            "# מיפוי גרסאות\n",
            "version_map = {\n",
            "    \"crash_test\": {\n",
            "        \"main\": \"main_crash_test.py\",\n",
            "        \"requirements\": \"requirements_crash_test.txt\",\n",
            "        \"title\": \"Crash Test\"\n",
            "    },\n",
            "    \"basic\": {\n",
            "        \"main\": \"main_test_basic.py\",\n",
            "        \"requirements\": \"requirements_basic.txt\",\n",
            "        \"title\": \"Test Basic\"\n",
            "    },\n",
            "    \"kivymd\": {\n",
            "        \"main\": \"main_test_kivymd.py\",\n",
            "        \"requirements\": \"requirements_kivymd.txt\",\n",
            "        \"title\": \"Test KivyMD\"\n",
            "    },\n",
            "    \"full\": {\n",
            "        \"main\": \"main_full.py\",\n",
            "        \"requirements\": \"requirements_full.txt\",\n",
            "        \"title\": \"Telegram Backup\"\n",
            "    }\n",
            "}\n",
            "\n",
            "if VERSION not in version_map:\n",
            "    print(f\"❌ גרסה לא חוקית: {VERSION}\")\n",
            "    print(\"בחר: crash_test, basic, kivymd, או full\")\n",
            "else:\n",
            "    config = version_map[VERSION]\n",
            "    \n",
            "    # העתקת הקבצים הנכונים\n",
            "    print(f\"📄 מעתיק {config['main']} -> main.py\")\n",
            "    shutil.copy(config[\"main\"], \"main.py\")\n",
            "    \n",
            "    print(f\"📦 מעתיק {config['requirements']} -> requirements.txt\")\n",
            "    shutil.copy(config[\"requirements\"], \"requirements.txt\")\n",
            "    \n",
            "    print(f\"\\n✅ נבחרה גרסה: {VERSION}\")\n",
            "    print(f\"📱 שם אפליקציה: {config['title']}\")\n",
            "    print(f\"📄 main: {config['main']}\")\n",
            "    print(f\"📦 requirements: {config['requirements']}\")\n",
            "    \n",
            "    # הצגת תוכן main.py\n",
            "    print(f\"\\n📋 תוכן main.py (10 שורות ראשונות):\")\n",
            "    !head -10 main.py\n",
            "    \n",
            "    print(f\"\\n📋 תוכן requirements.txt:\")\n",
            "    !cat requirements.txt\n",
            "    \n",
            "    # יצירת buildozer.spec\n",
            "    spec_content = f\"\"\"[app]\n",
            "title = {config['title']}\n",
            "package.name = telegrambackup{VERSION.replace('_', '')}\n",
            "package.domain = org.backup\n",
            "source.dir = .\n",
            "source.include_exts = py,png,jpg,kv,atlas\n",
            "version = 1.0\n",
            "\n",
            "requirements = python3,kivy==2.2.1,sentry-sdk==1.40.0{',kivymd' if VERSION in ['crash_test', 'kivymd', 'full'] else ''}{',telethon,openssl' if VERSION == 'full' else ''}\n",
            "\n",
            "orientation = portrait\n",
            "fullscreen = 0\n",
            "\n",
            "android.permissions = INTERNET,ACCESS_NETWORK_STATE\n",
            "android.api = 31\n",
            "android.minapi = 21\n",
            "android.archs = arm64-v8a\n",
            "android.accept_sdk_license = True\n",
            "android.logcat_filters = *:S python:D kivy:D\n",
            "\n",
            "[buildozer]\n",
            "log_level = 2\n",
            "warn_on_root = 0\n",
            "\"\"\"\n",
            "    \n",
            "    with open('buildozer.spec', 'w') as f:\n",
            "        f.write(spec_content)\n",
            "    \n",
            "    print(\"\\n✅ buildozer.spec נוצר!\")\n",
            "    print(f\"\\n🔍 בדיקת קבצים:\")\n",
            "    !ls -lh main.py requirements.txt buildozer.spec"
        ]
        
        print("✅ תא בחירת הגרסה עודכן!")
        break

# עדכון תא ההסבר (step4_header)
for i, cell in enumerate(notebook['cells']):
    if cell.get('metadata', {}).get('id') == 'step4_header':
        print(f"מצאתי את תא ההסבר במיקום {i}")
        cell['source'] = [
            "## 🎯 שלב 4: בחירת גרסה\\n",
            "\\n",
            "**בחר איזו גרסה לבנות:**\\n",
            "\\n",
            "- `crash_test` - 🧪 **טסט Sentry** (מהיר! ~10 דקות) - כפתור קריסה מכוונת\\n",
            "- `basic` - Kivy בלבד (בדיקה בסיסית)\\n",
            "- `kivymd` - Kivy + KivyMD (בדיקה בינונית)\\n",
            "- `full` - הכל + Telethon (גרסה מלאה)\\n",
            "\\n",
            "**המלצה**: התחל מ-`crash_test` כדי לוודא ש-Sentry עובד!"
        ]
        print("✅ תא ההסבר עודכן!")
        break

# שמירת ה-notebook
with open('build_apk_colab.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print("\n✅ הקובץ build_apk_colab.ipynb עודכן בהצלחה!")
print("\nהשינויים:")
print("- נוספה גרסת 'crash_test' - אפליקציה עם כפתור קריסה מכוונת")
print("- VERSION מוגדר כברירת מחדל ל-'crash_test'")
print("- עודכן ההסבר בתא 4")
