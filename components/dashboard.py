"""Dashboard overview cards."""
import streamlit as st


def render_dashboard(state):
    st.markdown("## Dashboard Overview")
    st.caption("A quick snapshot of your current dataset and mappings.")

    cols = st.columns(6)
    metrics = [
        ("Total Records", state.get("total_records", 0)),
        ("Unique Brands", state.get("unique_brands", 0)),
        ("Duplicates Detected", state.get("duplicates_detected", 0)),
        ("Approved Mappings", state.get("approved_mappings", 0)),
        ("Needs Review", state.get("needs_review", 0)),
        ("Disabled / 2P", state.get("disabled_2p", 0)),
    ]
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.metric(label=label, value=f"{value:,}")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### How it works")
        st.markdown(
            """
            1. **Upload** an Excel file (.xlsx / .xlsm / .xls).
            2. **Select** worksheets and click **Analyze Brands**.
            3. **Review** mappings in the Brand Mapping Manager.
            4. **Approve** or edit canonical names.
            5. Click **Convert & Verify** to generate CSVs.
            """
        )
    with c2:
        st.markdown("### Session Status")
        file_name = state.get("file_name")
        st.write("**File:**", file_name if file_name else "_(none loaded)_")
        st.write("**Worksheets selected:**", state.get("sheets_selected", 0))
        st.write("**Mapping file:**", state.get("mapping_file", "data/brand_mapping.json"))
        st.info(
            "Streamlit Community Cloud has an **ephemeral filesystem**. "
            "Use *Export All Brands* / *Backup JSON* to preserve mappings across redeploys."
        )