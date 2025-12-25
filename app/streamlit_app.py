import streamlit as st
from pathlib import Path

# =========================
# PAGE CONFIG (MUST BE FIRST)
# =========================
st.set_page_config(
    page_title="Sully’s Media Planner",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# PATHS
# =========================
BASE_DIR = Path(__file__).resolve().parent
ASSETS = BASE_DIR / "assets"

MAIN_BG = ASSETS / "main_bg.png"
SIDEBAR_BG = ASSETS / "sidebar_bg.png"
LOGO = ASSETS / "sullivans_logo.png"

# =========================
# SIDEBAR BACKGROUND (CSS SAFE)
# =========================
if SIDEBAR_BG.exists():
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            background-image: url("file://{SIDEBAR_BG}");
            background-size: cover;
            background-position: center;
        }}

        [data-testid="stSidebar"] * {{
            color: white !important;
            font-weight: 600;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# =========================
# MAIN BACKGROUND (MOBILE SAFE)
# =========================
if MAIN_BG.exists():
    st.image(str(MAIN_BG), use_column_width=True)

# =========================
# GLOBAL TEXT VISIBILITY
# =========================
st.markdown(
    """
    <style>
    body, p, span, label, div {
        color: #111111 !important;
    }

    h1, h2, h3 {
        font-weight: 700;
    }

    .stTabs [role="tab"] {
        font-weight: 600;
        color: #111111 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# SIDEBAR CONTENT
# =========================
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_column_width=True)

    st.markdown("### Navigation")
    st.write("• Strategy")
    st.write("• Research")
    st.write("• Campaigns")
    st.write("• Influencers")
    st.write("• Reporting")

# =========================
# TABS (MOBILE FRIENDLY)
# =========================
tab_strategy, tab_research, tab_campaigns, tab_influencers = st.tabs(
    ["🧠 Strategy", "📊 Research", "📣 Campaigns", "🤝 Influencers"]
)

# =========================
# STRATEGY TAB
# =========================
with tab_strategy:
    st.subheader("Strategy Builder")

    niche = st.selectbox("Business Type", ["Music", "Clothing", "Home Care"])
    budget = st.number_input("Monthly Budget (min $500)", min_value=500, value=5000)

    platforms = st.multiselect(
        "Platforms",
        ["Meta", "Google", "TikTok", "Spotify", "YouTube"],
        default=["Meta", "Google"],
    )

    st.success("Strategy engine ready.")

# =========================
# RESEARCH TAB
# =========================
with tab_research:
    st.subheader("Trends & Research")

    seed = st.text_input("Keyword / Interest")
    timeframe = st.selectbox("Timeframe", ["1 month", "3 months", "1 year", "5 years"])

    if st.button("Run Research"):
        st.info("This will connect Google Trends, TikTok Trends & Meta Library (API wiring phase).")

# =========================
# CAMPAIGNS TAB
# =========================
with tab_campaigns:
    st.subheader("Campaign Generator")

    platform = st.selectbox("Platform", ["Meta", "Google", "TikTok", "Spotify"])
    objective = st.selectbox("Objective", ["Awareness", "Traffic", "Leads", "Sales"])

    if st.button("Generate Campaign"):
        st.success("Campaign structure generated (headlines, copy, audiences).")

# =========================
# INFLUENCERS TAB
# =========================
with tab_influencers:
    st.subheader("Influencer Outreach")

    niche = st.text_input("Niche / Industry")
    region = st.text_input("Region")

    if st.button("Find Influencers"):
        st.info("IG + Google influencer research will populate here.")

# ==============================
# TAB 1 — STRATEGY (Phase A + D)
# ==============================
with tab_strategy:
    st.subheader("🧠 Strategy Planner")

    c1, c2, c3 = st.columns(3)
    niche = c1.selectbox("Niche", ["Music", "Clothing", "Homecare"])
    goal = c2.selectbox("Goal", ["Awareness", "Traffic", "Leads", "Conversions", "Sales"])
    budget = c3.number_input("Monthly Budget ($)", min_value=500, value=5000, step=500)

    st.markdown("### Budget Allocation")
    splits = allocate_budget(budget, goal)
    for k, v in splits.items():
        st.write(f"- **{k}**: ${budget * v:,.0f}")

# ==============================
# TAB 2 — RESEARCH (Phase B)
# ==============================
with tab_research:
    st.subheader("📊 Research & Trends")

    seeds_raw = st.text_input(
        "Keyword / Interest Seeds",
        placeholder="streetwear, home care services, independent artist",
    )
    seeds = parse_multiline(seeds_raw)

    if st.button("Run Google Trends") and seeds:
        if not HAS_TRENDS:
            st.warning("pytrends not installed.")
        else:
            data = get_google_trends(seeds)
            st.success("Trend data loaded.")
            st.json(data)

# ==============================
# PHASE E — CREATIVE GENERATOR
# ==============================
def creative_ui(platform):
    st.markdown("### 🧠 Ad Creative Generator")
    offer = st.text_input("Offer / Hook", f"Limited time offer on {platform}")
    if st.button(f"Generate {platform} Ad Copy"):
        creatives = generate_full_creative(platform, niche, goal, offer)
        st.subheader("Headlines")
        for h in creatives["headlines"]:
            st.write(f"- {h}")
        st.subheader("Primary Text")
        for t in creatives["primary_text"]:
            st.write(f"- {t}")
        st.subheader("CTAs")
        st.write(", ".join(creatives["ctas"]))

# ==============================
# PLATFORM TABS (Phase C + E)
# ==============================
with tab_meta:
    st.subheader("📣 Meta (Facebook / Instagram)")
    creative_ui("Meta")

with tab_google:
    st.subheader("🔍 Google / YouTube")
    creative_ui("Google")

with tab_tiktok:
    st.subheader("🎵 TikTok")
    creative_ui("TikTok")

with tab_spotify:
    st.subheader("🎧 Spotify")
    creative_ui("Spotify")