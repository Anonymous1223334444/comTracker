import praw
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from datetime import datetime

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

def fetch_reddit_posts(query: str, limit: int = 20):
    """Fetch up to `limit` recent reddit posts using pagination."""
    posts = []
    for submission in reddit.subreddit('all').search(query, sort='new', limit=None):
        posts.append({
            'id':          submission.id,
            'title':       submission.title,
            'url':         submission.url,
            'created_utc': submission.created_utc
        })
        if len(posts) >= limit:
            break
    return posts

def search_posts(query, max_results=50):
    results = []
    for submission in reddit.subreddit("all").search(query, limit=None):
        results.append({
            "service":     "reddit",
            "source":      f"r/{submission.subreddit.display_name}",
            "id":          submission.id,
            "title":       submission.title,
            "description": submission.selftext or "",
            "url":         submission.url,
            "date":        datetime.utcfromtimestamp(
                            submission.created_utc
                        ).isoformat(),
        })
        if len(results) >= max_results:
            break
    return results
