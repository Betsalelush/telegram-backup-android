#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sentry Error Fetcher
====================
This script fetches the latest errors from Sentry using the Sentry API.

Setup:
1. Get your Sentry Auth Token from: https://bubababa.sentry.io/settings/account/api/auth-tokens/
2. Set it as environment variable: set SENTRY_AUTH_TOKEN=your_token_here
3. Run: python get_sentry_errors.py

API Documentation: https://docs.sentry.io/api/events/list-a-projects-issues/
"""

import os
import requests
import json
from datetime import datetime
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
SENTRY_ORG = "bubababa"
SENTRY_PROJECT = "python-5n"  # or "test-crash-android"
SENTRY_AUTH_TOKEN = os.environ.get("SENTRY_AUTH_TOKEN")

if not SENTRY_AUTH_TOKEN:
    print("ERROR: Please set SENTRY_AUTH_TOKEN environment variable")
    print("Get your token from: https://bubababa.sentry.io/settings/account/api/auth-tokens/")
    exit(1)

# API endpoint
url = f"https://sentry.io/api/0/projects/{SENTRY_ORG}/{SENTRY_PROJECT}/issues/"

# Headers
headers = {
    "Authorization": f"Bearer {SENTRY_AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Parameters
params = {
    "statsPeriod": "24h",  # Last 24 hours
    "query": "is:unresolved",  # Only unresolved issues
    "limit": 10  # Get last 10 issues
}

print(f"Fetching errors from Sentry...")
print(f"   Organization: {SENTRY_ORG}")
print(f"   Project: {SENTRY_PROJECT}")
print()

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    issues = response.json()
    
    if not issues:
        print("No unresolved issues found!")
    else:
        print(f"Found {len(issues)} unresolved issues:\n")
        
        for i, issue in enumerate(issues, 1):
            title = issue.get("title", "Unknown")
            culprit = issue.get("culprit", "Unknown")
            count = issue.get("count", 0)
            last_seen = issue.get("lastSeen", "")
            level = issue.get("level", "error")
            
            # Parse timestamp
            if last_seen:
                dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                last_seen_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                last_seen_str = "Unknown"
            
            print(f"{i}. {title}")
            print(f"   Location: {culprit}")
            print(f"   Count: {count} events")
            print(f"   Last seen: {last_seen_str}")
            print(f"   Level: {level}")
            print(f"   URL: {issue.get('permalink', 'N/A')}")
            print()
    
    # Save to file
    with open("sentry_errors.json", "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)
    
    print(f"Full details saved to: sentry_errors.json")
    
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
