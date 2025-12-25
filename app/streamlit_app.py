# streamlit_app.py
# Sully’s Multi-Platform Growth Engine (Client-Ready)

import streamlit as st

# ===== CORE LOGIC =====
from core.strategies import allocate_budget
from core.scale_engine import evaluate_performance
from core.common_ai import (
    generate_headlines,
    generate_primary_text,
    generate_ctas,
)

# ===== RESEARCH =====
from research.trends_client import get_google_trends
from research.tiktok_trends import get_tiktok_trends
from research.meta_library import search_meta_ads

# ===== INFLUENCER + EMAIL =====
from influencer.influencer import find_influencers
from email.outreach import generate_outreach_email

# =========================
# PAGE CONFIG (MUST BE FIRST)
# =========================
st.set_page_config(
    page_title="Sully Growth Engine",
    layout="wide",
)

# =========================
# BASIC LIGHT THEME
# =========================
st.markdown(
    """
    <style>
    body, p, div, label {
        color: #111 !important;
        font-family: system-ui;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HEADER
# =========================
st.title("🚀 Sully Multi-Platform Growth Engine")
st.caption("Strategy → Research → Campaigns → Influencers → Scaling")

# =========================
# TABS
# =========================
tab_strategy, tab_research, tab_campaigns, tab_influencer, tab_scale = st.tabs([
    "🧠 Strategy",
    "📊 Research",
    "📣 Campaign Builder",
    "🤝 Influencers & Email",
    "📈 Scaling & Optimization",
])

# =========================
# TAB 1 — STRATEGY
# =========================
with tab_strategy:
    st.subheader("Strategy Planner")

    niche = st.selectbox("Niche", ["Music", "Clothing", "Homecare"])
    goal = st.selectbox("Primary Goal", ["Awareness", "Traffic", "Leads", "Sales"])
    budget = st.number_input("Monthly Budget ($)", min_value=500.0, value=5000.0)

    platforms = st.multiselect(
        "Platforms to use",
        ["Meta", "Google", "TikTok", "YouTube", "Spotify"],
        default=["Meta", "Google", "TikTok"],
    )

    if st.button("Generate Strategy"):
        splits = allocate_budget(budget, goal)
        st.success("Budget Allocation")
        st.json({k: v for k, v in splits.items() if k in [p.lower() for p in platforms]})

# =========================
# TAB 2 — RESEARCH
# =========================
with tab_research:
    st.subheader("Cross-Platform Research")

    seed = st.text_input("Keyword / Interest Seed", "streetwear brand")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Google / YouTube Trends"):
            st.json(get_google_trends(seed))

    with col2:
        if st.button("TikTok Trends"):
            st.json(get_tiktok_trends(seed))

    with col3:
        if st.button("Meta Ad Library"):
            st.json(search_meta_ads(seed))

# =========================
# TAB 3 — CAMPAIGN BUILDER
# =========================
with tab_campaigns:
    st.subheader("Ad Creative Generator")

    platform = st.selectbox("Platform", ["Meta", "Google", "TikTok", "YouTube"])
    niche = st.selectbox("Niche", ["Music", "Clothing", "Homecare"], key="cb_niche")
    goal = st.selectbox("Goal", ["Awareness", "Traffic", "Sales"], key="cb_goal")

    if st.button("Generate Creatives"):
        headlines = generate_headlines(platform, niche, goal)
        primary = generate_primary_text(platform, niche, goal)
        ctas = generate_ctas(goal)

        st.markdown("### Headlines")
        st.write(headlines)

        st.markdown("### Primary Text")
        st.write(primary)

        st.markdown("### CTAs")
        st.write(ctas)

# =========================
# TAB 4 — INFLUENCERS + EMAIL
# =========================
with tab_influencer:
    st.subheader("Influencer Discovery & Outreach")

    niche = st.selectbox("Niche", ["Music", "Clothing", "Homecare"], key="inf_niche")
    country = st.text_input("Country", "US")

    if st.button("Find Influencers"):
        influencers = find_influencers(niche, country)
        st.json(influencers)

    st.markdown("---")
    st.markdown("### Email Outreach")

    handle = st.text_input("Influencer Handle")
    brand = st.text_input("Brand Name", "Sully")
    offer = st.text_input("Offer", "Paid collaboration")

    if st.button("Generate Outreach Email"):
        email = generate_outreach_email(brand, niche, handle, offer)
        st.markdown("**Subject:**")
        st.write(email["subject"])
        st.markdown("**Body:**")
        st.write(email["body"])

# =========================
# TAB 5 — SCALING ENGINE
# =========================
with tab_scale:
    st.subheader("Scaling & Optimization Engine")

    st.caption("Simulated performance input (replace with real APIs later)")

    metrics = {
        "meta": {"roas": st.slider("Meta ROAS", 0.5, 4.0, 2.4)},
        "google": {"roas": st.slider("Google ROAS", 0.5, 4.0, 1.9)},
        "tiktok": {"roas": st.slider("TikTok ROAS", 0.5, 4.0, 3.1)},
    }

    if st.button("Evaluate & Optimize"):
        actions = evaluate_performance(metrics)
        st.success("Scaling Recommendations")
        st.json(actions)