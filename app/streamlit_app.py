# ==========================
# Sully's Mini Media Planner
# Brand new, light theme, logo on top
# ==========================

import os
from pathlib import Path
from datetime import datetime
import io
import json

import streamlit as st
import pandas as pd

# --- Optional: Google Trends (won't crash if missing) ---
try:
    from pytrends.request import TrendReq
    HAS_TRENDS = True
except ImportError:
    HAS_TRENDS = False

# ==========================
# Basic config + styling
# ==========================

st.set_page_config(
    page_title="Sully's Mini Media Planner",
    page_icon="💼",
    layout="wide"
)

def set_light_theme():
    """Force a light, clean look and readable font."""
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f7f7fb;
            color: #111111;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }
        h1, h2, h3 {
            color: #111111;
        }
        .platform-card {
            border-radius: 12px;
            padding: 1rem 1.25rem;
            border: 1px solid #e0e0ea;
            background: #ffffff;
            margin-bottom: 0.75rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

set_light_theme()

# ==========================
# Logo helper
# ==========================

LOGO_PATH = Path(__file__).with_name("sullivans_logo.png")

def show_header():
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), caption="", use_column_width=True)
        else:
            st.write("🧩 Upload `sullivans_logo.png` into the `app/` folder to see your logo here.")
    with col_title:
        st.markdown("### Sully's Mini Media Planner")
        st.markdown(
            "Plan **multi-platform campaigns** for Music, Clothing Brands, and Local Home Care "
            "with estimated reach, conversions, and ROI."
        )

show_header()

st.markdown("---")

# ==========================
# Helpers: media planner "brain"
# ==========================

PLATFORMS = [
    "Meta (FB + IG)",
    "TikTok Ads",
    "Google Search",
    "YouTube Ads",
    "Spotify Ads",
    "Twitter/X Ads",
    "Snapchat Ads",
]

GOALS = ["sales", "conversions", "leads", "awareness", "traffic"]

def clean_goal(goal: str) -> str:
    g = (goal or "").lower()
    if g not in GOALS:
        return "conversions"
    return g

def get_platform_params(goal: str):
    """
    Rough heuristic parameters (CPM, CTR, CVR, budget share) for each platform.
    All values are approximate and *not* real-time from platforms.
    """
    goal = clean_goal(goal)

    # Baseline by platform (CPM in $, CTR and CVR as fractions)
    base = {
        "Meta (FB + IG)":    {"share": 0.32, "cpm": 6.0,  "ctr": 0.017},
        "TikTok Ads":        {"share": 0.18, "cpm": 5.0,  "ctr": 0.014},
        "Google Search":     {"share": 0.22, "cpm": 9.0,  "ctr": 0.045},
        "YouTube Ads":       {"share": 0.10, "cpm": 7.0,  "ctr": 0.012},
        "Spotify Ads":       {"share": 0.05, "cpm": 8.0,  "ctr": 0.006},
        "Twitter/X Ads":     {"share": 0.07, "cpm": 4.5,  "ctr": 0.010},
        "Snapchat Ads":      {"share": 0.06, "cpm": 4.0,  "ctr": 0.012},
    }

    # Goal-based conversion rates (CVR from click to conversion)
    if goal in ["sales", "conversions"]:
        cvr_level = {
            "Meta (FB + IG)":    0.035,
            "TikTok Ads":        0.028,
            "Google Search":     0.050,
            "YouTube Ads":       0.015,
            "Spotify Ads":       0.012,
            "Twitter/X Ads":     0.018,
            "Snapchat Ads":      0.020,
        }
    elif goal == "leads":
        cvr_level = {
            "Meta (FB + IG)":    0.060,
            "TikTok Ads":        0.045,
            "Google Search":     0.080,
            "YouTube Ads":       0.030,
            "Spotify Ads":       0.020,
            "Twitter/X Ads":     0.030,
            "Snapchat Ads":      0.035,
        }
    elif goal == "awareness":
        cvr_level = {
            p: 0.005 for p in PLATFORMS
        }
    else:  # traffic
        cvr_level = {
            "Meta (FB + IG)":    0.015,
            "TikTok Ads":        0.013,
            "Google Search":     0.025,
            "YouTube Ads":       0.008,
            "Spotify Ads":       0.006,
            "Twitter/X Ads":     0.009,
            "Snapchat Ads":      0.010,
        }

    # Attach to base
    for p in PLATFORMS:
        base[p]["cvr"] = cvr_level.get(p, 0.01)

    return base

