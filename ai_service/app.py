from __future__ import annotations

import os, json, importlib
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

# ----------------------------------------------------------------------
# Dynamic import so we can support both SDK versions -------------------
# ----------------------------------------------------------------------
if importlib.util.find_spec("openai") and not importlib.util.find_spec("openai._client"):
    # === 0.27.x style =====================================================
    import openai

    openai.api_key = os.getenv("OPENAI_API_KEY")

    def _stream_completion(prompt: str):
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Réponds en français."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            temperature=0.3,
            stream=True,
        )
        for chunk in resp:
            token = chunk.choices[0].delta.get("content")
            if token:
                yield token

else:
    # === ≥ 1.0 style ======================================================
    from openai import OpenAI, OpenAIError

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _stream_completion(prompt: str):
        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                {"role": "system", "content": "Réponds en français."},
                {"role": "user", "content": prompt},
            ],
                max_tokens=1000,
                temperature=0.3,
            )
            for chunk in stream:
                token = chunk.choices[0].delta.content
                if token:
                    yield token
        except OpenAIError as e:
            raise RuntimeError(str(e)) from e


# ----------------------------------------------------------------------
app = Flask(__name__)
CORS(app)


@app.route("/report", methods=["POST"])
def report():
    data = request.get_json(silent=True) or {}
    articles = data.get("articles", [])[:20]
    stats = data.get("stats", {})
    if not articles:
        return jsonify({"error": "no articles supplied"}), 400

    text_block = "\n\n".join(
        f"{a.get('title','')} – {a.get('description','')}" for a in articles
    )

    parts = []
    total = stats.get("totalMentions")
    if total is not None:
        parts.append(f"Total mentions: {total}")
    top_sources = stats.get("topSources") or []
    if top_sources:
        parts.append(
            "Top sources: "
            + ", ".join(f"{s['name']} ({s['count']})" for s in top_sources)
        )
    timeline = stats.get("timeline") or []
    if timeline:
        parts.append(
            "Timeline: "
            + ", ".join(f"{t['date']}: {t['count']}" for t in timeline)
        )
    sent = stats.get("sentiment") or {}
    if sent:
        parts.append(
            "Sentiment distribution: "
            + ", ".join(f"{k}: {v}" for k, v in sent.items())
        )
    stats_block = "\n".join(parts)

    prompt = (
        "Tu es un analyste médias. En t'inspirant du style des rapports Brand24, "
        "rédige en français un compte rendu structuré des articles suivants avec les sections "
        "'Résumé', 'Tendances', 'Points saillants' et 'Recommandation'. "
        "Indique également un sentiment global (positif, neutre ou négatif). "
        "Réponds STRICTEMENT en JSON avec les clés 'summary' et 'sentiment'. "
        "La clé 'summary' doit contenir le rapport en Markdown avec paragraphes ou listes à puces si nécessaire."
        + stats_block
        + "\n\n"
        + text_block
        + "\n\nJSON:"
        + "\n\nRespond ONLY in JSON with keys 'summary' and 'sentiment'.\nJSON:"
    )

    def generate():
        try:
            for token in _stream_completion(prompt):
                yield f"data: {token}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return Response(generate(), mimetype="text/event-stream")

# ----------------------------------------------------------------------
if __name__ == "__main__":
    app.run(port=5007, debug=True)
