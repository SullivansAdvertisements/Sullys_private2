import streamlit as st
from pathlib import Path
from datetime import datetime
import pandas as pd

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Sully’s Marketing Intelligence",
    page_icon="🌺",
    layout="wide",
)

# -------------------------------------------------
# PATHS
# -------------------------------------------------
APP_DIR = Path(__file__).resolve().parent
ASSETS = APP_DIR / "assets"
LOGO = ASSETS / "sullivans_logo.png"
SIDEBAR_BG = ASSETS / "sidebar_bg.png"

# -------------------------------------------------
# GLOBAL LIGHT MODE + MOBILE SAFE CSS
# -------------------------------------------------
st.markdown(
    f"""
<style>
:root {{
    color-scheme: light !important;
}}

html, body, .stApp {{
    background-color: #f6f7fb !important;
}}

.block-container {{
    padding-top: 6rem;
}}

/* ===== HEADER ===== */
.sully-header {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 9999;
    background: white;
    border-bottom: 1px solid #e5e7eb;
    padding: 10px 18px;
    display: flex;
    align-items: center;
    gap: 14px;
}}

.sully-header img {{
    height: 40px;
}}

.sully-title {{
    font-size: 1.25rem;
    font-weight: 800;
    color: #0f172a;
}}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {{
    background-image: url("{SIDEBAR_BG.as_posix()}");
    background-size: cover;
    background-position: center;
}}

[data-testid="stSidebar"]::before {{
    content: "";
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.55);
    z-index: 0;
}}

[data-testid="stSidebar"] * {{
    position: relative;
    z-index: 1;
    color: white !important;
}}

/* ===== CARDS ===== */
.sully-card {{
    background: white;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.12);
    margin-bottom: 22px;
}}

/* ===== TEXT ===== */
h1, h2, h3 {{
    color: #0f172a !important;
    font-weight: 800;
}}

p, label, span {{
    color: #1e293b !important;
}}

/* ===== INPUTS ===== */
input, textarea, select {{
    background-color: white !important;
    color: #0f172a !important;
    border-radius: 10px !important;
    border: 1px solid #cbd5e1 !important;
}}

button {{
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
}}

/* ===== DROPDOWN FIX ===== */
div[role="listbox"] {{
    background-color: white !important;
    color: #0f172a !important;
}}
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown(
    f"""
<div class="sully-header">
    <img src="{LOGO.as_posix()}">
    <div class="sully-title">Sully’s Marketing Intelligence Platform</div>
</div>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_column_width=True)
    st.markdown("### Navigation")
    st.caption("Strategy • Research • Platforms")

# -------------------------------------------------
# TABS
# -------------------------------------------------
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

# -------------------------------------------------
# STRATEGY TAB
# -------------------------------------------------
with tab_strategy:
    st.markdown("<div class='sully-card'>", unsafe_allow_html=True)

    st.subheader("🧠 Strategy Planner")

    niche = st.selectbox("Industry", ["Music", "Clothing", "Home Care"])
    goal = st.selectbox(
        "Primary Goal", ["Awareness", "Traffic", "Leads", "Conversions", "Sales"]
    )
    budget = st.number_input(
        "Monthly Budget (USD)", min_value=5000, step=500, value=5000
    )
    geo = st.selectbox("Primary Market", ["Worldwide", "United States", "Canada", "UK"])

    if st.button("Generate Strategy"):
        st.success("Strategy generated")
        st.write(
            {
                "niche": niche,
                "goal": goal,
                "budget": budget,
                "geo": geo,
                "recommendation": "Split budget across Meta, Google, TikTok with performance rebalancing every 7 days.",
            }
        )

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# RESEARCH TAB
# -------------------------------------------------
with tab_research:
    st.markdown("<div class='sully-card'>", unsafe_allow_html=True)

    st.subheader("📊 Research & Trend Intelligence")

    seed = st.text_input("Keyword / Interest Seed", placeholder="streetwear, home care")
    timeframe = st.selectbox("Timeframe", ["30 days", "90 days", "1 year", "5 years"])

    if st.button("Run Research"):
        st.success("Research insights generated (placeholder)")
        st.write(
            {
                "Top Cities": ["New York", "Los Angeles", "Chicago"],
                "Top States": ["CA", "NY", "TX"],
                "Age Range": "18–34",
                "Gender Split": "60% Male / 40% Female",
                "Hashtags": ["#streetwear", "#urbanfashion", "#newdrop"],
            }
        )

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# PLATFORM SHELLS (SAFE)
# -------------------------------------------------
def platform_shell(platform_name):
    st.markdown("<div class='sully-card'>", unsafe_allow_html=True)
    st.subheader(platform_name)
    st.text_input(
        f"{platform_name} Campaign Name",
        value=f"{platform_name} Campaign {datetime.utcnow().date()}",
        key=f"{platform_name}_name",
    )
    st.text_area(
        "Headline Ideas",
        placeholder="Generated headlines will appear here",
        key=f"{platform_name}_headline",
    )
    st.text_area(
        "Ad Copy",
        placeholder="Generated ad copy will appear here",
        key=f"{platform_name}_copy",
    )
    st.button(f"Generate {platform_name} Campaign")
    st.markdown("</div>", unsafe_allow_html=True)


with tab_google:
    platform_shell("Google / YouTube")

with tab_tiktok:
    platform_shell("TikTok")

with tab_spotify:
    platform_shell("Spotify")

with tab_meta:
    platform_shell("Meta (Facebook & Instagram)")