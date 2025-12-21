# ===============================
# Sully’s Multi-Platform Media Planner
# ===============================

import io
from pathlib import Path
import streamlit as st
import pandas as pd

# ---- Clients ----
from clients.common_ai import (
    generate_headlines,
    generate_descriptions,
    generate_hashtags,
)
from clients.trends_client import get_advanced_trends
from clients.meta_client import (
    meta_connection_status,
    meta_reach_estimate,
    meta_sample_call,
)
from clients.google_client import (
    google_connection_status,
    youtube_connection_status,
    google_sample_call,
)
from clients.tiktok_client import (
    tiktok_connection_status,
    tiktok_sample_call,
)
from clients.spotify_client import (
    spotify_connection_status,
    spotify_sample_call,
)

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Sully’s Media Planner",
    page_icon="🌺",
    layout="wide",
)

# ===============================
# GLOBAL STYLING (LIGHT MODE)
# ===============================
st.markdown(
    """
    <style>
    .stApp { background-color: #f7f7fb; }
    body, p, span, label, div {
        color: #111 !important;
        font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto;
    }
    h1, h2, h3, h4 {
        color: #111 !important;
        font-weight: 700;
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    .stTabs [role="tab"] p { color: #111 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===============================
# ASSETS
# ===============================
APP_DIR = Path(__file__).resolve().parent
LOGO = APP_DIR / "assets" / "sullivans_logo.png"

# ===============================
# HEADER
# ===============================
cols = st.columns([1, 4])
with cols[0]:
    if LOGO.exists():
        st.image(str(LOGO), use_column_width=True)
with cols[1]:
    st.markdown("## Sully’s Multi-Platform Media Planner")
    st.caption(
        "Research → Strategy → Cross-Platform Campaign Planning "
        "(Meta · Google · YouTube · TikTok · Spotify)"
    )

st.markdown("---")

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_column_width=True)
    st.markdown("### Active Platforms")
    st.write("• Meta (FB + IG)")
    st.write("• Google / YouTube")
    st.write("• TikTok Ads")
    st.write("• Spotify Audio")

# ===============================
# TABS
# ===============================
tab_strategy, tab_research, tab_google, tab_tiktok, tab_spotify, tab_meta = st.tabs(
    [
        "🧠 Strategy",
        "📊 Research & Trends",
        "🔍 Google / YouTube",
        "🎵 TikTok",
        "🎧 Spotify",
        "📣 Meta",
    ]
)

# ======================================================
# 🧠 STRATEGY TAB
# ======================================================
with tab_strategy:
    st.subheader("🧠 Strategy Engine")

    c1, c2, c3 = st.columns(3)
    with c1:
        niche = st.selectbox("Niche", ["Music", "Clothing", "Homecare"])
    with c2:
        goal = st.selectbox(
            "Primary Goal",
            ["Awareness", "Traffic", "Leads", "Conversions", "Sales"],
        )
    with c3:
        monthly_budget = st.number_input(
            "Monthly Budget (USD)",
            min_value=5000,
            step=500,
            value=5000,
        )

    geo = st.selectbox("Target Region", ["Worldwide", "US", "UK", "CA", "EU"])

    if st.button("Generate Strategy"):
        st.success("Strategy Generated")

        st.markdown("### Budget Guidance")
        st.write("• Meta: 35–45%")
        st.write("• Google / YouTube: 25–35%")
        st.write("• TikTok: 15–25%")
        st.write("• Spotify: 5–10%")

        st.markdown("### Creative Direction")
        for h in generate_headlines(niche, goal):
            st.write("•", h)

# ======================================================
# 📊 RESEARCH & TRENDS TAB
# ======================================================
with tab_research:
    st.subheader("📊 Research & Trend Intelligence")

    seed = st.text_input("Keyword / Interest Seed", placeholder="streetwear, hip hop, home care")

    geo = st.selectbox("Geo", ["US", "Worldwide", "UK", "CA", "EU"])
    timeframe = st.selectbox(
        "Timeframe",
        ["now 7-d", "today 3-m", "today 12-m", "today 5-y"],
        index=2,
    )

    if st.button("Run Research"):
        with st.spinner("Fetching trend intelligence..."):
            data = get_advanced_trends(seed, geo=geo if geo != "Worldwide" else "", timeframe=timeframe)

        if data.get("interest_over_time") is not None:
            st.markdown("### Interest Over Time")
            st.line_chart(data["interest_over_time"])

        if data.get("regions") is not None:
            st.markdown("### Top Regions")
            st.dataframe(data["regions"])

        st.markdown("### Platform Hashtags")
        tags = generate_hashtags(seed, niche)
        for platform, vals in tags.items():
            st.write(f"**{platform.title()}**:", ", ".join(vals))

# ======================================================
# 🔍 GOOGLE / YOUTUBE TAB
# ======================================================
with tab_google:
    st.subheader("🔍 Google & YouTube Planner")

    ok_g, g_msg = google_connection_status(st.secrets)
    ok_y, y_msg = youtube_connection_status(st.secrets)

    st.write("Google Ads:", g_msg)
    st.write("YouTube:", y_msg)

    if st.button("Sample Google API Call"):
        st.json(google_sample_call())

# ======================================================
# 🎵 TIKTOK TAB
# ======================================================
with tab_tiktok:
    st.subheader("🎵 TikTok Campaign Planner")

    ok_tt, tt_msg = tiktok_connection_status(st.secrets)
    st.write(tt_msg)

    if st.button("Sample TikTok Call"):
        st.json(tiktok_sample_call())

# ======================================================
# 🎧 SPOTIFY TAB
# ======================================================
with tab_spotify:
    st.subheader("🎧 Spotify Audio Campaigns")

    ok_sp, sp_msg = spotify_connection_status(st.secrets)
    st.write(sp_msg)

    if st.button("Sample Spotify Call"):
        st.json(spotify_sample_call())

# ======================================================
# 📣 META TAB
# ======================================================
with tab_meta:
    st.subheader("📣 Meta Campaign Intelligence")

    ok_meta, meta_msg = meta_connection_status(st.secrets)
    st.write(meta_msg)

    daily_budget = st.number_input("Daily Budget ($)", min_value=10, value=50)

    if st.button("Estimate Reach"):
        reach = meta_reach_estimate(daily_budget)
        st.success("Estimated Reach")
        st.json(reach)

    if st.button("Test Meta API"):
        st.json(meta_sample_call(st.secrets))