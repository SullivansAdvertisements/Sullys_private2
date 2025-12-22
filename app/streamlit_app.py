import streamlit as st
from pathlib import Path

from clients.trends_client import run_trends_research
from clients.common_ai import (
    generate_strategy,
    generate_ad_copy,
    estimate_reach,
)
from clients.meta_client import meta_status
from clients.google_client import google_status
from clients.tiktok_client import tiktok_status
from clients.spotify_client import spotify_status

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Sully Marketing Intelligence",
    page_icon="🌺",
    layout="wide",
)

APP_DIR = Path(__file__).parent
ASSETS = APP_DIR / "assets"

# ---------------- STYLING ----------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background: url("{(ASSETS/'main_bg.png').as_posix()}") no-repeat center fixed;
        background-size: cover;
    }}
    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(255,255,255,0.9);
        z-index: -1;
    }}
    [data-testid="stSidebar"] {{
        background: url("{(ASSETS/'sidebar_bg.png').as_posix()}") no-repeat center;
        background-size: cover;
    }}
    body, p, div, label {{
        color: #111 !important;
        font-weight: 500;
    }}
    h1, h2, h3 {{
        font-weight: 800;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- HEADER ----------------
cols = st.columns([1,4])
with cols[0]:
    st.image(str(ASSETS/"sullivans_logo.png"), width=120)
with cols[1]:
    st.title("Sully Multi-Platform Marketing Brain")
    st.caption("Research → Strategy → Campaigns → Scaling")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.image(str(ASSETS/"sullivans_logo.png"))
    st.markdown("### System Status")
    st.write("Meta:", meta_status())
    st.write("Google:", google_status())
    st.write("TikTok:", tiktok_status())
    st.write("Spotify:", spotify_status())

# ---------------- TABS ----------------
tabs = st.tabs([
    "🧠 Strategy",
    "📊 Research",
    "✍️ Ad Generator",
    "📈 Reach Estimator",
    "📣 Platforms",
])

# ================= STRATEGY =================
with tabs[0]:
    st.subheader("Strategy Engine")

    budget = st.number_input(
        "Monthly Budget (min $500)",
        min_value=500,
        step=100,
        value=5000
    )

    niche = st.selectbox(
        "Business Type",
        ["Music Artist", "Clothing Brand", "Home Care", "General Business"]
    )

    platforms = st.multiselect(
        "Platforms",
        ["Meta", "Google/YouTube", "TikTok", "Spotify"],
        default=["Meta", "Google/YouTube"]
    )

    if st.button("Generate Strategy"):
        strategy = generate_strategy(niche, budget, platforms)
        st.json(strategy)

# ================= RESEARCH =================
with tabs[1]:
    st.subheader("Research & Trends")

    seed = st.text_input("Keyword / Interest Seed")
    geo = st.text_input("Location", "United States")

    if st.button("Run Research"):
        results = run_trends_research(seed, geo)
        st.json(results)

# ================= AD COPY =================
with tabs[2]:
    st.subheader("Ad Creative Generator")

    goal = st.selectbox(
        "Goal",
        ["Awareness", "Traffic", "Leads", "Sales"]
    )

    if st.button("Generate Ads"):
        ads = generate_ad_copy(seed, goal)
        st.dataframe(ads)

# ================= REACH =================
with tabs[3]:
    st.subheader("Estimated Reach (Transparent Model)")

    daily = st.number_input("Daily Budget ($)", value=50)

    if st.button("Estimate"):
        reach = estimate_reach(daily)
        st.json(reach)

# ================= PLATFORMS =================
with tabs[4]:
    st.subheader("Platform Modules")

    st.info("""
    • Meta: Campaign + Ad Set + Ad creation  
    • Google: Keyword & YouTube planning  
    • TikTok: Creative + trend hooks  
    • Spotify: Audio scripts  

    (Activation handled per client file)
    """)