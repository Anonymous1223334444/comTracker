from flask import Flask, request, jsonify
import os, re, sys
from dateutil import parser
from datetime import datetime, date
from flask_cors import CORS

from reddit_client import fetch_reddit_posts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.search import match_query

from utils.lang import detect_language, extract_country

app = Flask(__name__)
CORS(app)

@app.route("/articles", methods=["GET"])
def articles():
    q              = request.args.get('q','')
    ex             = [w for w in re.split(r"[,\s]+", request.args.get('exclude','').lower()) if w]
    lang_filter    = request.args.get('lang','').lower()
    country_filter = request.args.get('country','').lower()
    n              = int(request.args.get('n', 1000))  # fetch at least 1000 posts by default

    # default date window Jan 1, 2023 - today
    start_str = request.args.get('start')
    start = parser.isoparse(start_str).date() if start_str else date(2023, 1, 1)
    end_str = request.args.get('end')
    end = parser.isoparse(end_str).date() if end_str else date.today()

    posts = fetch_reddit_posts(q, n)
    normalized = []
    for p in posts:
        title    = p.get('title','')
        selftext = p.get('selftext','')
        body     = f"{title}\n\n{selftext}".strip()

        # text filters
        if not match_query(q, body.lower()): continue
        if ex and any(w in body.lower() for w in ex): continue

        # date filter
        try:
            dt = datetime.fromtimestamp(float(p.get('created_utc'))).astimezone()
        except Exception:
            continue
        if dt.date() < start or dt.date() > end: continue

        # language detection & filter
        lang = detect_language(body)
        if lang_filter and lang != lang_filter: continue

        # country detection & filter
        url = p.get('url','')
        cc  = extract_country(url)
        if country_filter and cc != country_filter: continue

        normalized.append({
            'service': 'reddit',
            'title':   title,
            'url':     url,
            'date':    dt.isoformat(),
            'langue':  lang,
            'country': cc
        })

    return jsonify(normalized)

if __name__ == "__main__":
    app.run(port=5003, debug=True)
