import json

# קריאת ה-notebook
with open('build_apk_colab.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# מציאת תא ההתקנה (id: install_deps)
for i, cell in enumerate(notebook['cells']):
    if cell.get('metadata', {}).get('id') == 'install_deps':
        print(f"מצאתי את תא ההתקנה במיקום {i}")
        
        # החלפת התוכן לתא התקנה פשוט
        cell['source'] = [
            "%%bash\n",
            "set -e\n",
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
        
        print("✅ תא ההתקנה עודכן!")
        break

# שמירת ה-notebook
with open('build_apk_colab.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print("\n✅ הקובץ build_apk_colab.ipynb עודכן בהצלחה!")
print("\nהשינויים:")
print("- תא 2 (install_deps) עכשיו רק מתקין Buildozer")
print("- הקוד שעובד עם הקבצים הוסר (הוא יופעל בתא 4 אחרי הורדת הפרויקט)")
