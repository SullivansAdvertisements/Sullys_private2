# ==========================
# Sully's Mini Media Planner
# Light theme, logo header, no background
# ==========================

import os
from datetime import datetime

import streamlit as st
import pandas as pd

# --------------------------
# PAGE CONFIG (light feel)
# --------------------------
st.set_page_config(
    page_title="Sully's Marketing Bot",
    page_icon="📊",
    layout="wide",
)

# --------------------------
# LOGO HEADER (top, no bg)
# --------------------------
LOGO_PATH = os.path.join(os.path.dirname(__file__), "sullivans_logo.png")

header_cols = st.columns([1, 4])
with header_cols[0]:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_column_width=True)
with header_cols[1]:
    st.markdown(
        """
        # Sully's Mini Media Planner  
        _Music · Clothing Brands · Local Home Care_
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# --------------------------
# HELPER: simple estimation brain
# --------------------------
PLATFORMS = [
    "Meta (FB + IG)",
    "TikTok Ads",
    "Google Search",
    "YouTube Ads",
    "Spotify Ads",
    "Twitter/X Ads",
    "Snapchat Ads",
]

DEFAULT_METRICS = {
    # platform: {goal: {cpm, cpc, ctr, cvr}}
    "Meta (FB + IG)": {
        "awareness":   {"cpm": 6.0,  "cpc": 0.90, "ctr": 0.012, "cvr": 0.025},
        "traffic":     {"cpm": 7.0,  "cpc": 0.75, "ctr": 0.018, "cvr": 0.030},
        "conversions": {"cpm": 10.0, "cpc": 1.20, "ctr": 0.015, "cvr": 0.040},
        "leads":       {"cpm": 9.0,  "cpc": 1.00, "ctr": 0.016, "cvr": 0.080},
        "sales":       {"cpm": 11.0, "cpc": 1.40, "ctr": 0.014, "cvr": 0.045},
    },
    "TikTok Ads": {
        "awareness":   {"cpm": 5.0,  "cpc": 0.80, "ctr": 0.014, "cvr": 0.018},
        "traffic":     {"cpm": 6.0,  "cpc": 0.70, "ctr": 0.020, "cvr": 0.022},
        "conversions": {"cpm": 9.0,  "cpc": 1.10, "ctr": 0.018, "cvr": 0.030},
        "leads":       {"cpm": 8.0,  "cpc": 0.95, "ctr": 0.019, "cvr": 0.055},
        "sales":       {"cpm": 10.0, "cpc": 1.30, "ctr": 0.017, "cvr": 0.035},
    },
    "Google Search": {
        "awareness":   {"cpm": 8.0,  "cpc": 1.00, "ctr": 0.020, "cvr": 0.030},
        "traffic":     {"cpm": 9.0,  "cpc": 1.20, "ctr": 0.030, "cvr": 0.035},
        "conversions": {"cpm": 12.0, "cpc": 1.80, "ctr": 0.035, "cvr": 0.060},
        "leads":       {"cpm": 11.0, "cpc": 1.60, "ctr": 0.033, "cvr": 0.080},
        "sales":       {"cpm": 13.0, "cpc": 2.20, "ctr": 0.032, "cvr": 0.070},
    },
    "YouTube Ads": {
        "awareness":   {"cpm": 5.5,  "cpc": 1.10, "ctr": 0.008, "cvr": 0.015},
        "traffic":     {"cpm": 6.5,  "cpc": 0.95, "ctr": 0.012, "cvr": 0.020},
        "conversions": {"cpm": 9.5,  "cpc": 1.40, "ctr": 0.014, "cvr": 0.030},
        "leads":       {"cpm": 8.5,  "cpc": 1.20, "ctr": 0.013, "cvr": 0.045},
        "sales":       {"cpm": 10.5, "cpc": 1.70, "ctr": 0.013, "cvr": 0.035},
    },
    "Spotify Ads": {
        "awareness":   {"cpm": 7.0,  "cpc": 1.30, "ctr": 0.005, "cvr": 0.010},
        "traffic":     {"cpm": 7.5,  "cpc": 1.10, "ctr": 0.007, "cvr": 0.015},
        "conversions": {"cpm": 9.0,  "cpc": 1.60, "ctr": 0.008, "cvr": 0.020},
        "leads":       {"cpm": 8.5,  "cpc": 1.40, "ctr": 0.008, "cvr": 0.030},
        "sales":       {"cpm": 10.0, "cpc": 1.90, "ctr": 0.007, "cvr": 0.025},
    },
    "Twitter/X Ads": {
        "awareness":   {"cpm": 5.5,  "cpc": 0.85, "ctr": 0.011, "cvr": 0.018},
        "traffic":     {"cpm": 6.5,  "cpc": 0.80, "ctr": 0.016, "cvr": 0.022},
        "conversions": {"cpm": 9.5,  "cpc": 1.30, "ctr": 0.017, "cvr": 0.030},
        "leads":       {"cpm": 8.5,  "cpc": 1.10, "ctr": 0.017, "cvr": 0.050},
        "sales":       {"cpm": 10.5, "cpc": 1.60, "ctr": 0.016, "cvr": 0.035},
    },
    "Snapchat Ads": {
        "awareness":   {"cpm": 4.5,  "cpc": 0.75, "ctr": 0.014, "cvr": 0.016},
        "traffic":     {"cpm": 5.5,  "cpc": 0.70, "ctr": 0.018, "cvr": 0.020},
        "conversions": {"cpm": 8.5,  "cpc": 1.10, "ctr": 0.019, "cvr": 0.028},
        "leads":       {"cpm": 7.5,  "cpc": 0.95, "ctr": 0.018, "cvr": 0.045},
        "sales":       {"cpm": 9.5,  "cpc": 1.35, "ctr": 0.017, "cvr": 0.032},
    },
}


def estimate_platform(
    platform: str,
    goal: str,
    budget: float,
    avg_revenue_per_conv: float,
):
    """
    Very rough estimation function.
    Returns dict with impressions, clicks, conversions, revenue, roi.
    """

    # Safety
    goal_key = goal.lower()
    if goal_key not in ["awareness", "traffic", "conversions", "leads", "sales"]:
        goal_key = "conversions"

    metrics = DEFAULT_METRICS.get(platform, {}).get(goal_key)
    if not metrics:
        return {
            "Platform": platform,
            "Goal": goal,
            "Budget": budget,
            "Impressions": 0,
            "Clicks": 0,
            "Conversions": 0,
            "Revenue": 0,
            "ROI %": 0,
        }

    cpm = metrics["cpm"]  # cost per 1000 impressions
    cpc = metrics["cpc"]  # cost per click
    ctr = metrics["ctr"]  # click-through rate
    cvr = metrics["cvr"]  # conversion rate

    # Awareness: calculate primarily via CPM
    impressions = (budget / cpm) * 1000.0

    # Traffic: approximate clicks from CTR & CPM vs CPC
    # We'll just use CPC for simpler math:
    clicks = budget / cpc if cpc > 0 else impressions * ctr

    # Conversions: from clicks * CVR
    conversions = clicks * cvr

    # Revenue: conversions * ARPU
    revenue = conversions * avg_revenue_per_conv

    roi = 0
    if budget > 0:
        roi = (revenue - budget) / budget * 100.0

    return {
        "Platform": platform,
        "Goal": goal,
        "Budget": round(budget, 2),
        "Impressions": int(impressions),
        "Clicks": int(clicks),
        "Conversions": round(conversions, 1),
        "Revenue": round(revenue, 2),
        "ROI %": round(roi, 1),
    }


# --------------------------
# SIDEBAR – User Inputs
# --------------------------
with st.sidebar:
    st.header("🧾 Campaign Inputs")

    niche = st.selectbox(
        "Niche",
        ["Music / Artist", "Clothing Brand", "Local Home Care"],
    )

    primary_goal = st.selectbox(
        "Primary Goal",
        ["Awareness", "Traffic", "Conversions", "Leads", "Sales"],
    )

    monthly_budget = st.number_input(
        "Total Monthly Budget (USD)",
        min_value=100.0,
        value=2500.0,
        step=50.0,
    )

    avg_revenue = st.number_input(
        "Average Revenue Per Conversion (USD)",
        min_value=1.0,
        value=80.0,
        step=5.0,
        help="E.g. average order value, value per lead, or per client",
    )

    st.markdown("### Targeting")

    geo_mode = st.selectbox(
        "Main Country / Geo",
        ["Worldwide", "United States", "Custom"],
    )

    custom_geo = ""
    if geo_mode == "Custom":
        custom_geo = st.text_input(
            "Enter main countries/regions",
            placeholder="e.g. US, UK, CA, EU, or specific cities",
        )

    st.markdown("### Platform Allocation")

    meta_share = st.slider("Meta (FB + IG) %", 0, 100, 35)
    tiktok_share = st.slider("TikTok %", 0, 100, 20)
    google_share = st.slider("Google Search %", 0, 100, 20)
    youtube_share = st.slider("YouTube %", 0, 100, 10)
    spotify_share = st.slider("Spotify %", 0, 100, 5)
    twitter_share = st.slider("Twitter/X %", 0, 100, 5)
    snap_share = st.slider("Snapchat %", 0, 100, 5)

    total_share = (
        meta_share
        + tiktok_share
        + google_share
        + youtube_share
        + spotify_share
        + twitter_share
        + snap_share
    )

    if total_share == 0:
        st.warning("Set at least one platform above 0%.")
    elif total_share != 100:
        st.info(f"Total allocation = {total_share}%. It will be normalized automatically.")

    run = st.button("🚀 Generate Plan")


# --------------------------
# MAIN LAYOUT
# --------------------------
st.subheader("🎯 Strategy Overview")

# Short narrative
geo_text = "Worldwide" if geo_mode == "Worldwide" else geo_mode
if geo_mode == "Custom" and custom_geo.strip():
    geo_text = custom_geo

st.markdown(
    f"""
**Niche:** `{niche}`  
**Primary Goal:** `{primary_goal}`  
**Geo Focus:** `{geo_text}`  
**Monthly Budget:** `${monthly_budget:,.0f}`  
**Avg Revenue / Conversion:** `${avg_revenue:,.2f}`  
"""
)

if not run:
    st.info("Set your inputs in the sidebar and click **Generate Plan** to see reach / conversion estimates.")
    st.stop()

# Normalize shares so they sum to 1
shares = {
    "Meta (FB + IG)": meta_share,
    "TikTok Ads": tiktok_share,
    "Google Search": google_share,
    "YouTube Ads": youtube_share,
    "Spotify Ads": spotify_share,
    "Twitter/X Ads": twitter_share,
    "Snapchat Ads": snap_share,
}
total_share = sum(shares.values())
if total_share == 0:
    st.error("Total platform allocation is 0%. Increase some sliders.")
    st.stop()

norm_shares = {p: v / total_share for p, v in shares.items() if v > 0}

# Compute estimates per platform
goal_key = primary_goal.lower()
rows = []
for plat, ratio in norm_shares.items():
    plat_budget = monthly_budget * ratio
    est = estimate_platform(plat, goal_key, plat_budget, avg_revenue)
    rows.append(est)

df = pd.DataFrame(rows)

st.subheader("📊 Estimated Reach, Clicks, Conversions & ROI by Platform")
st.dataframe(df, use_container_width=True)

# Totals
total_impressions = df["Impressions"].sum()
total_clicks = df["Clicks"].sum()
total_conversions = df["Conversions"].sum()
total_revenue = df["Revenue"].sum()
overall_roi = 0.0
if monthly_budget > 0:
    overall_roi = (total_revenue - monthly_budget) / monthly_budget * 100.0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Impressions", f"{int(total_impressions):,}")
col2.metric("Total Clicks", f"{int(total_clicks):,}")
col3.metric("Total Conversions", f"{total_conversions:,.1f}")
col4.metric("Overall ROI %", f"{overall_roi:,.1f}%")

st.markdown("---")
st.caption(
    "All numbers above are **rough planning estimates**, not live API data. "
    "To get true performance, you’ll connect each platform’s ad account and pull actual stats."
)
