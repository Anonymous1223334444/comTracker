from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os, re, sys, json

# chemin vers utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.search import match_query                         # noqa: E402
from youtube_client import fetch_videos, search_youtube      # noqa: E402

app = Flask(__name__)
CORS(app)  # autorise le front-end

# -------------------------------------------------------------------------
# Route de collecte “brute” (inchangée)
# -------------------------------------------------------------------------
@app.route("/collect", methods=["GET"])
def collect_youtube():
    query       = request.args.get("q")
    max_results = int(request.args.get("n", 20))

    if not query:
        return jsonify({"error": "Paramètre 'q' manquant"}), 400

    videos = search_youtube(query, max_results)

    date   = datetime.now().strftime("%Y-%m-%d")
    folder = f"data/raw/{date}"
    os.makedirs(folder, exist_ok=True)
    path   = f"{folder}/{query.replace(' ', '_')}_youtube.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "ok", "count": len(videos), "fichier": path})


# -------------------------------------------------------------------------
# Route utilisée par le front-end
# -------------------------------------------------------------------------
@app.route("/articles", methods=["GET"])
def articles():
    q   = request.args.get("q", "")
    ex  = [w for w in re.split(r"[,\s]+", request.args.get("exclude", "").lower()) if w]
    n   = int(request.args.get("n", 1000))

    videos = fetch_videos(q, n)

    results = []
    for v in videos:
        title = v["title"]

        # filtre inclure / exclure
        if q and not match_query(q, title):
            continue
        if ex and any(w in title.lower() for w in ex):
            continue

        results.append(
            {
                "service": "youtube",
                "id": v["videoId"],
                "title": title,
                "date": v["publishedAt"],
                "texte": title,
                "auteur": v.get("channelTitle", ""),
                "url": f"https://www.youtube.com/watch?v={v['videoId']}",
                
            }
        )

    return jsonify(results)


if __name__ == "__main__":
    app.run(port=5004, debug=True)
