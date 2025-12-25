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
with tab_with tabs[1]:  # Research & Trends tab
    st.header("📊 Research & Trends Engine"

    keyword = st.text_input("Enter keyword or niche", value="music artist")

    timeframe = st.selectbox(
        "Time Range",
        [
            "now 7-d",
            "today 1-m",
            "today 3-m",
            "today 12-m",
            "today 5-y"
        ]
    )

    geo = st.selectbox(
        "Geography",
        ["US", "Worldwide"]
    )
    
    st.markdown("#### Platforms")
    st.checkbox("Google Trends", value=True)
    st.checkbox("YouTube Trends", value=True)
    st.checkbox("TikTok Creative Center", value=True)
    st.checkbox("Meta Ad Library", value=True)

    st.button("Run Research")

    st.info(
        "This tab reads from:\n"
        "- research/google_trends.py\n"
        "- research/youtube_trends.py\n"
        "- research/tiktok_trends.py\n"
        "- research/meta_library.py\n\n"
        "No logic is duplicated here."
    )

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