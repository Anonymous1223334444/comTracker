from serpapi import GoogleSearch
from dateutil import parser, relativedelta
from datetime import datetime, timedelta
from config import SERPAPI_KEY, MAX_RESULTS
import re
import unicodedata as ud 

def search_posts(query: str, max_posts: int = MAX_RESULTS):
    """
    Fetch public LinkedIn posts via SerpAPI's LinkedIn Public
    Search Results API. Falls back gracefully if a timestamp
    can't be parsed.
    """
    keywords = [k.strip() for k in re.split(r"[,\s]+", query) if k.strip()]
    all_posts = []
    for kw in keywords:
        start = 0
        while len(all_posts) < max_posts:
            params = {
                "engine": "google",
                "q": f'site:linkedin.com/posts intitle:"{kw}"',
                "api_key": SERPAPI_KEY,
                "num": min(100, max_posts - len(all_posts)),
                "start": start,
            }
            data = GoogleSearch(params).get_dict()
            posts = data.get("organic_results", [])
            if not posts:
                break
            all_posts += posts
            start += 100
            if len(posts) < 100:
                break

    # deduplicate across several keywords
    seen = set()
    posts = []
    for p in all_posts:
        url = p.get("link")
        if url in seen:
            continue
        seen.add(url)
        posts.append(p)

    results = []
    # ------------------------------------------------------------------
    # Robust conversion of SerpAPI’s fuzzy “date” field
    #  • “Today” / “Aujourd’hui”
    #  • “Yesterday”
    #  • “3h”, “2d”, “4w”, …
    # ------------------------------------------------------------------
    _REL_RX = re.compile(r"(?P<num>\d+)\s*(?P<unit>[hdwmy])", re.I)

    def _norm(raw: str) -> datetime:
        raw = (raw or "").strip().lower()
        now = datetime.utcnow()
        if raw in ("today", "aujourd'hui", "aujourd'hui"):
            return now
        if raw == "yesterday":
            return now - timedelta(days=1)
        m = _REL_RX.fullmatch(raw)
        if m:
            num = int(m["num"])
            u   = m["unit"]
            return (
                now - (timedelta(hours=num)        if u == "h" else
                       timedelta(days=num)         if u == "d" else
                       timedelta(weeks=num)        if u == "w" else
                       relativedelta.relativedelta(months=num) if u == "m" else
                       relativedelta.relativedelta(years=num)) # “y”
            )
        # last resort: dateutil.parse or fall back to now
        try:
            return parser.parse(raw)
        except Exception:
            return now

    for p in posts:
        date_iso = _norm(p.get("date")).isoformat()

        results.append({
            "service":     "linkedin",
            "source":      p.get("source") or "LinkedIn", 
            "id":          p.get("position"),
            "title":       p.get("title") or "",
            "description": p.get("snippet") or "",
            "url":         p.get("link"),
            "date":        date_iso,
        })
    return results


_slug_re = re.compile(r"[^a-z0-9]+")
def slugify(text: str) -> str:
    """
    Convert arbitrary text (query string) to a safe filename / URL slug.

    Examples
    --------
    >>> slugify("Sonko, Diomaye Faye")
    'sonko-diomaye-faye'
    >>> slugify("newdealtechnologique")
    'newdealtechnologique'
    """
    if not text:
        return "untitled"

    # 1) Unicode → ASCII, lowercase
    text = (
        ud.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )

    # 2) replace every run of non-alphanumerics with a single “-”
    text = _slug_re.sub("-", text).strip("-")

    return text or "untitled"
