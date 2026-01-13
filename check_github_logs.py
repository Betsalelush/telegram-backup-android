import requests
import sys
import os

# GitHub Token (Load from environment or local config)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN_HERE")

REPO_OWNER = "Betsalelush"
REPO_NAME = "telegram-backup-android"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

def get_latest_run():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"
    params = {"per_page": 1}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        runs = response.json().get("workflow_runs", [])
        if not runs:
            print("No workflow runs found.")
            return None
        return runs[0]
    except Exception as e:
        print(f"Error fetching runs: {e}")
        return None

def get_jobs_for_run(run_id):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/jobs"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json().get("jobs", [])
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []

def main():
    try:
        latest_run = get_latest_run()
        if not latest_run:
            return

        run_id = latest_run['id']
        status = latest_run['status']
        conclusion = latest_run['conclusion']
        print(f"Latest Run ID: {run_id}")
        print(f"Status: {status}")
        print(f"Conclusion: {conclusion}")
        print(f"URL: {latest_run['html_url']}")

        jobs = get_jobs_for_run(run_id)
        for job in jobs:
            print(f"\nJob: {job['name']}")
            print(f"Status: {job['status']}")
            print(f"Conclusion: {job['conclusion']}")
            
            if job['status'] == 'in_progress':
                print("Active Steps:")
                for step in job['steps']:
                    if step['status'] == 'in_progress':
                         step_name = step['name'].encode('ascii', 'replace').decode('ascii')
                         print(f"  -> {step_name} (Running)")
                    elif step['status'] == 'completed':
                        pass

            if job['conclusion'] == 'failure':
                print("Job failed steps:")
                for step in job['steps']:
                    if step['conclusion'] == 'failure':
                        step_name = step['name'].encode('ascii', 'replace').decode('ascii')
                        print(f"  Step: {step_name} - {step['conclusion']}")
                        if step.get('completed_at'):
                             print(f"    FAILED! Completed at {step.get('completed_at')}")

                # Download logs logic (kept from original)
                print("\nFetching logs...")
                log_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/jobs/{job['id']}/logs"
                log_response = requests.get(log_url, headers=HEADERS)
                if log_response.status_code == 200:
                    print("Logs downloaded successfully.")
                    lines = log_response.text.split('\n')
                    
                    print("\n--- SEARCHING FOR FAILURES ---")
                    found_error = False
                    for i, line in enumerate(lines):
                        line_lower = line.lower()
                        if any(k in line_lower for k in ["failed", "error", "exception", "traceback"]):
                            if "0 failed" in line_lower or "ignored" in line_lower:
                                continue
                                
                            found_error = True
                            print(f"\nPotential Failure at line {i}:")
                            start = max(0, i - 2)
                            end = min(len(lines), i + 10)
                            for j in range(start, end):
                                print(f"{j}: {lines[j].encode('ascii', 'replace').decode('ascii')}")
                            
                            if i > 5000: 
                                break
                    
                    if not found_error:
                         print("No obvious failures found. Printing last 100 lines:")
                         for line in lines[-100:]:
                             print(line.encode('ascii', 'replace').decode('ascii'))
                else:
                    print(f"Failed to download logs. Status: {log_response.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
