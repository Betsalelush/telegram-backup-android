# Data Directory

This directory contains application data files and runtime information.

## Structure

```
data/
├── sessions/       # Telegram session files (.session)
├── progress/       # Transfer progress tracking files
├── accounts.json   # Account configurations
└── transfers.json  # Transfer task definitions
```

## Files

### accounts.json
Stores configuration for multiple Telegram accounts:
- Account IDs
- API credentials
- Phone numbers
- Session paths
- Connection status

### transfers.json
Stores transfer task definitions:
- Source and destination channels
- Transfer settings
- Task status
- Creation/modification timestamps

## Session Files

Session files are stored in `sessions/` directory with naming format:
- `session_<phone_number>.session` (without + sign)

## Progress Files

Progress files are stored in `progress/` directory with naming format:
- `<transfer_id>_progress.json`

Each progress file tracks:
- Sent message IDs
- Last processed message ID
- Total sent/skipped counts
- Timestamps
