from flask import Flask, request, jsonify
from flask_cors import CORS
from dateutil import parser
from datetime import datetime, date
import tldextract
from langdetect import detect
from youtube_client import fetch_videos

app = Flask(__name__)
CORS(app)

@app.route("/articles", methods=["GET"])
def articles():
    q              = request.args.get("q","")
    lang_filter    = request.args.get("lang","english").lower()
    country_filter = request.args.get("country","").lower()
    n              = int(request.args.get("n", 200))  # fetch at least 200 videos

    # default date window Jan 1, 2023 - today
    start_str = request.args.get('start')
    start = parser.isoparse(start_str).date() if start_str else date(2023, 1, 1)
    end_str = request.args.get('end')
    end = parser.isoparse(end_str).date() if end_str else date.today()

    raw = fetch_videos(q, n)
    normalized = []

    for item in raw:
        title       = item.get("title","")
        description = item.get("description","")
        body        = f"{title}\n\n{description}".strip()

        # language detection & filter
        try:
            lang = detect(body)
        except:
            lang = ""
        if lang_filter and lang != lang_filter: continue

        # date filter
        try:
            dt = parser.isoparse(item.get("date"))
        except:
            continue
        if dt.date() < start or dt.date() > end: continue

        # country detection & filter
        vid = item.get("id")
        url = item.get("url", f"https://www.youtube.com/watch?v={vid}")
        ext = tldextract.extract(url)
        parts = ext.suffix.split('.')
        last  = parts[-1]
        cc    = last if len(last)==2 else ''
        if country_filter and cc != country_filter: continue

        normalized.append({
            "service":   "youtube",
            "id":         vid,
            "date":       dt.isoformat(),
            "texte":      body,
            "metadonnees": {
                "auteur": item.get("channelTitle",""),
                "url":     url
            },
            "langue":    lang,
            "country":   cc
        })

    return jsonify(normalized)

if __name__ == "__main__":
    app.run(port=5004, debug=True)

