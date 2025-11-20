# ==========================
# Sully's Meta Super Bot (Clean Meta-only)
# ==========================

import os
import sys
from pathlib import Path
from datetime import datetime
import json

import requests
import streamlit as st
import pandas as pd

# ---------- BASIC PAGE CONFIG ----------
st.set_page_config(
    page_title="Sully's Meta Super Bot",
    page_icon="🌺",
    layout="wide",
)

# ---------- LOGO (TOP + SIDEBAR, NO BACKGROUND) ----------
APP_DIR = Path(__file__).resolve().parent
LOGO_PATH = APP_DIR / "sullivans_logo.png"  # make sure this file exists in /app

cols = st.columns([1, 3])
with cols[0]:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)
with cols[1]:
    st.markdown(
        "<h1 style='margin-bottom:0;'>Sully's Meta Super Bot</h1>"
        "<p style='color:#444;margin-top:4px;'>Meta (Facebook + Instagram) campaign planner & creator</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# Also show logo in sidebar
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)
    st.markdown("### Meta API Control Panel")


# ---------- META CONFIG (FROM STREAMLIT SECRETS) ----------
# Set these in Streamlit Cloud → Settings → Secrets:
# META_SYSTEM_USER_TOKEN, META_AD_ACCOUNT_ID, META_APP_ID, META_APP_SECRET (optional)
META_TOKEN = st.secrets.get("META_SYSTEM_USER_TOKEN")
META_AD_ACCOUNT_ID = st.secrets.get("META_AD_ACCOUNT_ID")  # digits only, no "act_"
META_APP_ID = st.secrets.get("META_APP_ID")
META_APP_SECRET = st.secrets.get("META_APP_SECRET")

GRAPH_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"


def meta_api(path: str, method: str = "GET", params: dict | None = None):
    """Small helper to call the Meta Graph API with the system user token."""
    if params is None:
        params = {}
    if not META_TOKEN:
        raise RuntimeError("META_SYSTEM_USER_TOKEN is not set in Streamlit secrets.")
    params["access_token"] = META_TOKEN

    url = f"{BASE_URL}/{path.lstrip('/')}"
    if method.upper() == "GET":
        resp = requests.get(url, params=params, timeout=30)
    else:
        resp = requests.post(url, data=params, timeout=30)

    try:
        data = resp.json()
    except Exception:
        resp.raise_for_status()
        return {"error": "Invalid JSON from Meta", "status": resp.status_code}
    if resp.status_code >= 400:
        raise RuntimeError(f"Meta API error {resp.status_code}: {json.dumps(data)}")
    return data


def map_goal_to_objective(goal: str) -> str:
    """Map high-level goal to a valid outcome-based Meta objective."""
    g = goal.lower()
    if "awareness" in g:
        return "OUTCOME_AWARENESS"
    if "traffic" in g:
        return "OUTCOME_TRAFFIC"
    if "lead" in g:
        return "OUTCOME_LEADS"
    if "sale" in g or "purchase" in g or "conversion" in g:
        return "OUTCOME_SALES"
    if "engage" in g or "video" in g:
        return "OUTCOME_ENGAGEMENT"
    if "app" in g:
        return "OUTCOME_APP_PROMOTION"
    # default fallback
    return "OUTCOME_TRAFFIC"


# ---------- SIDEBAR CONTROLS ----------
with st.sidebar:
    st.markdown("#### 1. Niche & Goal")

    niche = st.selectbox(
        "Niche",
        [
            "Music Artist",
            "Clothing Brand",
            "Local Home Care",
            "Other",
        ],
    )

    primary_goal = st.selectbox(
        "Primary Goal",
        [
            "Sales / Conversions",
            "Leads",
            "Traffic",
            "Awareness",
            "Engagement (Video / Posts)",
            "App Promotion",
        ],
    )

    st.markdown("#### 2. Budget & Geo")
    daily_budget = st.number_input(
        "Daily budget (USD)",
        min_value=1.0,
        value=20.0,
        step=1.0,
    )

    country = st.selectbox(
        "Main country",
        ["Worldwide", "United States", "United Kingdom", "Canada", "Australia", "Other"],
        index=0,
    )
    custom_geo = ""
    if country == "Other":
        custom_geo = st.text_input("Enter country/region name", value="")

    st.markdown("#### 3. Creative Direction")
    brand_name = st.text_input("Brand / Artist Name", value="")
    core_offer = st.text_area(
        "Core offer / hook",
        value="",
        placeholder="New album launch, 20% off collection, free home care consult, etc.",
    )
    url = st.text_input(
        "Destination URL (landing page, Linktree, etc.)",
        value="",
        placeholder="https://your-landing-page.com",
    )

    st.markdown("#### 4. Actions")
    run_plan = st.button("Generate Meta Strategy", type="primary")
    create_campaign = st.button("Create Meta Campaign in My Ad Account", type="secondary")


# ---------- META API HEALTH CHECK ----------
health_col1, health_col2 = st.columns(2)

with health_col1:
    st.subheader("Meta API Status")
    if not META_TOKEN or not META_AD_ACCOUNT_ID:
        st.error(
            "Meta secrets are missing.\n\n"
            "Set `META_SYSTEM_USER_TOKEN` and `META_AD_ACCOUNT_ID` in Streamlit **Secrets**."
        )
    else:
        try:
            me = meta_api("me", method="GET", params={"fields": "id,name"})
            st.success(f"Connected as: **{me.get('name', 'Unknown')}** (ID: {me.get('id')})")
        except Exception as e:
            st.error(f"Token check failed:\n\n{e}")

