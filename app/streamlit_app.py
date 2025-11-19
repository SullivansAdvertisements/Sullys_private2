# ==========================
# Sully's Media Brain — Meta First Version
# Clean, light theme, logo header, Meta API hook
# ==========================

import os
import sys
from pathlib import Path
from datetime import datetime
import json
import io

import requests
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# --------------------------
# Environment & Meta API setup
# --------------------------
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# Load .env if present (for local dev)
load_dotenv(dotenv_path=ROOT / ".env")

META_TOKEN = os.getenv("META_SYSTEM_USER_TOKEN")       # System user token
META_AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID")   # e.g. "123456789012345"
META_BUSINESS_ID = os.getenv("META_BUSINESS_ID")       # optional for later use

GRAPH_VERSION = "v19.0"


# --------------------------
# Streamlit page config & light theme CSS
# --------------------------
st.set_page_config(
    page_title="Sully's Media Brain",
    page_icon="🧠",
    layout="wide",
)

# Light theme + readable fonts
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f5f7;
    }
    body, .stMarkdown, .stTextInput, .stSelectbox, .stNumberInput, .stTextArea {
        color: #111827 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------
# Logo helper
# --------------------------
LOGO_PATH = Path(__file__).with_name("sullivans_logo.png")

def render_header():
    col_logo, col_title = st.columns([1, 3])
    with col_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_column_width=True)
        else:
            st.write(" ")
    with col_title:
        st.markdown(
            "<h1 style='margin-bottom:0.1rem;'>Sully's Media Brain</h1>",
            unsafe_allow_html=True,
        )
        st.caption("Mini media planner & Meta campaign helper — v1")


render_header()
st.markdown("---")


# --------------------------
# Meta performance “brain” (heuristic model)
# --------------------------
def estimate_meta_performance(monthly_budget_usd: float, goal: str, arpc: float) -> dict:
    """
    Simple heuristic model for Meta:
    - Uses rough CPM, CTR, CVR assumptions by goal.
    - Returns impressions, clicks, conversions, revenue, ROI%.
    NOT real-time official data, just a planning estimate.
    """
    # CPM (cost per 1,000 impressions), CTR, CVR assumptions by goal
    goal_key = goal.lower()
    if goal_key == "awareness":
        cpm = 4.0
        ctr = 0.005   # 0.5%
        cvr = 0.003   # 0.3%
    elif goal_key == "traffic":
        cpm = 6.0
        ctr = 0.010   # 1.0%
        cvr = 0.010   # 1.0%
    elif goal_key == "leads":
        cpm = 8.0
        ctr = 0.015   # 1.5%
        cvr = 0.030   # 3.0%
    elif goal_key == "sales":
        cpm = 10.0
        ctr = 0.020   # 2.0%
        cvr = 0.035   # 3.5%
    else:
        # default conservative
        cpm = 8.0
        ctr = 0.010
        cvr = 0.015

    spend = max(monthly_budget_usd, 0.0)
    impressions = (spend / cpm) * 1000 if cpm > 0 else 0
    clicks = impressions * ctr
    conversions = clicks * cvr

    revenue = conversions * max(arpc, 0.0)
    roi_pct = None
    if spend > 0:
        roi_pct = (revenue - spend) / spend * 100.0

    return {
        "cpm": cpm,
        "ctr": ctr,
        "cvr": cvr,
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "spend": spend,
        "revenue": revenue,
        "roi_pct": roi_pct,
    }


