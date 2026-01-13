import requests
import json
import base64
import sys
import os

# Token provided by user (Load from environment or use placeholder)
TOKEN = os.environ.get("SENTRY_AUTH_TOKEN", "YOUR_SENTRY_TOKEN_HERE")

# Base URL for Sentry API
BASE_URL = "https://sentry.io/api/0"
# The token decoding showed region_url: https://de.sentry.io
# Issues are usually accessible via the main API or region specific. Let's try region specific first if it exists, or just use sentry.io which redirects.
# Actually, for region-based Sentry, the API url might be different. Let's try https://de.sentry.io/api/0

BASE_URLs = ["https://de.sentry.io/api/0", "https://sentry.io/api/0"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

ORGANIZATION_SLUG = "bubababa" # From token
PROJECT_ID = "4510674676744272" # From DSN

def get_latest_issues(base_url):
    # Try fetching organization-wide issues
    url = f"{base_url}/organizations/{ORGANIZATION_SLUG}/issues/"
    params = {
        "limit": 5,
        "sort": "date", # Sort by last seen
        "statsPeriod": "24h" # Last 24 hours
    }
    print(f"Fetching organization issues from {url}...")
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch issues: {response.status_code} {response.text}")
        return []

def main():
    base_url = "https://de.sentry.io/api/0"
    
    print("\nFetching latest issues for organization bubababa...")
    issues = get_latest_issues(base_url)
    
    if not issues:
        # Try fall back to sentry.io if de.sentry.io fails or returns nothing (and not auth error)
        base_url = "https://sentry.io/api/0"
        print("Retrying with sentry.io...")
        issues = get_latest_issues(base_url)

    if not issues:
        print("No issues found or access denied.")
        return

def get_latest_event(base_url, issue_id):
    url = f"{base_url}/issues/{issue_id}/events/latest/"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch latest event: {response.status_code} {response.text}")
        return None

def main():
    base_url = "https://de.sentry.io/api/0"
    
    print("\nFetching latest issues for organization bubababa...")
    issues = get_latest_issues(base_url)
    
    if not issues:
        # Try fall back to sentry.io if de.sentry.io fails or returns nothing (and not auth error)
        base_url = "https://sentry.io/api/0"
        print("Retrying with sentry.io...")
        issues = get_latest_issues(base_url)

    if not issues:
        print("No issues found or access denied.")
        return

    print(f"\nFound {len(issues)} recent issues:")
    for i, issue in enumerate(issues):
        print(f"[{i+1}] {issue['title']} (Last seen: {issue['lastSeen']})")
        print(f"    Culprit: {issue.get('culprit')}")
        print(f"    ID: {issue['id']}")

    # Get details of the most recent issue
    latest_issue = issues[0]
    print(f"\nfetching traceback for most recent issue: {latest_issue['title']}")
    
    event = get_latest_event(base_url, latest_issue['id'])
    if event:
        print("\n--- CRASH DETAILS ---")
        print(f"Message: {event.get('message')}")
        
        # Try to print simple traceback
        try:
            for entry in event.get('entries', []):
                if entry['type'] == 'exception':
                    for value in entry['data']['values']:
                        print(f"\nException Type: {value.get('type')}")
                        print(f"Exception Value: {value.get('value')}")
                        if 'stacktrace' in value:
                            print("\nStacktrace:")
                            for frame in value['stacktrace']['frames']:
                                filename = frame.get('filename') or frame.get('module')
                                func = frame.get('function')
                                lineno = frame.get('lineno')
                                print(f"  File \"{filename}\", line {lineno}, in {func}")
                                if frame.get('context_line'):
                                    print(f"    {frame['context_line'].strip()}")
        except Exception as e:
            print(f"Error parsing traceback: {e}")
            print("Raw event data (truncated):")
            print(str(event)[:1000])

if __name__ == "__main__":
    main()
