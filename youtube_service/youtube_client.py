from googleapiclient.discovery import build
from config import YOUTUBE_API_KEY
from datetime import datetime
import requests

def fetch_videos(q: str, n: int = 10):
    """
    Recherche les n vidéos YouTube les plus récentes pour q.
    Renvoie une liste de dicts avec title, videoId, publishedAt.
    """
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'key':       YOUTUBE_API_KEY,
        'q':         q,
        'part':      'snippet',
        'maxResults': n,
        'type':      'video',
        'order':     'date'
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    items = resp.json().get('items', [])
    videos = []
    for it in items:
        snip = it['snippet']
        vid = it['id']['videoId']
        videos.append({
            'title':      snip['title'],
            'videoId':    vid,
            'publishedAt': snip['publishedAt']
        })
    return videos


def search_youtube(query, max_results=20):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    )
    response = request.execute()

    results = []
    for item in response["items"]:
        snippet    = item["snippet"]
        video_id   = item["id"]["videoId"]
        channel_id = snippet["channelId"]

        # one extra call – costs 1 quota unit 📈
        id=channel_id,
        ch_resp = youtube.channels().list(
            part="snippet"
        ).execute()
        ch_snip = ch_resp["items"][0]["snippet"]

        result = {
            "service":     "youtube",
            "source":      ch_snip.get("title", "YouTube"),
            "channelHandle": ch_snip.get("customUrl"),        
            "channelThumb":  ch_snip["thumbnails"]["default"]["url"],           
            "id":          video_id,
            "title":       snippet["title"],
            "description": snippet.get("description", ""),
            "url":         f"https://www.youtube.com/watch?v={video_id}",
            "date":        snippet["publishedAt"],
        }
        results.append(result)
    return results
