# Scripts Directory

This directory contains utility scripts for development, build, and maintenance tasks.

## Purpose

Store automation scripts, build helpers, deployment scripts, and other utilities.

## Suggested Scripts

```
scripts/
├── build/           # Build automation scripts
├── deploy/          # Deployment scripts
├── test/            # Testing utilities
└── maintenance/     # Maintenance and cleanup scripts
```

## Script Guidelines

When adding scripts:
1. Make scripts executable: `chmod +x script.sh`
2. Add shebang line at the top: `#!/bin/bash` or `#!/usr/bin/env python3`
3. Include usage documentation in comments
4. Test scripts before committing
5. Use descriptive names

## Examples

- `build_apk.sh` - Build Android APK
- `run_tests.py` - Run test suite
- `deploy_production.sh` - Deploy to production
- `cleanup_data.py` - Clean up old data files
