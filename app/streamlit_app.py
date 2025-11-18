# ==========================
# Sully's Mini Media Planner
# Fresh build: light theme, logo, multi-platform brain
# ==========================

from __future__ import annotations

import io
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd
import streamlit as st
# ==========================================
# Load environment variables (Meta, TikTok, Google, etc.)
# ==========================================
from dotenv import load_dotenv
load_dotenv()

META_TOKEN = os.getenv("META_SYSTEM_USER_TOKEN")
META_BM_ID = os.getenv("META_BUSINESS_ID")
META_AD_ACCOUNT = os.getenv("META_AD_ACCOUNT_ID")

# ---------- CONFIG ----------
APP_TITLE = "Sully's Mini Media Planner"
LOGO_PATH = Path(__file__).with_name("sullivans_logo.png")

PRIMARY_NICHES = [
    "Music / Artists",
    "Clothing Brand / Streetwear",
    "Local Home Care Services",
    "Other / General Business",
]

PRIMARY_GOALS = [
    "Sales / Purchases",
    "Leads / Sign-ups",
    "Brand Awareness",
    "Website Traffic",
]

PLATFORMS = [
    "Meta (FB + IG)",
    "TikTok Ads",
    "Google Search",
    "YouTube Ads",
    "Spotify Ads",
    "Twitter/X Ads",
    "Snapchat Ads",
]

COUNTRY_OPTIONS = [
    "Worldwide",
    "United States",
    "Canada",
    "United Kingdom",
    "Australia",
    "European Union (EU)",
    "Other (manual)",
]

# ---------- ASSUMPTION ENGINE ("BRAIN") ----------

@dataclass
class PlatformAssumptions:
    base_cpm: float        # $ per 1,000 impressions (awareness-ish)
    ctr: float             # % click-through rate
    cvr_sales: float       # % conversion rate for "Sales / Purchases"
    cvr_leads: float       # % conversion rate for "Leads / Sign-ups"
    cvr_awareness: float   # pseudo conversion for awareness goals (engaged users)
    cvr_traffic: float     # % users who go deep on site for traffic goals


# These are heuristic, average “good” account numbers.
# You can tweak them later inside the app if you want.
PLATFORM_DEFAULTS: Dict[str, PlatformAssumptions] = {
    "Meta (FB + IG)": PlatformAssumptions(
        base_cpm=6.0, ctr=1.2, cvr_sales=2.5, cvr_leads=5.0, cvr_awareness=8.0, cvr_traffic=3.5
    ),
    "TikTok Ads": PlatformAssumptions(
        base_cpm=4.0, ctr=1.5, cvr_sales=1.8, cvr_leads=4.0, cvr_awareness=10.0, cvr_traffic=4.0
    ),
    "Google Search": PlatformAssumptions(
        base_cpm=12.0, ctr=4.0, cvr_sales=5.0, cvr_leads=10.0, cvr_awareness=0.5, cvr_traffic=7.0
    ),
    "YouTube Ads": PlatformAssumptions(
        base_cpm=5.0, ctr=0.9, cvr_sales=1.5, cvr_leads=3.0, cvr_awareness=6.0, cvr_traffic=2.5
    ),
    "Spotify Ads": PlatformAssumptions(
        base_cpm=7.0, ctr=0.5, cvr_sales=1.0, cvr_leads=2.0, cvr_awareness=5.0, cvr_traffic=1.5
    ),
    "Twitter/X Ads": PlatformAssumptions(
        base_cpm=5.5, ctr=1.0, cvr_sales=1.3, cvr_leads=3.0, cvr_awareness=4.0, cvr_traffic=2.0
    ),
    "Snapchat Ads": PlatformAssumptions(
        base_cpm=3.5, ctr=1.3, cvr_sales=1.6, cvr_leads=3.5, cvr_awareness=7.0, cvr_traffic=3.0
    ),
}


