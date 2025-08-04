from flask import Flask, request, jsonify
from rss_scraper import collect_all, save_articles, fetch_rss_articles
from flask_cors import CORS
import re, sys, os
from dateutil import parser
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.search import match_query
from langdetect import detect  # optional
import tldextract          # optional

app = Flask(__name__)
CORS(app)

@app.route("/collect", methods=["GET"])
def collect_rss():
    articles = collect_all("feeds.txt")
    path     = save_articles(articles)
    return jsonify({"status": "ok", "count": len(articles), "fichier": path})

@app.route('/articles')
def articles():
    q              = request.args.get('q','').lower()
    ex             = [w for w in re.split(r"[,\s]+", request.args.get('exclude','').lower()) if w]
    start_str      = request.args.get('start')
    start          = parser.isoparse(start_str).date() if start_str else date(2023,1,1)
    end_str        = request.args.get('end')
    end            = parser.isoparse(end_str).date() if end_str else date.today()

    arts = fetch_rss_articles()
    normalized = []
    for a in arts:
        title = a.get('title','')
        link  = a.get('link','')
        # date filter\        
        try:
            dt = parser.isoparse(a.get('published'))
        except:
            continue
        if dt.date() < start or dt.date() > end: continue
        # text filters
        if not match_query(q, title.lower()): continue
        if ex and any(w in title.lower() for w in ex): continue

        normalized.append({
            'service': 'rss',
            'title':   title,
            'url':     link,
            'date':    dt.isoformat()
        })
    return jsonify(normalized)

if __name__ == "__main__":
    app.run(port=5002, debug=True)
