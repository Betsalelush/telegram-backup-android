# 🎯 תוכנית אב - Telegram Backup Android App
## ארכיטקטורה מלאה + משימות שלב אחר שלב

---

## 📊 סטטוס נוכחי

### Build Status
- **Build #48:** ✅ Running (reverse=True fix)
- **Build #47:** ✅ Success (disconnect button)
- **Build #46:** ✅ Success (disconnect + stop fix)

### Sentry Status
- **Organization:** bubababa
- **Project:** python-5n
- **Admin Token:** ✅ Available
- **Current Errors:** 7 unresolved (all from old builds)

---

## 🏗️ ארכיטקטורה מלאה

### 1. מבנה קבצים מוצע

```
telegram-backup-android/
├── .github/
│   └── workflows/
│       ├── build-apk.yml
│       └── build-apk-docker.yml
├── app/                          # ← קוד האפליקציה (חדש!)
│   ├── __init__.py
│   ├── main.py                   # ← Entry point
│   ├── config.py                 # ← Configuration
│   ├── managers/
│   │   ├── __init__.py
│   │   ├── account_manager.py   # ← ניהול חשבונות
│   │   ├── transfer_manager.py  # ← ניהול העברות
│   │   └── progress_manager.py  # ← ניהול התקדמות
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── accounts_screen.py   # ← מסך חשבונות
│   │   ├── action_screen.py     # ← מסך בחירת פעולה
│   │   └── transfer_screen.py   # ← מסך העברה
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py            # ← Logging + Sentry
│   │   └── helpers.py           # ← פונקציות עזר
│   └── kv/
│       ├── accounts.kv
│       ├── action.kv
│       └── transfer.kv
├── data/                         # ← נתונים (runtime)
│   ├── accounts.json
│   ├── transfers.json
│   ├── sessions/
│   └── progress/
├── docs/                         # ← תיעוד
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── CHANGELOG.md
├── scripts/                      # ← סקריפטים עזר
│   ├── get_sentry_errors.py
│   ├── trigger_build.py
│   └── cleanup.py
├── legacy/                       # ← קבצים ישנים
│   ├── main_full.py             # ← הגרסה הנוכחית
│   ├── main.py
│   └── ...
├── requirements.txt              # ← Dependencies ראשי
├── buildozer.spec
└── README.md
```

### 2. ארכיטקטורת Classes

```python
# AccountManager
class AccountManager:
    - accounts: List[Account]
    - clients: Dict[str, TelegramClient]
    
    + load_accounts()
    + save_accounts()
    + add_account(name, api_id, api_hash, phone)
    + remove_account(account_id)
    + connect_account(account_id)
    + disconnect_account(account_id)
    + get_connected_accounts()

# TransferManager
class TransferManager:
    - active_transfers: Dict[str, TransferTask]
    - account_manager: AccountManager
    
    + create_transfer(config)
    + start_transfer(transfer_id)
    + stop_transfer(transfer_id)
    + get_transfer_status(transfer_id)

# TransferTask
class TransferTask:
    - transfer_id: str
    - clients: List[TelegramClient]
    - source_channel: str
    - target_channel: str
    - use_round_robin: bool
    - running: bool
    
    + run()
    + stop()
    + get_progress()

# ProgressManager
class ProgressManager:
    + load_progress(transfer_id)
    + save_progress(transfer_id, data)
    + get_all_progress()
```

### 3. Data Models

```json
// accounts.json
{
  "accounts": [
    {
      "id": "acc_1234567890",
      "name": "חשבון ראשי",
      "api_id": "12345678",
      "api_hash": "abcdef...",
      "phone": "+972123456789",
      "session_path": "/data/.../session_972123456789",
      "is_connected": true,
      "created_at": "2026-01-11T20:00:00",
      "last_used": "2026-01-11T22:00:00"
    }
  ]
}

// transfers.json
{
  "transfers": [
    {
      "id": "transfer_1234567890",
      "name": "העברה 1",
      "source_channel": "-1001234567890",
      "source_name": "ערוץ מקור",
      "target_channel": "-1009876543210",
      "target_name": "ערוץ יעד",
      "account_ids": ["acc_1234567890"],
      "use_round_robin": false,
      "file_types": {
        "text": true,
        "photos": true,
        "videos": true,
        "documents": true
      },
      "start_id": 0,
      "status": "running",
      "created_at": "2026-01-11T22:30:00",
      "started_at": "2026-01-11T22:31:00",
      "progress": {
        "last_message_id": 12345,
        "sent_count": 100,
        "skipped_count": 5,
        "error_count": 2
      }
    }
  ]
}

// progress/transfer_1234567890.json
{
  "transfer_id": "transfer_1234567890",
  "sent_message_ids": [1, 2, 3, ...],
  "last_message_id": 12345,
  "total_sent": 100,
  "total_skipped": 5,
  "last_updated": "2026-01-11T23:00:00"
}
```

