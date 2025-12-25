# ================================
# Sully’s Multi-Platform Media Bot
# PHASE 1 – UI FOUNDATION (STABLE)
# ================================

from pathlib import Path
import base64
import streamlit as st

# -------------------------------
# PAGE CONFIG (MUST BE FIRST)
# -------------------------------
st.set_page_config(
    page_title="Sully’s Media Planner",
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------
# PATHS
# -------------------------------
APP_DIR = Path(__file__).resolve().parent
ASSETS_DIR = APP_DIR / "assets"

LOGO_PATH = ASSETS_DIR / "sullivans_logo.png"
MAIN_BG = ASSETS_DIR / "main_bg.png"
SIDEBAR_BG = ASSETS_DIR / "sidebar_bg.png"


# -------------------------------
# BACKGROUND HELPERS
# -------------------------------
def set_main_background(image_path: Path):
    if not image_path.exists():
        st.warning(f"Background image not found: {image_path}")
        return

    encoded = base64.b64encode(image_path.read_bytes()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def set_sidebar_background(image_path: Path):
    if not image_path.exists():
        return

    encoded = base64.b64encode(image_path.read_bytes()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
        }}
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# APPLY BACKGROUNDS
set_main_background(MAIN_BG)
set_sidebar_background(SIDEBAR_BG)

# -------------------------------
# GLOBAL STYLES (READABLE TEXT)
# -------------------------------
st.markdown(
    """
    <style>
    body, p, span, div, label {
        color: #111 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    h1, h2, h3, h4 {
        color: #000 !important;
        font-weight: 700;
    }
    .stTabs [role="tab"] p {
        color: #000 !important;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# SIDEBAR
# -------------------------------
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)

    st.markdown("### Platform Modules")
    st.write("• Strategy Engine")
    st.write("• Research & Trends")
    st.write("• Google / YouTube")
    st.write("• TikTok")
    st.write("• Spotify")
    st.write("• Meta")
    st.write("• Influencers & Email")

# -------------------------------
# HEADER
# -------------------------------
st.markdown("## Sully’s Multi-Platform Media Planner")
st.caption(
    "Strategy • Research • Campaign Creation • Influencers • Execution"
)

st.markdown("---")

# -------------------------------
# TABS
# -------------------------------
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

# ===============================
# STRATEGY TAB
# ===============================
with tab_strategy:
    st.subheader("🧠 Strategy Engine")

    niche = st.selectbox(
        "Business Niche",
        ["Music", "Clothing Brand", "Local Home Care"],
    )

    goal = st.selectbox(
        "Primary Goal",
        ["Awareness", "Traffic", "Leads", "Sales"],
    )

    budget = st.number_input(
        "Monthly Ad Budget (USD)",
        min_value=5000,
        step=500,
        value=5000,
    )

    platforms = st.multiselect(
        "Platforms to Include",
        ["Meta", "Google", "TikTok", "YouTube", "Spotify"],
        default=["Meta", "Google", "TikTok"],
    )

    if st.button("Generate Strategy (Phase 2 Logic)"):
        st.success("Strategy engine will run here in Phase 2.")
        st.json(
            {
                "niche": niche,
                "goal": goal,
                "budget": budget,
                "platforms": platforms,
            }
        )

# ===============================
# RESEARCH TAB
# ===============================
with tab_research:
    st.subheader("📊 Research & Trends")

    seed = st.text_input("Keyword / Interest Seed", "streetwear brand")

    timeframe = st.selectbox(
        "Timeframe",
        ["1 Month", "3 Months", "12 Months", "5 Years"],
    )

    st.info(
        "This tab will pull:\n"
        "- Google Trends\n"
        "- YouTube Trends\n"
        "- TikTok Creative Center\n"
        "- Meta Ad Library\n"
        "- Location & demographic insights"
    )

    if st.button("Run Research (Phase 3 APIs)"):
        st.warning("Research clients plug in during Phase 3.")

# ===============================
# GOOGLE / YOUTUBE TAB
# ===============================
with tab_google:
    st.subheader("🔍 Google & YouTube Campaign Builder")
    st.info("Google Ads & YouTube campaign creation will be wired next.")
    st.text_area("Generated Headlines")
    st.text_area("Generated Keywords")
    st.text_area("Audience Targeting")

# ===============================
# TIKTOK TAB
# ===============================
with tab_tiktok:
    st.subheader("🎵 TikTok Campaign Builder")
    st.info("TikTok Creative Center & Ads API will be wired next.")
    st.text_area("Hooks")
    st.text_area("Trending Hashtags")

# ===============================
# SPOTIFY TAB
# ===============================
with tab_spotify:
    st.subheader("🎧 Spotify Campaign Planner")
    st.info("Spotify Ads are planning-only (no public campaign API).")
    st.text_area("30s Audio Script")
    st.text_input("Destination URL")

# ===============================
# META TAB
# ===============================
with tab_meta:
    st.subheader("📣 Meta (Facebook & Instagram)")
    st.info(
        "Meta campaign → ad set → ad automation\n"
        "Reach estimates + pixel-based conversion setup\n"
        "will be enabled in Phase 4."
    )
    st.text_area("Primary Text")
    st.text_input("Headline")
    st.text_input("CTA")

# ===============================
# INFLUENCER TAB
# ===============================
with tab_influencer:
    st.subheader("🤝 Influencer & Email Outreach")

    st.text_input("Influencer Niche / Keyword")
    st.text_area("Generated Outreach Email")
    st.info("IG + Google influencer scraping plugs in Phase 5.")