"""
Brand normalization and detection helpers.
Preserves the original Tkinter app's normalization logic exactly.
"""
import re
import unicodedata

SKU_STRONG_RE = re.compile(r"[A-Za-z]+\-[A-Za-z]?\d{5,}", re.IGNORECASE)
TWO_P_RE = re.compile(r"\b2p\b", re.IGNORECASE)


def strip_accents(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in s if not unicodedata.combining(c))


def normalize_brand(name) -> str:
    if not name:
        return ""
    s = strip_accents(name).lower().strip()
    s = s.replace("&", " and ")
    s = re.sub(r"[\-_]+", " ", s)
    s = re.sub(r"\(.*?\)", "", s)
    s = s.replace(".", " ").replace("'", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def is_sku_like(raw) -> bool:
    raw = str(raw)
    return bool(SKU_STRONG_RE.search(raw)) or (
        raw.count("-") + raw.count("_") >= 2 and bool(re.search(r"\d{4,}", raw))
    )


def is_2p_brand(name) -> bool:
    """Detect any brand string that should be excluded as a '2P' variant."""
    return bool(TWO_P_RE.search(normalize_brand(name)))


def safe_name(s) -> str:
    s = re.sub(r"[^\w\-]+", "_", str(s).strip(), flags=re.UNICODE)
    return s.strip("_") or "Unknown_Brand"