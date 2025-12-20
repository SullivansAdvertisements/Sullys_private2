# Sully's Multi-Platform Ad Intelligence Bot (production-ready UI)
from clients.trends_client import get_advanced_trends
import io, json
from pathlib import Path
import streamlit as st
import pandas as pd

from clients.common_ai import generate_headlines, summarize_insights
from clients.trends_client import cross_platform_trends
from clients.google_client import google_campaign_generator
from clients.meta_client import (
    meta_campaign_generator, meta_delivery_estimate,
    create_campaign, create_adset, create_ad
)
from clients.tiktok_client import tiktok_campaign_generator
from clients.spotify_client import spotify_campaign_generator

# ---- Page setup ----
st.set_page_config(page_title="Sullivan's Ads Super Generator", page_icon="📈", layout="wide")
APP_DIR = Path(__file__).resolve().parent
ASSETS = APP_DIR / "assets"
LOGO = ASSETS / "sullivans_logo.png"
HEADER_BG = ASSETS / "header_bg.png"
SIDEBAR_BG = ASSETS / "sidebar_bg.png"

# ---- Branding & fixed header/sidebar backgrounds ----
st.markdown(f"""
<style>
header {{ background-image: url("file://{HEADER_BG}"); background-size: cover; }}
[data-testid="stSidebar"] {{ background-image: url("file://{SIDEBAR_BG}"); background-size: cover; }}
.stApp {{ background:#f7f7fb; }}
h1,h2,h3,h4,h5, .stMarkdown, label, p, span, div {{ color:#111 !important; }}
.stTabs [role="tab"] p {{ color:#111 !important; }}
</style>
""", unsafe_allow_html=True)

c1, c2 = st.columns([1,4])
with c1:
    if LOGO.exists(): st.image(str(LOGO), width=120)
with c2:
    st.title("Sullivan's Multi-Platform Ad Intelligence Bot")
    st.caption("AI research → strategy → campaigns (with live Meta estimates when keys are set).")
st.divider()

# ---- Global sidebar controls ----
with st.sidebar:
    st.header("Global Inputs")
    brand = st.text_input("Brand / Product", "Sully’s")
    objective = st.selectbox("Primary Objective", ["Awareness","Traffic","Leads","Conversions","Sales"])
    daily_budget = st.slider("Daily Budget ($)", 10, 5000, 100)
    seed_keywords = st.text_area("Seed Keywords / Interests", "streetwear, hip hop, home care")

# ---- Tabs ----
tab_trends, tab_google, tab_meta, tab_tiktok, tab_spotify, tab_ai = st.tabs(
    ["📊 Trends & Research","🔍 Google / YouTube","📘 Meta","🎵 TikTok","🎧 Spotify","🧠 AI Strategy"]
)

# ============ Trends ============
with tab_trends:
    st.subheader("Cross-Platform Trend Intelligence")
    colA, colB = st.columns([3,1])
    with colA:
        timeframe = st.selectbox("Google timeframe", ["now 7-d","today 3-m","today 12-m","today 5-y"], index=2)
        geo = st.text_input("Geo (Google Trends geo code)", value="")
    with colB:
        run_trends = st.button("Run Trend Research")

    if run_trends:
        data = cross_platform_trends(seed_keywords, timeframe=timeframe, geo=geo)
        st.markdown("### Raw Signals")
        st.json(data)
        st.markdown("### AI Summary")
        st.write(summarize_insights(data))

# ============ Google / YouTube ============
with tab_google:
    st.subheader("Google & YouTube Campaign Generator")
    if st.button("Generate Google/YouTube Plan"):
        st.json(google_campaign_generator(brand, objective, daily_budget, seed_keywords))

# ============ Meta ============
with tab_meta:
    st.subheader("Meta Campaign Builder + Delivery Estimate")

    # Live reach estimate (works with real Meta credentials)
    st.markdown("#### Quick Delivery Estimate")
    col1, col2, col3 = st.columns(3)
    with col1: country = st.text_input("Country (ISO)", "US")
    with col2: age_min, age_max = st.slider("Age range", 18, 65, (18, 45))
    with col3:
        if st.button("Estimate Daily Reach (Meta)"):
            est = meta_delivery_estimate(st.secrets, country=country, age_min=age_min, age_max=age_max)
            st.json(est)

    st.markdown("---")
    st.markdown("#### Full Campaign → Ad Set → Ad (creates PAUSED objects)")

    # 1) Campaign
    colc1, colc2 = st.columns(2)
    with colc1:
        camp_name = st.text_input("Campaign Name", f"{brand} – {objective} – Meta")
    with colc2:
        obj = st.selectbox("Objective", ["OUTCOME_AWARENESS","OUTCOME_TRAFFIC","OUTCOME_LEADS","OUTCOME_SALES"])
    if st.button("Create Campaign"):
        resp = create_campaign(st.secrets, camp_name, obj)
        st.json(resp)
        if isinstance(resp, dict) and resp.get("id"): st.session_state["campaign_id"] = resp["id"]

    # 2) Ad set
    st.markdown("##### Ad Set")
    d1, d2, d3 = st.columns(3)
    with d1:
        adset_name = st.text_input("Ad Set Name", "Core Audience")
    with d2:
        adset_budget = st.number_input("Daily Budget (USD)", min_value=1.0, value=float(daily_budget))
    with d3:
        campaign_id = st.text_input("Campaign ID", value=st.session_state.get("campaign_id",""))
    d4, d5 = st.columns(2)
    with d4:
        ad_country = st.text_input("Ad Set Country", country)
    with d5:
        age_min2, age_max2 = st.slider("Ad Set Age range", 18, 65, (age_min, age_max))
    if st.button("Create Ad Set"):
        resp = create_adset(st.secrets, campaign_id, adset_name, adset_budget, ad_country, age_min2, age_max2, obj)
        st.json(resp)
        if isinstance(resp, dict) and resp.get("id"): st.session_state["adset_id"] = resp["id"]

    # 3) Ad
    st.markdown("##### Ad (Page + optional IG)")
    a1, a2 = st.columns(2)
    with a1:
        link_url = st.text_input("Destination URL", "https://example.com")
        primary = st.text_area("Primary Text", "Tap to see the new drop.")
    with a2:
        headline = st.text_input("Headline", "New Collection Live")
        description = st.text_input("Description", "Limited quantities. Don’t miss it.")
    adset_id = st.text_input("Ad Set ID", value=st.session_state.get("adset_id",""))
    if st.button("Create Ad"):
        from clients.meta_client import _secrets
        c = _secrets(st.secrets)
        resp = create_ad(st.secrets, adset_id, f"{brand} – Main", c["page"], c["ig"], link_url, primary, headline, description)
        st.json(resp)

# ============ TikTok ============
with tab_tiktok:
    st.subheader("TikTok Campaign Generator")
    if st.button("Generate TikTok Plan"):
        st.json(tiktok_campaign_generator(brand, objective, daily_budget, seed_keywords))

# ============ Spotify ============
with tab_spotify:
    st.subheader("Spotify Audio Campaign Generator")
    if st.button("Generate Spotify Plan"):
        st.json(spotify_campaign_generator(brand, objective, daily_budget, seed_keywords))

# ============ AI Strategy ============
with tab_ai:
    st.subheader("Unified AI Campaign Strategy")
    if st.button("Generate Master Headlines"):
        st.json(generate_headlines(brand, objective, seed_keywords))
