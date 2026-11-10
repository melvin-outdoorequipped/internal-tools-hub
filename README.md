# Brand Matcher

Streamlit web app for Excel → CSV brand standardization. Preserves the
original Tkinter desktop logic (brand normalization, JSON aliases,
fuzzy auto-merge, Helly Hansen sub-brands, SKU/2P detection).

## Run locally (Windows PowerShell)

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py