def build_meta_campaign_blueprint(niche: str, goal: str, geo_label: str) -> dict:
    """Return a simple structured blueprint for how the campaign should look."""
    niche_key = niche.lower()
    goal_key = goal.lower()

    if niche_key.startswith("music"):
        base_audience = "17–34, interests in rap/hip-hop, streaming platforms, similar artists"
        creatives = [
            "15s vertical video with hook in first 2s, captions on",
            "Album art + headline promoting single/EP",
            "Reels using behind-the-scenes clips or concert footage",
        ]
    elif "clothing" in niche_key:
        base_audience = "18–34, streetwear/fashion interests, lookalike of purchasers, IG Shop engaged"
        creatives = [
            "UGC-style try-on video",
            "Carousel of best sellers",
            "Reels with outfit transitions and trending audio",
        ]
    else:
        # Local home care default
        base_audience = "35+, caregivers/family decision makers, interests in senior care, healthcare"
        creatives = [
            "Testimonial video from families",
            "Single image with clear value proposition and local focus",
            "Lead form ad with simple qualifying questions",
        ]

    objective_map = {
        "awareness": "REACH",
        "traffic": "TRAFFIC",
        "leads": "LEAD_GENERATION",
        "sales": "CONVERSIONS",
    }
    objective = objective_map.get(goal_key, "TRAFFIC")

    return {
        "campaign_name": f"{niche.title()} | {goal.title()} | {geo_label}",
        "objective": objective,
        "geo": geo_label,
        "recommended_structure": {
            "campaigns": 1,
            "ad_sets": 2,
            "ads_per_set": 3,
            "audience_notes": base_audience,
            "creative_ideas": creatives,
        },
    }


# --------------------------
# Meta API integration helpers
# --------------------------
def meta_api_available() -> bool:
    return bool(META_TOKEN and META_AD_ACCOUNT_ID)


def create_meta_campaign_api(blueprint: dict) -> dict:
    """
    Creates a PAUSED campaign in Meta Ads if credentials are configured.
    Returns a dict with either {"success": True, "id": "..."} or {"success": False, "error": "..."}.
    """
    if not meta_api_available():
        return {
            "success": False,
            "error": "META_SYSTEM_USER_TOKEN or META_AD_ACCOUNT_ID not set in environment/.env/Streamlit secrets.",
        }

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/act_{META_AD_ACCOUNT_ID}/campaigns"
    params = {
        "access_token": META_TOKEN,
        "name": blueprint["campaign_name"],
        "objective": blueprint["objective"],
        "status": "PAUSED",  # always create PAUSED for safety
        "special_ad_categories": "[]",
    }

    try:
        resp = requests.post(url, data=params, timeout=15)
        data = resp.json()
        if resp.status_code == 200 and "id" in data:
            return {"success": True, "id": data["id"], "raw": data}
        else:
            return {
                "success": False,
                "error": f"Meta API error {resp.status_code}: {data}",
            }
    except Exception as e:
        return {"success": False, "error": f"Request exception: {e}"}


# --------------------------
# Sidebar — inputs
# --------------------------
with st.sidebar:
    st.subheader("Campaign Inputs")

    niche = st.selectbox(
        "Niche",
        ["Music Artist", "Clothing Brand", "Local Home Care"],
    )

    primary_goal = st.selectbox(
        "Primary Goal",
        ["Awareness", "Traffic", "Leads", "Sales"],
    )

    monthly_budget = st.number_input(
        "Monthly Ad Budget (USD)",
        min_value=50.0,
        value=1000.0,
        step=50.0,
    )

    avg_revenue_per_conversion = st.number_input(
        "Avg revenue per conversion/customer (USD)",
        min_value=1.0,
        value=80.0,
        step=5.0,
        help="Used for ROI estimation.",
    )

    worldwide = st.checkbox("Worldwide targeting", value=False)
    country = st.text_input(
        "Main Country (e.g. US, CA, GB)",
        value="US",
        disabled=worldwide,
    )

    geo_label = "Worldwide" if worldwide else country

    audience_notes = st.text_area(
        "Audience description (interests, ages, placements)",
        placeholder="e.g. 18–34, IG Reels + Stories, interests in streetwear & hip-hop",
    )

    st.markdown("### Competitor URLs (optional)")
    competitors_text = st.text_area(
        "One per line",
        placeholder="https://competitor1.com\nhttps://competitor2.com",
    )
    competitor_urls = [u.strip() for u in competitors_text.splitlines() if u.strip()]

    actually_call_meta = st.checkbox(
        "Create PAUSED campaign in my Meta ad account (real API call)",
        value=False,
        help="Requires META_SYSTEM_USER_TOKEN and META_AD_ACCOUNT_ID environment variables. "
             "Campaign will be created PAUSED so it won't spend until you enable it.",
    )

    generate = st.button("🚀 Generate Plan")


# --------------------------
# Main content
# --------------------------
if not generate:
    st.info("Set your inputs in the sidebar and click **🚀 Generate Plan** to see estimates and a Meta campaign blueprint.")
    st.stop()

