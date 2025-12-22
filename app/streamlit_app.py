import streamlit as st
import base64
from pathlib import Path

# =========================
# PAGE CONFIG (LIGHT MODE)
# =========================
st.set_page_config(
    page_title="Sully’s Growth Planner",
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# ASSET PATHS
# =========================
APP_DIR = Path(__file__).parent
ASSETS = APP_DIR / "assets"

SIDEBAR_BG = ASSETS / "sidebar_bg.png"
HEADER_BG = ASSETS / "header_bg.png"
LOGO = ASSETS / "sullivans_logo.png"

# =========================
# BASE64 LOADER (CRITICAL)
# =========================
def load_b64(path):
    if not path.exists():
        return ""
    return base64.b64encode(path.read_bytes()).decode()

SIDEBAR_BG_B64 = load_b64(SIDEBAR_BG)
HEADER_BG_B64 = load_b64(HEADER_BG)
LOGO_B64 = load_b64(LOGO)

# =========================
# GLOBAL STYLES (FIXED)
# =========================
st.markdown(
    f"""
<style>

/* Force light mode */
html, body, [class*="css"] {{
    background-color: #f7f8fc !important;
    color: #111 !important;
}}

/* Sticky header */
.header {{
    position: sticky;
    top: 0;
    z-index: 999;
    background-image: url("data:image/png;base64,{HEADER_BG_B64}");
    background-size: cover;
    padding: 20px;
    border-radius: 0 0 14px 14px;
}}

/* Sidebar background */
[data-testid="stSidebar"] {{
    background-image: url("data:image/png;base64,{SIDEBAR_BG_B64}");
    background-size: cover;
}}

[data-testid="stSidebar"]::before {{
    content: "";
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.45);
}}

[data-testid="stSidebar"] * {{
    position: relative;
    z-index: 1;
    color: white !important;
}}

/* Inputs readable */
input, textarea, select {{
    background-color: white !important;
    color: black !important;
}}

</style>
""",
    unsafe_allow_html=True,
)

# =========================
# HEADER
# =========================
st.markdown(
    f"""
<div class="header">
    <img src="data:image/png;base64,{LOGO_B64}" height="48"/>
    <h2>Sully’s Multi-Platform Growth Engine</h2>
    <p>Strategy • Research • Budget Planning • Client-Ready</p>
</div>
""",
    unsafe_allow_html=True,
)

# =========================
# SIDEBAR CONTROLS
# =========================
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    client_mode = st.toggle("Client Presentation Mode (Read-Only)", value=False)

    st.markdown("### Platforms to Include")
    use_meta = st.checkbox("Meta (Facebook & Instagram)", value=True)
    use_google = st.checkbox("Google / YouTube", value=True)
    use_tiktok = st.checkbox("TikTok", value=True)
    use_spotify = st.checkbox("Spotify", value=False)

# =========================
# MAIN TABS
# =========================
tabs = st.tabs(
    [
        "🧠 Strategy",
        "📊 Research & Trends",
        "📣 Campaign Planning",
        "📧 Influencers & Email",
        "📊 Client Summary",
    ]
)

# =========================
# TAB 1 — STRATEGY
# =========================
with tabs[0]:
    st.subheader("🧠 Strategy Builder")

    niche = st.selectbox("Industry", ["Music", "Clothing", "Homecare"])
    goal = st.selectbox("Primary Goal", ["Awareness", "Leads", "Sales"])

    budget = st.number_input(
        "Monthly Ad Budget (USD)",
        min_value=500,
        value=5000,
        step=250,
        disabled=client_mode,
    )

    location = st.selectbox("Target Region", ["Worldwide", "US", "UK", "CA", "EU"])

    if st.button("Generate Strategy", disabled=client_mode):
        st.success("Strategy Generated")

        platforms = []
        if use_meta:
            platforms.append("Meta")
        if use_google:
            platforms.append("Google / YouTube")
        if use_tiktok:
            platforms.append("TikTok")
        if use_spotify:
            platforms.append("Spotify")

        split = round(budget / max(len(platforms), 1), 2)

        for p in platforms:
            st.markdown(f"### {p}")
            st.write(f"Recommended Monthly Budget: **${split:,.2f}**")
            st.write("Focus: audience testing → creative scaling → retargeting")

# =========================
# TAB 2 — RESEARCH
# =========================
with tabs[1]:
    st.subheader("📊 Research & Trends")

    keyword = st.text_input("Seed Keyword / Interest")
    timeframe = st.selectbox("Timeframe", ["30 days", "90 days", "1 year", "5 years"])

    st.write("Outputs:")
    st.write("- Related keywords")
    st.write("- Cities / States / Countries")
    st.write("- Age & gender insights")
    st.write("- Hashtags per platform")

    if st.button("Run Research", disabled=client_mode):
        st.success("Research Complete")
        st.write("• Rising queries")
        st.write("• Best locations")
        st.write("• Platform-specific interests")

# =========================
# TAB 3 — CAMPAIGN PLANNING
# =========================
with tabs[2]:
    st.subheader("📣 Campaign Planning")

    st.write("This section prepares campaigns for selected platforms.")

    if use_meta:
        st.markdown("### Meta Campaign")
        st.write("• Estimated reach (API)")
        st.write("• CPC & conversion range")

    if use_google:
        st.markdown("### Google / YouTube Campaign")
        st.write("• Keyword planner estimates")
        st.write("• Search + Video mix")

    if use_tiktok:
        st.markdown("### TikTok Campaign")
        st.write("• Trend-based hooks")
        st.write("• Creator-style ads")

# =========================
# TAB 4 — INFLUENCERS + EMAIL
# =========================
with tabs[3]:
    st.subheader("📧 Influencer & Email Outreach")

    st.write("• Find influencers by niche")
    st.write("• Generate outreach emails")
    st.write("• Export contact list")

    if st.button("Generate Outreach Copy", disabled=client_mode):
        st.success("Email Draft Ready")

# =========================
# TAB 5 — CLIENT SUMMARY
# =========================
with tabs[4]:
    st.subheader("📊 Client Presentation")

    st.write("Read-only overview for clients.")
    st.write("• Strategy")
    st.write("• Budget split")
    st.write("• Platform focus")