# ==========================
# Sully's Marketing Bot – Clean Media Planner
# ==========================

import os
from pathlib import Path
from datetime import datetime
import io
import json

import streamlit as st
import pandas as pd

# --------- BASIC PAGE SETUP ---------
st.set_page_config(
    page_title="Sully's Mini Media Planner",
    page_icon="📊",
    layout="wide",
)

# --------- LIGHT THEME STYLE OVERRIDE (no dark bg) ---------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f7f7f9;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3, h4, h5, h6, p, label, span {
        color: #111827 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------- LOGO & HEADER ---------
LOGO_PATH = Path(__file__).with_name("sullivans_logo.png")

header_col1, header_col2 = st.columns([1, 4])
with header_col1:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)
with header_col2:
    st.title("Sully’s Mini Media Planner")
    st.write("Strategic cross-platform planner for Music, Clothing Brands, and Local Home Care.")


# ========= PLATFORM “BRAIN” HEURISTICS =========

# Base CPMs (cost per 1000 impressions) in USD for Awareness
BASE_CPM = {
    "Meta": 8.0,
    "TikTok": 6.0,
    "Google Search": 20.0,   # search usually more expensive per 1000 impressions
    "YouTube": 10.0,
    "Spotify": 14.0,
    "Twitter/X": 7.0,
    "Snapchat": 5.0,
}

# Base CTR (click-through rate) per platform (for consideration)
BASE_CTR = {
    "Meta": 0.012,
    "TikTok": 0.015,
    "Google Search": 0.04,
    "YouTube": 0.01,
    "Spotify": 0.005,
    "Twitter/X": 0.01,
    "Snapchat": 0.012,
}

# Base CVR (conversion rate) for a generic “conversion” event
BASE_CVR = {
    "Meta": 0.035,
    "TikTok": 0.025,
    "Google Search": 0.06,
    "YouTube": 0.02,
    "Spotify": 0.015,
    "Twitter/X": 0.02,
    "Snapchat": 0.02,
}

# Goal multipliers: adjust CVR by primary goal
GOAL_CVR_MULT = {
    "awareness": 0.3,        # awareness goal leads to fewer direct conversions
    "traffic": 0.6,
    "engagement": 0.8,
    "leads": 1.0,
    "sales": 1.1,
    "streams": 0.7,          # e.g., music streams
}

# Budget split per funnel stage
FUNNEL_SPLIT = {
    "Awareness": 0.25,
    "Consideration": 0.35,
    "Conversion": 0.40,
}


def estimate_platform_metrics(platform: str,
                              monthly_budget: float,
                              goal: str,
                              avg_revenue_per_conversion: float) -> dict:
    """Return estimated reach, clicks, conversions, and ROI for one platform."""
    cpm = BASE_CPM[platform]
    ctr = BASE_CTR[platform]
    base_cvr = BASE_CVR[platform]

    goal_key = goal.lower()
    cvr_mult = GOAL_CVR_MULT.get(goal_key, 1.0)
    cvr = base_cvr * cvr_mult

    results = {}

    for stage, frac in FUNNEL_SPLIT.items():
        stage_budget = monthly_budget * frac

        # Awareness: focus on impressions & reach
        if stage == "Awareness":
            impressions = (stage_budget / cpm) * 1000 if cpm > 0 else 0
            reach = impressions * 0.6   # rough unique reach estimate
            clicks = impressions * ctr
            conversions = clicks * cvr
        # Consideration: smaller but higher-intent pool
        elif stage == "Consideration":
            impressions = (stage_budget / (cpm * 1.2)) * 1000 if cpm > 0 else 0
            reach = impressions * 0.5
            clicks = impressions * (ctr * 1.2)
            conversions = clicks * (cvr * 1.1)
        # Conversion: focus on efficient conversions
        else:  # "Conversion"
            impressions = (stage_budget / (cpm * 1.5)) * 1000 if cpm > 0 else 0
            reach = impressions * 0.4
            clicks = impressions * (ctr * 1.4)
            conversions = clicks * (cvr * 1.3)

        revenue = conversions * avg_revenue_per_conversion
        cost = stage_budget
        roi = ((revenue - cost) / cost * 100) if cost > 0 else 0
        cpa = (cost / conversions) if conversions > 0 else None

        results[stage] = {
            "budget": stage_budget,
            "impressions": impressions,
            "reach": reach,
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue,
            "roi_pct": roi,
            "cpa": cpa,
        }

    return results


def platform_split_by_niche(niche: str, selected_platforms: list[str]) -> dict:
    """Assign weights by niche across platforms that are enabled."""
    niche = niche.lower()
    weights = {p: 1.0 for p in selected_platforms}

    if niche == "music":
        for p in weights:
            if p in ["Spotify", "YouTube", "TikTok", "Meta"]:
                weights[p] *= 1.4
    elif niche == "clothing brand":
        for p in weights:
            if p in ["Meta", "TikTok", "Snapchat", "Twitter/X"]:
                weights[p] *= 1.3
    elif niche == "local home care":
        for p in weights:
            if p in ["Google Search", "Meta"]:
                weights[p] *= 1.5

    # Normalize to sum to 1
    total = sum(weights.values()) or 1.0
    for p in weights:
        weights[p] /= total
    return weights


# ========= SIDEBAR – USER INPUTS =========

