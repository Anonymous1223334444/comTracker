from langdetect import detect_langs
import tldextract


def detect_language(text: str, threshold: float = 0.8) -> str:
    """Detect language of text. Returns '' if unsure."""
    try:
        langs = detect_langs(text)
        if not langs:
            return ''
        best = langs[0]
        return best.lang if best.prob >= threshold else ''
    except Exception:
        return ''


def extract_country(url: str) -> str:
    """Return two-letter country code from URL suffix if available."""
    if not url:
        return ''
    ext = tldextract.extract(url)
    last = ext.suffix.split('.')[-1].lower()
    if len(last) == 2:
        return last
    return 'us' if last == 'com' else ''