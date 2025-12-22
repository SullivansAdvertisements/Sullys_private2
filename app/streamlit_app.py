import streamlit as st
from pathlib import Path

# -----------------------------
# IMPORT CORE / CLIENT MODULES
# -----------------------------
from core.strategies import allocate_budget
from core.common_ai import generate_ad_copy

from research.trends_client import get_google_trends
from research.tiktok_trends import get_tiktok_trends
from research.meta_library import get_meta_ad_examples

from clients.meta_client import meta_connection_status
from clients.google_client import google_connection_status
from clients.tiktok_client import tiktok_connection_status
from clients.spotify_client import spotify_connection_status

from influencer.influencer import find_influencers

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Sully’s Multi-Platform Media Planner",
    page_icon="🌺",
    layout="wide",
)

# -----------------------------
# ASSETS
# -----------------------------
APP_DIR = Path(__file__).resolve().parent
ASSETS = APP_DIR / "assets"

LOGO = ASSETS / "logo.png"
SIDEBAR_BG = ASSETS / "sidebar_bg.png"
BACKGROUND = ASSETS / "background.png"

# -----------------------------
# STYLING (LIGHT MODE, VISIBLE)
# -----------------------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{BACKGROUND.name}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    [data-testid="stSidebar"] {{
        background-image: url("{SIDEBAR_BG.name}");
        background-size: cover;
        background-position: center;
    }}

    body, p, span, div, label {{
        color: #111 !important;
        font-family: "Segoe UI", sans-serif;
    }}

    h1, h2, h3, h4 {{
        color: #111 !important;
        font-weight: 700;
    }}

    .stTabs [role="tab"] p {{
        color: #111 !important;
        font-weight: 600;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# HEADER
# -----------------------------
col1, col2 = st.columns([1, 4])
with col1:
    if LOGO.exists():
        st.image(str(LOGO), use_column_width=True)
with col2:
    st.markdown("## Sully’s Multi-Platform Media Planner")
    st.caption(
        "Strategy, research, influencer discovery, and campaign planning across Meta, Google, TikTok, Spotify."
    )

st.markdown("---")

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_column_width=True)

    st.markdown("### Planner Controls")

    total_budget = st.number_input(
        "Monthly Budget (USD)",
        min_value=5000,
        step=500,
        value=5000,
    )

    selected_platforms = st.multiselect(
        "Platforms to include",
        ["Meta", "Google", "TikTok", "Spotify"],
        default=["Meta", "Google", "TikTok"],
    )

    niche = st.selectbox(
        "Business Niche",
        ["Music", "Clothing", "Homecare"],
    )

    goal = st.selectbox(
        "Primary Goal",
        ["Awareness", "Traffic", "Leads", "Sales"],
    )

# -----------------------------
# TABS
# -----------------------------
tab_strategy, tab_research, tab_google, tab_tiktok, tab_spotify, tab_meta, tab_influencer = st.tabs(
    [
        "🧠 Strategy",
        "📊 Research & Trends",
        "🔍 Google / YouTube",
        "🎵 TikTok",
        "🎧 Spotify",
        "📣 Meta",
        "🤝 Influencers & Email",
    ]
)

# ======================================================
# STRATEGY TAB
# ======================================================
with tab_strategy:
    st.subheader("🧠 Cross-Platform Strategy Engine")

    try:
        allocation = allocate_budget(total_budget, selected_platforms)
        st.success("Budget allocation complete")

        st.markdown("### Budget Split")
        st.json(allocation)

        st.markdown("### Auto Recommendations")
        st.write(
            "• Scale Meta & Google once CPA stabilizes\n"
            "• Use TikTok for discovery + creative testing\n"
            "• Retarget across platforms after 14 days"
        )

    except Exception as e:
        st.error(str(e))

# ======================================================
# RESEARCH & TRENDS TAB
# ======================================================
with tab_research:
    st.subheader("📊 Research & Trend Intelligence")

    seed = st.text_input(
        "Keyword / Interest Seed",
        placeholder="streetwear, hip hop artist, home care services",
    )

    if seed:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### Google & YouTube Trends")
            st.dataframe(get_google_trends(seed))

        with col2:
            st.markdown("#### TikTok Trends")
            st.dataframe(get_tiktok_trends(seed))

        with col3:
            st.markdown("#### Meta Ad Library")
            st.dataframe(get_meta_ad_examples(seed))

# ======================================================
# GOOGLE / YOUTUBE TAB
# ======================================================
with tab_google:
    st.subheader("🔍 Google / YouTube Campaign Planner")

    ok, msg = google_connection_status(st.secrets)
    st.success(msg) if ok else st.warning(msg)

    if st.button("Generate Google Headlines"):
        copy = generate_ad_copy(niche, goal)
        st.json(copy)

# ======================================================
# TIKTOK TAB
# ======================================================
with tab_tiktok:
    st.subheader("🎵 TikTok Campaign Planner")

    ok, msg = tiktok_connection_status(st.secrets)
    st.success(msg) if ok else st.warning(msg)

    if st.button("Generate TikTok Hooks"):
        copy = generate_ad_copy(niche, goal)
        st.json(copy)

# ======================================================
# SPOTIFY TAB
# ======================================================
with tab_spotify:
    st.subheader("🎧 Spotify Audio Planner")

    ok, msg = spotify_connection_status(st.secrets)
    st.success(msg) if ok else st.warning(msg)

    if st.button("Generate Audio Script"):
        copy = generate_ad_copy(niche, goal)
        st.json(copy)

# ======================================================
# META TAB
# ======================================================
with tab_meta:
    st.subheader("📣 Meta Campaign Builder")

    ok, msg = meta_connection_status(st.secrets)
    st.success(msg) if ok else st.warning(msg)

    if st.button("Generate Meta Ad Copy"):
        copy = generate_ad_copy(niche, goal)
        st.json(copy)

# ======================================================
# INFLUENCER + EMAIL TAB
# ======================================================
with tab_influencer:
    st.subheader("🤝 Influencer Discovery & Outreach")

    influencer_seed = st.text_input(
        "Influencer Topic / Keyword",
        placeholder="streetwear influencers, hip hop creators",
    )

    if influencer_seed:
        results = find_influencers(influencer_seed)
        st.dataframe(results)

        st.markdown("### Outreach Email Template")
        st.code(
            f"""
Hi {{Creator Name}},

We love your content around {influencer_seed}.
We’re working with a brand in the {niche} space and would love to collaborate.

Let us know if you're interested!

– Sullivan’s Advertisements
            """,
            language="text",
        )