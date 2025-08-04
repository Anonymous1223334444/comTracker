from flask import Flask, request, jsonify
from flask_cors import CORS
import re, sys, os
from datetime import datetime, date
from dateutil import parser
from twitter_client import fetch_tweets
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.search import match_query
from utils.lang import detect_language, extract_country

app = Flask(__name__)
CORS(app)

@app.route('/articles', methods=['GET'])
def articles():
    q              = request.args.get('q', '')
    ex             = [w for w in re.split(r"[,\s]+", request.args.get('exclude', '').lower()) if w]
    lang_filter    = request.args.get('lang', '').lower()
    country_filter = request.args.get('country', '').lower()
    n              = int(request.args.get('n', 200))  # fetch at least 200 tweets

    # default date window Jan 1, 2023 - today
    start_str = request.args.get('start')
    start = parser.isoparse(start_str).date() if start_str else date(2023, 1, 1)
    end_str = request.args.get('end')
    end = parser.isoparse(end_str).date() if end_str else date.today()

    tweets = fetch_tweets(q, n)
    normalized = []
    for t in tweets:
        text = t.get('text', '')
        dt = None
        try:
            dt = parser.isoparse(t.get('created_at'))
        except:
            try:
                dt = parser.parse(t.get('created_at'))
            except:
                dt = None
        if not dt or dt.date() < start or dt.date() > end:
            continue
        if not match_query(q, text.lower()):
            continue
        if ex and any(w in text.lower() for w in ex):
            continue

        lang = detect_language(text)
        if lang_filter and lang != lang_filter:
            continue

        url = f"https://twitter.com/i/web/status/{t.get('id_str')}"
        cc  = extract_country(url)
        if country_filter and cc != country_filter:
            continue

        normalized.append({
            'service': 'twitter',
            'id':       t.get('id_str'),
            'title':    text,
            'url':      url,
            'date':     dt.isoformat(),
            'langue':   lang,
            'country':  cc
        })
    return jsonify(normalized)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
