def get_extractor(site):
    if site == "gfm":
        from .gfm import get_articles
    elif site == "rts":
        from .rts import get_articles
    elif site == "senepeople":
        from .senepeople import get_articles
    elif site == "lequotidien":
        from .lequotidien import get_articles
    else:
        raise ImportError("Unknown site")
    return get_articles

def list_extractors():
    """
    Renvoie la liste des services supportés par get_extractor().
    Utile pour /articles sans paramètre.
    """
    return ["gfm", "rts", "senepeople", "lequotidien"]