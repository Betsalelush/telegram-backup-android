# Contributing to Telegram Backup Android

Thank you for your interest in contributing to the Telegram Backup Android project! This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Basic knowledge of Python and Android development
- Familiarity with Kivy/KivyMD (for UI changes)
- Familiarity with Telethon (for Telegram API changes)

### Setting Up Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/telegram-backup-android.git
   cd telegram-backup-android
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements_full.txt
   pip install -r requirements-test.txt
   ```

3. **Verify Installation**
   ```bash
   # Check syntax
   python -m py_compile app/**/*.py
   
   # Run tests
   pytest tests/
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Follow the existing code style
- Keep changes focused and minimal
- Write tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run syntax check
python -m py_compile app/**/*.py

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing
```

### 4. Commit Changes

```bash
git add .
git commit -m "Brief description of changes"
```

Commit message guidelines:
- Use present tense ("Add feature" not "Added feature")
- Keep first line under 50 characters
- Add detailed description if needed
- Reference issues: "Fix #123: Description"

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style Guidelines

### Python Code

1. **Follow PEP 8**
   - Use 4 spaces for indentation
   - Maximum line length: 100 characters
   - Use descriptive variable names

2. **Documentation**
   - Add docstrings to all functions and classes
   - Use Google-style docstrings
   ```python
   def function_name(param1, param2):
       """
       Brief description.
       
       Args:
           param1: Description of param1
           param2: Description of param2
           
       Returns:
           Description of return value
       """
   ```

3. **Type Hints**
   - Use type hints where beneficial
   ```python
   def get_account(account_id: str) -> Optional[Dict]:
       pass
   ```

4. **Imports**
   - Group imports: stdlib, third-party, local
   - Use absolute imports from `app.`
   ```python
   import os
   import json
   
   from kivy.app import App
   from kivymd.app import MDApp
   
   from app.config import Config
   from app.utils.logger import logger
   ```

### Project Structure

```
app/
├── config.py          # Centralized configuration
├── main.py            # Application entry point
├── managers/          # Business logic
│   ├── account_manager.py
│   ├── progress_manager.py
│   └── transfer_manager.py
├── screens/           # UI screens
│   ├── login_screen.py
│   └── backup_screen.py
├── utils/             # Helper utilities
│   ├── logger.py
│   ├── clipboard.py
│   └── helpers.py
└── kv/               # UI layouts
    ├── login.kv
    └── backup.kv
```

## Testing Guidelines

### Writing Tests

1. **Test Coverage**
   - Write tests for all new functionality
   - Aim for >80% coverage
   - Focus on business logic

2. **Test Structure**
   ```python
   class TestMyClass:
       """Test MyClass functionality"""
       
       def test_specific_behavior(self):
           """Test specific behavior with given input"""
           # Arrange
           obj = MyClass()
           
           # Act
           result = obj.method()
           
           # Assert
           assert result == expected
   ```

3. **Use Fixtures**
   - Define reusable fixtures in `conftest.py`
   - Use fixtures for setup/teardown
   - Keep tests independent

4. **Mock External Dependencies**
   ```python
   from unittest.mock import MagicMock, patch
   
   @patch('app.module.external_service')
   def test_with_mock(mock_service):
       mock_service.return_value = 'expected'
       # ... test code ...
   ```

See [TESTING.md](TESTING.md) for detailed testing guide.

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] No syntax errors
- [ ] Changes are minimal and focused

### PR Description

Include:
1. **What** - What changes were made
2. **Why** - Why the changes were needed
3. **How** - How the changes work
4. **Testing** - How you tested the changes
5. **Screenshots** - For UI changes

### Review Process

1. Automated checks run (CI/CD)
2. Code review by maintainers
3. Address feedback
4. Approval and merge

## Reporting Issues

### Bug Reports

Include:
1. **Description** - Clear description of the bug
2. **Steps to Reproduce** - How to reproduce the issue
3. **Expected Behavior** - What should happen
4. **Actual Behavior** - What actually happens
5. **Environment** - Android version, app version
6. **Screenshots** - If applicable
7. **Logs** - Error messages, Sentry error ID

### Feature Requests

Include:
1. **Problem** - What problem does this solve
2. **Solution** - Proposed solution
3. **Alternatives** - Alternative solutions considered
4. **Additional Context** - Any other relevant information

## Code Review

### As a Reviewer

- Be constructive and respectful
- Focus on code quality and maintainability
- Test the changes locally if possible
- Approve when ready

### As a Contributor

- Be open to feedback
- Address comments promptly
- Ask questions if unclear
- Update PR based on feedback

## Resources

### Documentation
- [README.md](README.md) - Project overview
- [TESTING.md](TESTING.md) - Testing guide
- [MASTER_PLAN.md](MASTER_PLAN.md) - Project plan

### Libraries
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [KivyMD Documentation](https://kivymd.readthedocs.io/)
- [Telethon Documentation](https://docs.telethon.dev/)
- [Sentry Documentation](https://docs.sentry.io/)

### Tools
- [Buildozer](https://buildozer.readthedocs.io/) - Android packaging
- [GitHub Actions](https://docs.github.com/en/actions) - CI/CD

## Questions?

- Open an issue for questions
- Check existing issues and PRs
- Read the documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
