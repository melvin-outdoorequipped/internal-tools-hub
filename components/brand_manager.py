"""Interactive brand mapping manager using st.data_editor."""
import io
import pandas as pd
import streamlit as st

from core.brand_normalizer import normalize_brand


MATCH_TYPES = ["Exact", "Formatting", "Fuzzy Auto-Merge", "JSON Alias", "Manual Merge", "Disabled (2P)", "Suspicious (SKU)"]
STATUSES = ["Approved", "Needs Review", "Excluded"]


def _rows_to_df(rows):
    return pd.DataFrame(rows, columns=["Original_Brand", "Canonical_Brand", "Match_Type", "Status"])


def render_brand_manager(mapper):
    st.markdown("## Brand Mapping Manager")

    rows = st.session_state.get("brand_rows")
    if not rows:
        st.info("Upload an Excel file and click **Analyze Brands** to populate this table.")
        _render_import_export(mapper)
        return

    df = _rows_to_df(rows)

    # ---- filters ----
    c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
    with c1:
        search = st.text_input("Search", placeholder="Search brand, canonical, type...")
    with c2:
        f_type = st.multiselect("Match Type", MATCH_TYPES, default=MATCH_TYPES)
    with c3:
        f_status = st.multiselect("Status", STATUSES, default=STATUSES)
    with c4:
        if st.button("Clear Filters", use_container_width=True):
            st.session_state["_clear_filters"] = True
            st.rerun()

    # ensure default multiselect persists after clear
    if st.session_state.get("_clear_filters"):
        st.session_state["_clear_filters"] = False

    mask = df["Match_Type"].isin(f_type) & df["Status"].isin(f_status)
    if search:
        s = search.lower()
        mask &= (
            df["Original_Brand"].astype(str).str.lower().str.contains(s, na=False)
            | df["Canonical_Brand"].astype(str).str.lower().str.contains(s, na=False)
            | df["Match_Type"].astype(str).str.lower().str.contains(s, na=False)
            | df["Status"].astype(str).str.lower().str.contains(s, na=False)
        )
    filtered = df[mask].copy()
    filtered.insert(0, "Select", False)

    st.caption(f"Showing {len(filtered)} of {len(df)} rows")

    # ---- editable table ----
    edited = st.data_editor(
        filtered,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "Select": st.column_config.CheckboxColumn("Select", width="small"),
            "Original_Brand": st.column_config.TextColumn("Original Brand", disabled=True, width="medium"),
            "Canonical_Brand": st.column_config.TextColumn("Canonical Brand", width="medium"),
            "Match_Type": st.column_config.SelectboxColumn(
                "Match Type", options=MATCH_TYPES, disabled=True, width="medium"
            ),
            "Status": st.column_config.SelectboxColumn("Status", options=STATUSES, width="small"),
        },
        key="brand_editor",
    )

    # ---- actions ----
    a1, a2, a3 = st.columns([1, 1, 2])
    with a1:
        if st.button("Approve Selected", type="primary", use_container_width=True):
            _apply_edits(edited, mapper, approve=True)
    with a2:
        if st.button("Bulk Approve Visible", use_container_width=True):
            _bulk_approve(filtered, mapper)
    with a3:
        st.caption("Approve Selected applies edits + marks rows as Approved. Bulk Approve marks all visible rows Approved without needing checkbox selection.")

    st.divider()
    _render_import_export(mapper)


def _apply_edits(edited: pd.DataFrame, mapper, approve: bool):
    sel = edited[edited["Select"] == True]
    if sel.empty:
        st.warning("Select at least one row first.")
        return
    _commit(sel, mapper, approve=approve, message=f"Approved & saved {len(sel)} row(s).")


def _bulk_approve(filtered: pd.DataFrame, mapper):
    if filtered.empty:
        st.warning("Nothing to approve.")
        return
    _commit(filtered, mapper, approve=True, message=f"Bulk-approved {len(filtered)} row(s).")


def _commit(subset: pd.DataFrame, mapper, approve: bool, message: str):
    rows = st.session_state["brand_rows"]
    # index by Original_Brand for fast update
    by_orig = {str(r["Original_Brand"]): r for r in rows}
    for _, row in subset.iterrows():
        orig = str(row["Original_Brand"])
        if orig not in by_orig:
            continue
        canon = str(row["Canonical_Brand"]).strip()
        status = "Approved" if approve else str(row["Status"])
        mt = str(row["Match_Type"])
        if canon and normalize_brand(canon) != normalize_brand(orig):
            mt = "Manual Merge" if mt not in ("Disabled (2P)", "Suspicious (SKU)") else mt
        r = by_orig[orig]
        r["Canonical_Brand"] = canon
        r["Match_Type"] = mt
        r["Status"] = status

        # Persist mapping (skip disabled/2P auto-activation)
        if status == "Approved" and not mapper.is_disabled(canon):
            mapper.set_alias(orig, canon)
        elif status == "Excluded":
            mapper.set_disabled(orig, canon)

    ok = mapper.save()
    st.session_state["brand_rows"] = rows
    st.session_state["mapping_dirty"] = True
    if ok:
        st.success(message)
    else:
        st.warning(message + "  ⚠ Could not persist to disk (ephemeral filesystem). Use **Backup JSON** to save.")
    st.rerun()


def _render_import_export(mapper):
    st.markdown("### Import / Export Mappings")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        uploaded_csv = st.file_uploader("Import Master CSV", type=["csv"], key="import_csv")
        if uploaded_csv is not None and st.button("Apply Import", use_container_width=True):
            try:
                df = pd.read_csv(uploaded_csv)
                count = mapper.import_csv(df)
                mapper.save()
                st.success(f"Imported {count} mappings. Re-run Analyze Brands to refresh.")
                st.session_state["mapping_dirty"] = True
            except Exception as e:
                st.error(f"Import failed: {e}")

    with c2:
        rows = st.session_state.get("brand_rows") or []
        if rows:
            export_df = pd.DataFrame(rows)[["Original_Brand", "Canonical_Brand"]].sort_values("Original_Brand")
            st.download_button(
                "Export All Brands CSV",
                data=export_df.to_csv(index=False).encode("utf-8"),
                file_name="brand_mappings_export.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.button("Export All Brands CSV", disabled=True, use_container_width=True)

    with c3:
        st.download_button(
            "Backup brand_mapping.json",
            data=mapper.to_json_string().encode("utf-8"),
            file_name="brand_mapping.json",
            mime="application/json",
            use_container_width=True,
        )

    with c4:
        st.download_button(
            "Current JSON snapshot",
            data=mapper.to_json_string().encode("utf-8"),
            file_name="brand_mapping_snapshot.json",
            mime="application/json",
            use_container_width=True,
            help="Download the in-memory mapping state for review.",
        )

    st.caption(
        "⚠️ Streamlit Community Cloud resets the filesystem on redeploy/restart. "
        "Download the JSON backup regularly and re-import if needed."
    )