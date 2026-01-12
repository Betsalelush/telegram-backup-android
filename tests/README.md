# Tests Directory

תיקייה זו מיועדת לבדיקות הפרויקט.

## מבנה מומלץ

```
tests/
├── unit/              # בדיקות יחידה
│   ├── test_managers/
│   ├── test_screens/
│   └── test_utils/
├── integration/       # בדיקות אינטגרציה
└── e2e/              # בדיקות End-to-End
```

## הרצת בדיקות

```bash
# Install pytest
pip install pytest

# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/unit/test_managers/
```

## כתיבת בדיקות

ראה דוגמאות ב-[pytest documentation](https://docs.pytest.org/)

---

**עודכן:** 12/01/2026