---

## 📋 השוואת קבצים - Android vs Python Scripts

### קבצי Python בתיקייה backup-to-Chanel-telegram:

| קובץ | תיאור | פונקציות עיקריות | קיים ב-Android? |
|------|-------|------------------|----------------|
| **tor.py** | העברה עם multi-account + round-robin | `load_clients()`, `send_messages_batch()`, `smart_delay()` | ❌ חלקי |
| **boba.py** | העברה מערוץ ציבורי ללא חברות | `בחר_ערוץ()`, `העבר_הודעה()` | ✅ כן |
| **boby.py** | הורדה + העלאה (לערוצים מוגבלים) | Download + Upload logic | ❌ לא |
| **bob.py** | העברה בסיסית | Basic transfer | ✅ כן |
| **seshenqr.py** | יצירת session עם QR | QR code login | ❌ לא |
| **lo.py** | קיצור קישורים | URL shortening | ❌ לא |

### פונקציות חסרות ב-Android:

#### 1. מ-tor.py:
- ✅ `load_clients()` - טעינת מספר חשבונות מ-sessions.json
- ✅ `send_messages_batch()` - חלוקת הודעות בין חשבונות (round-robin)
- ✅ `smart_delay()` - השהיה דינמית לפי הצלחות
- ✅ `handle_flood_wait_for_client()` - ניהול FloodWait לכל חשבון
- ✅ `list_available_chats()` - רשימת ערוצים זמינים
- ✅ `choose_file_types()` - בחירת סוגי קבצים מתקדמת
- ❌ `choose_reset_progress()` - בחירה בין המשך/התחלה מחדש/ID ספציפי

#### 2. מ-boba.py:
- ✅ `בחר_ערוץ()` - בחירת ערוץ עם variations
- ❌ Support for t.me/c/ links
- ❌ PeerChannel handling

#### 3. מ-boby.py:
- ❌ Download + Upload transfer method
- ❌ Large file handling (>2GB)

#### 4. מ-seshenqr.py:
- ❌ QR code login
- ❌ Session string generation

### פונקציות קיימות רק ב-Android:

- ✅ `paste_to_field()` - הדבקה מ-clipboard
- ✅ `disconnect()` - ניתוק מ-Telegram
- ✅ `update_status()` - עדכון סטטוס UI
- ✅ Progress tracking per channel pair
- ✅ Sentry integration

---

## 🎯 רשימת משימות מלאה

### Phase 0: הכנה וניקיון (1-2 ימים)

#### Task 0.1: ✅ Sentry Configuration
- [x] בדיקת logs עם admin token
- [ ] הגדרת breadcrumbs לכל פעולה
- [ ] הוספת custom tags (account_id, transfer_id)
- [ ] הגדרת sampling rate ל-100%

#### Task 0.2: ✅ Project Cleanup
- [ ] העברת קבצים ישנים ל-`legacy/`
- [ ] מחיקת קבצים מיותרים (fix_*.py)
- [ ] ארגון requirements files
- [ ] יצירת מבנה תיקיות חדש

#### Task 0.3: ✅ Documentation
- [ ] ARCHITECTURE.md
- [ ] API.md (Sentry API usage)
- [ ] CHANGELOG.md
- [ ] README.md update

---

### Phase 1: תשתית (3-4 ימים)

#### Task 1.1: ✅ Hebrew Support
- [ ] UTF-8 encoding configuration
- [ ] Hebrew font support (Roboto)
- [ ] RTL layout support (if needed)
- [ ] Test Hebrew in logs

**Files to modify:**
- `app/main.py`
- `app/utils/logger.py`

**Test:**
- [ ] Hebrew text in UI
- [ ] Hebrew in logs
- [ ] No squares

---

#### Task 1.2: ✅ Directory Structure
- [ ] Create `app/` directory
- [ ] Create `app/managers/`
- [ ] Create `app/screens/`
- [ ] Create `app/utils/`
- [ ] Create `app/kv/`
- [ ] Create `data/` directory
- [ ] Create `scripts/` directory
- [ ] Create `docs/` directory

