import streamlit as st

from theme import inject_theme, section_label

st.set_page_config(
    page_title="Operations Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global premium theme (applies to Home + all tools)
inject_theme()

# ----------------------------------------------------------------------
# Navigation Setup
# ----------------------------------------------------------------------
pg = st.navigation({
    "Platform": [
        st.Page("app.py", title="Home", icon="🏠"),
    ],
    "Data Converters": [
        st.Page("views/amazon_converter.py", title="Databank Converter", icon="📦"),
        st.Page("views/all_listing_converter.py", title="All Listing Converter", icon="🛠️"),
        st.Page("views/aged_inventory_converter.py", title="Aged Inventory Converter", icon="📊"),
    ],
    "Analysis Tools": [
        st.Page("views/sku_gap_finder.py", title="SKU Gap Finder", icon="🔎"),
    ]
})

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand"><div class="dot">⚡</div>Command Center</div>
        <div class="sidebar-sub">Operations data toolkit</div>
        """,
        unsafe_allow_html=True,
    )


def tool_card(key: str, icon: str, title: str, desc: str, button_label: str, target: str) -> None:
    """A tool card: styled container with description + open button inside it."""
    with st.container(key=f"card_{key}"):
        st.markdown(
            f"""
            <div class="tool-icon">{icon}</div>
            <div class="tool-title">{title}</div>
            <div class="tool-desc">{desc}</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(button_label, key=f"btn_{key}", use_container_width=True):
            st.switch_page(target)


# ----------------------------------------------------------------------
# Home Page Layout
# ----------------------------------------------------------------------
if pg.title == "Home":
    st.markdown(
        """
        <div class="hero">
            <div class="hero-badge">Operations Platform</div>
            <h1 class="hero-title">Operations Command Center</h1>
            <p class="hero-sub">Clean, convert and reconcile your listing and inventory data in a few clicks.</p>
        </div>

        <div class="flow">
            <div class="flow-step"><div class="flow-num">1</div>
                <div><div class="flow-title">Convert</div>
                <div class="flow-desc">Turn raw All Listing &amp; inventory files into clean CSVs.</div></div></div>
            <div class="flow-step"><div class="flow-num">2</div>
                <div><div class="flow-title">Build the Databank</div>
                <div class="flow-desc">Standardize brands and export per-brand CSVs.</div></div></div>
            <div class="flow-step"><div class="flow-num">3</div>
                <div><div class="flow-title">Find the gaps</div>
                <div class="flow-desc">Spot SKUs that are missing from the Databank.</div></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_label("📁 Data Converters")
    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        tool_card("db", "📦", "Databank Converter",
                  "Standardize brand names, verify duplicates, and export clean CSVs for the Databank.",
                  "Open Databank", "views/amazon_converter.py")
    with col2:
        tool_card("al", "🛠️", "All Listing Converter",
                  "Convert raw Amazon All Listing files (XLS/ZIP) to clean CSVs with strict column filtering.",
                  "Open All Listing", "views/all_listing_converter.py")
    with col3:
        tool_card("ai", "📊", "Aged Inventory",
                  "Process FBA &amp; 3PL reports, extracting standard columns and separating by SM Manager.",
                  "Open Aged Inventory", "views/aged_inventory_converter.py")

    st.write("")
    section_label("🔎 Analysis Tools")
    col4, _, _ = st.columns(3, gap="medium")
    with col4:
        tool_card("gap", "🔎", "SKU Gap Finder",
                  "Compare your All Listing file against the Databank ZIP to instantly find missing SKUs.",
                  "Open Gap Finder", "views/sku_gap_finder.py")

else:
    pg.run()
