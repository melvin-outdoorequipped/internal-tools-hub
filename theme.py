"""
Shared premium theme for the Operations Command Center.
Import inject_theme() once in app.py (applies to every page) and use
page_header() / section_label() in the views.
"""
import streamlit as st

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --accent-1: #6366f1;
    --accent-2: #3b82f6;
    --accent-3: #22d3ee;
    --surface: rgba(255,255,255,0.035);
    --surface-hover: rgba(99,102,241,0.08);
    --border: rgba(148,163,184,0.16);
    --border-strong: rgba(99,102,241,0.55);
    --muted: #94a3b8;
    --radius: 16px;
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* Ambient background */
.stApp {
    background:
        radial-gradient(900px 500px at 8% -10%, rgba(99,102,241,0.16), transparent 60%),
        radial-gradient(800px 500px at 100% 0%, rgba(34,211,238,0.08), transparent 55%),
        #0b1020;
}

/* Chrome cleanup */
#MainMenu, footer { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2.2rem; padding-bottom: 4rem; max-width: 1240px; }

h1, h2, h3 { letter-spacing: -0.02em; }
h3 { font-weight: 700; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1226 0%, #0a0f20 100%);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebarNav"] a { border-radius: 10px; margin: 1px 6px; transition: background .2s; }
[data-testid="stSidebarNav"] a:hover { background: var(--surface-hover); }
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: linear-gradient(90deg, rgba(99,102,241,0.25), rgba(59,130,246,0.10));
    border: 1px solid rgba(99,102,241,0.35);
    font-weight: 600;
}
.sidebar-brand {
    display:flex; align-items:center; gap:.6rem; padding:.9rem .4rem 0;
    font-weight:800; letter-spacing:-0.01em;
}
.sidebar-brand .dot {
    width:30px; height:30px; border-radius:9px; display:grid; place-items:center;
    background: linear-gradient(135deg, var(--accent-1), var(--accent-2)); font-size:1rem;
    box-shadow: 0 6px 16px rgba(99,102,241,.45);
}
.sidebar-sub { color: var(--muted); font-size:.78rem; padding: 0 .4rem 1rem; }

