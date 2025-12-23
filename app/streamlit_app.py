import streamlit as st
import pandas as pd
import base64
from pathlib import Path

from core.common_ai import generate_headlines, generate_primary_text
from research.trends_client import get_google_trends
from research.meta_library import search_meta_ads
from research.tiktok_trends import get_tiktok_trends

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title="Sully’s Media Planner",
    page_icon="🌺",
    layout="wide",
)

# -------------------------
# Assets
# -------------------------
APP_DIR = Path(__file__).resolve().parent
ASSETS_DIR = APP_DIR / "assets"

LOGO_PATH = ASSETS_DIR / "sullivans_logo.png"
BACKGROUND_PATH = ASSETS_DIR / "main_bg.png"
SIDEBAR_BG_PATH = ASSETS_DIR / "sidebar_bg.png"


def load_base64(path):
    if not path.exists():
        return ""
    return base64.b64encode(path.read_bytes()).decode()


bg = load_base64(BACKGROUND_PATH)
sidebar_bg = load_base64(SIDEBAR_BG_PATH)

# -------------------------
# Styling
# -------------------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg}");
        background-size: cover;
        background-position: center;
    }}

    [data-testid="stSidebar"] {{
        background-image: url("data:image/png;base64,{sidebar_bg}");
        background-size: cover;
    }}

    body, p, label, span, div {{
        color: #111 !important;
        font-weight: 500;
    }}

    h1, h2, h3 {{
        font-weight: 800;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Header
# -------------------------
cols = st.columns([1, 4])
with cols[0]:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)
with cols[1]:
    st.markdown("## Sully’s Multi-Platform Media Planner")
    st.caption("Phase 2 — Research & Creative Intelligence")

# -------------------------
# Tabs
# -------------------------
tab_strategy, tab_research = st.tabs(
    ["🧠 Strategy", "📊 Research & Trends"]
)

# =========================
# TAB 1 — STRATEGY (lite)
# =========================
with tab_strategy:
    st.subheader("🧠 Strategy Overview")

    niche = st.selectbox("Industry", ["Music", "Clothing", "Homecare"])
    goal = st.selectbox("Goal", ["Awareness", "Traffic", "Leads", "Sales"])
    budget = st.number_input("Monthly Budget ($)", min_value=500, value=5000, step=500)

    st.success("Strategy locked. Use Research tab to build creatives.")

# =========================
# TAB 2 — RESEARCH & TRENDS
# =========================
with tab_research:
    st.subheader("📊 Research & Creative Intelligence")

    seed = st.text_input("Seed keyword / interest", placeholder="streetwear, home care, hip hop")
    country = st.selectbox("Country", ["US", "CA", "UK", "AU"])

    if st.button("Run Research"):
        if not seed:
            st.warning("Enter a seed keyword.")
        else:
            # --- Google Trends ---
            st.markdown("### 🔍 Google Trends")
            trends = get_google_trends(seed, country)
            if "error" in trends:
                st.error(trends["error"])
            else:
                if "interest_over_time" in trends:
                    st.line_chart(trends["interest_over_time"])
                if "regions" in trends:
                    st.dataframe(trends["regions"].head(10))

            # --- Meta Ad Library ---
            st.markdown("### 📣 Meta Ad Library")
            ads = search_meta_ads(seed, country)
            if ads:
                st.dataframe(pd.DataFrame(ads))
            else:
                st.info("No ads returned.")

            # --- TikTok Trends ---
            st.markdown("### 🎵 TikTok Trends")
            tiktok = get_tiktok_trends(seed)
            if tiktok:
                st.dataframe(pd.DataFrame(tiktok))
            else:
                st.info("No TikTok trend data.")

            # --- AI Creatives ---
            st.markdown("### ✍️ Ad Copy Generator")

            headlines = generate_headlines("Meta", niche, goal)
            body = generate_primary_text("Meta", niche, goal)

            st.write("**Headlines**")
            for h in headlines:
                st.write("•", h)

            st.write("**Primary Text**")
            for b in body:
                st.write("•", b)