**Files to create:**
- `app/__init__.py`
- `app/config.py`
- All subdirectories

**Test:**
- [ ] Import structure works
- [ ] Directories created on Android

---

#### Task 1.3: ✅ Configuration Management
- [ ] Create `app/config.py`
- [ ] Sentry DSN
- [ ] Default settings
- [ ] File paths

**Files to create:**
- `app/config.py`

```python
# app/config.py
import os

class Config:
    # Sentry
    SENTRY_DSN = "https://..."
    SENTRY_TRACES_SAMPLE_RATE = 1.0
    
    # Paths
    BASE_DIR = None  # Set at runtime
    SESSIONS_DIR = None
    PROGRESS_DIR = None
    ACCOUNTS_FILE = None
    TRANSFERS_FILE = None
    
    # Telegram
    MAX_MESSAGES_PER_MINUTE = 20
    SMART_DELAY_MIN = 2
    SMART_DELAY_MAX = 8
    
    @classmethod
    def setup(cls, base_dir):
        cls.BASE_DIR = base_dir
        cls.SESSIONS_DIR = os.path.join(base_dir, 'sessions')
        cls.PROGRESS_DIR = os.path.join(base_dir, 'progress')
        cls.ACCOUNTS_FILE = os.path.join(base_dir, 'accounts.json')
        cls.TRANSFERS_FILE = os.path.join(base_dir, 'transfers.json')
        
        # Create directories
        os.makedirs(cls.SESSIONS_DIR, exist_ok=True)
        os.makedirs(cls.PROGRESS_DIR, exist_ok=True)
```

**Test:**
- [ ] Config loads correctly
- [ ] Paths created

---

### Phase 2: Account Management (4-5 ימים)

#### Task 2.1: ✅ AccountManager Class
- [ ] Create `app/managers/account_manager.py`
- [ ] Implement `load_accounts()`
- [ ] Implement `save_accounts()`
- [ ] Implement `add_account()`
- [ ] Implement `remove_account()`
- [ ] Implement `connect_account()` (based on tor.py)
- [ ] Implement `disconnect_account()`
- [ ] Implement `get_connected_accounts()`

**Files to create:**
- `app/managers/__init__.py`
- `app/managers/account_manager.py`

**Based on:** tor.py lines 105-165

**Test:**
- [ ] Add account
- [ ] Save/load accounts
- [ ] Connect account
- [ ] Disconnect account

---

#### Task 2.2: ✅ Accounts Screen UI
- [ ] Create `app/screens/accounts_screen.py`
- [ ] Create `app/kv/accounts.kv`
- [ ] List of accounts
- [ ] Add account dialog
- [ ] Delete account confirmation
- [ ] Connect/disconnect buttons

**Files to create:**
- `app/screens/__init__.py`
- `app/screens/accounts_screen.py`
- `app/kv/accounts.kv`

**Test:**
- [ ] UI displays accounts
- [ ] Add account works
- [ ] Delete account works
- [ ] Connect/disconnect works

---

#### Task 2.3: ✅ Login Flow
- [ ] Send code
- [ ] Enter code
- [ ] 2FA support
- [ ] Save session

**Files to modify:**
- `app/managers/account_manager.py`

**Test:**
- [ ] Login without 2FA
- [ ] Login with 2FA
- [ ] Session persists

---

### Phase 3: Transfer Management (5-6 ימים)

#### Task 3.1: ✅ TransferManager Class
- [ ] Create `app/managers/transfer_manager.py`
- [ ] Implement `create_transfer()`
- [ ] Implement `start_transfer()`
- [ ] Implement `stop_transfer()`
- [ ] Implement `get_transfer_status()`

**Files to create:**
- `app/managers/transfer_manager.py`

**Test:**
- [ ] Create transfer
- [ ] Start transfer
- [ ] Stop transfer

---

#### Task 3.2: ✅ TransferTask Class (based on tor.py)
- [ ] Implement `run()` with round-robin
- [ ] Implement `send_messages_batch()` (tor.py line 487)
- [ ] Implement `send_single_message()` (tor.py line 381)
- [ ] Implement `get_next_client()` with FloodWait check
- [ ] Implement `smart_delay()` (tor.py line 87)

**Files to modify:**
- `app/managers/transfer_manager.py`

**Based on:** tor.py lines 381-549

**Test:**
- [ ] Single account transfer
- [ ] Multi-account round-robin
- [ ] FloodWait handling
- [ ] Smart delay works

