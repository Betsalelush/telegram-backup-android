# GitHub Actions Build Failure: LT_SYS_SYMBOL_USCORE macro undefined

## Environment
- **OS**: Ubuntu 24 (GitHub Actions runner)
- **Buildozer**: Latest (upgraded)
- **Python-for-Android**: Latest (upgraded)
- **Build Target**: Android APK (arm64-v8a)
- **Workflow**: `.github/workflows/build-apk.yml`

## Problem Description

Building an Android APK with Buildozer in GitHub Actions consistently fails with the following error during the `libffi` recipe build:

```
configure.ac:215: error: possibly undefined macro: LT_SYS_SYMBOL_USCORE
      If this token and others are legitimate, please use m4_pattern_allow.
      See the Autoconf documentation.
autoreconf: error: /usr/bin/autoconf failed with exit status: 1
```

## What We've Tried (7 attempts)

### Attempt 1-2: Android SDK Setup
- Installed Android SDK command-line tools
- Created symlink from `tools/bin/sdkmanager` to `cmdline-tools/latest/bin/sdkmanager`
- **Result**: Still failed with macro error

### Attempt 3-4: Autotools Dependencies
- Installed: `autoconf`, `automake`, `libtool`, `m4`
- Upgraded `buildozer` and `python-for-android` to latest versions
- **Result**: Still failed with macro error

### Attempt 5-6: Additional Macro Packages
- Installed: `libtool-bin`, `autoconf-archive`, `gettext`, `python3-dev`
- Added `DEBIAN_FRONTEND=noninteractive` to apt-get
- **Result**: Still failed with macro error

### Attempt 7 (Current): libltdl-dev + Autotools Upgrade
- Installed: `libltdl-dev`
- Added explicit upgrade step: `sudo apt-get install --only-upgrade -y autoconf automake libtool`
- **Result**: Waiting for results...

## Current Workflow Configuration

```yaml
- name: 📦 Install system dependencies
  run: |
    sudo apt-get update -qq
    DEBIAN_FRONTEND=noninteractive sudo apt-get install -y -qq \
      build-essential \
      git \
      zip \
      unzip \
      openjdk-17-jdk \
      autoconf \
      automake \
      libtool \
      libtool-bin \
      autoconf-archive \
      m4 \
      pkg-config \
      gettext \
      zlib1g-dev \
      libncurses5-dev \
      libncursesw5-dev \
      libtinfo6 \
      cmake \
      libffi-dev \
      libssl-dev \
      python3-dev \
      libltdl-dev

- name: 🔄 Update autotools macros
  run: |
    sudo apt-get install --only-upgrade -y autoconf automake libtool
```

## Questions

1. **Is this a known issue** with python-for-android in GitHub Actions?
2. **Are there additional steps** needed to make libtool macros available to buildozer's build environment?
3. **Should we run `libtoolize`** or `aclocal` manually before the build?
4. **Is there a recommended** GitHub Actions workflow for building Android APKs with buildozer?

## Additional Context

- The same project builds successfully in **Google Colab** with similar dependencies
- The error occurs specifically during the `libffi` recipe build within python-for-android
- All system packages are installed successfully before the build starts
- The build environment has all the required tools, but buildozer doesn't seem to find the libtool macros

## Repository

https://github.com/Betsalelush/telegram-backup-android

## Workflow File

https://github.com/Betsalelush/telegram-backup-android/blob/master/.github/workflows/build-apk.yml

## Latest Failed Run

https://github.com/Betsalelush/telegram-backup-android/actions/runs/20889749530

---

Any help or suggestions would be greatly appreciated! 🙏
