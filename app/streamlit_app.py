import streamlit as st
import pandas as pd
from datetime import datetime

# ===============================
# CONFIG
# ===============================
st.set_page_config(
    page_title="Sully Super Media Planner",
    page_icon="🌺",
    layout="wide",
)

st.markdown("""
<style>
.stApp { background-color: #f7f7fb; }
body, p, span, div, label { color:#111 !important; }
h1,h2,h3,h4 { font-weight:700; }
[data-testid="stSidebar"] {
    background-color:#151826;
}
[data-testid="stSidebar"] * {
    color:#ffffff !important;
}
.stTabs [role="tab"] p { color:#111 !important; }
</style>
""", unsafe_allow_html=True)

# ===============================
# CONSTANTS
# ===============================
MIN_BUDGET = 5000

PLATFORMS = ["Meta", "Google / YouTube", "TikTok", "Spotify"]

# ===============================
# PLANNING ENGINE
# ===============================
def get_budget_split(budget: float):
    if budget < 10000:
        return {
            "Meta": 0.45,
            "Google / YouTube": 0.30,
            "TikTok": 0.15,
            "Spotify": 0.10,
        }
    elif budget < 25000:
        return {
            "Meta": 0.40,
            "Google / YouTube": 0.35,
            "TikTok": 0.15,
            "Spotify": 0.10,
        }
    else:
        return {
            "Meta": 0.35,
            "Google / YouTube": 0.35,
            "TikTok": 0.20,
            "Spotify": 0.10,
        }

def efficiency_score(platform: str, budget: float):
    base = {
        "Meta": 8.5,
        "Google / YouTube": 9.0,
        "TikTok": 7.8,
        "Spotify": 6.8,
    }
    bonus = 1.0 if budget >= 25000 else 0.5 if budget >= 10000 else 0
    return min(10, round(base.get(platform, 6) + bonus, 1))

def auto_rebalance(platform_budgets: dict):
    recommendations = []
    for platform, amt in platform_budgets.items():
        if amt < 500:
            recommendations.append(
                f"⚠️ {platform}: Budget too low to exit learning phase."
            )
        elif amt > 20000:
            recommendations.append(
                f"✅ {platform}: Eligible for scaling & creative expansion."
            )
        else:
            recommendations.append(
                f"ℹ️ {platform}: Stable testing range."
            )
    return recommendations

def generate_strategy(niche, goal, budget, geo):
    split = get_budget_split(budget)
    allocations = {
        p: round(budget * pct, 2)
        for p, pct in split.items()
    }

    features = {
        "Creative Generator": budget >= 5000,
        "Trend Research": budget >= 5000,
        "Reach Estimates": budget >= 10000,
        "Auto Campaign Creation": budget >= 25000,
        "Influencer Outreach": budget >= 25000,
    }

    return allocations, features

# ===============================
# HEADER
# ===============================
st.markdown("## 🌺 Sully Super Media Planner")
st.caption("Agency-grade planning engine with auto-scaling & budget intelligence")

st.markdown("---")

# ===============================
# TABS
# ===============================
tab_strategy, tab_research, tab_google, tab_tiktok, tab_spotify, tab_meta = st.tabs([
    "🧠 Strategy",
    "📊 Research & Trends",
    "🔍 Google / YouTube",
    "🎵 TikTok",
    "🎧 Spotify",
    "📣 Meta",
])

# ===============================
# STRATEGY TAB
# ===============================
with tab_strategy:
    st.subheader("🧠 Planning Engine")

    c1, c2, c3 = st.columns(3)
    with c1:
        niche = st.selectbox("Niche", ["Music", "Clothing", "Homecare"])
    with c2:
        goal = st.selectbox("Primary Goal", ["Awareness", "Traffic", "Leads", "Sales"])
    with c3:
        budget = st.number_input(
            "Monthly Budget (USD)",
            min_value=MIN_BUDGET,
            value=5000,
            step=500
        )

    geo = st.text_input("Primary Market (Country / Region)", value="US")

    if budget < MIN_BUDGET:
        st.error("Minimum budget is $5,000.")
        st.stop()

    allocations, features = generate_strategy(niche, goal, budget, geo)

    st.markdown("### 💰 Auto-Scaled Budget Allocation")
    for p, amt in allocations.items():
        st.metric(p, f"${amt:,.0f}")

    st.markdown("### 📊 Efficiency Scores")
    cols = st.columns(len(PLATFORMS))
    for col, p in zip(cols, PLATFORMS):
        with col:
            st.metric(p, f"{efficiency_score(p, budget)}/10")

    st.markdown("### 🔁 Auto-Rebalancing Recommendations")
    for r in auto_rebalance(allocations):
        st.write(r)

    st.markdown("### 🔓 Feature Access")
    for f, enabled in features.items():
        if enabled:
            st.success(f"✅ {f}")
        else:
            st.warning(f"🔒 {f} (Increase budget to unlock)")

    if budget < 10000:
        st.info("🧠 Focus on 1–2 platforms for clean data.")
    elif budget < 25000:
        st.success("🧠 Strong multi-platform testing phase.")
    else:
        st.success("🚀 Full-funnel omnichannel scale unlocked.")

# ===============================
# RESEARCH TAB
# ===============================
with tab_research:
    st.subheader("📊 Research & Trends")

    keyword = st.text_input("Seed Keyword / Interest")
    timeframe = st.selectbox(
        "Timeframe",
        ["1 Month", "3 Months", "12 Months", "5 Years"]
    )

    if st.button("Run Research (Planner Mode)"):
        if not keyword:
            st.warning("Enter a keyword.")
        else:
            st.success("Research generated (planner-level)")

            df = pd.DataFrame({
                "Location": ["US", "CA", "UK", "AU"],
                "Interest Index": [92, 76, 64, 51]
            })

            st.markdown("#### 🌍 Top Locations")
            st.dataframe(df)

            st.markdown("#### 🎯 Audience Insights")
            st.write("- Age: 18–44")
            st.write("- Gender: Balanced")
            st.write("- Devices: Mobile dominant")

            st.info("🔌 Real API trend ingestion can be connected here.")

# ===============================
# PLATFORM TABS (SUPER GENERATORS)
# ===============================
def platform_shell(platform_name):
    st.subheader(f"{platform_name} Campaign Generator")

    daily_budget = st.number_input(
        "Daily Budget",
        min_value=10.0,
        value=50.0,
        step=10.0,
        key=platform_name
    )

    st.text_area(
        "Generated Headlines",
        value=(
            f"• Discover what everyone’s talking about\n"
            f"• Limited time – act now\n"
            f"• Built for {platform_name} audiences"
        ),
        height=100
    )

    st.text_area(
        "Primary Ad Copy",
        value=(
            "High-impact messaging aligned with platform behavior.\n"
            "Optimized for engagement and conversion."
        ),
        height=120
    )

    st.info("🔌 Real reach & conversion estimates connect here via API.")

with tab_google:
    platform_shell("Google / YouTube")

with tab_tiktok:
    platform_shell("TikTok")

with tab_spotify:
    platform_shell("Spotify")

with tab_meta:
    platform_shell("Meta")
    st.info("📣 Meta Reach Estimate API plugs in here (act_{ad_account_id}/reachestimate).")

st.markdown("---")
st.caption("Sully Super Media Planner · Planning Engine v1")