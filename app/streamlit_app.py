# ==========================
# Sullivan's Super Bot UI
# Light theme + logo + header & sidebar backgrounds
# ==========================

import os
import sys
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd

# --------------------------
# BASIC PAGE CONFIG
# --------------------------
st.set_page_config(
    page_title="Sullivan's Advertisements – Super Bot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent

LOGO_PATH = APP_DIR / "sullivans_logo.png"
HEADER_BG_PATH = APP_DIR / "header_bg.png"      # golden gate image
SIDEBAR_BG_PATH = APP_DIR / "sidebar_bg.png"    # angel image


# --------------------------
# GLOBAL STYLING (LIGHT THEME)
# --------------------------
def inject_base_css():
    header_bg_url = HEADER_BG_PATH.name
    sidebar_bg_url = SIDEBAR_BG_PATH.name

    st.markdown(
        f"""
        <style>
        /* Make app light and clean */
        .stApp {{
            background-color: #f7f5f0;
            color: #1f2933;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}

        /* Remove default header gap and add custom header area */
        .app-header {{
            width: 100%;
            padding: 24px 32px 16px 32px;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            justify-content: center;
            background-image: url("{header_bg_url}");
            background-size: cover;
            background-position: center;
            border-bottom: 1px solid rgba(0,0,0,0.08);
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        }}

        /* Sidebar background (angel image) */
        [data-testid="stSidebar"] > div:first-child {{
            background-image: url("{sidebar_bg_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            color: #f9fafb;
        }}

        /* Sidebar content overlay */
        [data-testid="stSidebar"] .sidebar-content-overlay {{
            background: rgba(3, 7, 18, 0.72);
            padding: 16px;
            border-radius: 18px;
            margin: 12px;
        }}

        /* Make sidebar widgets readable on dark overlay */
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .stText,
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] .stRadio,
        [data-testid="stSidebar"] .stSelectbox,
        [data-testid="stSidebar"] .stTextInput,
        [data-testid="stSidebar"] .stNumberInput {{
            color: #f9fafb !important;
        }}

        /* Main container card style */
        .main-card {{
            background: #ffffff;
            border-radius: 18px;
            padding: 24px 28px;
            box-shadow: 0 10px 30px rgba(15,23,42,0.15);
            margin-top: 18px;
        }}

        /* Section titles */
        .section-title {{
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }}

        .section-subtitle {{
            font-size: 0.9rem;
            color: #6b7280;
            margin-bottom: 1rem;
        }}

        /* Buttons */
        .stButton > button {{
            border-radius: 999px;
            padding: 0.6rem 1.4rem;
            border: none;
            background: linear-gradient(135deg, #0f766e, #22c55e);
            color: white;
            font-weight: 600;
            box-shadow: 0 10px 18px rgba(15,118,110,0.35);
        }}
        .stButton > button:hover {{
            filter: brightness(1.05);
            transform: translateY(-1px);
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


inject_base_css()


# --------------------------
# CUSTOM HEADER WITH LOGO
# --------------------------
def render_header():
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    if LOGO_PATH.exists():
        st.image(
            str(LOGO_PATH),
            width=220,
            caption=None,
        )
    else:
        st.markdown(
            "<h1 style='color:#f9fafb; text-shadow:0 0 18px rgba(0,0,0,0.6);'>Sullivan's Advertisements</h1>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


render_header()


# --------------------------
# SIDEBAR – basic controls (no APIs yet, just UI)
# --------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-content-overlay">', unsafe_allow_html=True)

    st.markdown("### 🎛️ Planner Controls")
    niche = st.selectbox("Primary niche", ["Music", "Clothing brand", "Local Home Care"])
    goal = st.selectbox(
        "Primary campaign goal",
        ["Awareness", "Traffic", "Leads", "Sales / Purchases", "App Installs"],
    )
    monthly_budget = st.number_input(
        "Monthly ad budget (USD)",
        min_value=100.0,
        value=2500.0,
        step=50.0,
    )

    st.markdown("### 🌍 Geo Targeting")
    country = st.text_input("Main country (or 'Worldwide')", value="Worldwide")
    cities = st.text_area(
        "Key cities / regions (optional)",
        placeholder="New York, Los Angeles, London\nor leave blank for broad targeting",
    )

    st.markdown("### 🔍 Inspiration Inputs")
    competitors = st.text_area(
        "Competitor URLs or profiles",
        placeholder="https://instagram.com/artist\nhttps://brand.com\nhttps://tiktok.com/@creator",
    )

    st.markdown("### ⚙️ Platforms to include")
    use_meta = st.checkbox("Meta (Facebook + Instagram)", value=True)
    use_tiktok = st.checkbox("TikTok Ads", value=True)
    use_google = st.checkbox("Google Search + YouTube", value=True)
    use_spotify = st.checkbox("Spotify / Audio", value=False)
    use_twitter = st.checkbox("Twitter / X", value=False)
    use_snap = st.checkbox("Snapchat", value=False)

    run = st.button("✨ Generate Strategic Plan")

    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------
# SUPER SIMPLE “BRAIN” PLACEHOLDER
# (no live APIs here – safe offline estimates)
# --------------------------
def estimate_channel_split(goal: str, budget: float):
    """Very simple static budget split + ROAS guess (just a placeholder)."""
    base = {
        "Meta": 0.35,
        "TikTok": 0.20,
        "Google Search": 0.20,
        "YouTube": 0.10,
        "Spotify": 0.05,
        "Twitter": 0.05,
        "Snapchat": 0.05,
    }

    # normalize based on toggles later
    if goal in ["Awareness"]:
        bias = {"Meta": 1.2, "TikTok": 1.2, "YouTube": 1.1}
    elif goal in ["Traffic"]:
        bias = {"Google Search": 1.2, "Meta": 1.1}
    elif goal in ["Leads"]:
        bias = {"Meta": 1.1, "Google Search": 1.1, "YouTube": 0.9}
    else:  # Sales / App Installs
        bias = {"Meta": 1.1, "Google Search": 1.2, "TikTok": 0.9}

    weighted = {}
    total = 0
    for ch, pct in base.items():
        w = pct * bias.get(ch, 1.0)
        weighted[ch] = w
        total += w
    for ch in weighted:
        weighted[ch] /= total

    # simple ROAS estimate ranges
    roas_ranges = {
        "Meta": (1.2, 3.0),
        "TikTok": (1.1, 2.5),
        "Google Search": (1.5, 3.5),
        "YouTube": (0.8, 2.0),
        "Spotify": (0.5, 1.5),
        "Twitter": (0.6, 1.4),
        "Snapchat": (0.7, 1.6),
    }

    rows = []
    for ch, pct in weighted.items():
        ch_budget = budget * pct
        lo, hi = roas_ranges[ch]
        rows.append(
            {
                "Channel": ch,
                "Budget (USD)": round(ch_budget, 2),
                "Est. ROAS Range": f"{lo:.1f}x – {hi:.1f}x",
            }
        )
    return pd.DataFrame(rows)


# --------------------------
# MAIN CONTENT
# --------------------------
st.markdown(
    """
<div class="main-card">
    <div class="section-title">Sullivan's Mini Media Planner</div>
    <div class="section-subtitle">
        Built for Music, Clothing Brands, and Local Home Care – a single view to sketch your cross-platform plan.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

if run:
    df = estimate_channel_split(goal, monthly_budget)

    st.markdown(
        """
<div class="main-card">
    <div class="section-title">📊 Budget & Channel Overview</div>
    <div class="section-subtitle">
        These are rough planning ranges – connect real APIs later to replace presets with live performance data.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.dataframe(df, use_container_width=True)

else:
    st.markdown(
        """
<div class="main-card">
    <p>Start by picking your <strong>niche</strong>, <strong>goal</strong>, and <strong>budget</strong> in the left sidebar, then click <em>“✨ Generate Strategic Plan”</em>.</p>
</div>
""",
        unsafe_allow_html=True,
    )
