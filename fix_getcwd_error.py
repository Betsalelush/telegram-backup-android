import json

# קריאת ה-notebook
with open('build_apk_colab.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# תיקון תא 1 - ניקוי
for i, cell in enumerate(notebook['cells']):
    if cell.get('metadata', {}).get('id') == 'clean_files':
        print(f"מצאתי את תא הניקוי במיקום {i}")
        cell['source'] = [
            "%%bash\n",
            "set -e\n",
            "\n",
            "# מעבר לתיקיית /content לפני ניקוי\n",
            "cd /content\n",
            "\n",
            "echo \"🧹 מנקה קבצים ישנים...\"\n",
            "rm -rf .buildozer bin *.apk *.log telegram-backup-android\n",
            "echo \"✅ ניקוי הושלם - מתחיל מההתחלה!\""
        ]
        print("✅ תא הניקוי תוקן!")
        break

# תיקון תא 2 - התקנה
for i, cell in enumerate(notebook['cells']):
    if cell.get('metadata', {}).get('id') == 'install_deps':
        print(f"מצאתי את תא ההתקנה במיקום {i}")
        cell['source'] = [
            "%%bash\n",
            "set -e\n",
            "\n",
            "# מעבר לתיקיית /content\n",
            "cd /content\n",
            "\n",
            "echo \"📦 מתקין Buildozer ותלויות...\"\n",
            "\n",
            "# התקנת תלויות מערכת\n",
            "apt-get update -qq\n",
            "apt-get install -y -qq \\\n",
            "  python3-pip \\\n",
            "  build-essential \\\n",
            "  git \\\n",
            "  zip \\\n",
            "  unzip \\\n",
            "  openjdk-17-jdk \\\n",
            "  autoconf \\\n",
            "  libtool \\\n",
            "  pkg-config \\\n",
            "  zlib1g-dev \\\n",
            "  libncurses5-dev \\\n",
            "  libncursesw5-dev \\\n",
            "  libtinfo5 \\\n",
            "  cmake \\\n",
            "  libffi-dev \\\n",
            "  libssl-dev \\\n",
            "  > /dev/null 2>&1\n",
            "\n",
            "# התקנת Buildozer\n",
            "pip install -q buildozer cython==0.29.33\n",
            "\n",
            "echo \"✅ Buildozer הותקן בהצלחה!\""
        ]
        print("✅ תא ההתקנה תוקן!")
        break

# שמירת ה-notebook
with open('build_apk_colab.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print("\n✅ הקובץ build_apk_colab.ipynb עודכן בהצלחה!")
print("\nהתיקונים:")
print("- תא 1: נוסף cd /content לפני rm -rf")
print("- תא 2: נוסף cd /content לפני apt-get")
print("- זה מונע שגיאות getcwd")
