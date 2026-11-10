"""
Fuzzy duplicate detection using SequenceMatcher at 90% threshold,
plus frequency-based canonical selection.
Preserves original _build_rows behavior.
"""
from difflib import SequenceMatcher

from core.brand_normalizer import normalize_brand, is_sku_like, is_2p_brand


def build_brand_rows(master, mapper):
    """Given a DataFrame with a Brand column and a BrandMapper, return
    (rows, stats) exactly matching the Tkinter app's _build_rows."""
    vc = master["Brand"].astype(str).str.strip().value_counts()
    raw_list = [str(x) for x in vc.index]
    freq = {str(k): int(v) for k, v in vc.items()}

    norm_groups = {}
    for raw in raw_list:
        n = normalize_brand(raw)
        norm_groups.setdefault(n, []).append(raw)

    display = {n: max(vars, key=lambda r: freq.get(r, 0)) for n, vars in norm_groups.items()}

    # Apply JSON aliases (respect disabled)
    for n in list(display):
        canon, disabled = mapper.lookup(display[n])
        if disabled:
            continue
        if canon is not None:
            display[n] = canon

    merged = dict(display)
    canon_keys = [
        k
        for k in display
        if not is_sku_like(display[k])
        and normalize_brand(k) not in mapper.disabled_aliases
        and not is_2p_brand(display[k])
    ]
    for i, a in enumerate(canon_keys):
        for b in canon_keys[i + 1 :]:
            ca, cb = display[a], display[b]
            if ca == cb:
                merged[b] = ca
                continue
            sim = SequenceMatcher(None, normalize_brand(ca), normalize_brand(cb)).ratio()
            if sim >= 0.90:
                if freq.get(cb, 0) > freq.get(ca, 0):
                    merged[a] = cb
                else:
                    merged[b] = ca

    rows = []
    for raw in raw_list:
        n = normalize_brand(raw)
        canon, disabled = mapper.lookup(raw)

        if disabled:
            canon = canon or raw
            mt, status = "Disabled (2P)", "Excluded"
        elif is_sku_like(raw):
            canon = merged.get(n, raw)
            mt, status = "Suspicious (SKU)", "Needs Review"
        elif canon is not None:
            mt, status = "JSON Alias", "Approved"
        else:
            canon = merged.get(n, raw)
            if canon != raw and normalize_brand(canon) != n:
                mt, status = "Fuzzy Auto-Merge", "Approved"
            elif canon != raw:
                mt, status = "Formatting", "Approved"
            else:
                mt, status = "Exact", "Approved"

        rows.append(
            dict(
                Original_Brand=raw,
                Canonical_Brand=canon,
                Match_Type=mt,
                Status=status,
            )
        )

    stats = {
        "Total Unique Brands Extracted": len(raw_list),
        "JSON Alias Hits": sum(1 for r in rows if r["Match_Type"] == "JSON Alias"),
        "Disabled/2P Excluded": sum(1 for r in rows if r["Match_Type"] == "Disabled (2P)"),
    }
    return rows, stats