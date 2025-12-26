# ============================================================
# Sully’s Advertisements – Multi-Platform Strategy Console
# UI ONLY – uses existing clients/, core/, research/, influencer/
# ============================================================

import streamlit as st
from pathlib import Path

# ---------- MUST BE FIRST ----------
st.set_page_config(
    page_title="Sullivan’s Advertisements",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- PATHS ----------
APP_DIR = Path(__file__).parent
ASSETS = APP_DIR / "assets"
MAIN_BG = ASSETS / "main_bg.png"
SIDEBAR_BG = ASSETS / "sidebar_bg.png"
LOGO = ASSETS / "sullivans_logo.png"

# ---------- BACKGROUND + SIDEBAR ----------
def inject_css():
    main_bg = MAIN_BG.as_posix()
    sidebar_bg = SIDEBAR_BG.as_posix()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("{main_bg}") no-repeat center center fixed;
            background-size: cover;
        }}

        section[data-testid="stSidebar"] {{
            background: url("{sidebar_bg}") no-repeat center center fixed;
            background-size: cover;
        }}

        h1, h2, h3, h4, h5, h6,
        p, label, span, div {{
            color: #111 !important;
        }}

        div[data-testid="stSelectbox"] > div {{
            background-color: white !important;
        }}

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {{
            background-color: white !important;
            color: black !important;
        }}

        .block-container {{
            padding-top: 2rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

inject_css()

# ---------- SIDEBAR ----------
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_column_width=True)

    st.markdown("### Navigation")
    st.caption("Sullivan’s Advertisements AI Console")

# ---------- HEADER ----------
st.markdown("## 📈 Sullivan’s Multi-Platform Growth Engine")
st.caption("Strategy • Research • Campaign Planning • Influencer Outreach")

# ---------- TABS ----------
tab_strategy, tab_research, tab_google, tab_tiktok, tab_spotify, tab_meta, tab_influencer, tab_email = st.tabs(
    [
        "🧠 Strategy",
        "📊 Research & Trends",
        "🔍 Google / YouTube",
        "🎵 TikTok",
        "🎧 Spotify",
        "📣 Meta",
        "🤝 Influencers",
        "✉️ Email Marketing",
    ]
)

# ============================================================
# STRATEGY TAB
# ============================================================
with tab_strategy:
    st.subheader("🧠 Campaign Strategy Builder")

    niche = st.selectbox(
        "Business Type",
        ["Music", "Clothing Brand", "Home Services", "E-commerce", "Local Business"],
        key="strategy_niche"
    )

    goal = st.selectbox(
        "Primary Goal",
        ["Awareness", "Traffic", "Leads", "Conversions", "Sales"],
        key="strategy_goal"
    )

    budget = st.number_input(
        "Monthly Budget (USD)",
        min_value=500,
        step=250,
        value=5000,
        key="strategy_budget"
    )

    platforms = st.multiselect(
        "Platforms to include",
        ["Meta", "Google / YouTube", "TikTok", "Spotify"],
        default=["Meta", "Google / YouTube", "TikTok"],
        key="strategy_platforms"
    )

if st.button("Generate Strategy Plan"):
    from core.strategies import generate_strategy

    strategy = generate_strategy(
        niche=niche,
        goal=goal,
        budget=budget,
        platforms=platforms
    )

    st.success("Strategy Generated")
    st.json(strategy)

    st.success("Strategy Generated")
    st.json(strategy)

# ============================================================
# RESEARCH TAB (USES research/ FOLDER)
# ============================================================
with tabs[1]:
    st.header("📊 Research & Trends Engine")

    # --- Imports INSIDE tab to avoid Streamlit crashes ---
    from research.google_trends import get_google_trends
    from research.youtube_trends import get_youtube_trends
    from research.tiktok_trends import get_tiktok_trends
    from research.meta_library import search_meta_ads

    # --- User Inputs ---
    seed = st.text_input("Seed Keyword / Niche", placeholder="e.g. streetwear, music marketing")
    geo = st.selectbox("Target Location", ["Worldwide", "United States", "United Kingdom", "Canada"])
    timeframe = st.selectbox(
        "Trend Timeframe",
        ["7d", "30d", "90d", "12m", "5y"]
    )

    run = st.button("🚀 Run Research")

    if run and seed:
        with st.spinner("Collecting cross-platform research..."):
            research_data = {
                "seed": seed,
                "geo": geo,
                "timeframe": timeframe,
                "google_trends": get_google_trends(seed, geo, timeframe),
                "youtube_trends": get_youtube_trends(seed, geo),
                "tiktok_trends": get_tiktok_trends(seed),
                "meta_ads": search_meta_ads(seed)
            }

            # --- Persist data for other tabs ---
            st.session_state["research"] = research_data

        st.success("Research complete. Data is now available to all platform tabs.")

        # --- Preview ---
        st.subheader("🔍 Research Snapshot")

        st.write("### Google / YouTube Trends")
        st.json(research_data["google_trends"])

        st.write("### TikTok Creative Center")
        st.json(research_data["tiktok_trends"])

        st.write("### Meta Ad Library")
        st.json(research_data["meta_ads"])

    elif run and not seed:
        st.warning("Please enter a seed keyword.")

# ============================================================
# GOOGLE / YOUTUBE
# ============================================================
with tab_google:
    st.subheader("🔍 Google & YouTube Campaign Planner")
    st.text_input("Landing Page URL", key="google_url")
    st.text_area("Primary Keywords", key="google_keywords")
    st.number_input("Daily Budget", min_value=5, value=50, key="google_budget")
    st.button("Generate Google / YouTube Plan")

# ============================================================
# TIKTOK
# ============================================================
with tab_tiktok:
    st.subheader("🎵 TikTok Campaign Planner")
    st.text_area("Creative Hooks", key="tiktok_hooks")
    st.number_input("Daily Budget", min_value=5, value=30, key="tiktok_budget")
    st.button("Generate TikTok Plan")

# ============================================================
# SPOTIFY
# ============================================================
with tab_spotify:
    st.subheader("🎧 Spotify Audio Campaign")
    st.text_area("30s Audio Script", key="spotify_script")
    st.number_input("Daily Budget", min_value=5, value=25, key="spotify_budget")
    st.button("Generate Spotify Plan")

# ============================================================
# META
# ============================================================
with tab_meta:
    st.subheader("📣 Meta (Facebook & Instagram)")
    st.text_area("Primary Text", key="meta_primary")
    st.text_input("Headline", key="meta_headline")
    st.text_input("CTA", key="meta_cta")
    st.button("Generate Meta Ad Copy")

# ============================================================
# INFLUENCERS
# ============================================================
with tab_influencer:
    st.subheader("🤝 Influencer Discovery")
    st.text_input("Niche / Keyword", key="influencer_keyword")
    st.selectbox("Platform", ["Instagram", "YouTube", "TikTok"], key="influencer_platform")
    st.button("Find Influencers")

# ============================================================
# EMAIL MARKETING
# ============================================================
with tab_email:
    st.subheader("✉️ Influencer Outreach Email")
    st.text_input("Brand Name", key="email_brand")
    st.text_input("Influencer Name", key="email_name")
    st.text_area("Offer / Pitch", key="email_pitch")
    st.button("Generate Outreach Email")