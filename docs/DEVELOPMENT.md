# Development Guide

Guide for developers contributing to Telegram Backup Android.

---

## Table of Contents

1. [Setup Development Environment](#setup-development-environment)
2. [Project Structure](#project-structure)
3. [Coding Standards](#coding-standards)
4. [Testing](#testing)
5. [Building](#building)
6. [Contributing](#contributing)

---

## Setup Development Environment

### Prerequisites

- Python 3.8 or higher
- Git
- Android SDK (for building APK)
- Code editor (VS Code, PyCharm recommended)

### Installation Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/Betsalelush/telegram-backup-android.git
   cd telegram-backup-android
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements_full.txt
   ```

4. **Install Development Tools**
   ```bash
   pip install pytest pytest-cov black flake8
   ```

5. **Setup Pre-commit Hooks** (Optional)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

---

## Project Structure

```
telegram-backup-android/
├── app/                      # Main application code
│   ├── __init__.py
│   ├── config.py            # Configuration
│   ├── main.py              # Entry point
│   ├── managers/            # Business logic
│   │   ├── account_manager.py
│   │   ├── progress_manager.py
│   │   └── transfer_manager.py
│   ├── screens/             # UI screens
│   │   ├── login_screen.py
│   │   └── backup_screen.py
│   ├── utils/               # Utilities
│   │   ├── logger.py
│   │   ├── encryption.py   # NEW: Encryption support
│   │   ├── storage.py      # NEW: Storage optimization
│   │   ├── clipboard.py
│   │   └── helpers.py
│   └── kv/                  # KivyMD layouts
│       ├── login.kv
│       └── backup.kv
├── data/                    # Application data
│   ├── sessions/           # Telegram sessions
│   ├── progress/           # Transfer progress
│   ├── accounts.json       # Account data
│   └── transfers.json      # Transfer configurations
├── tests/                   # Test suite
│   ├── test_structure.py
│   ├── test_managers.py
│   └── test_encryption_storage.py  # NEW
├── docs/                    # Documentation
│   ├── USER_GUIDE.md       # NEW: User documentation
│   ├── TECHNICAL.md        # NEW: Technical documentation
│   └── DEVELOPMENT.md      # This file
├── legacy/                  # Legacy code (reference)
├── scripts/                 # Build/utility scripts
├── main.py                 # Application entry point
├── buildozer.spec          # Android build config
└── requirements_full.txt   # Dependencies
```

---

## Coding Standards

### Python Style Guide

Follow **PEP 8** with these specifics:

**Naming Conventions**:
```python
# Classes: PascalCase
class AccountManager:
    pass

# Functions/methods: snake_case
def get_account_by_id(account_id):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# Private methods: _leading_underscore
def _internal_method(self):
    pass
```

**Docstrings**:
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When input is invalid
    """
    pass
```

**Type Hints**:
```python
from typing import Optional, List, Dict

def get_accounts(active_only: bool = False) -> List[Dict[str, Any]]:
    pass
```

### Code Formatting

Use **Black** for consistent formatting:
```bash
# Format entire project
black app/ tests/

# Check without modifying
black --check app/
```

### Linting

Use **Flake8** for style checking:
```bash
# Check code
flake8 app/ tests/

# With specific config
flake8 --max-line-length=100 app/
```

### Import Order

```python
# Standard library imports
import os
import sys
import json

# Third-party imports
import sentry_sdk
from kivymd.app import MDApp

# Local imports
from app.config import Config
from app.managers import AccountManager
```

---

## Testing

### Running Tests

**All Tests**:
```bash
python -m pytest tests/
```

**Specific Test File**:
```bash
python tests/test_managers.py
```

**With Coverage**:
```bash
python -m pytest --cov=app tests/
python -m pytest --cov=app --cov-report=html tests/
```

**Verbose Output**:
```bash
python -m pytest -v tests/
```

### Writing Tests

**Test Structure**:
```python
def test_feature_name():
    """Test that feature works correctly"""
    # Setup
    manager = create_test_manager()
    
    # Execute
    result = manager.do_something()
    
    # Assert
    assert result is not None
    assert result.status == "success"
    
    # Cleanup (if needed)
    cleanup_test_data()
```

**Using Fixtures**:
```python
import pytest

@pytest.fixture
def temp_directory():
    """Provide temporary directory for tests"""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_with_fixture(temp_directory):
    # Use temp_directory
    file_path = os.path.join(temp_directory, 'test.txt')
    ...
```

**Test Coverage Goals**:
- Minimum: 80% overall coverage
- Critical modules: 90%+ coverage
- New code: 100% coverage

---

## Building

### Desktop Testing

Run the app on desktop for quick testing:
```bash
python main.py
```

### Android APK Build

**Debug Build**:
```bash
buildozer android debug
```

**Release Build**:
```bash
buildozer android release
```

**Deploy to Device**:
```bash
buildozer android debug deploy run
```

### Buildozer Configuration

Edit `buildozer.spec` for build settings:
```ini
[app]
title = Telegram Backup
package.name = telegrambackup
package.domain = com.github.betsalelush
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 3.0.0
requirements = python3,kivy,kivymd,telethon,sentry-sdk,cryptography

[buildozer]
log_level = 2
warn_on_root = 1
```

### CI/CD (GitHub Actions)

The project uses GitHub Actions for automated builds:

**Workflow File**: `.github/workflows/build-apk.yml`

**Triggers**:
- Push to main/master branch
- Pull requests
- Manual workflow dispatch

**Steps**:
1. Checkout code
2. Setup Python
3. Install dependencies
4. Run tests
5. Build APK
6. Upload artifacts

---

## Contributing

### Workflow

1. **Fork & Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/telegram-backup-android.git
   ```

2. **Create Branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

3. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

4. **Test Changes**
   ```bash
   python -m pytest tests/
   black app/ tests/
   flake8 app/
   ```

5. **Commit**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

6. **Push**
   ```bash
   git push origin feature/my-new-feature
   ```

7. **Create Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Fill in description
   - Link related issues

### Commit Messages

Follow conventional commits:
```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Maintenance

**Examples**:
```
feat(encryption): add data encryption support

Implements encryption manager with Fernet cipher
for securing stored credentials and session files.

Closes #123
```

```
fix(transfer): handle deleted messages correctly

Skip deleted messages instead of crashing.
Add detailed logging for skipped messages.
```

### Pull Request Guidelines

**PR Checklist**:
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No new warnings

**PR Description Template**:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing done

## Screenshots (if applicable)
Add screenshots

## Checklist
- [ ] Code reviewed
- [ ] Tests added
- [ ] Documentation updated
```

---

## Debugging

### Desktop Debugging

**Enable Debug Mode**:
```python
# In app/config.py or main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Python Debugger**:
```python
import pdb; pdb.set_trace()  # Set breakpoint
```

### Android Debugging

**View Logs**:
```bash
adb logcat | grep python
```

**Install Debug APK**:
```bash
adb install -r bin/telegrambackup-debug.apk
```

**Connect Debugger**:
```bash
buildozer android debug deploy run logcat
```

---

## Best Practices

### Code Organization

1. **Keep files small**: Max 500 lines per file
2. **Single responsibility**: One class/module = one purpose
3. **DRY principle**: Don't Repeat Yourself
4. **KISS principle**: Keep It Simple, Stupid

### Error Handling

```python
# Always handle exceptions
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    # Handle or re-raise
    raise
finally:
    # Cleanup
    cleanup_resources()
```

### Logging

```python
# Use appropriate log levels
logger.debug("Detailed debugging info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")

# Include context
logger.error(f"Failed to process message {msg_id}: {error}")
```

### Security

1. **Never commit secrets**: Use environment variables
2. **Validate input**: Sanitize all user input
3. **Secure storage**: Use encryption for sensitive data
4. **Error messages**: Don't leak sensitive info in errors

### Performance

1. **Use async/await**: For I/O operations
2. **Batch operations**: Process in batches when possible
3. **Cache results**: Avoid redundant calculations
4. **Profile code**: Use profilers to find bottlenecks

---

## Resources

### Documentation
- [Python Documentation](https://docs.python.org/3/)
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [KivyMD Documentation](https://kivymd.readthedocs.io/)
- [Telethon Documentation](https://docs.telethon.dev/)

### Tools
- [Buildozer](https://buildozer.readthedocs.io/)
- [Pytest](https://docs.pytest.org/)
- [Black](https://black.readthedocs.io/)
- [Flake8](https://flake8.pycqa.org/)

### Community
- [GitHub Issues](https://github.com/Betsalelush/telegram-backup-android/issues)
- [GitHub Discussions](https://github.com/Betsalelush/telegram-backup-android/discussions)

---

## License

MIT License - See LICENSE file for details.
