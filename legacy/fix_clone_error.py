import json

# קריאת ה-notebook
with open('build_apk_colab.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# מציאת תא clone_repo (id: clone_repo)
for i, cell in enumerate(notebook['cells']):
    if cell.get('metadata', {}).get('id') == 'clone_repo':
        print(f"מצאתי את תא clone_repo במיקום {i}")
        
        # תיקון התא
        cell['source'] = [
            "import os\n",
            "\n",
            "# הגדרות GitHub\n",
            "GITHUB_USER = \"Betsalelush\"\n",
            "REPO_NAME = \"telegram-backup-android\"\n",
            "GITHUB_URL = f\"https://github.com/{GITHUB_USER}/{REPO_NAME}.git\"\n",
            "\n",
            "print(f\"📥 מוריד מ-GitHub: {GITHUB_USER}/{REPO_NAME}\\n\")\n",
            "\n",
            "# מחיקת תיקייה ישנה אם קיימת\n",
            "!rm -rf /content/{REPO_NAME}\n",
            "\n",
            "# מעבר לתיקיית /content לפני clone\n",
            "os.chdir('/content')\n",
            "\n",
            "# שיבוט הריפו\n",
            "!git clone {GITHUB_URL}\n",
            "\n",
            "# מעבר לתיקייה\n",
            "os.chdir(f'/content/{REPO_NAME}')\n",
            "\n",
            "print(f\"\\n✅ הפרויקט הורד בהצלחה!\")\n",
            "print(f\"📂 תיקייה: /content/{REPO_NAME}\\n\")\n",
            "\n",
            "# הצגת קבצים\n",
            "print(\"📄 קבצים בפרויקט:\")\n",
            "!ls -lh"
        ]
        
        print("✅ תא clone_repo תוקן!")
        break

# שמירת ה-notebook
with open('build_apk_colab.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print("\n✅ הקובץ build_apk_colab.ipynb עודכן בהצלחה!")
print("\nהתיקון:")
print("- נוסף os.chdir('/content') לפני git clone")
print("- זה מוודא שאנחנו בתיקייה הנכונה לפני ה-clone")