---

#### Task 3.3: ✅ ProgressManager Class
- [ ] Create `app/managers/progress_manager.py`
- [ ] Implement `load_progress()`
- [ ] Implement `save_progress()`
- [ ] Implement `get_all_progress()`

**Files to create:**
- `app/managers/progress_manager.py`

**Based on:** tor.py lines 37-69

**Test:**
- [ ] Save progress
- [ ] Load progress
- [ ] Resume from progress

---

#### Task 3.4: ✅ Transfer Screen UI
- [ ] Create `app/screens/transfer_screen.py`
- [ ] Create `app/kv/transfer.kv`
- [ ] Account selection (single/multi)
- [ ] Channel selection
- [ ] File type selection
- [ ] Start/stop buttons
- [ ] Progress display
- [ ] Log display

**Files to create:**
- `app/screens/transfer_screen.py`
- `app/kv/transfer.kv`

**Test:**
- [ ] UI displays correctly
- [ ] Account selection works
- [ ] Transfer starts
- [ ] Progress updates
- [ ] Log displays Hebrew

---

### Phase 4: Additional Features (3-4 ימים)

#### Task 4.1: ✅ Action Selection Screen
- [ ] Create `app/screens/action_screen.py`
- [ ] Create `app/kv/action.kv`
- [ ] New transfer button
- [ ] Active transfers button
- [ ] Manage accounts button
- [ ] Settings button

**Files to create:**
- `app/screens/action_screen.py`
- `app/kv/action.kv`

**Test:**
- [ ] Navigation works
- [ ] All buttons functional

---

#### Task 4.2: ✅ Channel Selection Helper
- [ ] Implement `list_available_chats()` (tor.py line 280)
- [ ] Implement channel ID variations (tor.py line 207)
- [ ] Support for t.me/c/ links (boba.py line 177)

**Files to modify:**
- `app/utils/helpers.py`

**Based on:** tor.py lines 167-315, boba.py lines 100-127

**Test:**
- [ ] List channels
- [ ] Select by ID
- [ ] Select by username
- [ ] Select by link

---

#### Task 4.3: ✅ File Type Selection
- [ ] Implement advanced file type selection (tor.py line 317)
- [ ] Custom file extensions
- [ ] All media option

**Files to modify:**
- `app/screens/transfer_screen.py`

**Based on:** tor.py lines 317-357

**Test:**
- [ ] Select text only
- [ ] Select specific types
- [ ] Select all
- [ ] Custom extensions

---

### Phase 5: Advanced Features (4-5 ימים)

#### Task 5.1: ✅ Download + Upload Method
- [ ] Implement download logic (boby.py)
- [ ] Implement upload logic
- [ ] Large file support (>2GB)

**Files to modify:**
- `app/managers/transfer_manager.py`

**Based on:** boby.py

**Test:**
- [ ] Download file
- [ ] Upload file
- [ ] Large files work

---

#### Task 5.2: ✅ Multiple Concurrent Transfers
- [ ] Support multiple active transfers
- [ ] Separate progress per transfer
- [ ] UI for active transfers list

**Files to modify:**
- `app/managers/transfer_manager.py`
- `app/screens/action_screen.py`

**Test:**
- [ ] Start multiple transfers
- [ ] Each has own progress
- [ ] Can stop individual transfer

---

#### Task 5.3: ✅ Enhanced Sentry Logging
- [ ] Breadcrumbs for all operations
- [ ] Custom tags (account_id, transfer_id)
- [ ] Performance monitoring
- [ ] User feedback

**Files to modify:**
- `app/utils/logger.py`
- All manager classes

**Test:**
- [ ] Breadcrumbs appear in Sentry
- [ ] Tags are set correctly
- [ ] Performance data captured

---

### Phase 6: Testing & Polish (3-4 ימים)

#### Task 6.1: ✅ Integration Testing
- [ ] Test full flow: login → transfer → disconnect
- [ ] Test multi-account
- [ ] Test round-robin
- [ ] Test resume from progress
- [ ] Test Hebrew text

**Test:**
- [ ] All features work together
- [ ] No crashes
- [ ] Progress persists

---

#### Task 6.2: ✅ UI Polish
- [ ] Improve layouts
- [ ] Add loading indicators
- [ ] Better error messages
- [ ] Hebrew RTL support

**Files to modify:**
- All KV files

**Test:**
- [ ] UI looks good
- [ ] Hebrew displays correctly
- [ ] Responsive

---

