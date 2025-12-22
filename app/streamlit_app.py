import streamlit as st
from pathlib import Path

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Sully’s Marketing Intelligence",
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------
# Paths (Streamlit Cloud safe)
# ----------------------------
APP_DIR = Path(__file__).parent
MAIN_BG = APP_DIR / "main_bg.png"          # ← recent logo as main background
SIDEBAR_BG = APP_DIR / "sidebar_bg.png"    # ← sidebar background
LOGO = APP_DIR / "sullivans_logo.png"      # optional header logo

# ----------------------------
# CSS Styling
# ----------------------------
st.markdown(
    f"""
    <style>

    /* ---------- MAIN APP BACKGROUND ---------- */
    .stApp {{
        background-image: url("{MAIN_BG.as_posix()}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }}

    /* Light overlay so text stays readable */
    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(255,255,255,0.88);
        z-index: -1;
    }}

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {{
        background-image: url("{SIDEBAR_BG.as_posix()}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    [data-testid="stSidebar"] * {{
        color: #ffffff !important;
        font-weight: 600;
    }}

    /* ---------- TEXT VISIBILITY ---------- */
    body, p, span, div, label {{
        color: #111111 !important;
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    h1, h2, h3, h4, h5 {{
        color: #0b0b0b !important;
        font-weight: 800;
    }}

    /* ---------- INPUTS ---------- */
    input, textarea, select {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}

    /* ---------- TABS ---------- */
    .stTabs [role="tab"] p {{
        color: #111111 !important;
        font-weight: 600;
    }}

    /* ---------- STICKY HEADER ---------- */
    header {{
        position: sticky;
        top: 0;
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(6px);
        z-index: 999;
        border-bottom: 1px solid #ddd;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Header
# ----------------------------
header_cols = st.columns([1, 4])
with header_cols[0]:
    if LOGO.exists():
        st.image(str(LOGO), width=120)

with header_cols[1]:
    st.title("Sully’s Multi-Platform Marketing Brain")
    st.caption(
        "Strategy • Research • Campaign Generation • Influencer Outreach"
    )

st.markdown("---")

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_column_width=True)

    st.markdown("### Platform Modules")
    st.write("• Meta (Facebook & Instagram)")
    st.write("• Google & YouTube")
    st.write("• TikTok")
    st.write("• Spotify")
    st.write("• Influencer + Email")

# ----------------------------
# Tabs
# ----------------------------
tab_strategy, tab_research, tab_google, tab_tiktok, tab_spotify, tab_meta, tab_influencer = st.tabs(
    [
        "🧠 Strategy",
        "📊 Research & Trends",
        "🔍 Google / YouTube",
        "🎵 TikTok",
        "🎧 Spotify",
        "📣 Meta",
        "🤝 Influencer + Email",
    ]
)

# ----------------------------
# Strategy Tab
# ----------------------------
with tab_strategy:
    st.subheader("🧠 Strategy Engine")

    budget = st.number_input(
        "Monthly Budget (minimum $500)",
        min_value=500,
        step=100,
        value=5000,
    )

    platforms = st.multiselect(
        "Select platforms to include",
        ["Meta", "Google / YouTube", "TikTok", "Spotify"],
        default=["Meta", "Google / YouTube", "TikTok"],
    )

    st.info(
        "Phase 2 will auto-rebalance budgets, forecast reach, and scale winners automatically."
    )

# ----------------------------
# Research Tab
# ----------------------------
with tab_research:
    st.subheader("📊 Research & Trends")

    seed = st.text_input(
        "Keyword / Interest Seed",
        placeholder="streetwear, hip hop artist, home care services",
    )

    location = st.text_input(
        "Target Location (Country / State / City)",
        placeholder="United States, California, Los Angeles",
    )

    st.info(
        "This tab will aggregate:\n"
        "- Google Trends\n"
        "- YouTube search demand\n"
        "- TikTok trending topics\n"
        "- Meta Ad Library signals\n"
        "- Hashtags & audience interests\n\n"
        "All wired in Phase 2."
    )

# ----------------------------
# Google / YouTube Tab
# ----------------------------
with tab_google:
    st.subheader("🔍 Google & YouTube Campaign Generator")
    st.info("Campaign + keyword + audience builder coming next phase.")

# ----------------------------
# TikTok Tab
# ----------------------------
with tab_tiktok:
    st.subheader("🎵 TikTok Campaign Generator")
    st.info("Creative hooks, Spark Ads & trend-driven targeting coming next phase.")

# ----------------------------
# Spotify Tab
# ----------------------------
with tab_spotify:
    st.subheader("🎧 Spotify Audio Campaigns")
    st.info("Audio scripts + audience discovery coming next phase.")

# ----------------------------
# Meta Tab
# ----------------------------
with tab_meta:
    st.subheader("📣 Meta Campaign Builder")
    st.info(
        "Campaign → Ad Set → Ad automation\n"
        "Real reach estimates via Meta Reach API\n"
        "Pixel + IG actor support\n\n"
        "Activates in Phase 2."
    )

# ----------------------------
# Influencer + Email Tab
# ----------------------------
with tab_influencer:
    st.subheader("🤝 Influencer Research + Email Outreach")

    st.info(
        "This module will:\n"
        "- Find influencers by niche & location\n"
        "- Generate outreach emails\n"
        "- Build contact lists\n"
        "- Export to CSV\n\n"
        "Activates in Phase 3."
    )