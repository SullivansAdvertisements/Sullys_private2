# =========================================================
# Sully's Multi-Platform Media Planner (CLIENT-READY)
# =========================================================
# Modes:
# - Builder Mode (internal use)
# - Client Presentation Mode (read-only link)
#
# Tabs:
# 🧠 Strategy
# 📊 Research & Trends
# 🔍 Google / YouTube
# 🎵 TikTok
# 🎧 Spotify
# 📣 Meta
#
# Minimum Monthly Budget: $5,000
# =========================================================

import json
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Sully’s Media Planner",
    page_icon="🌺",
    layout="wide",
)

# ---------------------------------------------------------
# GLOBAL STYLES (VISIBLE TEXT + MOBILE SAFE)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp { background-color: #f7f7fb; }
    body, p, li, span, div, label {
        color: #111 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    h1, h2, h3, h4 { color: #111 !important; font-weight: 700; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111827;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Tabs */
    .stTabs [role="tab"] p {
        color: #111 !important;
        font-size: 1rem;
        font-weight: 600;
    }

    /* Mobile spacing */
    @media (max-width: 768px) {
        h1 { font-size: 1.6rem; }
        h2 { font-size: 1.3rem; }
        h3 { font-size: 1.1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# FILE PATHS (LOGOS / IMAGES)
# ---------------------------------------------------------
APP_DIR = Path(__file__).resolve().parent
LOGO_PATH = APP_DIR / "sullivans_logo.png"

# ---------------------------------------------------------
# SIDEBAR – VIEW MODE
# ---------------------------------------------------------
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)

    st.markdown("## ⚙️ View Mode")
    CLIENT_MODE = st.toggle(
        "Client Presentation Mode",
        value=False,
        help="Read-only link for clients"
    )

    st.markdown("---")
    st.markdown("### Platforms")
    st.write("• Strategy")
    st.write("• Research & Trends")
    st.write("• Google / YouTube")
    st.write("• TikTok")
    st.write("• Spotify")
    st.write("• Meta")

# ---------------------------------------------------------
# CLIENT MODE CSS (HIDES INPUTS)
# ---------------------------------------------------------
if CLIENT_MODE:
    st.markdown(
        """
        <style>
        input, textarea, select, button {
            display: none !important;
        }
        header, footer {
            visibility: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
h1, h2 = st.columns([1, 4])
with h1:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)
with h2:
    st.markdown("## Sully’s Multi-Platform Media Planner")
    st.caption("Strategy • Research • Campaign Planning")

st.markdown("---")

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def parse_multiline(text):
    return [x.strip() for x in text.replace(",", "\n").split("\n") if x.strip()]

def generate_strategy(niche, goal, budget, geo):
    split = {
        "Meta": 0.35,
        "Google / YouTube": 0.30,
        "TikTok": 0.20,
        "Spotify": 0.15,
    }
    return {
        "niche": niche,
        "goal": goal,
        "geo": geo,
        "budget": budget,
        "platforms": {
            k: round(budget * v, 2) for k, v in split.items()
        }
    }

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
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

# =========================================================
# TAB 1 – STRATEGY
# =========================================================
with tab_strategy:
    st.subheader("🧠 Media Strategy Builder")

    if not CLIENT_MODE:
        niche = st.selectbox("Industry", ["Music", "Clothing", "Home Care"])
        goal = st.selectbox("Primary Goal", ["Awareness", "Leads", "Sales"])
        geo = st.text_input("Target Market", value="United States")
        budget = st.number_input(
            "Monthly Budget (USD)",
            min_value=5000,
            step=500,
            value=5000,
        )

        if st.button("Generate Strategy"):
            plan = generate_strategy(niche, goal, budget, geo)
            st.session_state["plan"] = plan

    if "plan" in st.session_state:
        plan = st.session_state["plan"]
        st.markdown("### 📊 Strategy Overview")
        st.write(f"**Industry:** {plan['niche']}")
        st.write(f"**Goal:** {plan['goal']}")
        st.write(f"**Market:** {plan['geo']}")
        st.write(f"**Monthly Budget:** ${plan['budget']:,.0f}")

        st.markdown("### 💰 Budget Allocation")
        for p, v in plan["platforms"].items():
            st.write(f"**{p}:** ${v:,.0f}")

# =========================================================
# TAB 2 – RESEARCH & TRENDS
# =========================================================
with tab_research:
    st.subheader("📊 Research & Trends")

    if not CLIENT_MODE:
        seeds = st.text_area(
            "Keyword / Interest Seeds",
            placeholder="streetwear, home care services, independent artist",
        )

        st.caption("This tab is designed to connect Google Trends, TikTok Creative Center, YouTube, Meta Ad Library.")

        if st.button("Run Research"):
            st.success("Research pulled (API wiring happens in trends_client.py)")
            st.write("Top Regions, Rising Keywords, Interest Clusters")

    st.info(
        "Client View: This section shows validated trends, locations, and interests once connected to live APIs."
    )

# =========================================================
# TAB 3 – GOOGLE / YOUTUBE
# =========================================================
with tab_google:
    st.subheader("🔍 Google / YouTube Campaign Planner")
    st.write("Search + Video campaign structure")
    st.write("• Keyword clusters")
    st.write("• Intent mapping")
    st.write("• Placement strategy")
    st.info("Live Google Ads API wiring belongs in `google_client.py`")

# =========================================================
# TAB 4 – TIKTOK
# =========================================================
with tab_tiktok:
    st.subheader("🎵 TikTok Campaign Planner")
    st.write("• Creative hooks")
    st.write("• Audience discovery")
    st.write("• Trend-based ad concepts")
    st.info("Live TikTok Ads API wiring belongs in `tiktok_client.py`")

# =========================================================
# TAB 5 – SPOTIFY
# =========================================================
with tab_spotify:
    st.subheader("🎧 Spotify Campaign Planner")
    st.write("• Audio ad concepts")
    st.write("• Listener targeting")
    st.write("• Podcast placements")
    st.info("Live Spotify Ads API wiring belongs in `spotify_client.py`")

# =========================================================
# TAB 6 – META
# =========================================================
with tab_meta:
    st.subheader("📣 Meta (Facebook + Instagram)")

    st.write("• Campaign → Ad Set → Ad flow")
    st.write("• Audience targeting")
    st.write("• Creative generation")
    st.write("• Reach & delivery estimates")

    st.info(
        "Live Meta campaign creation, reach estimates, and delivery forecasting "
        "must be handled inside `meta_client.py` using official Graph API endpoints."
    )

# ---------------------------------------------------------
# CLIENT EXPORT
# ---------------------------------------------------------
if CLIENT_MODE and "plan" in st.session_state:
    st.markdown("---")
    st.download_button(
        "📥 Download Client Strategy",
        data=json.dumps(st.session_state["plan"], indent=2),
        file_name="sully_media_strategy.json",
        mime="application/json",
    )