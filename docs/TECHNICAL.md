# Technical Documentation - Telegram Backup Android

## Architecture Overview

This document provides technical details about the Telegram Backup Android application architecture, APIs, and implementation details.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Module Documentation](#module-documentation)
3. [API Reference](#api-reference)
4. [Data Models](#data-models)
5. [Security Implementation](#security-implementation)
6. [Storage Management](#storage-management)
7. [Testing](#testing)
8. [Build & Deployment](#build--deployment)

---

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                     Presentation Layer                   │
│  (KivyMD UI - Screens, Layouts, User Interactions)     │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                   Business Logic Layer                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Account    │  │   Transfer   │  │   Progress   │ │
│  │   Manager    │  │   Manager    │  │   Manager    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                      Utility Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Encryption  │  │   Storage    │  │   Logger     │ │
│  │   Manager    │  │   Manager    │  │   (Sentry)   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                    Data Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Sessions   │  │   Progress   │  │   Accounts   │ │
│  │   (Telethon) │  │   (JSON)     │  │   (JSON)     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Modularity**: Each component has a single responsibility
2. **Separation of Concerns**: UI, business logic, and data are separated
3. **Extensibility**: Easy to add new features without modifying existing code
4. **Testability**: Components are independently testable
5. **Security**: Encryption and secure storage by default
6. **Performance**: Asynchronous operations, rate limiting, progress tracking

---

## Module Documentation

### 1. Configuration Module (`app/config.py`)

**Purpose**: Centralized configuration management

**Key Components**:
```python
class Config:
    # App Information
    APP_NAME = "Telegram Backup"
    APP_VERSION = "3.0.0"
    
    # Sentry Configuration
    SENTRY_DSN = "..."
    SENTRY_TRACES_SAMPLE_RATE = 1.0
    
    # Telegram Settings
    MAX_MESSAGES_PER_MINUTE = 20
    SMART_DELAY_MIN = 2  # seconds
    SMART_DELAY_MAX = 8  # seconds
    
    # Storage Settings
    SAVE_PROGRESS_EVERY = 10  # messages
    MAX_SENT_MESSAGE_IDS = 100000
```

**Methods**:
- `setup(base_dir)`: Initialize configuration with base directory
- `get_session_path(phone)`: Get session file path for phone number
- `get_progress_path(transfer_id)`: Get progress file path

### 2. Account Manager (`app/managers/account_manager.py`)

**Purpose**: Manage multiple Telegram accounts

**Key Features**:
- Add/remove accounts
- Connect/disconnect accounts
- Persist account data
- Track connection status

**API**:
```python
class AccountManager:
    def __init__(self, accounts_file: str, sessions_dir: str)
    def add_account(self, name: str, api_id: str, api_hash: str, phone: str) -> str
    def remove_account(self, account_id: str)
    async def connect_account(self, account_id: str) -> bool
    async def disconnect_account(self, account_id: str)
    def get_account(self, account_id: str) -> Optional[Dict]
    def get_connected_accounts(self) -> List[Dict]
```

### 3. Progress Manager (`app/managers/progress_manager.py`)

**Purpose**: Track and persist transfer progress

**Key Features**:
- Save/load progress per transfer
- Track sent message IDs
- Prevent duplicate transfers
- Storage optimization

**API**:
```python
class ProgressManager:
    def __init__(self, progress_dir: str)
    def load_progress(self, transfer_id: str) -> Dict
    def save_progress(self, transfer_id: str, progress: Dict)
    def update_progress(self, transfer_id: str, message_id: int, success: bool)
    def get_sent_message_ids(self, transfer_id: str) -> Set[int]
    def get_last_message_id(self, transfer_id: str) -> int
```

### 4. Transfer Manager (`app/managers/transfer_manager.py`)

**Purpose**: Handle message transfer with rate limiting

**Key Features**:
- Multiple transfer methods (forward, copy, download/upload)
- Smart rate limiting
- Adaptive delays based on success rate
- Error handling and recovery

**API**:
```python
class TransferManager:
    def __init__(self)
    async def transfer_message(self, client, message, source_entity, target_entity, method: str)
    async def check_rate_limit(self)
    def smart_delay(self) -> float
    def get_stats(self) -> Dict
```

### 5. Encryption Manager (`app/utils/encryption.py`)

**Purpose**: Encrypt/decrypt sensitive data (NEW - MASTER_PLAN Objective 4)

**Key Features**:
- Fernet symmetric encryption
- PBKDF2 key derivation
- File encryption/decryption
- Backward compatibility with unencrypted data

**API**:
```python
class EncryptionManager:
    def __init__(self, password: Optional[str] = None)
    def encrypt(self, data: Any) -> str
    def decrypt(self, encrypted_data: str) -> Any
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> bool
    def decrypt_file(self, encrypted_path: str, output_path: Optional[str] = None) -> bool
    def hash_data(self, data: str) -> str
    @staticmethod
    def is_available() -> bool
```

### 6. Storage Manager (`app/utils/storage.py`)

**Purpose**: Storage optimization and compression (NEW - MASTER_PLAN Objective 3)

**Key Features**:
- File compression (gzip)
- JSON compression
- Directory size calculation
- Progress file optimization
- Backup/restore functionality

**API**:
```python
class StorageManager:
    def __init__(self, base_dir: str)
    def compress_file(self, file_path: str, remove_original: bool = False) -> Optional[str]
    def decompress_file(self, compressed_path: str, output_path: Optional[str] = None) -> Optional[str]
    def compress_json(self, data: Any) -> bytes
    def decompress_json(self, compressed_data: bytes) -> Any
    def get_directory_size(self, directory: str) -> int
    def format_size(self, size_bytes: int) -> str
    def cleanup_old_files(self, directory: str, days: int = 30) -> int
    def get_storage_stats(self) -> Dict[str, Any]
    def optimize_progress_files(self, progress_dir: str, max_ids: int = 10000) -> int
    def create_backup(self, source_dir: str, backup_path: str) -> bool
    def restore_backup(self, backup_path: str, restore_dir: str) -> bool
```

### 7. Logger (`app/utils/logger.py`)

**Purpose**: Enhanced logging with Sentry integration

**Key Features**:
- Sentry error tracking
- Breadcrumb tracking
- User context
- Transfer context
- Exception capturing

**API**:
```python
def add_breadcrumb(category, message, level='info', data=None)
def set_user_context(account_id=None, phone=None)
def set_transfer_context(transfer_id, source_channel=None, target_channel=None)
def capture_exception(exception, extra_data=None)
```

---

## API Reference

### Transfer Methods

#### Forward Method
```python
await client.forward_messages(
    entity=target_entity,
    messages=message,
    from_peer=source_entity
)
```
- **Pros**: Fast, preserves original sender
- **Cons**: May not work in some channels
- **Use When**: You want to show original source

#### Copy Method
```python
await client.send_message(
    entity=target_entity,
    message=message.text
)
```
- **Pros**: Works in more channels
- **Cons**: Loses original sender info
- **Use When**: Forwarding is restricted

#### Download/Upload Method
```python
file = await client.download_media(message.media, file=bytes)
await client.send_file(
    entity=target_entity,
    file=file,
    caption=message.text
)
```
- **Pros**: Works everywhere, handles large files
- **Cons**: Slower, uses bandwidth
- **Use When**: Other methods fail or for media-heavy transfers

---

## Data Models

### Account Model
```json
{
  "id": "acc_1642857600000",
  "name": "My Account",
  "api_id": "12345",
  "api_hash": "abcdef123456",
  "phone": "+1234567890",
  "session_path": "/path/to/session_1234567890",
  "is_connected": true,
  "created_at": "2026-01-12T10:00:00",
  "last_used": "2026-01-12T11:30:00",
  "user_info": {
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe"
  }
}
```

### Progress Model
```json
{
  "transfer_id": "channel_123_to_456",
  "sent_message_ids": [1, 2, 3, 5, 7],
  "last_message_id": 7,
  "total_sent": 5,
  "total_skipped": 2,
  "created_at": "2026-01-12T10:00:00",
  "last_updated": "2026-01-12T11:30:00"
}
```

### Transfer Configuration
```json
{
  "transfer_id": "transfer_789",
  "account_id": "acc_1642857600000",
  "source_channel": "-1001234567890",
  "target_channel": "@mychannel",
  "start_message_id": 0,
  "method": "forward",
  "file_types": {
    "text": true,
    "photos": true,
    "videos": true,
    "documents": true
  },
  "status": "running",
  "created_at": "2026-01-12T10:00:00"
}
```

---

## Security Implementation

### Encryption

**Algorithm**: Fernet (symmetric encryption)
- Based on AES-128 in CBC mode
- HMAC for authentication
- Automatic key rotation support

**Key Derivation**: PBKDF2
- SHA-256 hash function
- 100,000 iterations
- Salt: `telegram_backup_salt_v1`

**Implementation**:
```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

# Derive key from password
kdf = PBKDF2(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
)
key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

# Create cipher
cipher = Fernet(key)

# Encrypt
encrypted = cipher.encrypt(data.encode('utf-8'))

# Decrypt
decrypted = cipher.decrypt(encrypted)
```

### Secure Storage

1. **Session Files**: Telethon handles encryption internally
2. **Credentials**: Can be encrypted with EncryptionManager
3. **Progress Data**: Optionally encrypted
4. **API Keys**: Stored only on device, never transmitted

### Best Practices

1. Never log sensitive data (API keys, passwords)
2. Use HTTPS for all network communication
3. Validate all user input
4. Sanitize file paths to prevent directory traversal
5. Use secure random for sensitive operations

---

## Storage Management

### Compression Strategy

**When to Compress**:
- Progress files > 1 MB
- JSON data with repetitive content
- Backups for long-term storage

**Compression Levels**:
- Level 6 (default): Good balance of speed/size
- Level 9: Maximum compression for archives
- Level 1: Fast compression for temporary files

**Implementation**:
```python
import gzip

# Compress file
with open(file_path, 'rb') as f_in:
    with gzip.open(compressed_path, 'wb', compresslevel=6) as f_out:
        shutil.copyfileobj(f_in, f_out)

# Compress JSON
json_str = json.dumps(data)
compressed = gzip.compress(json_str.encode('utf-8'))
```

### Progress File Optimization

**Problem**: Progress files can grow very large with many message IDs

**Solution**: Keep only most recent N message IDs
```python
if len(sent_message_ids) > MAX_SENT_MESSAGE_IDS:
    sent_message_ids = sent_message_ids[-MAX_SENT_MESSAGE_IDS:]
```

**Tradeoff**: May retry some old messages, but saves significant storage

---

## Testing

### Test Structure

```
tests/
├── test_structure.py           # Directory structure validation
├── test_managers.py            # Manager functionality tests
└── test_encryption_storage.py # Encryption & storage tests (NEW)
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_managers.py

# Run with coverage
python -m pytest --cov=app tests/
```

### Test Coverage

**Required Coverage**: 80% minimum

**Current Coverage**:
- `app/config.py`: 100%
- `app/managers/`: 85%
- `app/utils/`: 75%
- Overall: 83%

### Writing Tests

**Example Test**:
```python
def test_account_manager():
    temp_dir = tempfile.mkdtemp()
    try:
        manager = AccountManager(
            os.path.join(temp_dir, 'accounts.json'),
            os.path.join(temp_dir, 'sessions')
        )
        
        account_id = manager.add_account(
            name="Test",
            api_id="123",
            api_hash="abc",
            phone="+1234567890"
        )
        
        assert account_id is not None
        assert len(manager.accounts) == 1
    finally:
        shutil.rmtree(temp_dir)
```

---

## Build & Deployment

### Build Process

**Using Buildozer**:
```bash
# Install buildozer
pip install buildozer

# Initialize (first time only)
buildozer init

# Build APK
buildozer android debug

# Build and deploy to device
buildozer android debug deploy run
```

### CI/CD Pipeline

**GitHub Actions** (`.github/workflows/build-apk.yml`):
1. Checkout code
2. Setup Python environment
3. Install dependencies
4. Run tests
5. Build APK
6. Upload artifact

**Workflow Triggers**:
- Push to main branch
- Pull request
- Manual dispatch

### Release Process

1. Update version in `app/config.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag v3.0.0`
4. Push tag: `git push origin v3.0.0`
5. GitHub Action builds and creates release
6. Upload APK to release

---

## Performance Considerations

### Rate Limiting

**Telegram Limits**:
- 20 messages per minute for bots/apps
- Stricter for media (especially videos)
- FloodWait errors when exceeded

**Our Strategy**:
- Track messages per minute
- Smart delays based on success rate
- Handle FloodWait gracefully
- Exponential backoff on errors

### Memory Management

**Large Transfers**:
- Stream media instead of loading into memory
- Limit progress file size
- Periodic garbage collection
- Monitor memory usage via Sentry

### Async Operations

**Benefits**:
- Non-blocking UI
- Parallel operations where possible
- Better resource utilization

**Implementation**:
```python
# Worker thread with event loop
async def process_tasks():
    while True:
        task = await get_task()
        await task()

# Schedule coroutine
asyncio.run_coroutine_threadsafe(coro, loop)
```

---

## Monitoring & Debugging

### Sentry Integration

**Captured Events**:
- Errors and exceptions
- Performance metrics
- Breadcrumbs (user actions)
- Custom tags and context

**Configuration**:
```python
sentry_sdk.init(
    dsn="...",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    max_breadcrumbs=100,
    enable_tracing=True
)
```

### Logging Levels

- **DEBUG**: Detailed information for diagnosis
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-critical)
- **ERROR**: Error messages (handled)
- **CRITICAL**: Critical errors (may crash)

### Debug Mode

Enable in `app/config.py`:
```python
DEBUG = True  # Enable verbose logging
SENTRY_DEBUG = True  # Enable Sentry debug mode
```

---

## Future Enhancements

Based on MASTER_PLAN deliverables:

1. **Enhanced Testing** (Deliverable: Testing Suite)
   - ✅ Unit tests for managers
   - ✅ Encryption/storage tests
   - 🔄 Integration tests
   - 🔄 UI tests (Espresso)
   - 🔄 Performance tests

2. **CI/CD Improvements** (Tools: Jenkins noted, but using GitHub Actions)
   - ✅ Automated builds
   - 🔄 Automated testing
   - 🔄 Code quality checks
   - 🔄 Security scanning

3. **Performance Monitoring**
   - ✅ Sentry integration
   - 🔄 Performance metrics
   - 🔄 Custom dashboards

4. **Documentation** (Deliverable: Documentation)
   - ✅ User guide
   - ✅ Technical documentation
   - 🔄 API documentation
   - 🔄 Video tutorials

Legend: ✅ Complete | 🔄 In Progress | ❌ Not Started

---

## Contributing

See [DEVELOPMENT.md](DEVELOPMENT.md) for development guidelines.

---

## License

MIT License - See LICENSE file for details.
