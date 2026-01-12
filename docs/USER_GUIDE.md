# User Guide - Telegram Backup Android

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Getting Started](#getting-started)
5. [Using the App](#using-the-app)
6. [Security & Encryption](#security--encryption)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Overview

Telegram Backup Android is a secure, reliable application for backing up your Telegram messages and media to another channel or chat. Built with modern encryption and storage optimization, it ensures your data remains safe and manageable.

**Version:** 3.0.0  
**Status:** Production Ready  
**Last Updated:** January 2026

---

## Features

### 🔐 Security Features
- **Modern Encryption**: All sensitive data (API credentials, session files) can be encrypted using industry-standard cryptography
- **Secure Storage**: Sessions and credentials are stored securely on your device
- **2FA Support**: Full support for Two-Factor Authentication
- **Privacy**: No data is sent to third parties

### 📦 Storage Optimization
- **Compression**: Progress files and backups can be compressed to save space
- **Smart Progress Tracking**: Efficiently tracks transferred messages without excessive storage
- **Automatic Cleanup**: Option to clean up old progress files
- **Storage Statistics**: Monitor how much space the app is using

### 🔄 Transfer Features
- **Multiple Transfer Methods**:
  - Forward (with credit to original sender)
  - Copy (without credit)
  - Download & Upload (for channels where forwarding is restricted)
- **Selective Transfer**: Choose which message types to transfer (text, photos, videos, documents)
- **Smart Rate Limiting**: Automatically manages transfer speed to avoid Telegram limits
- **Resume Capability**: Continue from where you left off if interrupted
- **Progress Tracking**: Real-time progress display with ETA

### 📱 User Experience
- **Material Design**: Modern, intuitive interface
- **Multi-Account Support**: Manage multiple Telegram accounts
- **Real-time Status**: Live updates on transfer progress
- **Error Handling**: Comprehensive error logging and reporting

---

## Installation

### Requirements
- Android 5.0 (Lollipop) or higher
- ~50 MB free storage space
- Active internet connection
- Telegram account

### Steps

1. **Download the APK**
   - Get the latest release from the [Releases page](https://github.com/Betsalelush/telegram-backup-android/releases)
   - Or build from source (see [Development Guide](DEVELOPMENT.md))

2. **Install the APK**
   - Enable "Install from Unknown Sources" in Android settings
   - Tap the downloaded APK file
   - Follow installation prompts

3. **Grant Permissions**
   - Storage: For saving session files and progress
   - Network: For connecting to Telegram servers

---

## Getting Started

### 1. Get API Credentials

Before using the app, you need Telegram API credentials:

1. Visit https://my.telegram.org
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Note your **API ID** and **API Hash**

**Important**: Keep these credentials secure!

### 2. First Launch

When you first open the app:

1. **Enter API Credentials**
   - API ID (numeric)
   - API Hash (alphanumeric string)
   - Phone Number (with country code, e.g., +1234567890)

2. **Request Verification Code**
   - Tap "Send Verification Code"
   - You'll receive a code via Telegram
   - Enter the code when prompted

3. **2FA (if enabled)**
   - If you have Two-Factor Authentication enabled
   - Enter your 2FA password when prompted

---

## Using the App

### Managing Accounts

The app supports multiple Telegram accounts:

1. **Add Account**
   - Tap "Manage Accounts"
   - Tap "Add Account"
   - Enter account details
   - Complete authentication

2. **Switch Accounts**
   - Go to "Manage Accounts"
   - Select the account you want to use

3. **Remove Account**
   - Long-press on account in list
   - Confirm removal

### Starting a Backup

1. **Select Source Channel**
   - Enter channel ID or username
   - Examples: `@channelname` or `-1001234567890`

2. **Select Target Channel**
   - Enter destination channel ID or username
   - You must be admin in target channel

3. **Configure Transfer Options**
   - **Message Types**: Select what to transfer
     - [ ] Text messages
     - [ ] Photos
     - [ ] Videos
     - [ ] Documents
   
   - **Transfer Method**:
     - Forward (keeps original sender info)
     - Copy (appears as new messages from you)
     - Download & Upload (for restricted channels)
   
   - **Start Message ID** (optional):
     - Leave as 0 to start from beginning
     - Or enter specific message ID to resume

4. **Start Transfer**
   - Tap "Start Backup"
   - Monitor progress in real-time
   - Use "Stop" to pause (progress is saved)

### Monitoring Progress

The app shows:
- **Progress Bar**: Visual progress indicator
- **Message Count**: Current/Total messages
- **Speed**: Messages per second
- **ETA**: Estimated time to completion
- **Status**: Current operation
- **Log**: Detailed activity log

---

## Security & Encryption

### Encryption Features

**Data Encryption** (Optional but Recommended):
- Protects stored API credentials
- Encrypts session files
- Secures progress data

**To Enable Encryption**:
1. Go to Settings
2. Enable "Encrypt Stored Data"
3. Set a master password
4. Confirm password

**Important Notes**:
- If you forget the encryption password, data cannot be recovered
- Encryption adds minimal overhead
- Backward compatible with unencrypted data

### Best Practices

1. **Secure Your Credentials**
   - Never share API ID/Hash
   - Don't screenshot credentials
   - Use strong 2FA password

2. **Regular Backups**
   - Export account data periodically
   - Keep backups in secure location

3. **Network Security**
   - Use on trusted networks
   - Avoid public WiFi for sensitive transfers

---

## Troubleshooting

### Common Issues

**"Failed to connect"**
- Check internet connection
- Verify API credentials are correct
- Ensure phone number has country code

**"Channel not found"**
- Verify channel ID/username is correct
- Ensure you've joined the channel
- Check if channel is public or private

**"Rate limit exceeded"**
- App automatically handles rate limits
- Wait for timer to complete
- Consider reducing transfer speed in settings

**"Authorization failed"**
- Re-enter verification code
- Check if account is banned/restricted
- Verify 2FA password is correct

**"Storage full"**
- Free up device storage
- Enable compression in settings
- Clean old progress files

### Error Logs

The app logs all errors to help with debugging:

1. **View Logs**
   - Settings → View Logs
   - Or check system logs via ADB

2. **Report Issues**
   - Include error messages
   - Specify steps to reproduce
   - Attach logs if possible

---

## FAQ

**Q: Is this app safe to use?**  
A: Yes. The app uses official Telegram APIs and stores all data locally on your device. Encryption is available for sensitive data.

**Q: Will my account get banned?**  
A: As long as you follow Telegram's terms of service and don't abuse the API, you should be fine. The app includes rate limiting to prevent issues.

**Q: Can I transfer between different accounts?**  
A: Yes! You can have multiple accounts and transfer between any channels you have access to.

**Q: What happens if transfer is interrupted?**  
A: Progress is saved automatically. You can resume from where you left off.

**Q: How much data can I transfer?**  
A: There's no hard limit, but Telegram may impose rate limits. The app handles these automatically.

**Q: Does this work with private channels?**  
A: Yes, as long as you're a member of the private channel.

**Q: Can I schedule automatic backups?**  
A: Not yet, but this feature is planned for a future release.

**Q: How do I update the app?**  
A: Download the latest APK and install over the existing version. Your data will be preserved.

**Q: Can I backup groups or personal chats?**  
A: Currently focused on channels, but group support may be added in future.

**Q: Is my data stored in the cloud?**  
A: No, all data is stored locally on your Android device.

---

## Support

For help and support:
- **Issues**: [GitHub Issues](https://github.com/Betsalelush/telegram-backup-android/issues)
- **Documentation**: [GitHub Wiki](https://github.com/Betsalelush/telegram-backup-android/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/Betsalelush/telegram-backup-android/discussions)

---

## License

This project is open source. See [LICENSE](../LICENSE) file for details.