/* ---------- Hero ---------- */
.hero {
    position: relative; overflow: hidden;
    padding: 3.2rem 2.4rem; border-radius: 22px; margin-bottom: 1.6rem;
    background:
        radial-gradient(600px 300px at 90% -20%, rgba(34,211,238,.25), transparent 60%),
        radial-gradient(700px 400px at 0% 120%, rgba(99,102,241,.45), transparent 60%),
        linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 30px 60px -20px rgba(15,23,42,.8);
}
.hero::after {
    content:""; position:absolute; inset:0; pointer-events:none;
    background-image: linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px);
    background-size: 36px 36px;
    mask-image: radial-gradient(ellipse at 70% 30%, #000 0%, transparent 70%);
}
.hero > * { position: relative; z-index: 1; }
.hero-badge {
    display:inline-block; padding:.28rem .8rem; border-radius:999px; font-size:.75rem; font-weight:600;
    letter-spacing:.06em; text-transform:uppercase; color:#c7d2fe;
    background: rgba(99,102,241,.22); border:1px solid rgba(165,180,252,.35); margin-bottom:1rem;
}
.hero-title {
    font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; margin: 0; line-height:1.1;
    background: linear-gradient(90deg, #ffffff 30%, #a5b4fc 100%);
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub { font-size:1.08rem; color:#a8b4cc; margin-top:.8rem; max-width: 640px; }

/* ---------- Workflow strip ---------- */
.flow { display:grid; grid-template-columns: repeat(3, 1fr); gap:.9rem; margin: 0 0 2.2rem; }
.flow-step {
    background: var(--surface); border:1px solid var(--border); border-radius:14px;
    padding: .95rem 1.1rem; display:flex; gap:.8rem; align-items:flex-start;
}
.flow-num {
    flex:0 0 28px; height:28px; border-radius:8px; display:grid; place-items:center;
    font-weight:700; font-size:.85rem; color:white;
    background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
}
.flow-title { font-weight:600; font-size:.95rem; }
.flow-desc { color: var(--muted); font-size:.82rem; margin-top:.1rem; }
@media (max-width: 800px) { .flow { grid-template-columns: 1fr; } }

/* ---------- Section label ---------- */
.section-label {
    display:flex; align-items:center; gap:.6rem; margin: 1.2rem 0 .9rem;
    font-size:1.05rem; font-weight:700;
}
.section-label::after { content:""; flex:1; height:1px; background: var(--border); }

/* ---------- Tool cards (st.container(key="card_*")) ---------- */
[class*="st-key-card_"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.4rem 1.2rem;
    transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease, background .25s ease;
    height: 100%;
}
[class*="st-key-card_"]:hover {
    transform: translateY(-4px);
    border-color: var(--border-strong);
    background: var(--surface-hover);
    box-shadow: 0 18px 40px -12px rgba(59,130,246,.35);
}
.tool-icon {
    width:48px; height:48px; border-radius:13px; display:grid; place-items:center; font-size:1.5rem;
    background: linear-gradient(135deg, rgba(99,102,241,.28), rgba(34,211,238,.16));
    border:1px solid rgba(129,140,248,.3); margin-bottom:1rem;
}
.tool-title { font-size:1.15rem; font-weight:700; margin-bottom:.4rem; }
.tool-desc  { font-size:.92rem; color: var(--muted); line-height:1.55; min-height: 4.6em; margin-bottom:.4rem; }

/* ---------- Page header (tool pages) ---------- */
.page-header { margin-bottom: 1.8rem; padding-bottom: 1.2rem; border-bottom: 1px solid var(--border); }
.page-header .eyebrow {
    font-size:.72rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase;
    color: #818cf8; margin-bottom:.4rem;
}
.page-header h1 { margin:0; font-size:2rem; font-weight:800; }
.page-header p { color: var(--muted); margin:.4rem 0 0; font-size:1rem; }

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button {
    border-radius: 10px; font-weight: 600; padding: .55rem 1.1rem;
    border: 1px solid var(--border); transition: all .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--border-strong); transform: translateY(-1px);
}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
    border: none; color: white;
    box-shadow: 0 8px 20px -6px rgba(99,102,241,.55);
}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {
    filter: brightness(1.1); box-shadow: 0 12px 26px -6px rgba(99,102,241,.7);
}

/* ---------- Inputs ---------- */
[data-testid="stFileUploaderDropzone"] {
    border: 1.5px dashed rgba(129,140,248,.45); border-radius: 14px;
    background: rgba(99,102,241,.05); transition: all .2s ease;
}
[data-testid="stFileUploaderDropzone"]:hover { background: rgba(99,102,241,.10); border-color: #818cf8; }

/* ---------- Alerts, metrics, tables, tabs, expanders ---------- */
[data-testid="stAlert"] { border-radius: 12px; border: 1px solid var(--border); }
div[data-testid="stMetric"] {
    background: var(--surface); border:1px solid var(--border); border-radius:14px; padding:14px 18px;
}
div[data-testid="stMetricLabel"] { color: var(--muted); font-size:.82rem; }
div[data-testid="stMetricValue"] { font-size:1.7rem; font-weight:700; }
[data-testid="stDataFrame"] { border:1px solid var(--border); border-radius:12px; overflow:hidden; }
[data-testid="stExpander"] { border:1px solid var(--border); border-radius:12px; background: var(--surface); }

[data-baseweb="tab-list"] { gap:6px; border-bottom:1px solid var(--border); }
button[data-baseweb="tab"] { border-radius:10px 10px 0 0; padding: .6rem 1rem; font-weight:600; }
[data-baseweb="tab-highlight"] { background: linear-gradient(90deg, var(--accent-1), var(--accent-3)); height:3px; }

hr { border-color: var(--border) !important; }
"""


def inject_theme() -> None:
    """Inject the global premium CSS. Call once from the entrypoint."""
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str, eyebrow: str = "Tool") -> None:
    st.markdown(
        f"""
        <div class="page-header">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{icon} {title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)
