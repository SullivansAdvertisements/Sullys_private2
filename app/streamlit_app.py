import streamlit as st
import streamlit as st
import pandas as pd
from datetime import datetime

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Sully's Multi-Platform Media Planner",
    page_icon="📊",
    layout="wide",
)

# -------------------------------
# GLOBAL STYLING (LIGHT MODE ONLY)
# -------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffffff;
        color: #111111;
    }
    body, p, span, label, div {
        color: #111111 !important;
        font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
    }
    h1, h2, h3 {
        font-weight: 700;
    }
    [data-testid="stSidebar"] {
        background-color: #f4f4f4;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# HEADER
# -------------------------------
st.markdown("## 🚀 Sully’s Multi-Platform Campaign Planner")
st.caption(
    "Strategy • Research • Campaign Planning for Meta, Google, TikTok & Spotify"
)
st.markdown("---")

# -------------------------------
# SIDEBAR CONTROLS
# -------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Global Settings")

    monthly_budget = st.number_input(
        "Monthly Budget (USD)",
        min_value=500,
        value=5000,
        step=500,
    )

    platforms = st.multiselect(
        "Platforms to include",
        ["Meta", "Google / YouTube", "TikTok", "Spotify"],
        default=["Meta", "Google / YouTube", "TikTok"],
    )

    st.markdown("---")
    st.caption("Client-safe • Read-only ready")

# -------------------------------
# TABS
# -------------------------------
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

# ===============================
# STRATEGY TAB
# ===============================
with tab_strategy:
    st.subheader("🧠 Strategy Engine")

    niche = st.selectbox(
        "Business Type",
        ["Music Artist", "Clothing Brand", "Home Care", "Other"],
    )

    goal = st.selectbox(
        "Primary Goal",
        ["Awareness", "Traffic", "Leads", "Sales"],
    )

    geo = st.text_input("Primary Market", value="United States")

    st.markdown("### 📊 Recommended Budget Split")

    if monthly_budget >= 500:
        splits = {}
        if "Meta" in platforms:
            splits["Meta"] = round(monthly_budget * 0.35, 2)
        if "Google / YouTube" in platforms:
            splits["Google / YouTube"] = round(monthly_budget * 0.30, 2)
        if "TikTok" in platforms:
            splits["TikTok"] = round(monthly_budget * 0.20, 2)
        if "Spotify" in platforms:
            splits["Spotify"] = round(monthly_budget * 0.15, 2)

        df = pd.DataFrame(
            [{"Platform": k, "Monthly Budget ($)": v} for k, v in splits.items()]
        )
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Minimum monthly budget is $500.")

# ===============================
# RESEARCH TAB
# ===============================
with tab_research:
    st.subheader("📊 Research & Trend Discovery")

    seed = st.text_input(
        "Keyword / Interest Seed",
        placeholder="streetwear, hip hop artist, home care services",
    )

    timeframe = st.selectbox(
        "Time Range",
        ["1 month", "3 months", "12 months", "5 years"],
    )

    st.markdown("### 🔍 What this tab does (Phase-1)")
    st.info(
        """
        • Keyword expansion  
        • Interest validation  
        • Location & demographic planning  
        • Platform-agnostic research  

        (Live APIs plug in Phase-2)
        """
    )

    if st.button("Run Research"):
        if seed:
            st.success("Research generated (placeholder)")
            st.write(
                {
                    "Top Interests": [seed, f"{seed} marketing", f"{seed} ads"],
                    "Best Platforms": platforms,
                    "Top Locations": ["US", "CA", "UK"],
                    "Age Focus": "18-45",
                }
            )
        else:
            st.warning("Enter a keyword or interest.")

# ===============================
# GOOGLE / YOUTUBE TAB
# ===============================
with tab_google:
    st.subheader("🔍 Google / YouTube Campaign Planner")

    if "Google / YouTube" not in platforms:
        st.info("Platform not selected in sidebar.")
    else:
        st.text_input("Landing Page URL", value="https://example.com")
        st.text_area(
            "Search Keywords",
            placeholder="buy streetwear online\nbest home care near me",
        )
        st.button("Generate Google Campaign (Preview Only)")
        st.caption("API execution added in Phase-2")

# ===============================
# TIKTOK TAB
# ===============================
with tab_tiktok:
    st.subheader("🎵 TikTok Campaign Planner")

    if "TikTok" not in platforms:
        st.info("Platform not selected in sidebar.")
    else:
        st.text_area(
            "Creative Hooks",
            placeholder="POV you found your new favorite brand\nWatch till the end",
            key="tiktok_hooks",
        )
        st.button("Generate TikTok Campaign (Preview Only)")
        st.caption("TikTok Ads API added in Phase-2")

# ===============================
# SPOTIFY TAB
# ===============================
with tab_spotify:
    st.subheader("🎧 Spotify Audio Campaign")

    if "Spotify" not in platforms:
        st.info("Platform not selected in sidebar.")
    else:
        st.text_area(
            "30-Second Audio Script",
            placeholder="Hey, while you're listening, check out...",
            key="spotify_script",
        )
        st.button("Generate Spotify Plan (Preview Only)")
        st.caption("Spotify Ads Studio only (no public API)")

# ===============================
# META TAB
# ===============================
with tab_meta:
    st.subheader("📣 Meta (Facebook & Instagram)")

    if "Meta" not in platforms:
        st.info("Platform not selected in sidebar.")
    else:
        st.markdown("### Campaign Preview")
        st.text_input("Campaign Name", value="Sully Meta Campaign")
        st.text_area(
            "Primary Text",
            placeholder="Limited drop live now. Tap in.",
            key="meta_primary",
        )
        st.text_input("Headline", value="New Collection Out Now")
        st.button("Generate Meta Campaign (Preview Only)")
        st.caption("Graph API creation enabled in Phase-2")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption(
    f"Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} • Client-Safe Mode"
)