import streamlit as st
from pathlib import Path

# =========================
# PAGE CONFIG (MUST BE FIRST)
# =========================
st.set_page_config(
    page_title="Sully’s Media Planner",
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# PATHS
# =========================
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

LOGO_PATH = ASSETS_DIR / "sullivans_logo.png"
MAIN_BG_PATH = ASSETS_DIR / "main_bg.png"
SIDEBAR_BG_PATH = ASSETS_DIR / "sidebar_bg.png"

# =========================
# BACKGROUND STYLES
# =========================
def inject_backgrounds():
    css = "<style>"

    # MAIN BACKGROUND
    if MAIN_BG_PATH.exists():
        css += f"""
        .stApp {{
            background-image: url("file://{MAIN_BG_PATH}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        """

    # SIDEBAR BACKGROUND
    if SIDEBAR_BG_PATH.exists():
        css += f"""
        [data-testid="stSidebar"] {{
            background-image: url("file://{SIDEBAR_BG_PATH}");
            background-size: cover;
            background-position: center;
        }}
        """

    # TEXT VISIBILITY (VERY IMPORTANT)
    css += """
    body, p, span, label, div {
        color: #111111 !important;
    }

    h1, h2, h3, h4 {
        color: #111111 !important;
        font-weight: 700;
    }

    .stTabs [role="tab"] {
        color: #111111 !important;
        font-weight: 600;
    }

    [data-testid="stSidebar"] * {
        color: white !important;
        font-weight: 500;
    }
    """

    css += "</style>"
    st.markdown(css, unsafe_allow_html=True)

inject_backgrounds()
# =========================
# HEADER
# =========================
col1, col2 = st.columns([1, 4])

with col1:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)

with col2:
    st.markdown("## 🚀 Sully’s Multi-Platform Media Planner")
    st.caption("Strategy • Research • Campaign Creation • Scaling")

st.markdown("---")
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)
    st.markdown("### Navigation")
#
# ------------------------------
# Phase E – Creative Brain
# ------------------------------
def generate_full_creative(platform, niche, goal, offer):
    base_hooks = {
        "Music": [
            "New release out now",
            "This sound is blowing up",
            "Fans can’t stop replaying this",
        ],
        "Clothing": [
            "New drop just landed",
            "Limited stock available",
            "Upgrade your fit today",
        ],
        "Homecare": [
            "Care your family can trust",
            "Support your loved ones today",
            "Professional home care services",
        ],
    }

    headlines = [
        f"{h} – {offer}"
        for h in base_hooks.get(niche, ["Discover more"])
    ]

    primary_text = [
        f"If you're looking for {niche.lower()} solutions, this is for you. {offer}.",
        f"{offer}. Trusted by people who care about quality.",
        f"Don’t miss this. {offer}.",
    ]

    ctas = ["Learn More", "Get Started", "Book Now", "Shop Now"]

    return {
        "headlines": headlines,
        "primary_text": primary_text,
        "ctas": ctas,
    }

# ------------------------------
# Phase A – Strategy Engine
# ------------------------------
def allocate_budget(total_budget, goal):
    if goal == "Awareness":
        return {"Meta": 0.35, "TikTok": 0.30, "YouTube": 0.25, "Google": 0.10}
    if goal in ["Sales", "Conversions"]:
        return {"Meta": 0.40, "Google": 0.35, "TikTok": 0.15, "YouTube": 0.10}
    return {"Meta": 0.35, "Google": 0.30, "TikTok": 0.20, "YouTube": 0.15}

# ------------------------------
# Phase B – Google Trends
# ------------------------------
@st.cache_data(ttl=3600)
def get_google_trends(seeds):
    if not HAS_TRENDS:
        return None
    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload(seeds, timeframe="today 12-m")
    return pytrends.related_queries()

# ------------------------------
# Header
# ------------------------------
h1, h2 = st.columns([1, 3])
with h1:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)
with h2:
    st.markdown("## 🌺 Sully’s Multi-Platform Media Planner")
    st.caption("Strategy • Research • Creative Generation (Phases A–E)")

st.markdown("---")

# ------------------------------
# Sidebar
# ------------------------------
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)
    st.markdown("### Active Phases")
    st.write("✅ Strategy")
    st.write("✅ Research")
    st.write("✅ Budget Allocation")
    st.write("✅ Creative Generator")

# ------------------------------
# Tabs
# ------------------------------
tab_strategy, tab_research, tab_meta, tab_google, tab_tiktok, tab_spotify = st.tabs(
    [
        "🧠 Strategy",
        "📊 Research",
        "📣 Meta",
        "🔍 Google / YouTube",
        "🎵 TikTok",
        "🎧 Spotify",
    ]
)

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