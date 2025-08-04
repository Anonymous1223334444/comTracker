# presse_service/extractors/rts.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

def get_articles():
    base_url = "https://www.rts.sn"
    resp = requests.get(base_url, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    articles = []

    # 1) Trouver le header "A LA UNE" (ASCII) en h2 ou h3
    header = soup.find(
        lambda t: t.name in ('h2','h3')
                  and 'A LA UNE' in t.get_text(strip=True).upper()
    )
    # 2) Parcourir tous les siblings jusqu'au prochain header
    if header:
        for sib in header.find_next_siblings():
            if sib.name in ('h2','h3'):
                break
            for a in sib.find_all('a', href=True):
                href = urljoin(base_url, a['href'])
                if '/actualites/' not in href:
                    continue
                title = a.get_text(strip=True)
                if not title:
                    continue
                articles.append({
                    "id": href,
                    "date": datetime.now().isoformat(),
                    "source": "rts",
                    "texte": title,
                    "métadonnées":{"url": href}
                })

    # 3) Fallback : mêmes critères sur tout le document
    if not articles:
        for a in soup.find_all('a', href=True):
            href = urljoin(base_url, a['href'])
            title = a.get_text(strip=True)
            if '/actualites/' in href and len(title) > 20:
                articles.append({
                    "id": href,
                    "date": datetime.now().isoformat(),
                    "source": "rts",
                    "texte": title,
                    "métadonnées":{"url": href}
                })

    return articles
