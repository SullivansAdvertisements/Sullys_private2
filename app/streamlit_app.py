import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
# ==========================================================
# Sully's Multi-Platform Marketing Intelligence Platform
# ==========================================================

# -------------------------
# PATH FIX (REQUIRED FOR STREAMLIT CLOUD)
# -------------------------
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.append(str(APP_ROOT))

# -------------------------
# STANDARD IMPORTS
# -------------------------
import streamlit as st
import pandas as pd
from datetime import datetime

# -------------------------
# INTERNAL IMPORTS (SAFE)
# -------------------------
from core.strategies import allocate_budget
from core.common_ai import (
    generate_meta_creatives,
    generate_google_ads,
    generate_tiktok_hooks,
    generate_spotify_script,
)

from research.trends_client import get_google_trends
from research.tiktok_trends import get_tiktok_trends
from research.meta_library import search_meta_ads

from clients.meta_client import meta_connection_status
from clients.google_client import google_connection_status
from clients.tiktok_client import tiktok_connection_status
from clients.spotify_client import spotify_connection_status

from influencer.influencer import find_influencers

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Sully’s Marketing Intelligence",
    page_icon="🌺",
    layout="wide",
)

# -------------------------
# STYLING (LIGHT MODE, MOBILE SAFE)
# -------------------------
st.markdown("""
<style>
.stApp {
    background-color: #f8f9fc;
}
h1, h2, h3, h4 {
    color: #111;
}
p, label, div, span {
    color: #111 !important;
}
[data-testid="stSidebar"] {
    background-color: #141628;
}
[data-testid="stSidebar"] * {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# ASSETS
# -------------------------
ASSETS = APP_ROOT / "assets"
LOGO = ASSETS / "logo.png"

# -------------------------
# HEADER
# -------------------------
cols = st.columns([1, 4])
with cols[0]:
    if LOGO.exists():
        st.image(str(LOGO), use_column_width=True)
with cols[1]:
    st.title("Sully’s Marketing Intelligence Platform")
    st.caption("Campaign planning, research, and creative generation across all major ad platforms.")

st.divider()

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_column_width=True)
    st.markdown("### Platform Status")
    st.write("Meta:", meta_connection_status(st.secrets)[1])
    st.write("Google:", google_connection_status(st.secrets)[1])
    st.write("TikTok:", tiktok_connection_status(st.secrets)[1])
    st.write("Spotify:", spotify_connection_status(st.secrets)[1])

# -------------------------
# TABS
# -------------------------
tab_strategy, tab_research, tab_meta, tab_google, tab_tiktok, tab_spotify, tab_influencer = st.tabs([
    "🧠 Strategy",
    "📊 Research",
    "📣 Meta",
    "🔍 Google / YouTube",
    "🎵 TikTok",
    "🎧 Spotify",
    "🤝 Influencers",
])

# ==========================================================
# STRATEGY TAB
# ==========================================================
with tab_strategy:
    st.subheader("Strategy Planner")

    niche = st.selectbox("Business Type", ["Music", "Clothing", "Home Care"])
    goal = st.selectbox("Primary Goal", ["Awareness", "Traffic", "Leads", "Sales"])
    budget = st.number_input("Monthly Budget (minimum $500)", min_value=500, value=5000, step=500)

    platforms = st.multiselect(
        "Platforms to Use",
        ["Meta", "Google", "TikTok", "YouTube", "Spotify"],
        default=["Meta", "Google", "TikTok"]
    )

    if st.button("Generate Strategy"):
        plan = allocate_budget(budget, platforms, goal)
        st.success("Strategy Generated")
        st.json(plan)

# ==========================================================
# RESEARCH TAB
# ==========================================================
with tab_research:
    st.subheader("Advanced Research & Trends")

    keyword = st.text_input("Seed Keyword / Interest")
    country = st.text_input("Country (ISO)", value="US")

    if st.button("Run Research"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### Google Trends")
            st.json(get_google_trends(keyword, country))

        with col2:
            st.markdown("### TikTok Trends")
            st.json(get_tiktok_trends(keyword))

        with col3:
            st.markdown("### Meta Ad Library")
            st.json(search_meta_ads(keyword))

# ==========================================================
# META TAB
# ==========================================================
with tab_meta:
    st.subheader("Meta Campaign Generator")

    meta_ok, meta_msg = meta_connection_status(st.secrets)
    if not meta_ok:
        st.warning(meta_msg)
    else:
        st.success(meta_msg)

    headline = generate_headlines("Meta", niche, goal)[0]
    primary = generate_primary_text(niche, goal)
    cta = generate_ctas(goal)[0]

    st.markdown("### Suggested Ad Copy")
    st.write("Headline:", headline)
    st.write("Primary Text:", primary)
    st.write("CTA:", cta)

# ==========================================================
# GOOGLE / YOUTUBE TAB
# ==========================================================
with tab_google:
    st.subheader("Google & YouTube Campaign Planner")

    st.write("Suggested Headlines:")
    for h in generate_headlines("Google", niche, goal):
        st.write("-", h)

# ==========================================================
# TIKTOK TAB
# ==========================================================
with tab_tiktok:
    st.subheader("TikTok Creative Planner")

    hooks = generate_headlines("TikTok", niche, goal)
    st.markdown("### Video Hooks")
    for h in hooks:
        st.write("-", h)

# ==========================================================
# SPOTIFY TAB
# ==========================================================
with tab_spotify:
    st.subheader("Spotify Audio Planner")

    st.markdown("### Audio Script Starter")
    st.write(generate_primary_text(niche, "Awareness"))

# ==========================================================
# INFLUENCER TAB
# ==========================================================
with tab_influencer:
    st.subheader("Influencer Discovery")

    niche_kw = st.text_input("Influencer Niche Keyword")
    if st.button("Find Influencers"):
        st.json(find_influencers(niche_kw))