with health_col2:
    st.subheader("Ad Account")
    if META_AD_ACCOUNT_ID:
        try:
            act_id = f"act_{META_AD_ACCOUNT_ID}"
            acc = meta_api(
                act_id,
                method="GET",
                params={"fields": "id,account_id,name,currency,timezone_name"},
            )
            st.success(
                f"Ad Account: **{acc.get('name','?')}** (ID: {acc.get('account_id')})\n\n"
                f"Currency: {acc.get('currency')}, Timezone: {acc.get('timezone_name')}"
            )
        except Exception as e:
            st.error(f"Ad account lookup failed:\n\n{e}")
    else:
        st.warning("No `META_AD_ACCOUNT_ID` found in secrets.")


st.markdown("---")


# ---------- STRATEGY GENERATION (LOCAL BRAIN, NO FAKE NUMBERS) ----------
st.subheader("🎯 Meta Strategy Blueprint")

if run_plan:
    obj = map_goal_to_objective(primary_goal)
    geo_label = (
        "Worldwide"
        if country == "Worldwide"
        else custom_geo if country == "Other" and custom_geo
        else country
    )

    st.write(f"**Niche:** {niche}")
    st.write(f"**Goal:** {primary_goal} → Meta objective: `{obj}`")
    st.write(f"**Daily Budget:** ${daily_budget:,.2f}")
    st.write(f"**Geo:** {geo_label}")
    if brand_name:
        st.write(f"**Brand/Artist:** {brand_name}")
    if core_offer:
        st.write(f"**Core Offer:** {core_offer}")
    if url:
        st.write(f"**URL:** {url}")

    # Simple, human-readable plan – no fake reach, no fake ROI
    st.markdown("#### Suggested Campaign Structure")

    if niche == "Music Artist":
        st.markdown(
            """
- **Campaign type:** OUTCOME_ENGAGEMENT or OUTCOME_TRAFFIC  
- **Ad sets:**  
  - Fan lookalikes (if you have a pixel or Custom Audience)  
  - Interest stack: similar artists, genres, Spotify, Apple Music  
  - Retargeting: video viewers & IG engagers  
- **Placements:** Reels, Stories, IG Feed, FB Feed, In-stream video  
- **Creative:** Short vertical videos (7–15s) with hook in first 2 seconds, CTA to listen or pre-save.
"""
        )
    elif niche == "Clothing Brand":
        st.markdown(
            """
- **Campaign type:** OUTCOME_SALES (if you have pixel), else OUTCOME_TRAFFIC  
- **Ad sets:**  
  - Broad Advantage+ (18–44, fashion/shopper interests)  
  - Interest-based (streetwear, sneakers, fast fashion)  
  - Retargeting: product viewers, cart abandoners, IG engagers  
- **Placements:** IG Reels, IG Feed, FB Feed, Stories  
- **Creative:** UGC try-ons, outfit carousel, discount hooks, clear product shots.
"""
        )
    elif niche == "Local Home Care":
        st.markdown(
            """
- **Campaign type:** OUTCOME_LEADS  
- **Ad sets:**  
  - Geo-target radius around service area  
  - Demographic filter: 35+ (targeting adult children of seniors)  
- **Lead method:** Native lead forms or conversion leads to your site  
- **Placements:** FB Feed, IG Feed, maybe Audience Network  
- **Creative:** Trust-building: testimonials, staff introductions, clear services, phone + form CTA.
"""
        )
    else:
        st.markdown(
            """
- **Campaign type:** match Meta outcome to your business goal  
- **Ad sets:** one broad, one interest, one retargeting  
- **Creative:** At least 3–5 variations per ad set, mix static + video + carousel.
"""
        )

    st.info(
        "This section is your **blueprint** only. No fake reach/ROI numbers are shown — "
        "delivery data will come from the real Meta API once campaigns run."
    )
else:
    st.write("Click **Generate Meta Strategy** in the sidebar to see a tailored plan.")


st.markdown("---")


# ---------- REAL META CAMPAIGN CREATION ----------
st.subheader("🚀 Create Meta Campaign (Real API Call)")

if create_campaign:
    if not (META_TOKEN and META_AD_ACCOUNT_ID):
        st.error(
            "Meta token or ad account ID missing. Set `META_SYSTEM_USER_TOKEN` and "
            "`META_AD_ACCOUNT_ID` in Streamlit secrets first."
        )
    else:
        try:
            obj = map_goal_to_objective(primary_goal)
            act_id = f"act_{META_AD_ACCOUNT_ID}"

            # Build a campaign name
            ts = datetime.utcnow().strftime("%Y%m%d")
            base_geo = (
                "WW"
                if country == "Worldwide"
                else custom_geo if country == "Other" and custom_geo
                else country.replace(" ", "")
            )
            camp_name = f"{niche} | {primary_goal} | {base_geo} | {ts}"

            params = {
                "name": camp_name,
                "objective": obj,
                "status": "PAUSED",  # keep safe; user can enable in Ads Manager
                # must be a JSON array string
                "special_ad_categories": "[]",
            }

            st.write("Creating campaign with parameters:")
            st.json(params)

            resp = meta_api(f"act_{META_AD_ACCOUNT_ID}/campaigns", method="POST", params=params)

            st.success("✅ Campaign created successfully!")
            st.json(resp)
            st.info(
                "The campaign is created as **PAUSED**. "
                "Go to Meta Ads Manager to set ad sets, ads, pixel/conversions, and turn it ON."
            )
        except Exception as e:
            st.error(f"Meta campaign creation failed:\n\n{e}")


# ---------- NOTES ----------
st.markdown("---")
st.caption(
    "Note: This bot only shows **real Meta API results** (no fake reach, no fake ROI). "
    "For reach, conversions, and ROI, read performance from Meta Insights once your campaigns have delivery."
)
