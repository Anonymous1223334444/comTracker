import re

def match_query(q_raw: str, text: str) -> bool:
    """
    If q_raw contains commas we treat each chunk as an OR-keyword.
    Otherwise we consider the *whole* string a single phrase that
    must appear unchanged.

    Examples
    --------
    "Jonh Abraham Cena"       ➜  exact phrase match
    "jean,Abraham,Cena"       ➜  match any of the 3 tokens
    """
    q_raw = (q_raw or "").strip().lower()
    if not q_raw:
        return True         
    text = (text or "").lower()

    if "," in q_raw:         
        return any(kw and kw in text for kw in (k.strip() for k in q_raw.split(",")))
    else:                    
        norm_text = re.sub(r"\s+", " ", text)
        norm_q    = re.sub(r"\s+", " ", q_raw)
        return norm_q in norm_text
