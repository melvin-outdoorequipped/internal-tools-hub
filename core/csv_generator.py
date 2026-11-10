"""
CSV generation with row-count verification, mirroring _run() from the
Tkinter app but returning in-memory files for Streamlit download.
"""
import io
import zipfile
from typing import Dict, List, Tuple

import pandas as pd

from core.brand_normalizer import normalize_brand, safe_name


def apply_lookup(master: pd.DataFrame, current_rows: List[dict], mapper) -> pd.DataFrame:
    """Attach Clean_Brand column and drop disabled/2P rows."""
    lookup = {}
    for r in current_rows:
        if mapper.is_disabled(r["Canonical_Brand"]):
            continue
        lookup[normalize_brand(r["Original_Brand"])] = r["Canonical_Brand"]

    master = master.copy()
    master["Clean_Brand"] = (
        master["Brand"].astype(str).str.strip().map(lambda x: lookup.get(normalize_brand(x), x))
    )
    master = master[~master["Clean_Brand"].astype(str).apply(mapper.is_disabled)].copy()
    return master


def generate_csvs(master: pd.DataFrame, mapper) -> Tuple[Dict[str, bytes], List[dict], pd.DataFrame]:
    """
    Build per-brand CSVs (bytes), verification report rows, and audit DataFrame.
    Returns (files_dict, report_rows, audit_df).
    """
    counts = master["Clean_Brand"].value_counts().to_dict()
    counts = {b: c for b, c in counts.items() if not mapper.is_disabled(b)}

    files: Dict[str, bytes] = {}
    report: List[dict] = []

    for brand, excel_count in counts.items():
        brand_df = master[master["Clean_Brand"] == brand].drop(columns=["Clean_Brand"])
        buf = io.BytesIO()
        brand_df.to_csv(buf, index=False)
        buf.seek(0)
        data = buf.getvalue()

        # Verification: re-read from buffer
        try:
            csv_count = len(pd.read_csv(io.BytesIO(data)))
        except Exception:
            csv_count = -1

        status = "MATCH" if excel_count == csv_count else "MISMATCH!"
        files[f"{safe_name(brand)}.csv"] = data
        report.append(
            dict(Brand=str(brand), Excel_Rows=int(excel_count), CSV_Rows=int(csv_count), Status=status)
        )

    return files, report, pd.DataFrame(report) if report else pd.DataFrame()


def build_audit_df(current_rows: List[dict]) -> pd.DataFrame:
    return pd.DataFrame(current_rows)


def build_zip(files: Dict[str, bytes], audit_df: pd.DataFrame, report_df: pd.DataFrame) -> bytes:
    """Create a single ZIP containing all CSVs + audit + verification report."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
        if not audit_df.empty:
            z.writestr("_brand_mapping_audit.csv", audit_df.to_csv(index=False))
        if not report_df.empty:
            z.writestr("_verification_report.csv", report_df.to_csv(index=False))
    buf.seek(0)
    return buf.getvalue()