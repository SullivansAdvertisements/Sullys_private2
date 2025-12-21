# ===============================
# Sully’s Multi-Platform Media Planner (ADVANCED)
# ===============================

import io
from pathlib import Path
import streamlit as st
import pandas as pd

# ---- Clients (logic only, no UI inside them) ----
from clients.common_ai import (
    generate_headlines,
    generate_descriptions,
    generate_hashtags,
    generate_email_outreach,
)
from clients.trends_client import get_advanced_trends
from clients.meta_client import (
    meta_connection_status,
    meta_reach_estimate,
)
from clients.google_client import google_connection_status
from clients.tiktok_client import tiktok_connection_status
from clients.spotify_client import spotify_connection_status

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Sully’s Media Planner",
    page_icon="🌺",
    layout="wide",
)

# ===============================
# LIGHT THEME (NO DARK MODE)
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
        "Research → Strategy → Campaign Planning → Influencers → Email Outreach"
    )

st.markdown("---")

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_column_width=True)

    st.markdown("### Platforms")
    st.write("• Meta (FB + IG)")
    st.write("• Google / YouTube")
    st.write("• TikTok")
    st.write("• Spotify")
    st.write("• Influencers")
    st.write("• Email Outreach")

# ===============================
# TABS
# ===============================
(
    tab_strategy,
    tab_research,
    tab_meta,
    tab_google,
    tab_tiktok,
    tab_spotify,
    tab_influencers,
    tab_email,
) = st.tabs(
    [
        "🧠 Strategy",
        "📊 Research & Trends",
        "📣 Meta",
        "🔍 Google / YouTube",
        "🎵 TikTok",
        "🎧 Spotify",
        "🤝 Influencers",
        "✉️ Email Marketing",
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

    region = st.selectbox("Target Region", ["Worldwide", "US", "UK", "CA", "EU"])

    if st.button("Generate Strategy"):
        st.success("Strategy Generated")

        st.markdown("### Budget Allocation (Auto-Guided)")
        st.write("• Meta: 35–45%")
        st.write("• Google / YouTube: 25–35%")
        st.write("• TikTok: 15–25%")
        st.write("• Spotify: 5–10%")

        st.markdown("### Headline Direction")
        for h in generate_headlines(niche, goal):
            st.write("•", h)

# ======================================================
# 📊 RESEARCH & TRENDS TAB
# ======================================================
with tab_research:
    st.subheader("📊 Advanced Research & Trends")

    seed = st.text_input(
        "Keyword / Interest Seed",
        placeholder="streetwear, hip hop, home care",
    )
    geo = st.selectbox("Geo", ["US", "Worldwide", "UK", "CA", "EU"])
    timeframe = st.selectbox(
        "Timeframe",
        ["now 7-d", "today 3-m", "today 12-m", "today 5-y"],
        index=2,
    )

    if st.button("Run Research"):
        with st.spinner("Fetching cross-platform trend intelligence..."):
            data = get_advanced_trends(
                seed,
                geo="" if geo == "Worldwide" else geo,
                timeframe=timeframe,
            )

        if data.get("interest_over_time") is not None:
            st.markdown("### Interest Over Time")
            st.line_chart(data["interest_over_time"])

        if data.get("regions") is not None:
            st.markdown("### Top Regions")
            st.dataframe(data["regions"])

        st.markdown("### Hashtags by Platform")
        tags = generate_hashtags(seed, niche)
        for platform, vals in tags.items():
            st.write(f"**{platform.title()}**:", ", ".join(vals))

# ======================================================
# 📣 META TAB
# ======================================================
with tab_meta:
    st.subheader("📣 Meta Reach & Planning")

    ok, msg = meta_connection_status(st.secrets)
    st.write(msg)

    daily_budget = st.number_input(
        "Daily Budget ($)",
        min_value=10,
        value=50,
    )

    if st.button("Estimate Meta Reach"):
        reach = meta_reach_estimate(daily_budget)
        st.success("Estimated Reach")
        st.json(reach)

# ======================================================
# 🔍 GOOGLE / YOUTUBE TAB
# ======================================================
with tab_google:
    st.subheader("🔍 Google / YouTube Status")
    ok, msg = google_connection_status(st.secrets)
    st.write(msg)

# ======================================================
# 🎵 TIKTOK TAB
# ======================================================
with tab_tiktok:
    st.subheader("🎵 TikTok Ads Status")
    ok, msg = tiktok_connection_status(st.secrets)
    st.write(msg)

# ======================================================
# 🎧 SPOTIFY TAB
# ======================================================
with tab_spotify:
    st.subheader("🎧 Spotify Ads Status")
    ok, msg = spotify_connection_status(st.secrets)
    st.write(msg)

# ======================================================
# 🤝 INFLUENCER TAB
# ======================================================
with tab_influencers:
    st.subheader("🤝 Influencer List Builder")

    inf_niche = st.selectbox("Industry", ["Music", "Fashion", "Homecare"])
    inf_platform = st.selectbox("Platform", ["Instagram", "TikTok", "YouTube"])
    inf_size = st.selectbox(
        "Creator Size",
        ["Nano (1k–10k)", "Micro (10k–100k)", "Mid (100k–500k)", "Macro (500k+)"],
    )

    if st.button("Generate Influencer Criteria"):
        st.success("Influencer Target Profile")
        st.write(f"• Platform: {inf_platform}")
        st.write(f"• Niche: {inf_niche}")
        st.write(f"• Size: {inf_size}")
        st.write("• Look for consistent engagement & niche relevance")

# ======================================================
# ✉️ EMAIL MARKETING TAB
# ======================================================
with tab_email:
    st.subheader("✉️ Influencer / Brand Email Outreach")

    email_type = st.selectbox(
        "Email Type",
        ["Influencer Collaboration", "Brand Partnership", "Press / Promo"],
    )
    sender = st.text_input("Your Brand / Name", value="Sully’s")
    offer = st.text_input(
        "Offer / Pitch",
        value="Paid collaboration + long-term partnership opportunity",
    )

    if st.button("Generate Email"):
        email = generate_email_outreach(
            email_type=email_type,
            sender=sender,
            offer=offer,
            niche=niche,
        )

        st.success("Email Draft Generated")
        st.text_area("Email Copy", email, height=220)