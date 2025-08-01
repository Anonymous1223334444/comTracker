from flask import Flask, request, jsonify
from flask_cors import CORS
import os, json
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
CORS(app)

@app.route('/report', methods=['POST'])
def report():
    data = request.get_json() or {}
    articles = data.get('articles', [])[:20]
    text = "\n\n".join(
        f"{a.get('title','')} - {a.get('description','')}" for a in articles
    )
    prompt = (
        "Summarize the following articles and give an overall sentiment "
        "(positive, neutral or negative). "
        "Respond in JSON with keys 'summary' and 'sentiment'.\n\n" + text + "\n\nJSON:"
    )
    try:
        resp = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=300,
            temperature=0.3,
        )
        content = resp.choices[0].message.content.strip()
        try:
            result = json.loads(content)
        except Exception:
            result = {'summary': content, 'sentiment': ''}
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5007, debug=True)