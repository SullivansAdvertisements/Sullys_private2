import sys
import os

# --- HARD SET APP ROOT ---
APP_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENTS_DIR = os.path.join(APP_DIR, "clients")

if CLIENTS_DIR not in sys.path:
    sys.path.insert(0, CLIENTS_DIR)

import streamlit as st

# --- CLIENT IMPORTS ---
from common_ai import generate_headlines, summarize_insights
from google_client import google_insights
from meta_client import meta_insights
from tiktok_client import tiktok_insights
from spotify_client import spotify_insights
from trends_client import trend_research
import os
st.sidebar.write("Clients dir exists:", os.path.exists(CLIENTS_DIR))
st.sidebar.write("Files:", os.listdir(CLIENTS_DIR) if os.path.exists(CLIENTS_DIR) else "MISSING")



# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Sullivan's Ads Super Generator",
    page_icon="📈",
    layout="wide"
)

APP_DIR = Path(__file__).parent
ASSETS = APP_DIR / "assets"
LOGO = ASSETS / "sullivans_logo.png"
HEADER_BG = ASSETS / "header_bg.png"
SIDEBAR_BG = ASSETS / "sidebar_bg.png"

# ============================================================
# STYLES
# ============================================================
st.markdown(f"""
<style>
header {{
    background-image: url("file://{HEADER_BG}");
    background-size: cover;
}}
[data-testid="stSidebar"] {{
    background-image: url("file://{SIDEBAR_BG}");
    background-size: cover;
}}
.block-container {{ padding-top: 2rem; }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
col1, col2 = st.columns([1, 4])
with col1:
    if LOGO.exists():
        st.image(str(LOGO), width=120)
with col2:
    st.title("Sullivan's Multi-Platform Ad Intelligence Bot")
    st.caption("AI-powered research, planning & campaign generation")

st.divider()

# ============================================================
# SIDEBAR INPUTS (GLOBAL)
# ============================================================
with st.sidebar:
    st.header("Campaign Inputs")
    brand = st.text_input("Brand / Product")
    objective = st.selectbox("Primary Objective", [
        "Awareness", "Traffic", "Leads", "Conversions", "Sales"
    ])
    daily_budget = st.slider("Daily Budget ($)", 10, 5000, 100)
    seed_keywords = st.text_area(
        "Seed Keywords / Interests",
        "streetwear, hip hop culture, viral fashion"
    )

# ============================================================
# TABS
# ============================================================
tab_trends, tab_google, tab_meta, tab_tiktok, tab_spotify, tab_ai = st.tabs([
    "📊 Trends & Research",
    "🔍 Google / YouTube",
    "📘 Meta (Facebook / Instagram)",
    "🎵 TikTok",
    "🎧 Spotify",
    "🧠 AI Strategy"
])

# ============================================================
# TRENDS TAB
# ============================================================
with tab_trends:
    st.subheader("Cross-Platform Trend Intelligence")

    if st.button("Run Trend Research"):
        trends = cross_platform_trends(seed_keywords)
        st.json(trends)

        summary = summarize_insights(trends)
        st.markdown("### AI Trend Summary")
        st.write(summary)

# ============================================================
# GOOGLE / YOUTUBE TAB
# ============================================================
with tab_google:
    st.subheader("Google & YouTube Campaign Generator")

    if st.button("Generate Google Campaign"):
        result = google_campaign_generator(
            brand=brand,
            objective=objective,
            budget=daily_budget,
            keywords=seed_keywords
        )
        st.json(result)

# ============================================================
# META TAB
# ============================================================
with tab_meta:
    st.subheader("Meta Ads Campaign Generator")

    if st.button("Generate Meta Campaign"):
        result = meta_campaign_generator(
            brand=brand,
            objective=objective,
            budget=daily_budget,
            keywords=seed_keywords
        )
        st.json(result)

# ============================================================
# TIKTOK TAB
# ============================================================
with tab_tiktok:
    st.subheader("TikTok Ads Campaign Generator")

    if st.button("Generate TikTok Campaign"):
        result = tiktok_campaign_generator(
            brand=brand,
            objective=objective,
            budget=daily_budget,
            keywords=seed_keywords
        )
        st.json(result)

# ============================================================
# SPOTIFY TAB
# ============================================================
with tab_spotify:
    st.subheader("Spotify Audio Campaign Generator")

    if st.button("Generate Spotify Campaign"):
        result = spotify_campaign_generator(
            brand=brand,
            objective=objective,
            budget=daily_budget,
            keywords=seed_keywords
        )
        st.json(result)

# ============================================================
# AI STRATEGY TAB
# ============================================================
with tab_ai:
    st.subheader("Unified AI Campaign Strategy")

    if st.button("Generate Master Strategy"):
        headlines = generate_headlines(
            brand=brand,
            objective=objective,
            keywords=seed_keywords
        )
        st.markdown("### Cross-Platform Headlines")
        st.write(headlines)
