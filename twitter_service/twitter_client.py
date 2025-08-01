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
    """
    Recherche les n tweets les plus récents contenant q.
    Renvoie une liste de dicts avec id_str, text, created_at.
    """
    resp = client.search_recent_tweets(
        query=q,
        max_results=min(n,100),
        tweet_fields=['id','created_at','text']
    )
    tweets = []
    if resp.data:
        for t in resp.data:
            # created_at est déjà un datetime
            dt = t.created_at.astimezone(timezone.utc).isoformat()
            tweets.append({
                'id_str':     str(t.id),
                'text':       t.text,
                'created_at': dt
            })
    return tweets