# Build heuristic plan
perf = estimate_meta_performance(monthly_budget, primary_goal, avg_revenue_per_conversion)
blueprint = build_meta_campaign_blueprint(niche, primary_goal, geo_label)

st.subheader("📊 Meta Performance Estimates")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Estimated Impressions", f"{perf['impressions']:,.0f}")
col2.metric("Estimated Clicks", f"{perf['clicks']:,.0f}")
col3.metric("Estimated Conversions", f"{perf['conversions']:,.1f}")
if perf["roi_pct"] is not None:
    col4.metric("Est. ROI", f"{perf['roi_pct']:,.1f}%")
else:
    col4.metric("Est. ROI", "n/a")

st.caption(
    "These are **rough planning estimates**, based on assumed CPM/CTR/CVR for Meta by goal. "
    "They are not official forecasts from Meta."
)

st.subheader("🧱 Meta Campaign Blueprint")

st.write(f"**Campaign Name:** `{blueprint['campaign_name']}`")
st.write(f"**Objective:** `{blueprint['objective']}`")
st.write(f"**Geo:** `{blueprint['geo']}`")
if competitor_urls:
    st.write("**Competitors considered (for strategy only):**")
    for u in competitor_urls:
        st.write(f"- {u}")

st.markdown("#### Recommended Structure")
s = blueprint["recommended_structure"]
st.markdown(
    f"""
- **Campaigns:** {s["campaigns"]}
- **Ad sets per campaign:** {s["ad_sets"]}
- **Ads per ad set:** {s["ads_per_set"]}
- **Audience notes:** {s["audience_notes"]}
    """
)

st.markdown("#### Creative Ideas")
for i, idea in enumerate(s["creative_ideas"], start=1):
    st.write(f"{i}. {idea}")

# ROI details table
st.subheader("💰 Spend & ROI Breakdown")
roi_df = pd.DataFrame(
    [
        {
            "Platform": "Meta (FB + IG)",
            "Goal": primary_goal,
            "Monthly Spend (USD)": round(perf["spend"], 2),
            "Est. Impressions": round(perf["impressions"]),
            "Est. Clicks": round(perf["clicks"]),
            "Est. Conversions": round(perf["conversions"], 1),
            "Est. Revenue (USD)": round(perf["revenue"], 2),
            "Est. ROI (%)": round(perf["roi_pct"], 1) if perf["roi_pct"] is not None else None,
        }
    ]
)
st.dataframe(roi_df, use_container_width=True)

# Optionally call Meta API
st.subheader("🛠 Meta API Execution")

if actually_call_meta:
    if not meta_api_available():
        st.error(
            "Meta API credentials are not configured. "
            "Set `META_SYSTEM_USER_TOKEN` and `META_AD_ACCOUNT_ID` in your `.env` "
            "or Streamlit secrets before enabling this."
        )
    else:
        st.warning(
            "You are about to create a **PAUSED campaign** in your Meta ad account. "
            "It will not spend until you enable it in Ads Manager."
        )
        if st.button("✅ Confirm and create campaign in Meta"):
            result = create_meta_campaign_api(blueprint)
            if result.get("success"):
                st.success(f"Created Meta campaign with ID: {result['id']}")
                st.json(result.get("raw", {}))
            else:
                st.error(f"Meta API call failed: {result.get('error')}")
else:
    st.info(
        "Meta API execution is **off**. Turn on the checkbox in the sidebar if you want "
        "to actually send this campaign to your Meta ad account (it will be created PAUSED)."
    )

# Export plan JSON
st.subheader("📥 Export Plan")
export_payload = {
    "niche": niche,
    "primary_goal": primary_goal,
    "monthly_budget": monthly_budget,
    "avg_revenue_per_conversion": avg_revenue_per_conversion,
    "geo_label": geo_label,
    "audience_notes": audience_notes,
    "competitors": competitor_urls,
    "performance_estimate": perf,
    "meta_blueprint": blueprint,
    "generated_at": datetime.utcnow().isoformat() + "Z",
}

buf = io.StringIO()
json.dump(export_payload, buf, indent=2)
st.download_button(
    "⬇️ Download plan as JSON",
    data=buf.getvalue(),
    file_name="sullys_meta_plan.json",
    mime="application/json",
)
