# import feedparser
# from datetime import datetime
# import os
# import hashlib
# import json


# def parse_rss(url):
#     feed = feedparser.parse(url)
#     articles = []
#     for entry in feed.entries:
#         uid = hashlib.md5(entry.link.encode()).hexdigest()
#         article = {
#             "id": uid,
#             "date": entry.published if "published" in entry else datetime.utcnow().isoformat(),
#             "source": "rss",
#             "texte": entry.title + "\n\n" + entry.get("summary", ""),
#             "métadonnées": {
#                 "lien": entry.link,
#                 "source_title": feed.feed.get("title", ""),
#                 "tags": [tag["term"] for tag in entry.get("tags", [])] if "tags" in entry else []
#             }
#         }
#         articles.append(article)
#     return articles

# def collect_all(feeds_file="feeds.txt"):
#     articles = []
#     with open(feeds_file, "r") as f:
#         urls = f.read().splitlines()
#     for url in urls:
#         articles.extend(parse_rss(url))
#     return articles

# def save_articles(articles):
#     date = datetime.now().strftime("%Y-%m-%d")
#     folder = f"data/raw/{date}"
#     os.makedirs(folder, exist_ok=True)
#     path = os.path.join(folder, "rss_articles.json")
#     with open(path, "w", encoding="utf-8") as f:
#         json.dump(articles, f, ensure_ascii=False, indent=2)
#     return path


import feedparser
from datetime import datetime
import os
import hashlib
import json

# --- Paramètres personnalisables ---
KEYWORDS = ["sonko", "diomaye", "newdealtechnologique", "mntc"]
START_DATE = datetime(2025, 7, 1)  # articles à partir de cette date

def contains_keywords(text):
    text = text.lower()
    return any(kw in text for kw in KEYWORDS)

def parse_rss(url):
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        pub_date = None
        if "published_parsed" in entry and entry.published_parsed:
            pub_date = datetime(*entry.published_parsed[:6])
        elif "updated_parsed" in entry and entry.updated_parsed:
            pub_date = datetime(*entry.updated_parsed[:6])
        else:
            continue  # impossible de déterminer la date

        if pub_date < START_DATE:
            continue  # trop ancien

        title = entry.title
        summary = entry.get("summary", "")
        full_text = title + "\n\n" + summary

        if not contains_keywords(full_text):
            continue  # pas pertinent

        uid = hashlib.md5(entry.link.encode()).hexdigest()
        article = {
            "id": uid,
            "date": pub_date.isoformat(),
            "source": "rss",
            "texte": full_text,
            "métadonnées": {
                "lien": entry.link,
                "source_title": feed.feed.get("title", ""),
                "tags": [tag["term"] for tag in entry.get("tags", [])] if "tags" in entry else []
            }
        }
        articles.append(article)
    return articles

def collect_all(feeds_file="feeds.txt"):
    articles = []
    with open(feeds_file, "r") as f:
        urls = f.read().splitlines()
    for url in urls:
        articles.extend(parse_rss(url))
    return articles

def fetch_rss_articles(feeds_file="feeds.txt"):
    articles = []
    with open(feeds_file, encoding="utf-8") as f:
        feed_urls = [line.strip() for line in f if line.strip()]

    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # 1) déterminer la date de publication
            pub_date = None
            if getattr(entry, "published_parsed", None):
                pub_date = datetime(*entry.published_parsed[:6])
            elif getattr(entry, "updated_parsed", None):
                pub_date = datetime(*entry.updated_parsed[:6])
            else:
                continue

            # 2) date >= START_DATE ?
            if pub_date < START_DATE:
                continue

            # 3) constituer le texte à filtrer
            title   = entry.get("title", "")
            summary = entry.get("summary", "")
            full_text = f"{title}\n\n{summary}"

            # 4) mot-clé présent ?
            if not contains_keywords(full_text):
                continue

            # 5) on normalise le format pour le frontend
            articles.append({
                "title":     title,
                "link":      entry.get("link"),
                "published": pub_date.isoformat()
            })

    return articles

def save_articles(articles):
    date = datetime.now().strftime("%Y-%m-%d")
    folder = f"data/raw/{date}"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "rss_articles_filtered.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    return path
