[app]
title = Test Basic
package.name = testbasic
package.domain = org.backup
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = legacy, tests, bin, .buildozer, .git, __pycache__
version = 1.0

requirements = python3,kivy==2.2.1,sentry-sdk==1.40.0

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 31
android.minapi = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
android.logcat_filters = *:S python:D kivy:D

[buildozer]
log_level = 2
warn_on_root = 0