def get_goal_cvr(ass: PlatformAssumptions, primary_goal: str) -> float:
    """Select the conversion-rate assumption based on primary goal."""
    if primary_goal == "Sales / Purchases":
        return ass.cvr_sales
    if primary_goal == "Leads / Sign-ups":
        return ass.cvr_leads
    if primary_goal == "Brand Awareness":
        return ass.cvr_awareness
    if primary_goal == "Website Traffic":
        return ass.cvr_traffic
    return ass.cvr_sales


def platform_weight_by_niche(niche: str) -> Dict[str, float]:
    """How each platform should roughly share budget for that niche (before user selection)."""
    if niche == "Music / Artists":
        return {
            "Meta (FB + IG)": 0.25,
            "TikTok Ads": 0.25,
            "YouTube Ads": 0.20,
            "Spotify Ads": 0.15,
            "Twitter/X Ads": 0.10,
            "Google Search": 0.03,
            "Snapchat Ads": 0.02,
        }
    if niche == "Clothing Brand / Streetwear":
        return {
            "Meta (FB + IG)": 0.30,
            "TikTok Ads": 0.25,
            "Google Search": 0.15,
            "YouTube Ads": 0.10,
            "Snapchat Ads": 0.10,
            "Twitter/X Ads": 0.07,
            "Spotify Ads": 0.03,
        }
    if niche == "Local Home Care Services":
        return {
            "Google Search": 0.40,
            "Meta (FB + IG)": 0.30,
            "YouTube Ads": 0.15,
            "Twitter/X Ads": 0.05,
            "TikTok Ads": 0.05,
            "Snapchat Ads": 0.03,
            "Spotify Ads": 0.02,
        }
    # Default equal split
    return {p: 1.0 / len(PLATFORMS) for p in PLATFORMS}


def estimate_platform(
    platform: str,
    primary_goal: str,
    monthly_budget: float,
    avg_revenue_per_conv: float,
    niche: str,
    country: str,
) -> Dict[str, float | str]:
    """
    Core brain for a single platform:
    - Allocates budget
    - Estimates impressions, reach, clicks, conversions, CPA, ROAS, ROI
    """
    ass = PLATFORM_DEFAULTS[platform]
    cpm = ass.base_cpm
    ctr = ass.ctr / 100.0
    cvr = get_goal_cvr(ass, primary_goal) / 100.0

    impressions = (monthly_budget / cpm) * 1000 if cpm > 0 else 0.0
    # Very rough: reach ~ 70% of impressions for awareness-type flights
    reach = impressions * 0.7
    clicks = impressions * ctr
    conversions = clicks * cvr

    est_revenue = conversions * avg_revenue_per_conv
    cost = monthly_budget

    cpa = cost / conversions if conversions > 0 else 0.0
    roas = est_revenue / cost if cost > 0 else 0.0
    roi_pct = ((est_revenue - cost) / cost * 100.0) if cost > 0 else 0.0

    return {
        "Platform": platform,
        "Goal": primary_goal,
        "Niche": niche,
        "Country": country,
        "Budget_USD": round(cost, 2),
        "Impressions": round(impressions),
        "Reach": round(reach),
        "Clicks": round(clicks),
        "Conversions": round(conversions, 2),
        "Est_Revenue_USD": round(est_revenue, 2),
        "CPA_USD": round(cpa, 2) if cpa else 0.0,
        "ROAS": round(roas, 2),
        "ROI_%": round(roi_pct, 1),
    }