with st.sidebar:
    st.header("Campaign Inputs")

    niche = st.selectbox(
        "Niche",
        ["Music", "Clothing Brand", "Local Home Care"],
        index=0,
    )

    monthly_budget = st.number_input(
        "Monthly Ad Spend (USD)",
        min_value=100.0,
        value=2500.0,
        step=50.0,
    )

    primary_goal = st.selectbox(
        "Primary Goal",
        ["Awareness", "Traffic", "Engagement", "Leads", "Sales", "Streams"],
        index=0,
    )

    avg_revenue = st.number_input(
        "Average Revenue per Conversion (USD)",
        min_value=1.0,
        value=80.0,
        step=1.0,
        help="For Music: per sale/booking. Clothing: per order. Home Care: estimated first-month value."
    )

    st.markdown("### Geography")
    geo_mode = st.radio(
        "Target type",
        ["Country", "Worldwide"],
        horizontal=True,
    )
    if geo_mode == "Country":
        country = st.text_input("Country (ISO or name)", value="US")
        geo_label = country
    else:
        country = "WORLD"
        geo_label = "Worldwide"

    st.markdown("### Platforms")
    default_platforms = {
        "Meta (FB + IG)": True,
        "TikTok": True,
        "Google Search": True,
        "YouTube": True,
        "Spotify": False,
        "Twitter/X": False,
        "Snapchat": False,
    }
    platform_flags = {}
    for label, default in default_platforms.items():
        platform_flags[label] = st.checkbox(label, value=default)

    selected_platforms = []
    platform_name_map = {
        "Meta (FB + IG)": "Meta",
        "TikTok": "TikTok",
        "Google Search": "Google Search",
        "YouTube": "YouTube",
        "Spotify": "Spotify",
        "Twitter/X": "Twitter/X",
        "Snapchat": "Snapchat",
    }
    for label, on in platform_flags.items():
        if on:
            selected_platforms.append(platform_name_map[label])

    if not selected_platforms:
        st.warning("Select at least one platform to generate a plan.")

    generate = st.button("Generate Plan", type="primary")


# ========= MAIN – PLAN GENERATION =========

st.subheader("📋 Strategic Plan Overview")

if not generate:
    st.info("Configure your inputs in the sidebar and click **Generate Plan** to see recommendations.")
else:
    if not selected_platforms:
        st.error("Please select at least one platform in the sidebar.")
    else:
        # 1) Determine platform budget shares by niche
        splits = platform_split_by_niche(niche, selected_platforms)

        # 2) Compute estimates per platform & stage
        rows = []
        total_conversions = 0.0
        total_cost = 0.0
        total_revenue = 0.0

        for platform, weight in splits.items():
            platform_budget = monthly_budget * weight
            metrics = estimate_platform_metrics(
                platform,
                platform_budget,
                primary_goal,
                avg_revenue,
            )
            for stage, data in metrics.items():
                rows.append({
                    "Platform": platform,
                    "Stage": stage,
                    "Budget ($)": round(data["budget"], 2),
                    "Impressions": int(data["impressions"]),
                    "Reach": int(data["reach"]),
                    "Clicks": int(data["clicks"]),
                    "Conversions": round(data["conversions"], 2),
                    "Est. Revenue ($)": round(data["revenue"], 2),
                    "ROI %": round(data["roi_pct"], 1),
                    "CPA ($)": round(data["cpa"], 2) if data["cpa"] is not None else None,
                })
                total_cost += data["budget"]
                total_revenue += data["revenue"]
                total_conversions += data["conversions"]

        df = pd.DataFrame(rows)

        # 3) Show global summary
        overall_roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
        overall_cpa = (total_cost / total_conversions) if total_conversions > 0 else None

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Monthly Budget", f"${monthly_budget:,.0f}")
        c2.metric("Estimated Conversions", f"{total_conversions:,.1f}")
        c3.metric("Estimated Revenue", f"${total_revenue:,.0f}")
        c4.metric("Overall ROI", f"{overall_roi:,.1f}%")

        if overall_cpa is not None:
            st.caption(f"Estimated blended CPA: **${overall_cpa:,.2f}**")

        # 4) Detailed table per platform & stage
        st.subheader("📊 Platform & Funnel Breakdown")
        st.dataframe(df, use_container_width=True)

        # 5) Simple note on why ROI can be negative
        if avg_revenue < (overall_cpa or 0):
            st.warning(
                "Your average revenue per conversion may be too low relative to the estimated cost per conversion, "
                "which can make ROI negative. Try increasing AOV/LTV or tightening targeting."
            )

        # 6) Export plan JSON
        st.subheader("⬇️ Export Plan")
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        summary = {
            "niche": niche,
            "geo": geo_label,
            "monthly_budget": monthly_budget,
            "primary_goal": primary_goal,
            "avg_revenue_per_conversion": avg_revenue,
            "platform_splits": splits,
            "rows": rows,
            "totals": {
                "cost": total_cost,
                "revenue": total_revenue,
                "conversions": total_conversions,
                "roi_pct": overall_roi,
                "cpa": overall_cpa,
            },
            "generated_at_utc": ts,
        }
        buf = io.StringIO()
        json.dump(summary, buf, indent=2)
        st.download_button(
            label="Download Plan (JSON)",
            data=buf.getvalue(),
            file_name=f"sully_plan_{ts}.json",
            mime="application/json",
        )

        st.info(
            "These numbers are heuristic estimates to guide planning, not live data from Meta/TikTok/Google APIs. "
            "Once your APIs are wired, this planner can be upgraded to pull real performance baselines."
        )