#### Task 6.3: ✅ Documentation
- [ ] Update README.md
- [ ] Complete ARCHITECTURE.md
- [ ] Complete API.md
- [ ] Complete CHANGELOG.md

**Files to modify:**
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/CHANGELOG.md`

**Test:**
- [ ] Documentation is clear
- [ ] Examples work

---

### Phase 7: Cleanup & Release (2-3 ימים)

#### Task 7.1: ✅ Project Cleanup
- [ ] Remove all legacy files
- [ ] Clean up requirements files
- [ ] Remove unused imports
- [ ] Format code

**Files to delete:**
- `legacy/` directory (after backup)
- `fix_*.py` files
- Unused requirements files

**Test:**
- [ ] App still works
- [ ] Build succeeds

---

#### Task 7.2: ✅ Final Testing
- [ ] Test on Android device
- [ ] Test all features
- [ ] Check Sentry logs
- [ ] Performance testing

**Test:**
- [ ] Everything works
- [ ] No errors in Sentry
- [ ] Good performance

---

#### Task 7.3: ✅ Release
- [ ] Create release notes
- [ ] Tag version (v3.0.0)
- [ ] Build final APK
- [ ] Update documentation

**Test:**
- [ ] APK installs
- [ ] All features work
- [ ] Documentation complete

---

## 📊 סיכום משימות

### Total Tasks: 35
### Estimated Time: 30-40 days

| Phase | Tasks | Days | Status |
|-------|-------|------|--------|
| 0. הכנה | 3 | 1-2 | 🔄 Pending |
| 1. תשתית | 3 | 3-4 | 🔄 Pending |
| 2. Account Management | 3 | 4-5 | 🔄 Pending |
| 3. Transfer Management | 4 | 5-6 | 🔄 Pending |
| 4. Additional Features | 3 | 3-4 | 🔄 Pending |
| 5. Advanced Features | 3 | 4-5 | 🔄 Pending |
| 6. Testing & Polish | 3 | 3-4 | 🔄 Pending |
| 7. Cleanup & Release | 3 | 2-3 | 🔄 Pending |

---

## 🎯 סדר ביצוע מומלץ

### Week 1-2: Foundation
1. Task 0.1: Sentry Configuration ✅
2. Task 0.2: Project Cleanup
3. Task 1.1: Hebrew Support
4. Task 1.2: Directory Structure
5. Task 1.3: Configuration Management

### Week 3-4: Account Management
6. Task 2.1: AccountManager Class
7. Task 2.2: Accounts Screen UI
8. Task 2.3: Login Flow

### Week 5-6: Transfer Management
9. Task 3.1: TransferManager Class
10. Task 3.2: TransferTask Class
11. Task 3.3: ProgressManager Class
12. Task 3.4: Transfer Screen UI

### Week 7-8: Features & Polish
13. Task 4.1: Action Selection Screen
14. Task 4.2: Channel Selection Helper
15. Task 4.3: File Type Selection
16. Task 5.1: Download + Upload Method
17. Task 5.2: Multiple Concurrent Transfers
18. Task 5.3: Enhanced Sentry Logging

### Week 9-10: Testing & Release
19. Task 6.1: Integration Testing
20. Task 6.2: UI Polish
21. Task 6.3: Documentation
22. Task 7.1: Project Cleanup
23. Task 7.2: Final Testing
24. Task 7.3: Release

---

## ⚠️ החלטות חשובות

### 1. קובץ main חדש?
**המלצה: כן! ✅**

**סיבות:**
- הקוד הנוכחי (main_full.py) הוא 1168 שורות
- ארכיטקטורה חדשה לחלוטין
- קל יותר להתחיל מחדש מאשר לשנות
- נשמור את הישן ב-`legacy/` לעזרה

**תוכנית:**
1. העבר `main_full.py` → `legacy/main_full.py`
2. צור `app/main.py` חדש
3. העתק פונקציות רלוונטיות בהדרגה

### 2. מבנה תיקיות?
**המלצה: מבנה מודולרי ✅**

**סיבות:**
- קל לתחזוקה
- קל לבדיקות
- קל להוסיף פיצ'רים
- מקצועי יותר

### 3. Sentry Configuration?
**המלצה: breadcrumbs מלאים ✅**

**סיבות:**
- נראה כל פעולה
- קל לדבג
- מעקב אחר performance
- User feedback

---

## 🚀 נתחיל?

**המשימה הראשונה:** Task 0.1 - Sentry Configuration

האם להתחיל? 🎯
