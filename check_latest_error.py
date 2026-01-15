"""
Get detailed information about the latest Sentry error
"""
import requests
import json

import os
# Sentry Configuration
TOKEN = os.getenv("SENTRY_AUTH_TOKEN", "")
BASE_URL = "https://de.sentry.io/api/0"
ORGANIZATION_SLUG = "bubababa"
PROJECT_SLUG = "telegram-backup-android"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def fetch_issues(limit=5):
    """Fetch recent issues from Sentry"""
    url = f"{BASE_URL}/organizations/{ORGANIZATION_SLUG}/issues/"
    params = {
        "statsPeriod": "14d",
        "limit": limit
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def fetch_latest_event(issue_id):
    """Fetch the latest event for an issue"""
    url = f"{BASE_URL}/issues/{issue_id}/events/latest/"
    
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

# Get latest issue
issues = fetch_issues(1)
if not issues:
    print("No issues found")
    exit()

issue = issues[0]
print("=" * 80)
print(f"LATEST ERROR: {issue.get('title')}")
print("=" * 80)
print(f"Last seen: {issue.get('lastSeen')}")
print(f"Count: {issue.get('count')}")
print(f"Level: {issue.get('level')}")
print()

# Get event details
event = fetch_latest_event(issue['id'])

# Print full exception
if 'exception' in event and 'values' in event['exception']:
    for exc in event['exception']['values']:
        print(f"\nException Type: {exc.get('type')}")
        print(f"Exception Value: {exc.get('value')}")
        print()
        
        # Full stacktrace
        if 'stacktrace' in exc and 'frames' in exc['stacktrace']:
            frames = exc['stacktrace']['frames']
            print(f"FULL STACK TRACE ({len(frames)} frames):")
            print("-" * 80)
            
            for i, frame in enumerate(frames, 1):
                filename = frame.get('filename', 'unknown')
                function = frame.get('function', 'unknown')
                lineno = frame.get('lineno', '?')
                context_line = frame.get('context_line', '').strip()
                
                print(f"\n[{i}] {filename}:{lineno}")
                print(f"    Function: {function}")
                if context_line:
                    print(f"    Code: {context_line}")
                    
                # Show context (pre and post lines)
                if 'pre_context' in frame and frame['pre_context']:
                    print("    Context before:")
                    for line in frame['pre_context'][-3:]:
                        print(f"      {line}")
                        
                if 'post_context' in frame and frame['post_context']:
                    print("    Context after:")
                    for line in frame['post_context'][:3]:
                        print(f"      {line}")

# Print full event JSON for debugging
print("\n" + "=" * 80)
print("FULL EVENT DATA (for debugging):")
print("=" * 80)
print(json.dumps(event, indent=2))
