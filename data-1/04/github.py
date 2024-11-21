from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urlencode
import json
import time
from collections import Counter
import queue
import threading
from typing import Dict, Any, Tuple
import logging
from datetime import datetime
import sys
import os

def setup_logging(log_level=logging.DEBUG):
    """Setup logging configuration"""
    # Console handler for info and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s: %(message)s'
    ))
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    return root_logger

class RateLimitedGitHub:
    def __init__(self, token: str, requests_per_hour: int = 5000):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Python-urllib'
        }
        self.delay = 3600 / requests_per_hour
        self.last_request_time = 0
        self.request_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.total_requests = 0
        
        self.logger.info(f"Initialized with rate limit of {requests_per_hour} requests/hour")
        self.logger.debug(f"Calculated delay between requests: {self.delay:.2f} seconds")
        
        # Start worker thread
        self.worker = threading.Thread(target=self._process_queue, daemon=True)
        self.worker.start()
        self.logger.debug("Started worker thread")

    def _wait_for_rate_limit(self):
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.delay:
            wait_time = self.delay - time_since_last
            self.logger.debug(f"Rate limiting: waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
        self.last_request_time = time.time()

    def _make_request(self, url: str, params: Dict = None) -> Tuple[int, Any]:
        if params:
            url = f"{url}?{urlencode(params)}"
        
        self.logger.debug(f"Making request to: {url}")
        request = Request(url, headers=self.headers)
        
        try:
            with urlopen(request) as response:
                self.total_requests += 1
                self.logger.debug(
                    f"Request successful. Status: {response.status}. "
                    f"Total requests made: {self.total_requests}"
                )
                return response.status, json.loads(response.read().decode('utf-8'))
        except URLError as e:
            self.logger.error(f"Request failed: {str(e)}")
            if hasattr(e, 'code'):
                return e.code, e.read().decode('utf-8')
            return 500, str(e)

    def _process_queue(self):
        self.logger.debug("Queue processor started")
        while True:
            url, params = self.request_queue.get()
            if url is None:  # Poison pill
                self.logger.debug("Received stop signal, shutting down worker")
                break
                
            self._wait_for_rate_limit()
            result = self._make_request(url, params)
            self.response_queue.put(result)
            self.request_queue.task_done()

    def get(self, url: str, params: Dict = None) -> Tuple[int, Any]:
        self.logger.debug(f"Queuing request: {url} with params: {params}")
        self.request_queue.put((url, params))
        return self.response_queue.get()

def analyze_github_repo(repo_path: str, token: str) -> Dict:
    logger = logging.getLogger('analyzer')
    logger.info(f"Starting analysis of repository: {repo_path}")
    
    github = RateLimitedGitHub(token)
    base_url = f'https://api.github.com/repos/{repo_path}/issues'
    
    # Get all pull requests
    all_prs = []
    page = 1
    
    logger.info("Fetching pull requests...")
    while True:
        logger.debug(f"Fetching page {page}")
        status, response = github.get(base_url, {
            'state': 'all',  # Explicitly get both open and closed issues
            'per_page': 100,
            'page': page,
            'sort': 'created',  # Sort by creation date
            'direction': 'desc'  # Get newest first
        })
        
        if status != 200:
            logger.error(f"Failed to fetch page {page}: {status} - {response}")
            break
            
        if not response:
            logger.debug(f"No more pages after page {page-1}")
            break
            
        # Filter to only include PRs
        prs = [item for item in response if 'pull_request' in item]
        logger.info(f"Page {page}: Found {len(prs)} pull requests")
        all_prs.extend(prs)
        page += 1

    # Log statistics about open vs closed PRs
    open_prs = len([pr for pr in all_prs if pr['state'] == 'open'])
    closed_prs = len([pr for pr in all_prs if pr['state'] == 'closed'])
    logger.info(f"Total pull requests found: {len(all_prs)}")
    logger.info(f"Open PRs: {open_prs}, Closed PRs: {closed_prs}")

    # Save raw data
    output_file = 'all_pull_requests.json'
    logger.info(f"Saving raw data to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_prs, f, indent=2, ensure_ascii=False)

    # Analyze comments
    logger.info("Analyzing comments and collecting statistics...")
    pr_comments = [(pr['number'], pr['comments'], pr['title']) for pr in all_prs]
    most_commented = sorted(pr_comments, key=lambda x: x[1], reverse=True)[:5]

    # Analyze commenters and labels
    commenters = Counter()
    labels = Counter()
    
    for pr in all_prs:
        # Count labels
        for label in pr.get('labels', []):
            label_str = f"{label['name']} (#{label['color']})"
            labels[label_str] += 1
            logger.debug(f"Counted label: {label_str}")
            
        # Get comments if PR has any
        if pr['comments'] > 0:
            logger.debug(f"Fetching comments for PR #{pr['number']}")
            comments_url = f"{base_url}/{pr['number']}/comments"
            status, comments = github.get(comments_url)
            if status == 200:
                for comment in comments:
                    user = comment['user']['login']
                    commenters[user] += 1
                    logger.debug(f"Counted comment by {user}")

    logger.info("Analysis complete")
    return {
        'total_prs': len(all_prs),
        'most_commented': most_commented,
        'top_commenters': commenters.most_common(5),
        'top_labels': labels.most_common(5),
        'all_prs': all_prs  # Include all PRs in results
    }

def main():
    # Setup logging first
    logger = setup_logging()
    logger.info("Starting GitHub repository analysis")

    try:
        # safe-global/safe-modules
        repo_path = input("Enter repository path (org/project): ")
        
        token = input("Enter your GitHub token: ")
        
        logger.info(f"Analyzing repository: {repo_path}")
        results = analyze_github_repo(repo_path, token)
        
        # Print results
        print(f"\nTotal PRs analyzed: {results['total_prs']}")
        open_prs = sum(1 for pr in results['all_prs'] if pr['state'] == 'open')
        closed_prs = sum(1 for pr in results['all_prs'] if pr['state'] == 'closed')
        print(f"Status breakdown: {open_prs} open, {closed_prs} closed")
        
        print("\nMost commented PRs:")
        for number, comments, title in results['most_commented']:
            print(f"#{number} ({comments} comments): {title}")
        
        print("\nTop 5 commenters:")
        for user, count in results['top_commenters']:
            print(f"{user}: {count} comments")
        
        print("\nTop 5 labels:")
        for label, count in results['top_labels']:
            print(f"{label}: used {count} times")
        
        logger.info("Analysis completed successfully")
        print("\nComplete PR data saved to 'all_pull_requests.json'")

    except KeyboardInterrupt:
        logger.warning("Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"An error occurred. Check the log file for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()