"""
Listing Converter — Streamlit Web App.
Converted from Tkinter desktop application.
"""
import zipfile
from datetime import datetime

import pandas as pd
import streamlit as st

from theme import page_header, section_label

# Added "item-name"
COLUMNS = ["seller-sku", "asin1", "item-name", "status"]

page_header("🛠️", "All Listing Converter",
            "Convert raw Amazon files to clean CSVs.",
            eyebrow="Data Converter")

section_label("Step 1 · Select All Listing File")
st.info("Upload an All Listing XLS/XLSX file (or ZIP). It will be converted into a single CSV containing only `seller-sku`, `asin1`, `item-name`, and `status`.")

file_t1 = st.file_uploader("Upload Excel or ZIP", type=["xlsx", "xls", "zip"], key="upload_t1")

if st.button("📂 Convert to CSV", type="primary", key="btn_t1"):
    if file_t1 is None:
        st.warning("Please upload a file first.")
    else:
        with st.spinner("Processing files..."):
            try:
                frames = []
                
                def process_sheets(sheets_dict):
                    for name, df in sheets_dict.items():
                        # Clean column names (strip spaces, lower case for safety, remove BOM)
                        df.columns = [str(c).strip().lstrip("\ufeff") for c in df.columns]
                        
                        # Handle Amazon's occasional "item name" vs "item-name" formatting
                        if "item name" in df.columns and "item-name" not in df.columns:
                            df.rename(columns={"item name": "item-name"}, inplace=True)
                            
                        missing = [c for c in COLUMNS if c not in df.columns]
                        if missing:
                            st.warning(f"⚠ Sheet '{name}' skipped — missing columns: {missing}")
                            continue
                            
                        kept = df[COLUMNS].dropna(how="all")
                        frames.append(kept)
                        st.write(f"✓ Sheet '{name}': {len(kept)} rows kept.")

                if file_t1.name.lower().endswith(".zip"):
                    with zipfile.ZipFile(file_t1, "r") as z:
                        excel_files = [
                            f for f in z.namelist()
                            if f.endswith((".xlsx", ".xls")) and not f.startswith("__MACOSX")
                        ]
                        if not excel_files:
                            st.error("❌ No Excel file found inside the ZIP.")
                        else:
                            target_excel = excel_files[0]
                            st.write(f"Extracting: {target_excel}")
                            with z.open(target_excel) as f:
                                engine = "openpyxl" if target_excel.endswith(".xlsx") else "xlrd"
                                sheets = pd.read_excel(f, sheet_name=None, dtype=str, engine=engine)
                                process_sheets(sheets)
                else:
                    engine = "openpyxl" if file_t1.name.endswith(".xlsx") else "xlrd"
                    sheets = pd.read_excel(file_t1, sheet_name=None, dtype=str, engine=engine)
                    process_sheets(sheets)

                if frames:
                    final_df = pd.concat(frames, ignore_index=True).fillna("")
                    st.success(f"✅ Total rows combined: {len(final_df)}")

                    csv_data = final_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

                    date_str = datetime.now().strftime("%Y-%m-%d")
                    filename = f"All Listing ({date_str}).csv"

                    st.download_button(
                        label="⬇️ Download Converted CSV",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv",
                        type="primary"
                    )
                else:
                    st.error("❌ No valid data found. Please ensure your files contain the required columns.")

            except Exception as e:
                st.error(f"❌ Error: {e}")