def estimate_performance(niche: str, goal: str, monthly_budget: float, avg_rev_per_conv: float):
    """
    Returns a dict: platform -> metrics (spend, impressions, clicks, conversions, revenue, roi)
    """
    goal = clean_goal(goal)
    params = get_platform_params(goal)
    result = {}

    # Niche tweak: adjust performance a bit by category
    niche = (niche or "").lower()
    if "music" in niche:
        niche_boost = {
            "Spotify Ads": 1.25,
            "TikTok Ads": 1.12,
            "YouTube Ads": 1.08,
        }
    elif "clothing" in niche or "brand" in niche:
        niche_boost = {
            "Meta (FB + IG)": 1.12,
            "TikTok Ads": 1.10,
            "Snapchat Ads": 1.08,
        }
    elif "home" in niche or "care" in niche:
        niche_boost = {
            "Google Search": 1.18,
            "Meta (FB + IG)": 1.10,
        }
    else:
        niche_boost = {}

    for p in PLATFORMS:
        share = params[p]["share"]
        cpm = params[p]["cpm"]
        ctr = params[p]["ctr"]
        cvr = params[p]["cvr"]

        spend = monthly_budget * share
        if spend <= 0 or cpm <= 0:
            impressions = clicks = conversions = revenue = roi = 0.0
        else:
            impressions = (spend / cpm) * 1000.0
            clicks = impressions * ctr
            conversions = clicks * cvr

            # niche-specific boost on conversions
            boost = niche_boost.get(p, 1.0)
            conversions *= boost

            revenue = conversions * avg_rev_per_conv
            roi = (revenue - spend) / spend if spend > 0 else 0.0

        result[p] = {
            "spend": spend,
            "impressions": impressions,
            "estimated_reach": impressions * 0.7,  # simple reach approximation
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue,
            "roi": roi,
        }

    return result

def build_platform_strategy(niche: str, goal: str, country_label: str):
    """
    High-level plan per platform: objective, audience notes, creative notes.
    """
    goal = clean_goal(goal)
    strategies = {}

    for p in PLATFORMS:
        if p == "Meta (FB + IG)":
            objective = {
                "sales": "Sales / Conversions",
                "conversions": "Sales / Conversions",
                "leads": "Leads",
                "awareness": "Reach",
                "traffic": "Traffic",
            }[goal]
            audience = f"Custom + lookalikes based on {niche} engagers; {country_label} plus top cities."
            creative = "Mixed: short videos, carousels, and UGC-style creatives tailored to niche."
        elif p == "TikTok Ads":
            objective = "Video Views" if goal in ["awareness", "traffic"] else "Conversions"
            audience = f"Interest + behavior segments in {country_label} around {niche} trends."
            creative = "Vertical, sound-on, trend-aware videos with clear hook in first 2 seconds."
        elif p == "Google Search":
            objective = "Leads" if goal in ["leads", "conversions", "sales"] else "Traffic"
            audience = f"High intent queries for {niche}; geo-targeted to {country_label}."
            creative = "Responsive search ads + strong site links, callouts, and extensions."
        elif p == "YouTube Ads":
            objective = "Awareness" if goal == "awareness" else "Conversions"
            audience = f"In-market and custom intent audiences related to {niche} in {country_label}."
            creative = "6–15s skippable/non-skippable video, strong branding and call-to-action."
        elif p == "Spotify Ads":
            objective = "Awareness"
            audience = f"{niche} listeners / genres in {country_label}, day-parted to active listening."
            creative = "30s audio spots + companion banners, clear CTA in script."
        elif p == "Twitter/X Ads":
            objective = "Engagement" if goal in ["awareness", "traffic"] else "Website Conversions"
            audience = f"People following or engaging with {niche} topics and creators in {country_label}."
            creative = "Short punchy copy, 1–2 strong hooks per tweet, optional video or image."
        else:  # Snapchat Ads
            objective = "Awareness" if goal == "awareness" else "Conversions"
            audience = f"Younger audiences (13–34) interested in {niche} in {country_label}."
            creative = "Full-screen vertical snaps, quick storytelling and swipe-up CTA."

        strategies[p] = {
            "objective": objective,
            "audience": audience,
            "creative": creative,
        }

    return strategies

