# App Package

Main application code organized in a modular structure.

## Structure

```
app/
├── __init__.py          # Package initialization
├── main.py              # Main application entry point
├── config.py            # Configuration management
├── managers/            # Business logic managers
│   ├── __init__.py
│   ├── account_manager.py
│   ├── transfer_manager.py
│   └── progress_manager.py
├── screens/             # UI screens
│   ├── __init__.py
│   ├── accounts_screen.py
│   ├── action_screen.py
│   └── transfer_screen.py
├── utils/               # Utility functions
│   ├── __init__.py
│   ├── logger.py
│   └── helpers.py
└── kv/                  # KivyMD layouts
    ├── accounts.kv
    ├── action.kv
    └── transfer.kv
```

## Usage

The app is launched from `main.py` which initializes the ScreenManager and loads all screens.
