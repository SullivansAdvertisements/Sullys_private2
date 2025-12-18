# ==============================
# STREAMLIT APP ENTRY POINT
# ==============================

import sys
import os

# Ensure app/ is treated as root (critical for Streamlit Cloud)
sys.path.append(os.path.dirname(__file__))

import streamlit as st

# ==============================
# IMPORT CLIENT MODULES
# ==============================

from clients.common_ai import (
    generate_headlines,
    summarize_insights
)

from clients.google_client import google_insights
from clients.meta_client import meta_insights
from clients.tiktok_client import tiktok_insights
from clients.spotify_client import spotify_insights
from clients.trends_client import trend_research

# ==============================
# STREAMLIT PAGE CONFIG
# ==============================

st.set_page_config(
    page_title="Sullivan’s Advertisements – Marketing AI",
    layout="wide"
)

st.title("📊 Sullivan’s Advertisements – Marketing Research AI")
st.caption("Unified research, trends & ad intelligence across platforms")

# ==============================
# SIDEBAR INPUTS
# ==============================

with st.sidebar:
    st.header("🔍 Research Controls")

    seed_input = st.text_input(
        "Seed Keyword / Artist / Brand",
        placeholder="e.g. streetwear brand, hip hop artist, local business"
    )

    generate_btn = st.button("Run Research")

# ==============================
# TABS
# ==============================

tab_google, tab_meta, tab_tiktok, tab_spotify, tab_trends, tab_ai = st.tabs(
    [
        "Google",
        "Meta",
        "TikTok",
        "Spotify",
        "Trends",
        "AI Summary"
    ]
)

# ==============================
# GOOGLE TAB
# ==============================

with tab_google:
    st.subheader("Google Insights")

    if generate_btn and seed_input:
        data = google_insights(seed_input)
        st.write(data)
    else:
        st.info("Enter a seed input and click Run Research.")

# ==============================
# META TAB
# ==============================

with tab_meta:
    st.subheader("Meta (Facebook / Instagram) Insights")

    if generate_btn and seed_input:
        data = meta_insights(seed_input)
        st.write(data)
    else:
        st.info("Waiting for input.")

# ==============================
# TIKTOK TAB
# ==============================

with tab_tiktok:
    st.subheader("TikTok Insights")

    if generate_btn and seed_input:
        data = tiktok_insights(seed_input)
        st.write(data)
    else:
        st.info("Waiting for input.")

# ==============================
# SPOTIFY TAB
# ==============================

with tab_spotify:
    st.subheader("Spotify Insights")

    if generate_btn and seed_input:
        data = spotify_insights(seed_input)
        st.write(data)
    else:
        st.info("Waiting for input.")

# ==============================
# TRENDS TAB
# ==============================

with tab_trends:
    st.subheader("Trend Research (1M – 5Y)")

    if generate_btn and seed_input:
        data = trend_research(seed_input)
        st.write(data)
    else:
        st.info("Waiting for input.")

# ==============================
# AI SUMMARY TAB
# ==============================

with tab_ai:
    st.subheader("AI Strategy Summary")

    if generate_btn and seed_input:
        combined_text = f"""
        Google: {google_insights(seed_input)}
        Meta: {meta_insights(seed_input)}
        TikTok: {tiktok_insights(seed_input)}
        Spotify: {spotify_insights(seed_input)}
        Trends: {trend_research(seed_input)}
        """

        summary = summarize_insights(combined_text)
        headlines = generate_headlines(seed_input)

        st.markdown("### 📌 Key Insights")
        st.write(summary)

        st.markdown("### 🧠 Suggested Headlines")
        for h in headlines:
            st.write(f"• {h}")

    else:
        st.info("Run research to generate AI insights.")
