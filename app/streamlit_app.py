# ============================================
# Sully's Multi-Platform Media Planner
# SAFE BASE VERSION – All tabs render correctly
# ============================================

import streamlit as st
import pandas as pd
from pathlib import Path

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="Sully's Media Planner",
    page_icon="🌺",
    layout="wide",
)

# -------------------------
# Styling (light theme + readable text)
# -------------------------
st.markdown(
    """
    <style>
    .stApp { background-color: #f7f7fb; }
    body, p, li, span, div, label {
        color: #111111 !important;
        font-family: "Segoe UI", system-ui, sans-serif;
    }
    h1, h2, h3, h4, h5 {
        color: #111111 !important;
        font-weight: 700;
    }
    [data-testid="stSidebar"] {
        background-color: #151826;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    .stTabs [role="tab"] p {
        color: #111111 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Logo
# -------------------------
APP_DIR = Path(__file__).resolve().parent
LOGO_PATH = APP_DIR / "sullivans_logo.png"

if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=160)

st.title("Sully’s Multi-Platform Media Planner")
st.caption("Strategy • Research • Campaign Planning across all major ad platforms")

st.markdown("---")

# =========================
# TABS
# =========================
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

# =========================
# TAB 1 — STRATEGY
# =========================
with tab_strategy:
    st.subheader("🧠 Strategy Planner")

    c1, c2, c3 = st.columns(3)
    with c1:
        niche = st.selectbox("Niche", ["Music", "Clothing", "Homecare"])
    with c2:
        goal = st.selectbox(
            "Primary Goal",
            ["Awareness", "Traffic", "Leads", "Conversions", "Sales"],
        )
    with c3:
        budget = st.number_input(
            "Monthly Budget (USD)",
            min_value=100.0,
            value=2500.0,
            step=50.0,
        )

    geo = st.text_input("Target Location", value="United States")

    if st.button("Generate Strategy"):
        st.success("Strategy generated")
        st.write("**Summary:**")
        st.write(f"- Niche: {niche}")
        st.write(f"- Goal: {goal}")
        st.write(f"- Budget: ${budget:,.2f}")
        st.write(f"- Location: {geo}")

        st.write("**Recommended Platforms:**")
        st.write("- Meta (FB / IG)")
        st.write("- Google Search & YouTube")
        st.write("- TikTok")
        st.write("- Spotify (Audio awareness)")

# =========================
# TAB 2 — RESEARCH & TRENDS
# =========================
with tab_research:
    st.subheader("📊 Advanced Trends & Research")

    seed = st.text_input(
        "Keyword / Interest Seed",
        placeholder="streetwear, home care services, hip hop artist",
    )

    timeframe = st.selectbox(
        "Timeframe",
        ["7 days", "30 days", "12 months", "5 years"],
        index=2,
    )

    if st.button("Run Research"):
        st.info("Research results (placeholder – API wiring safe)")

        df = pd.DataFrame(
            {
                "Metric": [
                    "Top Locations",
                    "Age Range",
                    "Gender Split",
                    "Related Interests",
                ],
                "Insight": [
                    "US, CA, UK",
                    "18–34",
                    "Male 62% / Female 38%",
                    "Sneakers, Hip Hop, Online Shopping",
                ],
            }
        )
        st.dataframe(df, use_container_width=True)

        st.caption(
            "This tab will connect to Google Trends, TikTok Creative Center, "
            "YouTube search data, Instagram hashtag insights, and Meta Ad Library."
        )

# =========================
# TAB 3 — GOOGLE / YOUTUBE
# =========================
with tab_google:
    st.subheader("🔍 Google / YouTube Campaign Planner")

    st.write("**Campaign Planning (Safe Shell)**")

    keywords = st.text_area(
        "Search Keywords",
        placeholder="home care near me\nstreetwear brand\nmusic promotion",
    )

    daily_budget = st.number_input(
        "Daily Budget (USD)", min_value=5.0, value=50.0, step=5.0
    )

    if st.button("Generate Google / YouTube Plan"):
        st.success("Plan generated")
        st.write("- Campaign Type: Search + YouTube")
        st.write("- Goal: High-intent traffic")
        st.write("- Keywords:")
        st.write(keywords)
        st.write(f"- Daily Budget: ${daily_budget:,.2f}")

# =========================
# TAB 4 — TIKTOK
# =========================
with tab_tiktok:
    st.subheader("🎵 TikTok Campaign Planner")

    hooks = st.text_area(
        "Creative Hooks",
        placeholder="POV: you found your new favorite brand\nWatch till the end",
    )

    if st.button("Generate TikTok Campaign"):
        st.success("TikTok campaign framework generated")
        st.write("- Format: In-feed video")
        st.write("- Placement: TikTok For You")
        st.write("- Hooks:")
        st.write(hooks)

# =========================
# TAB 5 — SPOTIFY
# =========================
with tab_spotify:
    st.subheader("🎧 Spotify Ads Planner")

    script = st.text_area(
        "30-Second Audio Script",
        placeholder="Hey, it’s Sully’s Advertisements…",
    )

    if st.button("Generate Spotify Plan"):
        st.success("Spotify audio plan generated")
        st.write("- Format: Audio Ad")
        st.write("- Targeting: Music genres + age")
        st.write("- Script:")
        st.write(script)

# =========================
# TAB 6 — META
# =========================
with tab_meta:
    st.subheader("📣 Meta (Facebook & Instagram)")

    st.write("**Meta Campaign Builder – Safe Mode**")

    st.info(
        "This tab is ready for full Meta API wiring.\n\n"
        "Next upgrades:\n"
        "- Campaign → Ad Set → Ad creation\n"
        "- Pixel & IG Actor usage\n"
        "- Interest targeting from Research tab\n"
        "- Reach & conversion estimates via Meta endpoints"
    )

    if st.button("Test Meta Tab"):
        st.success("Meta tab loaded successfully")
