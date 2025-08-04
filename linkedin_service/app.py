from flask import Flask, request, jsonify
from flask_cors import CORS
import os, re, json, sys
from datetime import datetime, date
from dateutil import parser
from linkedin_client import search_posts, slugify
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.search import match_query
from utils.lang import detect_language, extract_country

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, expose_headers=["Content-Type"])

BASE = 'data'
os.makedirs(BASE, exist_ok=True)

def _path(query: str) -> str:
    return f"{BASE}/{slugify(query)}.json"

def _save(query: str, articles):
    with open(_path(query), 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

def _load(query: str):
    path = _path(query)
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        return json.load(f)

@app.route('/collect', methods=['GET'])
def collect():
    q = request.args.get('q', '').lower()
    n = int(request.args.get('n', 1000))
    out = search_posts(q, n)
    _save(q, out)
    return jsonify({'status': 'ok', 'count': len(out)})

@app.route('/articles', methods=['GET'])
def articles():
    q              = request.args.get('q', '').lower()
    ex             = [w for w in re.split(r"[,\s]+", request.args.get('exclude', '').lower()) if w]
    lang_filter    = request.args.get('lang', '').lower()
    country_filter = request.args.get('country', '').lower()
    n              = int(request.args.get('n', 1000))

    start_str = request.args.get('start')
    start = parser.isoparse(start_str).date() if start_str else date(2023, 1, 1)
    end_str   = request.args.get('end')
    end       = parser.isoparse(end_str).date() if end_str else date.today()

    items = _load(q)
    if not items:
        items = search_posts(q, n)
        _save(q, items)

    normalized = []
    for a in items:
        title = a.get('title', '')
        desc  = a.get('description') or a.get('summary') or ''
        body  = f"{title}\n\n{desc}".strip()

        date_val = a.get('published') or a.get('publishedAt') or a.get('date')
        try:
            dt = parser.isoparse(date_val)
        except:
            continue
        if dt.date() < start or dt.date() > end: continue

        if not match_query(q, body.lower()): continue
        if ex and any(w in body.lower() for w in ex): continue
        
        lang = detect_language(body)
        if lang_filter and lang != lang_filter: continue

        url     = a.get('url') or a.get('link') or ''
        cc      = extract_country(url)
        if country_filter and cc != country_filter: continue

        normalized.append({
            'service':    'linkedin',
            'id':          a.get('id'),
            'title':       title,
            'description': desc,
            'url':         url,
            'date':        dt.isoformat(),
            'langue':      lang,
            'country':     cc
        })
    return jsonify(normalized)

if __name__ == "__main__":
    app.run(port=5006, debug=True)
