[app]
title = Telegram Backup
package.name = telegrambackup
package.domain = org.bezalel
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = maxuser, tests, bin, .buildozer, .git, __pycache__, .github, node_modules, .idea, .vscode
source.exclude_patterns = license,images/*/*.jpg,check_*.py,fetch_*.py,test_*.py,syntax_check.py,scan_encoding.py,read_head.py
version = 3.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,telethon==1.36.0,sentry-sdk==1.40.0,pyjnius==1.6.1,requests,pyaes,rsa,pyasn1,pyshorteners

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,FOREGROUND_SERVICE,WAKE_LOCK,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,READ_MEDIA_AUDIO
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
android.logcat_filters = *:S python:D kivy:D

[buildozer]
log_level = 2
warn_on_root = 0
