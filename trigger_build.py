#!/usr/bin/env python3
"""
GitHub Actions Trigger Script
==============================
Triggers GitHub Actions workflow using GitHub CLI (gh) or REST API.

Prerequisites:
1. Install GitHub CLI: winget install GitHub.CLI
2. Login: gh auth login
3. Run: python trigger_build.py

Or use REST API with Personal Access Token.
"""

import subprocess
import sys
import os
import requests
import json

def trigger_with_gh_cli(version="full"):
    """Trigger workflow using GitHub CLI"""
    print(f"🚀 Triggering build with GitHub CLI...")
    print(f"   Version: {version}")
    
    try:
        # Check if gh is installed
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print("❌ GitHub CLI (gh) not installed!")
            print("Install with: winget install GitHub.CLI")
            return False
        
        print(f"✅ GitHub CLI version: {result.stdout.strip()}")
        
        # Trigger workflow
        cmd = [
            "gh", "workflow", "run",
            "build-apk.yml",
            "-f", f"version={version}",
            "-R", "Betsalelush/telegram-backup-android"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Workflow triggered successfully!")
            print(result.stdout)
            
            # List recent runs
            print("\n📊 Recent workflow runs:")
            subprocess.run([
                "gh", "run", "list",
                "--workflow=build-apk.yml",
                "--limit=5",
                "-R", "Betsalelush/telegram-backup-android"
            ])
            
            return True
        else:
            print(f"❌ Failed to trigger workflow!")
            print(f"Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) not found!")
        print("Install with: winget install GitHub.CLI")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def trigger_with_api(version="full", token=None):
    """Trigger workflow using GitHub REST API"""
    if not token:
        token = os.environ.get("GITHUB_TOKEN")
    
    if not token:
        print("❌ No GitHub token provided!")
        print("Set GITHUB_TOKEN environment variable or pass token as argument")
        return False
    
    print(f"🚀 Triggering build with GitHub API...")
    print(f"   Version: {version}")
    
    url = "https://api.github.com/repos/Betsalelush/telegram-backup-android/actions/workflows/build-apk.yml/dispatches"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    data = {
        "ref": "master",
        "inputs": {
            "version": version
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 204:
            print("✅ Workflow triggered successfully!")
            return True
        else:
            print(f"❌ Failed to trigger workflow!")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "full"
    
    print("=" * 60)
    print("GitHub Actions Build Trigger")
    print("=" * 60)
    print()
    
    # Try GitHub CLI first
    if trigger_with_gh_cli(version):
        print("\n✅ Done!")
    else:
        print("\n⚠️ GitHub CLI failed, trying API method...")
        print("You need a GitHub Personal Access Token")
        print("Create one at: https://github.com/settings/tokens")
        print("Required scopes: repo, workflow")
        print()
        
        token = input("Enter GitHub token (or press Enter to skip): ").strip()
        if token:
            trigger_with_api(version, token)
        else:
            print("❌ Skipped API method")
