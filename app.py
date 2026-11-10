import streamlit as st

st.set_page_config(
    page_title="Internal Tools Hub",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="hero-title">Internal Tools Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Select a tool from the sidebar to begin.</div>', unsafe_allow_html=True)

st.markdown("### Available Tools")

# Create a grid for your tools
col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.markdown(
            """
            <div class="tool-card">
                <h3>📦 Amazon Listing Databank Converter</h3>
                <p>Upload Excel workbooks, standardize brand names, verify duplicates, and export clean CSVs for the Databank.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.write("") # spacing
        # Link to the new page
        st.page_link("pages/1_Amazon_Listing_Databank_Converter.py", label="Open Converter", icon="➡️")

with col2:
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
        st.button("Coming Soon...", disabled=True, use_container_width=True)