def build_campaign_structure(platform: str, primary_goal: str, niche: str) -> List[str]:
    """
    High-level recommended campaign structure per platform.
    This is text only for now, not API calls.
    """
    items: List[str] = []

    if platform == "Meta (FB + IG)":
        if primary_goal in ("Sales / Purchases", "Leads / Sign-ups"):
            items.extend([
                "1 x Prospecting campaign (Advantage+ or Sales objective)",
                "1 x Retargeting campaign (Custom audiences: engagers + website visitors)",
                "Ad sets split by: top geos, age buckets, and key interests",
                "Use 3–5 creatives per ad set: UGC, testimonial, product demo, carousel",
            ])
        elif primary_goal == "Brand Awareness":
            items.extend([
                "1 x Awareness campaign (Reach or Awareness objective)",
                "Broad targeting with frequency cap, creative testing for hooks",
            ])
        else:  # Traffic
            items.extend([
                "1 x Traffic campaign, auto placements, traffic to LP / smartlink",
                "Exclude converters, optimize for Landing Page Views",
            ])

    elif platform == "TikTok Ads":
        items.extend([
            "Campaign objective aligned to: Video Views / Traffic / Conversions",
            "3–6 short-form creatives (9–15s) with strong hooks in first 2 seconds",
            "Use broad interest stacks and let learning phase optimize",
        ])

    elif platform == "Google Search":
        items.extend([
            "1–3 Search campaigns grouped by intent: Brand, Core Non-Brand, Competitors",
            "Exact + Phrase for high-intent queries, Broad with smart bidding for scale",
            "Structured ad groups with tight keyword themes, RSA + strong ad assets",
        ])

    elif platform == "YouTube Ads":
        items.extend([
            "1 x Awareness + 1 x Action campaign (In-Stream Skippable)",
            "Target custom segments (search terms, URLs) plus remarketing audiences",
        ])

    elif platform == "Spotify Ads":
        items.extend([
            "1–2 Audio campaigns targeting music tastes, interests, and locations",
            "Include companion display where possible; clear CTA in the script",
        ])

    elif platform == "Twitter/X Ads":
        items.extend([
            "Campaign for engagement/website clicks based on goal",
            "Target by keywords, handles, and lookalikes; rotate creatives weekly",
        ])

    elif platform == "Snapchat Ads":
        items.extend([
            "1 x Prospecting and 1 x Retargeting campaign",
            "Top Snap + Story ads with short, vertical creatives and bold CTA",
        ])

    # Add a generic safety note
    items.append("Set up proper pixel/conversion tracking before scaling budgets.")
    return items


# ---------- UI LAYOUT ----------

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧠",
    layout="wide",
)

# Light theme / basic CSS for readability
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f7fb;
        color: #111827;
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3 {
        color: #111827;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header with logo + title
header_col1, header_col2 = st.columns([1, 4])
with header_col1:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)
with header_col2:
    st.title(APP_TITLE)
    st.caption("Multi-platform strategy + reach/conversion/ROI estimator for Meta, TikTok, Google, YouTube, Spotify, X, Snapchat")


# ---------- SIDEBAR: INPUTS ----------

with st.sidebar:
    st.subheader("🧩 Planner Inputs")

    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=160)

    niche = st.selectbox("Niche / Vertical", PRIMARY_NICHES, index=0)
    primary_goal = st.selectbox("Primary Goal", PRIMARY_GOALS, index=0)

    monthly_budget = st.number_input(
        "Total Monthly Ad Budget (USD)",
        min_value=100.0,
        value=3000.0,
        step=100.0,
    )

    avg_rev_per_conv = st.number_input(
        "Avg Revenue per Conversion (USD)",
        min_value=1.0,
        value=80.0,
        step=5.0,
        help="For sales: AOV. For leads: estimated LTV per lead that becomes a customer.",
    )

    country_choice = st.selectbox("Target Country / Region", COUNTRY_OPTIONS, index=0)
    if country_choice == "Other (manual)":
        country = st.text_input("Enter country/region name", value="Worldwide")
    else:
        country = country_choice

    selected_platforms = st.multiselect(
        "Platforms to include",
        PLATFORMS,
        default=PLATFORMS,
    )

    st.markdown("---")
    run = st.button("🚀 Generate Strategic Plan", type="primary")


# ---------- MAIN LOGIC ----------

if not run:
    st.info(
        "Set your niche, goal, budget, and platforms in the sidebar, then click **“🚀 Generate Strategic Plan”**."
    )
    st.stop()

# Compute platform budgets using niche weights
weights = platform_weight_by_niche(niche)
# Filter to selected platforms only
weights = {p: w for p, w in weights.items() if p in selected_platforms}

if not weights:
    st.error("Please select at least one platform in the sidebar.")
    st.stop()

# Normalize weights
total_w = sum(weights.values())
if total_w <= 0:
    weights = {p: 1.0 / len(weights) for p in weights}
