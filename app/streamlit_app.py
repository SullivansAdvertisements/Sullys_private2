# ================================================
# SULLY MARKETING BOT – META API READY EDITION
# ================================================

import os
import json
import time
import requests
from datetime import datetime
import streamlit as st
import pandas as pd

# -----------------------------
# 1. LOAD META API SECRETS
# -----------------------------
# You MUST add these inside Streamlit Secrets:
# META_SYSTEM_USER_TOKEN
# META_BUSINESS_ID
# META_AD_ACCOUNT_ID
# META_APP_ID
# META_APP_SECRET

META_TOKEN = st.secrets.get("META_SYSTEM_USER_TOKEN", None)
META_BM_ID = st.secrets.get("META_BUSINESS_ID", None)
META_AD_ACCOUNT = st.secrets.get("META_AD_ACCOUNT_ID", None)
META_APP_ID = st.secrets.get("META_APP_ID", None)
META_APP_SECRET = st.secrets.get("META_APP_SECRET", None)

# -----------------------------
# CHECK IF META API DETAILS EXIST
# -----------------------------
def meta_api_ready():
    return (
        META_TOKEN is not None
        and META_BM_ID is not None
        and META_AD_ACCOUNT is not None
        and META_APP_ID is not None
        and META_APP_SECRET is not None
    )

# -----------------------------
# STREAMLIT PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Sully's Marketing BOT",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Transparent Logo Header
st.markdown(
    """
    <div style="text-align:center;">
        <img src="https://raw.githubusercontent.com/SullivansAdvertisements/Assets/main/sullivans_logo.png"
             style="width:160px; margin-top:10px;">
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("Sully's Ultimate Marketing & Media Planning Bot")
st.caption("Connected • Smart • API-Ready • Multi-Platform")

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("Campaign Inputs")

niche = st.sidebar.selectbox("Choose Niche", ["Music Artist", "Clothing Brand", "Local Home Care"])
goal = st.sidebar.selectbox("Goal", ["Awareness", "Traffic", "Conversions", "Leads", "Sales"])
budget = st.sidebar.number_input("Monthly Budget ($)", value=500, min_value=50, step=50)
country = st.sidebar.text_input("Target Country (ex: US)", value="US")

run_campaign = st.sidebar.button("Generate Campaign Strategy")

# -----------------------------
# META API CALL FUNCTIONS
# -----------------------------

META_GRAPH = "https://graph.facebook.com/v18.0"

def meta_get_estimate(campaign_objective, daily_budget):
    """
    Calls Meta's Reach Estimate API.
    Requires real SYSTEM USER TOKEN + BUSINESS ACCOUNT.
    """
    if not meta_api_ready():
        return {"error": "Meta API not configured in st.secrets"}

    url = f"{META_GRAPH}/act_{META_AD_ACCOUNT}/delivery_estimate"

    params = {
        "optimization_goal": campaign_objective,
        "daily_budget": int(daily_budget * 100),  # convert to cents
        "targeting_spec": json.dumps({
            "geo_locations": {"countries": [country]},
            "publisher_platforms": ["facebook", "instagram"]
        }),
        "access_token": META_TOKEN
    }

    r = requests.get(url, params=params)

    try:
        data = r.json()
    except:
        return {"error": "Invalid response from Meta"}

    return data


# -----------------------------
# MAIN BOT LOGIC
# -----------------------------
if run_campaign:

    st.subheader("📊 Campaign Strategy Summary")

    daily_budget = budget / 30

    st.write(f"**Budget:** ${budget}")
    st.write(f"**Daily Budget:** ${daily_budget:.2f}")
    st.write(f"**Goal:** {goal}")
    st.write(f"**Niche:** {niche}")
    st.write(f"**Country:** {country}")

    st.markdown("---")

    # ==========================================================
    # META REACH ESTIMATE (Real API Call)
    # ==========================================================
    st.subheader("📡 Meta (Facebook + Instagram) API Prediction")

    if meta_api_ready():
        with st.spinner("Fetching real-time reach from Meta..."):
            if goal == "Awareness":
                meta_goal = "REACH"
            elif goal == "Traffic":
                meta_goal = "LINK_CLICKS"
            elif goal == "Leads":
                meta_goal = "LEAD_GENERATION"
            elif goal == "Conversions":
                meta_goal = "OFFSITE_CONVERSIONS"
            else:
                meta_goal = "IMPRESSIONS"

            estimate = meta_get_estimate(meta_goal, daily_budget)

        st.write("### Meta API Response:")
        st.json(estimate)

    else:
        st.warning("⚠️ Meta API is NOT configured yet. Add your credentials in Streamlit Secrets.")

    st.markdown("---")

    # ==========================================================
    # PLATFORM STRATEGIC BREAKDOWN
    # ==========================================================
    st.subheader("🧠 Platform Strategy (Automatic)")

    strategy = {
        "Awareness": {
            "Messaging": "Maximize visibility and reach.",
            "Suggested Platforms": ["Meta", "TikTok", "YouTube"],
            "Expected Reach": f"{int(budget * 80)} - {int(budget * 160)} people/month"
        },
        "Traffic": {
            "Messaging": "Drive qualified clicks.",
            "Suggested Platforms": ["Meta", "Google Search", "TikTok"],
            "Expected Clicks": f"{int(budget * 3)} - {int(budget * 6)}"
        },
        "Leads": {
            "Messaging": "Generate high-intent leads.",
            "Suggested Platforms": ["Meta", "Google Search"],
            "Expected Leads": f"{int(budget * 0.4)} - {int(budget * 1.2)}"
        },
        "Sales": {
            "Messaging": "Acquire customers profitably.",
            "Suggested Platforms": ["Meta", "Google Search", "YouTube"],
            "Expected Purchases": f"{int(budget * 0.1)} - {int(budget * 0.3)}"
        },
    }

    st.write(strategy.get(goal, {}))

    st.markdown("---")

    # ==========================================================
    # ROI CALCULATOR
    # ==========================================================
    st.subheader("💰 ROI Estimator")

    avg_rev = st.number_input("Average Revenue per Customer ($)", min_value=1, value=80)

    if "Expected Purchases" in strategy.get(goal, {}):
        low = int(budget * 0.1)
        high = int(budget * 0.3)
        roi_low = (low * avg_rev) - budget
        roi_high = (high * avg_rev) - budget
        st.write(f"**ROI Range:** ${roi_low} → ${roi_high}")
    else:
        st.info("ROI available for **Sales** campaigns only.")

else:
    st.info("Click **Generate Campaign Strategy** to start.")

