"""
JSON-backed brand mapping store.
Preserves original load/save/lookup semantics, plus helpers for
export/backup and the Streamlit UI.
"""
import json
import os
from typing import Dict, Tuple, Optional

from core.brand_normalizer import normalize_brand, is_2p_brand


class BrandMapper:
    def __init__(self, path: str):
        self.path = path
        self.aliases: Dict[str, str] = {}
        self.disabled_aliases: Dict[str, str] = {}
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.load()

    # ---------- persistence ----------
    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.get("aliases", {}).items():
                        self.aliases[normalize_brand(k)] = v
                    for k, v in data.get("disabled_aliases", {}).items():
                        self.disabled_aliases[normalize_brand(k)] = v
            except Exception:
                # corrupted file -> start fresh but keep backup
                try:
                    os.rename(self.path, self.path + ".bak")
                except Exception:
                    pass

    def save(self) -> bool:
        """Write JSON safely. Returns True on success."""
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "aliases": dict(sorted(self.aliases.items())),
                        "disabled_aliases": dict(sorted(self.disabled_aliases.items())),
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            os.replace(tmp, self.path)
            return True
        except Exception:
            return False

    def to_json_string(self) -> str:
        return json.dumps(
            {
                "aliases": dict(sorted(self.aliases.items())),
                "disabled_aliases": dict(sorted(self.disabled_aliases.items())),
            },
            indent=2,
            ensure_ascii=False,
        )

    # ---------- lookup ----------
    def lookup(self, raw) -> Tuple[Optional[str], bool]:
        """Return (canonical, is_disabled). Disabled takes precedence."""
        n = normalize_brand(raw)
        if n in self.disabled_aliases:
            return self.disabled_aliases[n], True
        if n in self.aliases:
            canon = self.aliases[n]
            if is_2p_brand(canon):
                return canon, True
            return canon, False
        if is_2p_brand(raw):
            return None, True
        return None, False

    def is_disabled(self, raw) -> bool:
        _, disabled = self.lookup(raw)
        return disabled

    # ---------- mutation ----------
    def set_alias(self, original: str, canonical: str):
        self.aliases[normalize_brand(original)] = canonical

    def set_disabled(self, original: str, canonical: str):
        self.disabled_aliases[normalize_brand(original)] = canonical

    def remove_alias(self, original: str):
        n = normalize_brand(original)
        self.aliases.pop(n, None)

    # ---------- import / export ----------
    def import_csv(self, df) -> int:
        """Import Original_Brand / Canonical_Brand columns. Returns count."""
        import pandas as pd  # local import to keep module light
        if not isinstance(df, pd.DataFrame):
            return 0
        if "Original_Brand" not in df.columns or "Canonical_Brand" not in df.columns:
            raise ValueError("CSV must have 'Original_Brand' and 'Canonical_Brand' columns.")
        count = 0
        for _, row in df.iterrows():
            orig = str(row["Original_Brand"]).strip()
            canon = str(row["Canonical_Brand"]).strip()
            if orig and canon and orig.lower() != "nan" and canon.lower() != "nan":
                self.set_alias(orig, canon)
                count += 1
        return count