"""Excel upload + sheet selection UI (with DOCT Databank sync)."""
import io
import pandas as pd
import streamlit as st

from core.excel_processor import load_workbook, read_sheet_names


def process_doct_file(file_bytes: bytes) -> tuple:
    """Processes the uploaded DOCT Excel file to get the SKU map and Brand list."""
    sku_map = {}
    brands = set()
    try:
        xl = pd.ExcelFile(io.BytesIO(file_bytes))
        # Hardcoded sheets based on DOCT structure
        sheets = ["Amazon1", "Amazon2", "SKUVault or 3PL", "FBA Inv"]
        
        for sheet in sheets:
            if sheet in xl.sheet_names:
                df = xl.parse(sheet)
                df.columns = [str(c).strip().lower() for c in df.columns]
                
                # 1. Build SKU -> Brand Map
                sku_col = next((c for c in df.columns if 'sku' in c), None)
                brand_col = next((c for c in df.columns if 'brand' in c), None)
                if sku_col and brand_col:
                    df_clean = df.dropna(subset=[sku_col, brand_col])
                    sheet_map = dict(zip(
                        df_clean[sku_col].astype(str).str.strip().str.upper(),
                        df_clean[brand_col].astype(str).str.strip()
                    ))
                    sku_map.update(sheet_map)
                
                # 2. Build Canonical Brand List
                for col in df.columns:
                    if 'brand' in str(col).lower():
                        b_vals = df[col].dropna().astype(str).str.strip().unique()
                        brands.update({b for b in b_vals if b.lower() not in ('nan', '')})
    except Exception as e:
        st.error(f"Error processing DOCT file: {e}")
        return {}, set()

    return sku_map, brands


def render_upload():
    # --------------------------------------------------------------
    # 1. DOCT DATABANK UPLOAD
    # --------------------------------------------------------------
    st.markdown("## 1. DOCT Databank")
    st.info("Upload the latest DOCT Excel file to sync brands and SKUs.")
    
    uploaded_doct = st.file_uploader(
        "Upload DOCT Excel", 
        type=["xlsx", "xlsm", "xls"], 
        key="doct_uploader",
        label_visibility="collapsed"
    )
    
    if uploaded_doct is not None:
        doct_key = f"{uploaded_doct.name}_{uploaded_doct.size}"
        if st.session_state.get("doct_file_key") != doct_key:
            with st.spinner("Syncing DOCT Data..."):
                sku_map, brands = process_doct_file(uploaded_doct.getvalue())
                
                st.session_state["doct_sku_map"] = sku_map
                st.session_state["doct_brands"] = brands
                st.session_state["doct_file_key"] = doct_key
                st.rerun()

    if st.session_state.get("doct_sku_map") is not None:
        brands_count = len(st.session_state.get("doct_brands", []))
        skus_count = len(st.session_state["doct_sku_map"])
        st.success(f"✅ DOCT Synced: **{brands_count}** Brands, **{skus_count}** SKUs")
    else:
        st.warning("⚠️ DOCT Databank not uploaded yet. Analysis will fail without it.")

    st.divider()

    # --------------------------------------------------------------
    # 2. MAIN EXCEL UPLOAD
    # --------------------------------------------------------------
    st.markdown("## 2. Excel Upload")
    uploaded = st.file_uploader(
        "Drag & drop your Excel file",
        type=["xlsx", "xlsm", "xls"],
        help="Supports .xlsx, .xlsm and .xls workbooks with one or more worksheets.",
    )

    if uploaded is None:
        return None, None, []

    file_key = f"{uploaded.name}_{uploaded.size}"

    if st.session_state.get("file_key") != file_key:
        with st.spinner(f"Reading workbook structure ({uploaded.size / (1024*1024):.1f} MB)… please wait."):
            try:
                uploaded.seek(0)
                xl = load_workbook(uploaded)
                sheet_names = read_sheet_names(xl)
            except Exception as e:
                st.error(f"Could not read workbook: {e}")
                return None, None, []

        st.session_state["file_key"] = file_key
        st.session_state["xl"] = xl
        st.session_state["file_name"] = uploaded.name
        st.session_state["sheet_names"] = sheet_names
        st.session_state["selected_sheets"] = list(sheet_names)
        st.session_state["master_df"] = None
        st.session_state["brand_rows"] = None
        st.session_state["convert_result"] = None
        st.rerun()

    xl = st.session_state["xl"]
    sheet_names = st.session_state["sheet_names"]
    file_size_mb = uploaded.size / (1024 * 1024)

    st.success(
        f"**File:** {st.session_state['file_name']}  •  "
        f"**{len(sheet_names)} worksheets**  •  **{file_size_mb:.1f} MB**"
    )

    st.markdown("### Select Worksheets")
    c1, c2, c3 = st.columns([1, 1, 4])
    if c1.button("Select All", use_container_width=True):
        st.session_state["selected_sheets"] = list(sheet_names)
        st.rerun()
    if c2.button("Clear All", use_container_width=True):
        st.session_state["selected_sheets"] = []
        st.rerun()

    selected = st.multiselect(
        "Worksheets",
        options=sheet_names,
        default=st.session_state.get("selected_sheets", sheet_names),
        label_visibility="collapsed",
    )
    st.session_state["selected_sheets"] = selected

    st.caption(f"{len(selected)} of {len(sheet_names)} worksheets selected")

    if file_size_mb > 30:
        st.warning(
            f"⚠️ This workbook is {file_size_mb:.1f} MB. "
            "If you have many large sheets selected, analysis may take 30–60 seconds. "
            "Consider deselecting sheets you don't need."
        )

    return uploaded, xl, selected