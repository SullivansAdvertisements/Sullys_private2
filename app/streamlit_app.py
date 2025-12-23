# ==============================
# Sully’s Multi-Platform Media Planner
# Phases A → E (STABLE)
# ==============================

import streamlit as st
import pandas as pd
from pathlib import Path

# Optional Google Trends
try:
    from pytrends.request import TrendReq
    HAS_TRENDS = True
except ImportError:
    HAS_TRENDS = False

# ------------------------------
# Page config + styling
# ------------------------------
st.set_page_config(
    page_title="Sully’s Media Planner",
    page_icon="🌺",
    layout="wide",
)
def set_background(image_path: str):
    import base64
    from pathlib import Path

    image_file = Path(image_path)
    if not image_file.exists():
        st.warning(f"Background image not found: {image_path}")
        return

    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    set_background("assets/main_bg.png")
    
st.markdown(
    """
    <style>
    .stApp { background-color: #f7f7fb; }
    body, p, div, span, label { color: #111 !important; }
    h1, h2, h3, h4 { font-weight: 700; }
    [data-testid="stSidebar"] { background-color: #151826; }
    [data-testid="stSidebar"] * { color: #fff !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

APP_DIR = Path(__file__).resolve().parent
LOGO_PATH = APP_DIR / "sullivans_logo.png"

# ------------------------------
# Helpers
# ------------------------------
def parse_multiline(raw: str):
    return [x.strip() for x in raw.replace(",", "\n").split("\n") if x.strip()]

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