# ==========================
# Optional: Google Trends helper
# ==========================

def get_trends(seed_terms, geo="US", timeframe="today 12-m", gprop=""):
    """
    Wraps pytrends; returns dict with:
    - interest_over_time (DataFrame or None)
    - by_region (DataFrame or None)
    - related_suggestions (list)
    """
    if not HAS_TRENDS or not seed_terms:
        return {"interest_over_time": None, "by_region": None, "related_suggestions": []}

    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(seed_terms, timeframe=timeframe, geo=geo, gprop=gprop)

        out = {"interest_over_time": None, "by_region": None, "related_suggestions": []}

        iot = pytrends.interest_over_time()
        if isinstance(iot, pd.DataFrame) and not iot.empty:
            if "isPartial" in iot.columns:
                iot = iot.drop(columns=["isPartial"])
            out["interest_over_time"] = iot

        reg = pytrends.interest_by_region(resolution="REGION", inc_low_vol=True, inc_geo_code=True)
        if isinstance(reg, pd.DataFrame) and not reg.empty:
            out["by_region"] = reg

        rq = pytrends.related_queries()
        suggestions = []
        if isinstance(rq, dict):
            for term, buckets in rq.items():
                for key in ("top", "rising"):
                    df = buckets.get(key)
                    if isinstance(df, pd.DataFrame) and "query" in df.columns:
                        suggestions.extend(df["query"].dropna().astype(str).tolist())
        # de-dupe
        seen = set()
        uniq = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                uniq.append(s)
        out["related_suggestions"] = uniq[:100]

        return out
    except Exception as e:
        # Handle rate limiting (429) or any error gracefully
        return {"error": str(e), "interest_over_time": None, "by_region": None, "related_suggestions": []}

# ==========================
# Sidebar: Inputs
# ==========================

with st.sidebar:
    st.subheader("Plan Inputs")

    niche = st.selectbox(
        "Primary Niche",
        ["Music", "Clothing Brand", "Local Home Care"],
        index=0
    )

    goal = st.selectbox(
        "Primary Goal",
        ["sales", "conversions", "leads", "awareness", "traffic"],
        index=2
    )

    monthly_budget = st.number_input("Monthly Ad Budget (USD)", min_value=100.0, value=2500.0, step=100.0)

    avg_rev = st.number_input(
        "Average revenue per conversion (USD)",
        min_value=1.0,
        value=80.0,
        step=5.0,
        help="If this is too low vs. your CPM/CVR, ROI can go negative."
    )

    st.markdown("### Country / Region")
    country_choice = st.selectbox(
        "Main region",
        ["Worldwide", "United States (US)", "Canada (CA)", "United Kingdom (GB)", "Custom"],
        index=0
    )
    if country_choice == "Custom":
        country_label = st.text_input("Custom country or region label", value="US / Global")
    elif country_choice == "Worldwide":
        country_label = "Worldwide"
    else:
        country_label = country_choice

    st.markdown("### Google Trends (optional)")
    if HAS_TRENDS:
        use_trends = st.checkbox("Use Google Trends insights", value=False)
        trend_geo = st.text_input("Trends Geo (e.g. US, GB, WORLD)", value="WORLD")
        trend_kw_raw = st.text_area(
            "Trend seed keywords (comma or new lines)",
            placeholder="trap beats, streetwear, home care services"
        )
    else:
        use_trends = False
        trend_geo = "WORLD"
        trend_kw_raw = ""
        st.info("Install `pytrends` to enable Google Trends: `pip install pytrends`")

    run = st.button("Generate Strategic Plan")

# ==========================
# Main: Results
# ==========================

if not run:
    st.info("👈 Set your niche, goal, budget, and then click **Generate Strategic Plan**.")
