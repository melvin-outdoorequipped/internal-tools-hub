import streamlit as st

st.set_page_config(
    page_title="Internal Tools Hub",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# Custom CSS for the Home Screen
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
      .block-container { padding-top: 3rem; max-width: 1200px; }
      .hero-title { font-size: 3rem; font-weight: 800; margin-bottom: 0.5rem; }
      .hero-sub { font-size: 1.2rem; opacity: 0.7; margin-bottom: 3rem; }
      .tool-card {
          padding: 1.5rem; 
          border-radius: 12px; 
          border: 1px solid rgba(127,127,127,0.2);
          background: rgba(127,127,127,0.05);
          transition: 0.2s;
          height: 100%;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# 1. Define the custom sidebar navigation
# ----------------------------------------------------------------------
pg = st.navigation({
    "Tools": [
        st.Page("app.py", title="Home", icon="🏠"),
        st.Page("views/amazon_converter.py", title="Amazon Databank Converter", icon="📦"),
        st.Page("views/all_listing_converter.py", title="All Listing Converter", icon="🛠️"),
    ]
})

# ----------------------------------------------------------------------
# 2. Render the Home Page
# ----------------------------------------------------------------------
if pg.title == "Home":
    st.markdown('<div class="hero-title">Internal Tools Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Select a tool from the sidebar to begin.</div>', unsafe_allow_html=True)

    st.markdown("### Available Tools")

    # 3-Column Layout for Tools
    col1, col2, col3 = st.columns(3)

    # Tool 1: Amazon Databank Converter
    with col1:
        with st.container():
            st.markdown(
                """
                <div class="tool-card">
                    <h3>📦 Amazon Databank Converter</h3>
                    <p>Upload Excel workbooks, standardize brand names, verify duplicates, and export clean CSVs for the Databank.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            st.write("") 
            if st.button("Open Converter", key="btn_databank", use_container_width=True):
                st.switch_page("views/amazon_converter.py")

    # Tool 2: All Listing Converter
    with col2:
        with st.container():
            st.markdown(
                """
                <div class="tool-card">
                    <h3>🛠️ All Listing Converter</h3>
                    <p>Convert raw Amazon All Listing files (XLS/XLSX/ZIP) to clean CSVs containing only the required columns.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            st.write("") 
            if st.button("Open Tool", key="btn_all_listing", use_container_width=True):
                st.switch_page("views/all_listing_converter.py")

    # Tool 3: Future Tool
    with col3:
        with st.container():
            st.markdown(
                """
                <div class="tool-card">
                    <h3>🧩 Future Tool</h3>
                    <p>This space is reserved for your next web application or utility.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            st.write("")
            st.button("Coming Soon...", key="btn_future", disabled=True, use_container_width=True)

# ----------------------------------------------------------------------
# 3. Run the selected page if not on Home
# ----------------------------------------------------------------------
else:
    pg.run()