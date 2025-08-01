import praw
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from datetime import datetime

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

def fetch_reddit_posts(query: str, limit: int = 20):
    """
    Recherche les `limit` posts les plus récents contenant `query`
    dans tous les subreddits, et renvoie une liste de dicts :
    { id, title, url, created_utc }
    """
    posts = []
    # Recherche globale (subreddit='all')
    for submission in reddit.subreddit('all').search(query, sort='new', limit=limit):
        posts.append({
            'id':          submission.id,
            'title':       submission.title,
            'url':         submission.url,
            'created_utc': submission.created_utc
        })
    return posts

def search_posts(query, max_results=50):
    results = []
    for submission in reddit.subreddit("all").search(query, limit=max_results):
        results.append({
            "service":     "reddit",
            "source":      f"r/{submission.subreddit.display_name}",        # badge
            "id":          submission.id,
            "title":       submission.title,
            "description": submission.selftext or "",
            "url":         submission.url,
            "date":        datetime.utcfromtimestamp(
                            submission.created_utc
                        ).isoformat(),
        })
    return results
