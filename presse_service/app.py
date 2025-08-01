from flask import Flask, request, jsonify
from extractors import get_extractor, list_extractors
import os, re, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import save_articles
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/collect", methods=["GET"])
def collect():
    site = request.args.get("site")
    if not site:
        return jsonify({"error": "Missing `site` parameter"}), 400
    try:
        extractor = get_extractor(site)
    except ImportError:
        return jsonify({"error": f"Unknown site '{site}'"}), 400

    articles = extractor()
    path = save_articles(articles)
    return jsonify(
        {"status": "ok", "count": len(articles), "fichier": path}
    )

@app.route("/articles", methods=["GET"])
def articles():
    """
    Agrège tous les articles des extracteurs presse
    /articles?service=gfm&rts...&q=&exclude=
    """
    service = request.args.get("service")
    q  = request.args.get("q", "").lower()
    # split on comma or ANY whitespace
    ex = [w for w in re.split(r"[,\s]+", request.args.get("exclude", "").lower()) if w]

    results  = []
    targets  = [service] if service else list_extractors()

    for svc in targets:
        try:
            extractor = get_extractor(svc)
            for a in extractor():
                title_desc = f"{a.get('title','')} {a.get('description','')}".lower()

                # positive filter
                if q and q not in title_desc:
                    continue
                # negative filter
                if ex and any(word in title_desc for word in ex):
                    continue

                a["service"] = svc
                results.append(a)
        except ImportError:
            continue
    return jsonify(results)


if __name__ == "__main__":
    app.run(port=5005, debug=True)