else:
    # 1) Calculate estimates
    perf = estimate_performance(niche, goal, monthly_budget, avg_rev)
    strat = build_platform_strategy(niche, goal, country_label)

    st.subheader("📊 High-Level Summary")

    # Build summary table
    rows = []
    for p in PLATFORMS:
        m = perf[p]
        rows.append({
            "Platform": p,
            "Est. Spend": round(m["spend"], 2),
            "Est. Reach": int(m["estimated_reach"]),
            "Est. Clicks": int(m["clicks"]),
            "Est. Conversions": int(m["conversions"]),
            "Est. Revenue": round(m["revenue"], 2),
            "ROI (%)": round(m["roi"] * 100.0, 1),
        })
    df_summary = pd.DataFrame(rows)
    st.dataframe(df_summary, use_container_width=True)

    total_spend = df_summary["Est. Spend"].sum()
    total_revenue = df_summary["Est. Revenue"].sum()
    total_roi = (total_revenue - total_spend) / total_spend if total_spend > 0 else 0.0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Spend (USD)", f"${total_spend:,.0f}")
    with col2:
        st.metric("Total Revenue (USD)", f"${total_revenue:,.0f}")
    with col3:
        st.metric("Blended ROI", f"{total_roi*100:,.1f}%")

    st.markdown("---")
    st.subheader("🧠 Per-Platform Strategy & Estimates")

    for p in PLATFORMS:
        m = perf[p]
        s = strat[p]
        st.markdown(f"#### {p}")
        with st.container():
            st.markdown('<div class="platform-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"**Objective:** {s['objective']}")
                st.markdown(f"**Audience Direction:** {s['audience']}")
                st.markdown(f"**Creative Direction:** {s['creative']}")
            with c2:
                st.write("**Estimates**")
                st.write(f"- Spend: `${m['spend']:,.0f}` / month")
                st.write(f"- Reach: ~`{int(m['estimated_reach']):,}` people")
                st.write(f"- Clicks: ~`{int(m['clicks']):,}`")
                st.write(f"- Conversions: ~`{int(m['conversions']):,}`")
                st.write(f"- Revenue: `${m['revenue']:,.0f}`")
                st.write(f"- ROI: `{m['roi']*100:,.1f}%`")
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================
    # Optional Google Trends section
    # ==========================

    st.markdown("---")
    st.subheader("📈 Google Trends Insights (Research Mode)")

    if use_trends and HAS_TRENDS:
        # parse seeds
        seeds = []
        if trend_kw_raw.strip():
            for part in trend_kw_raw.replace(",", "\n").split("\n"):
                v = part.strip()
                if v:
                    seeds.append(v)
        if not seeds:
            # if user left empty, auto-seed from niche
            if "music" in niche.lower():
                seeds = ["trap beats", "afrobeats", "independent artist"]
            elif "clothing" in niche.lower():
                seeds = ["streetwear", "vintage clothing", "y2k fashion"]
            else:
                seeds = ["home care services", "elder care", "caregiver near me"]

        with st.spinner("Pulling Google Trends data..."):
            t = get_trends(seeds, geo=trend_geo or "WORLD", timeframe="today 12-m")

        if "error" in t and t["error"]:
            st.warning(f"Trends error: {t['error']}")
        else:
            iot = t.get("interest_over_time")
            reg = t.get("by_region")
            sugg = t.get("related_suggestions", [])

            st.markdown(f"**Seed terms used:** {', '.join(seeds)}")

            if isinstance(iot, pd.DataFrame) and not iot.empty:
                st.write("**Interest over time**")
                st.line_chart(iot)

            if isinstance(reg, pd.DataFrame) and not reg.empty:
                st.write("**Top regions by interest**")
                st.dataframe(reg.head(20))

            if sugg:
                st.write("**Related queries (top + rising)**")
                st.dataframe(pd.DataFrame({"Query": sugg[:50]}))

            st.info("Use these insights to refine your keywords, creatives, and regional targeting on each platform.")
    else:
        st.info("Enable Google Trends in the sidebar (and ensure `pytrends` is installed) to see interest charts and related queries.")

    # ==========================
    # Download plan as JSON
    # ==========================

    st.markdown("---")
    st.subheader("⬇️ Download Plan")

    export_data = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "niche": niche,
        "goal": goal,
        "monthly_budget": monthly_budget,
        "avg_revenue_per_conversion": avg_rev,
        "country_label": country_label,
        "platform_estimates": perf,
        "platform_strategies": strat,
    }

    buf = io.StringIO()
    json.dump(export_data, buf, indent=2)
    st.download_button(
        label="Download JSON Media Plan",
        data=buf.getvalue(),
        file_name="sully_media_plan.json",
        mime="application/json"
    )
