import json

# קריאת ה-Notebook
with open(r'E:\app backup\telegram-backup-android\build_apk_colab.ipynb', 'r', encoding='utf-8') as f:
    data = json.load(f)

# תיקון תא 4 - החלפת REPO_NAME בשם הקבוע
cell_4 = data['cells'][4]

# מחפש את השורה עם REPO_NAME ומחליף
new_source = []
for line in cell_4['source']:
    if 'os.chdir(f\'/content/{REPO_NAME}\')' in line:
        new_source.append('os.chdir(\'/content/telegram-backup-android\')\n')
    else:
        new_source.append(line)

cell_4['source'] = new_source

# שמירת ה-Notebook
with open(r'E:\app backup\telegram-backup-android\build_apk_colab.ipynb', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('✅ Notebook תוקן!')
print('📝 תיקנתי: החלפתי REPO_NAME בשם הקבוע telegram-backup-android')
