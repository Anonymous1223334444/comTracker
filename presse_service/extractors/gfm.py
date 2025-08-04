# presse_service/extractors/gfm.py

import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

def get_articles():
    base_url = "https://www.gfm.sn"
    # cloudscraper simule un vrai navigateur et gère Cloudflare
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    resp = scraper.get(base_url, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    articles = []

    # Extraction via <article> si dispo
    for art in soup.find_all('article'):
        link = art.find('a', href=True)
        if not link: continue
        href = urljoin(base_url, link['href'])
        title = link.get_text(strip=True)
        if not title or base_url not in href: continue

        # date ISO si <time datetime="...">
        date = datetime.now().isoformat()
        time_tag = art.find('time')
        if time_tag and time_tag.has_attr('datetime'):
            date = time_tag['datetime']

        articles.append({
            "id": href, "date": date,
            "source": "gfm", "texte": title,
            "métadonnées":{"url": href}
        })

    # Fallback sur liens internes avec titre significatif
    if not articles:
        for link in soup.find_all('a', href=True):
            href = urljoin(base_url, link['href'])
            title = link.get_text(strip=True)
            if len(title) < 20: continue
            if not href.startswith(base_url): continue
            articles.append({
                "id": href,
                "date": datetime.now().isoformat(),
                "source": "gfm",
                "texte": title,
                "métadonnées":{"url": href}
            })

    return articles
