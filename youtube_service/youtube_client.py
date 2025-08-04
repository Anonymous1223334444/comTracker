"""
Client léger pour interroger l’API YouTube.

Deux fonctions :
* fetch_videos : rapide, sans appel supplémentaire, idéal pour /articles
* search_youtube : version “riche” (récupère aussi la vignette du channel)
"""

import requests
from googleapiclient.discovery import build
from config import YOUTUBE_API_KEY

# ---------------------------------------------------------------------
def fetch_videos(q: str, n: int = 10):
    """
    Renvoie les `n` vidéos les plus récentes contenant `q`.

    Clés retournées :
      title, description, videoId, publishedAt, channelTitle
    """
    url = "https://www.googleapis.com/youtube/v3/search"
    videos, next_token = [], None

    while len(videos) < n:
        params = {
            "key":        YOUTUBE_API_KEY,
            "q":          q,
            "part":       "snippet",
            "type":       "video",
            "order":      "date",
            "maxResults": min(50, n - len(videos)),
        }
        if next_token:
            params["pageToken"] = next_token

        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        for it in data.get("items", []):
            snip = it["snippet"]
            videoId = it["id"]["videoId"]
            videos.append(
                {
                    "title":        snip["title"],
                    "description":  snip.get("description", ""),
                    "videoId":      it["id"]["videoId"],
                    "publishedAt":  snip["publishedAt"],
                    "url":           f"https://www.youtube.com/watch?v={videoId}",
                    "channelTitle": snip.get("channelTitle", ""),
                }
            )
            if len(videos) >= n:
                break

        next_token = data.get("nextPageToken")
        if not next_token:
            break

    return videos


# ---------------------------------------------------------------------
def search_youtube(query, max_results=20):
    """Version “riche” (utilisée par /collect) – garde ton code existant."""
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    req = youtube.search().list(
        q=query, part="snippet", type="video", maxResults=max_results
    )
    resp = req.execute()

    results = []
    for item in resp["items"]:
        snip      = item["snippet"]
        video_id  = item["id"]["videoId"]
        channel_id = snip["channelId"]

        ch_resp = youtube.channels().list(part="snippet", id=channel_id).execute()
        ch_snip = ch_resp["items"][0]["snippet"]

        results.append(
            {
                "service":       "youtube",
                "source":        ch_snip.get("title", "YouTube"),
                "channelHandle": ch_snip.get("customUrl"),
                "channelThumb":  ch_snip["thumbnails"]["default"]["url"],
                "id":            video_id,
                "title":         snip["title"],
                "description":   snip.get("description", ""),
                "url":           f"https://www.youtube.com/watch?v={video_id}",
                "date":          snip["publishedAt"],
            }
        )
    print(results[0])
    return results

