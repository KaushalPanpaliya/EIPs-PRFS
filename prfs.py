import requests
from datetime import datetime, timedelta
from collections import defaultdict
import pytz

# GitHub repository details
REPO_OWNER = "ethereum"
REPO_NAME = "EIPs"

# Your GitHub personal access token
GITHUB_TOKEN = "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"

# Headers for authentication
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# API endpoint
BASE_URL = f"https://api.github.com/repos/ethereum/EIPs/pulls"

# Get the current date and times for filtering
current_date = datetime.now(pytz.UTC)
one_day_ago = current_date - timedelta(days=1)
one_month_ago = current_date - timedelta(days=30)

# Function to fetch pull requests
def fetch_pull_requests(state='closed', merged_after=None):
    pull_requests = []
    page = 1
    
    while True:
        params = {
            "state": state,
            "sort": "updated",
            "direction": "desc",
            "page": page,
            "per_page": 100
        }
        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        
        # Check if the response is successful
        if response.status_code != 200:
            print(f"Error: Unable to fetch data, status code {response.status_code}")
            break
        
        try:
            data = response.json()
        except ValueError:
            print("Error: Unable to parse JSON response")
            break
        
        # Ensure data is a list
        if not isinstance(data, list):
            print("Error: Unexpected response format")
            break

        if not data:
            break

        for pr in data:
            if isinstance(pr, dict) and pr.get('merged_at'):
                try:
                    merged_at = datetime.strptime(pr['merged_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)
                    if merged_after and merged_at < merged_after:
                        continue
                    pull_requests.append(pr)
                except Exception as e:
                    print(f"Error processing pull request {pr.get('url', 'unknown')}: {e}")

        page += 1
    
    return pull_requests

# Function to count merged pull requests by user
def count_merged_prs(pull_requests):
    user_pr_count = defaultdict(int)
    for pr in pull_requests:
        try:
            user_pr_count[pr['user']['login']] += 1
        except Exception as e:
            print(f"Error counting pull request {pr.get('url', 'unknown')}: {e}")
    return user_pr_count

# Fetch pull requests merged in the last day
try:
    prs_last_day = fetch_pull_requests(merged_after=one_day_ago)
    count_last_day = count_merged_prs(prs_last_day)
except Exception as e:
    print(f"Error fetching or counting pull requests for the last day: {e}")

# Fetch pull requests merged in the last month
try:
    prs_last_month = fetch_pull_requests(merged_after=one_month_ago)
    count_last_month = count_merged_prs(prs_last_month)
except Exception as e:
    print(f"Error fetching or counting pull requests for the last month: {e}")

print("Merged PRs in the last day by user:")
for user, count in count_last_day.items():
    print(f"{user}: {count}")

print("\nMerged PRs in the last month by user:")
for user, count in count_last_month.items():
    print(f"{user}: {count}")
