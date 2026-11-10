"""
Aged Inventory Converter (FBA & 3PL).
Extracts specific columns and exports separate CSVs per US SM Manager, bundled in a ZIP.
Handles both standard FBA files and dedicated 3PL files.
"""
import io
import zipfile
import re
import pandas as pd
import streamlit as st

from theme import page_header, section_label

page_header("📊", "Aged Inventory Converter",
            "Convert Aged Inventory reports (FBA &amp; 3PL) into standardized CSVs, separated by US SM Manager.",
            eyebrow="Data Converter")

section_label("Upload Aged Inventory Files")
st.info("Upload one or multiple Excel files (both FBA and 3PL). The tool will extract the exact columns requested and output CSVs using the original filenames.")

# Accept multiple files
file_uploads = st.file_uploader(
    "Upload Excel Files", 
    type=["xlsx", "xls"], 
    accept_multiple_files=True, 
    key="aged_inv_upload"
)

# The exact output columns you requested
TARGET_COLUMNS = [
    "UPC", "Brand", "ASIN", "SKU", "V2 SKU",
    "UPC in 3PL", "SKU in 3PL",
    "30-90DaysSince", "120-180DaysSince", "210-270DaysSince", "300-390DaysSince",
    "0-90", "91-180", "181-270", "271-365", "366-455", "180+"
]

# Define common ways these columns might appear in the uploaded Excel files
# so we can map them correctly even if they have slight variations in the header
COLUMN_MAPPING = {
    "UPC": ["upc"],
    "Brand": ["brand"],
    "ASIN": ["asin", "asin1"],
    "SKU": ["sku", "seller-sku"],
    "V2 SKU": ["v2 sku", "v2_sku", "v2sku"],
    "UPC in 3PL": ["upc in 3pl", "upc 3pl", "3pl upc"],
    "SKU in 3PL": ["sku in 3pl", "sku 3pl", "3pl sku"],
    "30-90DaysSince": ["30-90dayssince", "30-90 days since"],
    "120-180DaysSince": ["120-180dayssince", "120-180 days since"],
    "210-270DaysSince": ["210-270dayssince", "210-270 days since"],
    "300-390DaysSince": ["300-390dayssince", "300-390 days since"],
    "0-90": ["0-90"],
    "91-180": ["91-180"],
    "181-270": ["181-270"],
    "271-365": ["271-365"],
    "366-455": ["366-455"],
    "180+": ["180+"]
}

def extract_manager_name(filename):
    """Extracts the manager name from filenames for grouping purposes."""
    # Matches names like "Adrianna 3PL Inventory..." or "... - Sheila.xlsx"
    match = re.search(r'^([A-Za-z]+)\s', filename, re.IGNORECASE)
    if match:
        return match.group(1).capitalize()
    
    match = re.search(r'-\s*([A-Za-z]+)\.(xlsx|xls)$', filename, re.IGNORECASE)
    if match:
        return match.group(1).capitalize()
        
    base_name = filename.rsplit('.', 1)[0]
    return base_name

if st.button("🔄 Convert to CSVs", type="primary", use_container_width=True):
    if not file_uploads:
        st.warning("Please upload at least one Excel file.")
    else:
        with st.spinner(f"Processing {len(file_uploads)} file(s)..."):
            try:
                processed_files = []
                all_combined_frames = []
                
                for file_upload in file_uploads:
                    manager_name = extract_manager_name(file_upload.name)
                    
                    # Create the new filename: replace .xlsx/.xls with .csv
                    new_filename = re.sub(r'\.(xlsx|xls)$', '.csv', file_upload.name, flags=re.IGNORECASE)
                    
                    st.write(f"Processing: **{file_upload.name}**")
                    
                    try:
                        sheets = pd.read_excel(file_upload, sheet_name=None)
                    except Exception as e:
                        st.warning(f"Could not read {file_upload.name}: {e}")
                        continue
                    
                    file_frames = []
                    for sheet_name, df in sheets.items():
                        if df.empty:
                            continue
                            
                        # Clean column names for matching (strip, lower)
                        df.columns = [str(c).strip().lower() for c in df.columns]
                        
                        # Skip sheets that clearly aren't the data we want
                        if "brand" not in df.columns and "sku" not in df.columns and "asin" not in df.columns:
                            continue
                            
                        extracted_df = pd.DataFrame()
                        
                        # Map columns based on our dictionary
                        for target in TARGET_COLUMNS:
                            found = False
                            # Check all possible variations for this column
                            for variation in COLUMN_MAPPING.get(target, [target.lower()]):
                                if variation in df.columns:
                                    extracted_df[target] = df[variation]
                                    found = True
                                    break
                            
                            # If column doesn't exist in this file, create it blank
                            if not found:
                                extracted_df[target] = ""
                        
                        file_frames.append(extracted_df)
                    
                    if file_frames:
                        # Combine all valid sheets within THIS file
                        combined_file_df = pd.concat(file_frames, ignore_index=True)
                        
                        # Drop completely empty rows
                        combined_file_df = combined_file_df.dropna(subset=["Brand", "SKU", "ASIN"], how="all")

                        # Convert to CSV bytes
                        csv_data = combined_file_df.to_csv(index=False).encode("utf-8-sig")
                        
                        # Store the exact new filename and data
                        processed_files.append((new_filename, csv_data))
                        
                        # Add to master preview (adding manager name for clarity)
                        display_df = combined_file_df.copy()
                        display_df.insert(0, "Manager", manager_name)
                        all_combined_frames.append(display_df)

                if not processed_files:
                    st.error("❌ Could not find any valid data sheets in the uploaded files.")
                else:
                    # Prepare ZIP buffer
                    zip_buffer = io.BytesIO()
                    
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
                        for filename, csv_data in processed_files:
                            z.writestr(filename, csv_data)
                            
                    zip_buffer.seek(0)
                    
                    # Combine all for preview
                    master_preview_df = pd.concat(all_combined_frames, ignore_index=True)
                    
                    st.success(f"✅ Successfully processed {len(file_uploads)} file(s) into {len(processed_files)} CSV(s).")
                    
                    # Show preview
                    section_label("Preview")
                    st.dataframe(master_preview_df.head(100), use_container_width=True, hide_index=True)
                    if len(master_preview_df) > 100:
                        st.caption(f"*Showing the first 100 of {len(master_preview_df)} rows.*")

                    # Download buttons
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="⬇️ Download All (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name="Aged_Inventory_CSVs.zip",
                            mime="application/zip",
                            type="primary",
                            use_container_width=True
                        )
                        
                    with col2:
                        combined_csv = master_preview_df.to_csv(index=False).encode("utf-8-sig")
                        st.download_button(
                            label="⬇️ Download Combined Master CSV",
                            data=combined_csv,
                            file_name="Aged_Inventory_Combined.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

            except Exception as e:
                st.error(f"❌ Error processing files: {e}")