"""
Amazon Listing Databank Converter — Streamlit web application.
"""
import os
import streamlit as st

from core.brand_mapper import BrandMapper
from core.excel_processor import load_data
from core.fuzzy_matcher import build_brand_rows

from components.dashboard import render_dashboard
from components.upload import render_upload
from components.brand_manager import render_brand_manager
from components.reports import render_convert_button, render_results
from theme import page_header

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPPING_FILE = os.path.join(HERE, "data", "brand_mapping.json")

def _init_state():
    defaults = {
        "xl": None, "file_name": None, "file_key": None,
        "sheet_names": [], "selected_sheets": [], "master_df": None,
        "brand_rows": None, "convert_result": None, "mapping_dirty": False,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

_init_state()

@st.cache_resource(show_spinner=False)
def get_mapper(path: str) -> BrandMapper:
    return BrandMapper(path)

mapper = get_mapper(MAPPING_FILE)

# ----------------------------------------------------------------------
# Local Sidebar
# ----------------------------------------------------------------------
with st.sidebar:
    st.divider()
    st.markdown("### 📦 Databank Converter")
    st.markdown("**Mapping File**")
    st.code("data/brand_mapping.json", language="text")
    st.caption(f"Aliases: {len(mapper.aliases)}  •  Disabled: {len(mapper.disabled_aliases)}")

    with st.expander("ℹ️ Persistence note"):
        st.markdown(
            "Streamlit Community Cloud uses an **ephemeral filesystem**. "
            "Download the JSON backup from the Brand Mapping Manager to preserve mappings."
        )

# ----------------------------------------------------------------------
# Main Content Area
# ----------------------------------------------------------------------
page_header("📦", "Amazon Listing Databank Converter",
            "Standardize brand names across Excel worksheets and export clean, per-brand CSVs for your Databank.",
            eyebrow="Data Converter")

# Tabs for the different phases of the app
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard", 
    "📤 Upload & Analyze", 
    "⚙️ Brand Mapping Manager", 
    "📥 Convert & Export"
])

def _compute_stats():
    rows = st.session_state.get("brand_rows") or []
    master = st.session_state.get("master_df")
    total_records = len(master) if master is not None else 0
    unique_brands = len(rows)
    duplicates = sum(1 for r in rows if r["Match_Type"] in ("Fuzzy Auto-Merge", "Formatting", "Manual Merge", "JSON Alias"))
    approved = sum(1 for r in rows if r["Status"] == "Approved")
    needs_review = sum(1 for r in rows if r["Status"] == "Needs Review")
    disabled = sum(1 for r in rows if r["Status"] == "Excluded")
    return {
        "total_records": total_records, "unique_brands": unique_brands,
        "duplicates_detected": duplicates, "approved_mappings": approved,
        "needs_review": needs_review, "disabled_2p": disabled,
        "file_name": st.session_state.get("file_name"),
        "sheets_selected": len(st.session_state.get("selected_sheets") or []),
        "mapping_file": "data/brand_mapping.json",
    }

stats = _compute_stats()

with tab1:
    render_dashboard(stats)

with tab2:
    uploaded, xl, selected = render_upload()
    if xl is not None and selected:
        if st.button("🔎 Analyze Brands", type="primary"):
            with st.spinner("Reading Excel and analyzing brands..."):
                try:
                    master = load_data(xl, selected, mapper)
                    rows, brand_stats = build_brand_rows(master, mapper)

                    st.session_state["master_df"] = master
                    st.session_state["brand_rows"] = rows
                    st.session_state["convert_result"] = None

                    st.success(
                        f"Loaded {len(master):,} rows across {len(selected)} sheet(s). "
                        f"Found {len(rows)} unique brands."
                    )
                    st.json(brand_stats)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    if st.session_state.get("master_df") is not None:
        with st.expander("Preview processed data", expanded=False):
            st.dataframe(
                st.session_state["master_df"].head(50),
                use_container_width=True,
                hide_index=True,
            )

with tab3:
    render_brand_manager(mapper)

with tab4:
    render_convert_button(mapper)
    render_results()