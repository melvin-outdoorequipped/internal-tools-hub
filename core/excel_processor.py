"""
Excel reading, sheet discovery, header cleaning, forward-fill, and
Helly Hansen sub-brand logic.
"""
import pandas as pd

DESIRED_COLUMNS = ["Brand", "SKU", "UPC", "ASIN", "Date", "Category", "Sub_brand"]

def clean_headers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(axis=1, how="all")
    rename = {}
    for idx, col in enumerate(df.columns):
        c = str(col).strip().lower()
        if idx == 0: 
            rename[col] = "Brand"
        elif c in ("sku", "skus"): 
            rename[col] = "SKU"
        elif c in ("upc", "upc/ean", "ean"): 
            rename[col] = "UPC"
        elif c == "asin": 
            rename[col] = "ASIN"
        elif c == "date": 
            rename[col] = "Date"
        elif c == "category": 
            rename[col] = "Category"
        elif "sub" in c and "brand" in c: 
            rename[col] = "Sub_brand"
        elif "sub" in c and "brand" in c.replace(" ", ""): 
            rename[col] = "Sub_brand"
            
    df = df.rename(columns=rename)
    return df[[c for c in DESIRED_COLUMNS if c in df.columns]]

def combine_brand(row) -> str:
    b = str(row["Brand"]).strip()
    sb = str(row["Sub_brand"]).strip()
    if pd.isna(row["Sub_brand"]) or sb.lower() in ("", "nan", "none"): 
        return b
        
    if "helly" in b.lower():
        sb_lower = sb.lower()
        if "sport" in sb_lower: 
            return "Helly Hansen Sportswear"
        elif "work" in sb_lower: 
            return "Helly Hansen Workwear"
        else: 
            return f"{b} - {sb}"
            
    return b

def read_sheet_names(file_obj) -> list:
    xl = pd.ExcelFile(file_obj)
    return xl.sheet_names

def load_workbook(file_obj):
    return pd.ExcelFile(file_obj)

def load_data(xl: pd.ExcelFile, selected_sheets, mapper, doct_sku_map=None, log=None) -> pd.DataFrame:
    frames = []
    for s in selected_sheets:
        df = xl.parse(s).dropna(how="all")
        df = clean_headers(df)

        if "Brand" in df.columns:
            # 1. DOCT OVERRIDE: If the SKU is in DOCT, it dictates the Brand.
            if doct_sku_map and "SKU" in df.columns:
                # Clean SKUs for matching
                clean_skus = df["SKU"].astype(str).str.strip().str.upper()
                
                # Look up the exact DOCT brand for each SKU
                doct_matched_brands = clean_skus.map(doct_sku_map)
                
                # Where DOCT found a match, overwrite the Excel Brand.
                # Where DOCT didn't find a match (NaN), keep the Excel Brand.
                df["Brand"] = doct_matched_brands.combine_first(df["Brand"])

            # 2. FORWARD FILL: For any remaining blank brands (SKUs not in DOCT)
            df["Brand"] = df["Brand"].ffill()
            
            # 3. CLEANUP
            df = df[df["Brand"].notna()]
            df = df[~df["Brand"].astype(str).str.lower().str.strip().isin(["brand", "brand name"])]

            # 4. SUB-BRAND LOGIC
            if "Sub_brand" in df.columns:
                df["Sub_brand"] = df["Sub_brand"].ffill()
                df["Brand"] = df.apply(combine_brand, axis=1)

            frames.append(df)

    if not frames:
        raise ValueError("No valid data found in selected sheets.")

    master = pd.concat(frames, ignore_index=True)
    
    # 5. FILTER DISABLED/2P
    before = len(master)
    master = master[~master["Brand"].astype(str).apply(mapper.is_disabled)].copy()
    
    if log and (before - len(master)):
        log(f"Filtered out {before - len(master)} rows belonging to disabled/2P brands.")

    return master