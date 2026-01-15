"""
Comprehensive Sentry Error Checker
Fetches detailed error information from Sentry
"""
import requests
import json
from datetime import datetime

# Sentry Configuration
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


def fetch_issues(limit=50):
    """Fetch recent issues from Sentry"""
    url = f"{BASE_URL}/organizations/{ORGANIZATION_SLUG}/issues/"
    params = {
        "statsPeriod": "14d",  # Last 14 days
        "limit": limit
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching issues: {e}")
        return []


def fetch_issue_details(issue_id):
    """Fetch detailed information about a specific issue"""
    url = f"{BASE_URL}/issues/{issue_id}/"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching issue {issue_id}: {e}")
        return None


def fetch_latest_event(issue_id):
    """Fetch the latest event for an issue"""
    url = f"{BASE_URL}/issues/{issue_id}/events/latest/"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching latest event for {issue_id}: {e}")
        return None


def format_timestamp(ts_string):
    """Format timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(ts_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts_string


def print_separator(char="=", length=80):
    """Print a separator line"""
    print(char * length)


def main():
    print_separator()
    print("COMPREHENSIVE SENTRY ERROR REPORT")
    print_separator()
    print()
    
    # Fetch issues
    print("Fetching recent issues...")
    issues = fetch_issues(limit=20)
    
    if not issues:
        print("No issues found or error fetching data")
        return
    
    print(f"Found {len(issues)} issues\n")
    print_separator("-")
    
    # Group issues by type
    errors_by_type = {}
    
    for idx, issue in enumerate(issues, 1):
        issue_type = issue.get('type', 'Unknown')
        title = issue.get('title', 'No title')
        culprit = issue.get('culprit', 'Unknown')
        last_seen = format_timestamp(issue.get('lastSeen', ''))
        count = issue.get('count', 0)
        user_count = issue.get('userCount', 0)
        issue_id = issue.get('id', '')
        status = issue.get('status', 'unknown')
        level = issue.get('level', 'error')
        
        # Store in dict
        if issue_type not in errors_by_type:
            errors_by_type[issue_type] = []
        
        errors_by_type[issue_type].append({
            'title': title,
            'culprit': culprit,
            'last_seen': last_seen,
            'count': count,
            'user_count': user_count,
            'id': issue_id,
            'status': status,
            'level': level
        })
        
        # Print summary
        print(f"\n[{idx}] {title[:100]}")
        print(f"    Type: {issue_type} | Level: {level.upper()} | Status: {status}")
        print(f"    Last seen: {last_seen}")
        print(f"    Occurrences: {count} | Affected users: {user_count}")
        if culprit:
            print(f"    Culprit: {culprit}")
    
    print()
    print_separator()
    print("\nSUMMARY BY ERROR TYPE:")
    print_separator("-")
    
    for error_type, errors in errors_by_type.items():
        total_count = sum(int(e['count']) if isinstance(e['count'], str) else e['count'] for e in errors)
        print(f"\n{error_type}: {len(errors)} unique issues, {total_count} total occurrences")
    
    # Fetch detailed info for top 3 most recent errors
    print()
    print_separator()
    print("\nDETAILED ANALYSIS OF TOP 3 RECENT ERRORS:")
    print_separator()
    
    for idx, issue in enumerate(issues[:3], 1):
        issue_id = issue.get('id')
        title = issue.get('title', 'No title')
        
        print(f"\n\n{'='*80}")
        print(f"ERROR #{idx}: {title}")
        print('='*80)
        
        # Fetch latest event
        event = fetch_latest_event(issue_id)
        
        if event:
            # Print exception details
            if 'exception' in event and 'values' in event['exception']:
                for exc in event['exception']['values']:
                    exc_type = exc.get('type', 'Unknown')
                    exc_value = exc.get('value', 'No message')
                    
                    print(f"\nException: {exc_type}")
                    print(f"Message: {exc_value}")
                    
                    # Print stacktrace
                    if 'stacktrace' in exc and 'frames' in exc['stacktrace']:
                        frames = exc['stacktrace']['frames']
                        print(f"\nStack Trace ({len(frames)} frames):")
                        
                        # Show last 5 frames (most relevant)
                        for frame in frames[-5:]:
                            filename = frame.get('filename', 'unknown')
                            function = frame.get('function', 'unknown')
                            lineno = frame.get('lineno', '?')
                            context_line = frame.get('context_line', '').strip()
                            
                            print(f"\n  File: {filename}:{lineno}")
                            print(f"  Function: {function}")
                            if context_line:
                                print(f"  Code: {context_line}")
            
            # Print breadcrumbs
            if 'breadcrumbs' in event and 'values' in event['breadcrumbs']:
                breadcrumbs = event['breadcrumbs']['values']
                if breadcrumbs:
                    print(f"\nBreadcrumbs (last {min(5, len(breadcrumbs))}):")
                    for bc in breadcrumbs[-5:]:
                        timestamp = format_timestamp(bc.get('timestamp', ''))
                        message = bc.get('message', 'No message')
                        category = bc.get('category', 'unknown')
                        print(f"  [{timestamp}] {category}: {message}")
            
            # Print context/tags
            if 'tags' in event:
                print(f"\nTags:")
                for tag in event['tags'][:10]:  # Show first 10 tags
                    key = tag.get('key', '')
                    value = tag.get('value', '')
                    print(f"  {key}: {value}")
    
    print()
    print_separator()
    print("\nReport Complete!")
    print_separator()


if __name__ == "__main__":
    main()