else:
    weights = {p: w / total_w for p, w in weights.items()}

rows: List[Dict[str, float | str]] = []
for platform, w in weights.items():
    plat_budget = monthly_budget * w
    row = estimate_platform(
        platform=platform,
        primary_goal=primary_goal,
        monthly_budget=plat_budget,
        avg_revenue_per_conv=avg_rev_per_conv,
        niche=niche,
        country=country,
    )
    rows.append(row)

df = pd.DataFrame(rows)

# ---------- OVERVIEW TABLE ----------

st.subheader("📊 Platform Overview — Estimates")

st.caption("These are model-based estimates, not live API data. Use as a planning starting point.")
st.dataframe(
    df[
        [
            "Platform",
            "Budget_USD",
            "Impressions",
            "Reach",
            "Clicks",
            "Conversions",
            "CPA_USD",
            "Est_Revenue_USD",
            "ROAS",
            "ROI_%",
        ]
    ],
    use_container_width=True,
)

total_cost = df["Budget_USD"].sum()
total_rev = df["Est_Revenue_USD"].sum()
overall_roas = total_rev / total_cost if total_cost > 0 else 0.0
overall_roi = (total_rev - total_cost) / total_cost * 100.0 if total_cost > 0 else 0.0

st.markdown(
    f"""
**Total Monthly Spend:** ${total_cost:,.0f}  
**Estimated Revenue:** ${total_rev:,.0f}  
**Overall ROAS:** {overall_roas:,.2f}x  
**Overall ROI:** {overall_roi:,.1f}%
"""
)

if avg_rev_per_conv < 80:
    st.warning(
        "Your average revenue per conversion is relatively low. "
        "If estimated CPA is higher than your revenue per customer, ROI will be negative. "
        "You can increase AOV, improve conversion rate, or lower CPMs/CPAs to fix that."
    )

# ---------- PER-PLATFORM DETAILS ----------

st.subheader("🧠 Strategic Breakdown by Platform")

for platform in df["Platform"]:
    plat_data = df[df["Platform"] == platform].iloc[0].to_dict()
    with st.expander(f"{platform} — {primary_goal} plan", expanded=False):
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(
                f"""
**Goal:** {primary_goal}  
**Monthly Budget:** ${plat_data['Budget_USD']:,.0f}  
**Est. Impressions:** {plat_data['Impressions']:,.0f}  
**Est. Reach:** {plat_data['Reach']:,.0f}  
**Est. Clicks:** {plat_data['Clicks']:,.0f}  
**Est. Conversions:** {plat_data['Conversions']:,.2f}  
**Est. CPA:** ${plat_data['CPA_USD']:,.2f}  
**Est. ROAS:** {plat_data['ROAS']:,.2f}x  
**Est. ROI:** {plat_data['ROI_%']:,.1f}%
"""
            )
        with c2:
            st.markdown("**Recommended Campaign Structure**")
            items = build_campaign_structure(platform, primary_goal, niche)
            st.markdown("\n".join([f"- {it}" for it in items]))

# ---------- EXPORT PLAN ----------

st.subheader("⬇️ Export Plan")

ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
export_name = f"sully_media_plan_{ts}.json"

export_payload = {
    "generated_at": ts,
    "niche": niche,
    "goal": primary_goal,
    "country": country,
    "monthly_budget_usd": monthly_budget,
    "avg_revenue_per_conversion_usd": avg_rev_per_conv,
    "platforms": rows,
    "overall": {
        "total_cost": float(total_cost),
        "total_revenue": float(total_rev),
        "overall_roas": float(overall_roas),
        "overall_roi_pct": float(overall_roi),
    },
}

buf = io.StringIO()
json.dump(export_payload, buf, indent=2)
st.download_button(
    label="Download full plan as JSON",
    data=buf.getvalue(),
    file_name=export_name,
    mime="application/json",
)

st.info(
    "You can feed this JSON into separate scripts that actually create campaigns via each platform's API "
    "(Meta Marketing API, Google Ads API, TikTok Marketing API, Spotify Ad Studio, X Ads, Snapchat Ads)."
)
