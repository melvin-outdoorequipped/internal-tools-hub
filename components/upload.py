"""Excel upload + sheet selection UI."""
import streamlit as st
import pandas as pd

from core.excel_processor import load_workbook, read_sheet_names


def render_upload():
    st.markdown("## Excel Upload")
    uploaded = st.file_uploader(
        "Drag & drop your Excel file",
        type=["xlsx", "xlsm", "xls"],
        help="Supports .xlsx, .xlsm and .xls workbooks with one or more worksheets.",
    )

    if uploaded is None:
        return None, None, []

    file_key = f"{uploaded.name}_{uploaded.size}"

    # Read workbook once and cache in session state
    if st.session_state.get("file_key") != file_key:
        try:
            uploaded.seek(0)
            xl = load_workbook(uploaded)
            sheet_names = read_sheet_names(xl)
            st.session_state["file_key"] = file_key
            st.session_state["xl"] = xl
            st.session_state["file_name"] = uploaded.name
            st.session_state["sheet_names"] = sheet_names
            st.session_state["selected_sheets"] = list(sheet_names)
            st.session_state["master_df"] = None
            st.session_state["brand_rows"] = None
            st.session_state["convert_result"] = None
        except Exception as e:
            st.error(f"Failed to read workbook: {e}")
            return None, None, []

    xl = st.session_state["xl"]
    sheet_names = st.session_state["sheet_names"]

    st.success(f"**File:** {st.session_state['file_name']}  •  **{len(sheet_names)} worksheets**")

    # Sheet selection
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

    return uploaded, xl, selected