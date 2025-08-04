import os
import tweepy
from datetime import datetime
import time
from datetime import timezone

BEARER_TOKEN = os.getenv("BEARER_TOKEN")

client = tweepy.Client(bearer_token=BEARER_TOKEN)

def search_tweets(query, max_results=50):
    try:
        response = client.search_recent_tweets(
            query=query,
            max_results=min(max_results, 100),
            tweet_fields=["created_at", "lang", "author_id"]
        )
        tweets = []
        if response.data:
            for tweet in response.data:
                tweets.append({
                    "id": tweet.id,
                    "date": tweet.created_at.isoformat(),
                    "source": "twitter",
                    "texte": tweet.text,
                    "utilisateur": tweet.author_id,
                    "métadonnées": {"langue": tweet.lang}
                })
        return tweets

    except tweepy.TooManyRequests as e:
        print("🛑 Limite atteinte, on attend 15 minutes...")
        time.sleep(15 * 60)
        return search_tweets(query, max_results)
    
def fetch_tweets(q: str, n: int = 20):
    """Fetch up to `n` recent tweets matching query using pagination."""
    tweets = []
    next_token = None
    while len(tweets) < n:
        resp = client.search_recent_tweets(
            query=q,
            max_results=min(n - len(tweets), 100),
            tweet_fields=['id', 'created_at', 'text'],
            next_token=next_token
        )
        if resp.data:
            for t in resp.data:
                dt = t.created_at.astimezone(timezone.utc).isoformat()
                tweets.append({
                    'id_str':     str(t.id),
                    'text':       t.text,
                    'created_at': dt
                })
        next_token = getattr(resp.meta, 'next_token', None) if hasattr(resp, 'meta') else None
        if not next_token:
            break
    return tweets
