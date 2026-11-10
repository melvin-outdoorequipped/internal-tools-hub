"""Conversion report + downloads UI."""
import streamlit as st
import pandas as pd

from core.csv_generator import apply_lookup, generate_csvs, build_audit_df, build_zip


def render_convert_button(mapper):
    st.markdown("## Convert & Verify")
    ready = st.session_state.get("master_df") is not None and st.session_state.get("brand_rows")
    if not ready:
        st.info("Analyze brands first — the Convert button will unlock once a dataset and mappings are available.")
        return

    if st.button("Convert & Verify", type="primary", use_container_width=True):
        _run_conversion(mapper)


def _run_conversion(mapper):
    master = st.session_state["master_df"]
    rows = st.session_state["brand_rows"]

    progress = st.progress(0, text="Applying mappings...")
    try:
        with_mapping = apply_lookup(master, rows, mapper)
        progress.progress(30, text="Generating per-brand CSVs...")

        files, report, report_df = generate_csvs(with_mapping, mapper)
        progress.progress(75, text="Building audit + ZIP...")

        audit_df = build_audit_df(rows)
        zip_bytes = build_zip(files, audit_df, report_df)

        st.session_state["convert_result"] = {
            "files": files,
            "report_df": report_df,
            "audit_df": audit_df,
            "zip": zip_bytes,
        }
        mapper.save()
        progress.progress(100, text="Done.")
    except Exception as e:
        progress.empty()
        st.error(f"Conversion failed: {e}")
        return

    st.rerun()


def render_results():
    result = st.session_state.get("convert_result")
    if not result:
        return

    st.markdown("### Conversion Results")
    report_df = result["report_df"]
    if report_df.empty:
        st.warning("No CSVs were generated.")
        return

    total = len(report_df)
    matches = (report_df["Status"] == "MATCH").sum()
    mismatches = total - matches

    c1, c2, c3 = st.columns(3)
    c1.metric("Files Generated", total)
    c2.metric("Verified MATCH", int(matches))
    c3.metric("MISMATCH", int(mismatches), delta=None if mismatches == 0 else f"-{mismatches}", delta_color="inverse")

    st.dataframe(report_df, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇ Download All (ZIP)",
        data=result["zip"],
        file_name="brand_matcher_output.zip",
        mime="application/zip",
        type="primary",
        use_container_width=True,
    )

    with st.expander("Download individual CSVs"):
        for name, data in result["files"].items():
            st.download_button(
                f"{name}",
                data=data,
                file_name=name,
                mime="text/csv",
                key=f"dl_{name}",
            )
        st.download_button(
            "_brand_mapping_audit.csv",
            data=result["audit_df"].to_csv(index=False).encode("utf-8"),
            file_name="_brand_mapping_audit.csv",
            mime="text/csv",
        )