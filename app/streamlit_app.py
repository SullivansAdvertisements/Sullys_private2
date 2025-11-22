# ==========================
# Sully's Super Media Planner (Meta + Trends)
# Clean full replacement
# ==========================

import os
import sys
import base64
from pathlib import Path
from datetime import datetime
import io
import json

import streamlit as st
import pandas as pd

# ---------- Optional: Google Trends ----------
try:
    from pytrends.request import TrendReq
    HAS_TRENDS = True
except ImportError:
    HAS_TRENDS = False

# ---------- Optional: Meta Marketing API ----------
try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.campaign import Campaign
    from facebook_business.adobjects.adset import AdSet
    from facebook_business.adobjects.adcreative import AdCreative
    from facebook_business.adobjects.ad import Ad
    HAS_META_SDK = True
except ImportError:
    HAS_META_SDK = False


# ==========================
# Basic config
# ==========================

st.set_page_config(
    page_title="Sully's Super Media Planner",
    page_icon="🌺",
    layout="wide",
)

APP_DIR = Path(__file__).resolve().parent
HEADER_BG = APP_DIR / "header_bg.png"
SIDEBAR_BG = APP_DIR / "sidebar_bg.png"
LOGO_PATH = APP_DIR / "sullivans_logo.png"


# ==========================
# UI helpers: CSS for header/sidebar/logo
# ==========================

def _img_to_base64(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        data = path.read_bytes()
        return base64.b64encode(data).decode("utf-8")
    except Exception:
        return None


def inject_layout_css():
    header_b64 = _img_to_base64(HEADER_BG)
    sidebar_b64 = _img_to_base64(SIDEBAR_BG)

    header_css = ""
    if header_b64:
        header_css = f"""
        .app-header {{
            background-image: url("data:image/png;base64,{header_b64}");
            background-size: cover;
            background-position: center;
            padding: 1.2rem 1.5rem;
            border-radius: 0 0 18px 18px;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        """

    sidebar_css = ""
    if sidebar_b64:
        sidebar_css = f"""
        [data-testid="stSidebar"]] {{
            background-image: url("data:image/png;base64,{sidebar_b64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        [data-testid="stSidebar"] * {{
            color: #ffffff !important;
        }}
        """

    css = f"""
    <style>
    .stApp {{
        background-color: #f4f5fb;
    }}
    {header_css}
    {sidebar_css}
    .app-title {{
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffffff;
        text-shadow: 0 0 6px rgba(0,0,0,0.6);
    }}
    .app-subtitle {{
        font-size: 0.9rem;
        color: #f9f9ff;
    }}
    .metric-card {{
        background: #ffffff;
        padding: 1rem 1.2rem;
        border-radius: 1rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
        border: 1px solid rgba(148, 163, 184, 0.3);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header():
    inject_layout_css()
    logo_col, text_col = st.columns([1, 4])
    with logo_col:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_column_width=True)
    with text_col:
        st.markdown('<div class="app-title">Sully’s Super Media Planner</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="app-subtitle">'
            'AI-assisted planning for Meta, powered by Google Trends & your strategy.'
            '</div>',
            unsafe_allow_html=True,
        )


# ==========================
# Google Trends helper
# ==========================

if HAS_TRENDS:
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_trends(seed_terms, geo="US", timeframe="today 12-m", gprop=""):
        """
        Minimal Google Trends wrapper.
        Returns dict with keys:
          - interest_over_time (df)
          - by_region (df)
          - related_suggestions (list)
        """
        if not seed_terms:
            return {}

        try:
            pytrends = TrendReq(hl="en-US", tz=360)
            pytrends.build_payload(seed_terms, timeframe=timeframe, geo=geo, gprop=gprop)

            out = {}

            # Interest over time
            iot = pytrends.interest_over_time()
            if isinstance(iot, pd.DataFrame) and not iot.empty:
                if "isPartial" in iot.columns:
                    iot = iot.drop(columns=["isPartial"])
                out["interest_over_time"] = iot

            # Interest by region
            reg = pytrends.interest_by_region(
                resolution="REGION",
                inc_low_vol=True,
                inc_geo_code=True,
            )
            if isinstance(reg, pd.DataFrame) and not reg.empty:
                first = seed_terms[0]
                if first in reg.columns:
                    reg = reg.sort_values(first, ascending=False)
                out["by_region"] = reg

            # Related queries
            rq = pytrends.related_queries()
            suggestions = []
            if isinstance(rq, dict):
                for term, buckets in rq.items():
                    for key in ("top", "rising"):
                        df = buckets.get(key)
                        if isinstance(df, pd.DataFrame) and "query" in df.columns:
                            suggestions.extend(df["query"].dropna().astype(str).tolist())
            seen = set()
            uniq = []
            for s in suggestions:
                if s not in seen:
                    seen.add(s)
                    uniq.append(s)
            out["related_suggestions"] = uniq[:100]

            return out
        except Exception as e:
            # 429 and other errors are shown here
            return {"error": str(e)}
else:
    def get_trends(seed_terms, geo="US", timeframe="today 12-m", gprop=""):
        return {"error": "pytrends not installed"}


# ==========================
# Simple "brain" to generate a plan
# ==========================

def generate_simple_strategy(niche, budget, goal, geo, competitors, trends_info):
    """
    Lightweight strategy generator:
    - Uses niche, goal, budget
    - Mixes in Google Trends related_suggestions (if any)
    """
    base_keywords = {
        "music": ["new music", "independent artist", "spotify playlist", "rap music", "afrobeats"],
        "clothing": ["streetwear", "hoodies", "graphic tees", "vintage clothing", "sneaker drops"],
        "homecare": ["home care services", "senior care", "in home caregiver", "alzheimers care"],
        "consignment": ["consignment shop", "resell clothing", "thrift store near me"],
    }
    niche_key = "music"
    if "cloth" in niche.lower():
        niche_key = "clothing"
    elif "home" in niche.lower():
        niche_key = "homecare"
    elif "consign" in niche.lower():
        niche_key = "consignment"

    kws = list(base_keywords.get(niche_key, []))

    # Trends suggestions
    if trends_info and isinstance(trends_info, dict):
        rel = trends_info.get("related_suggestions") or []
        for q in rel[:20]:
            if q not in kws:
                kws.append(q)

    # Very simple platform priorities for Meta
    meta_focus = {
        "awareness": "Broad video + image ads focused on story & brand.",
        "traffic": "Feed + Reels link ads to your best-performing pages.",
        "conversions": "Retarget site visitors & warm audiences with strong offers.",
        "sales": "Catalog/Shop ads (if ecom) and bottom-of-funnel remarketing.",
        "leads": "Lead forms with simple questions and clear value exchange.",
    }
    goal_key = goal.lower()
    if goal_key not in meta_focus:
        goal_key = "awareness"

    plan = {
        "geo": geo,
        "keywords": kws,
        "meta": {
            "objective_note": meta_focus[goal_key],
            "daily_budget_hint": round(float(budget) / 30, 2),
        },
        "competitors": competitors,
    }
    return plan


# ==========================
# Meta API helper
# ==========================

def map_goal_to_meta_objective(goal: str) -> str:
    """
    Map user goal to Meta OUTCOME_* objective.
    These match the newer Meta requirement.
    """
    g = (goal or "").lower()
    if "lead" in g:
        return "OUTCOME_LEADS"
    if "sale" in g or "conversion" in g or "purchase" in g:
        return "OUTCOME_SALES"
    if "traffic" in g or "click" in g:
        return "OUTCOME_TRAFFIC"
    if "app" in g:
        return "OUTCOME_APP_PROMOTION"
    if "engage" in g:
        return "OUTCOME_ENGAGEMENT"
    # default
    return "OUTCOME_AWARENESS"


def map_goal_to_meta_optimization(goal: str) -> str:
    g = (goal or "").lower()
    if "lead" in g:
        return "LEAD_GENERATION"
    if "sale" in g or "conversion" in g or "purchase" in g:
        return "CONVERSIONS"
    if "traffic" in g or "click" in g:
        return "LINK_CLICKS"
    if "engage" in g:
        return "POST_ENGAGEMENT"
    return "REACH"


def create_meta_campaign_flow(goal: str, budget: float, country_code: str, landing_url: str, plan_keywords: list[str]) -> dict:
    """
    Creates: Campaign -> Ad Set -> Ad Creative -> Ad
    Uses real Meta Marketing API *if* SDK and creds exist.
    Returns a dict with 'ok' and 'details' or 'error'.
    """
    if not HAS_META_SDK:
        return {"ok": False, "error": "facebook_business SDK not installed (add 'facebook-business' to requirements.txt)."}

    secrets = st.secrets
    required_keys = [
        "META_SYSTEM_USER_TOKEN",
        "META_APP_ID",
        "META_APP_SECRET",
        "META_AD_ACCOUNT_ID",
        "META_PAGE_ID",
    ]
    missing = [k for k in required_keys if k not in secrets or not str(secrets[k]).strip()]
    if missing:
        return {"ok": False, "error": f"Missing Meta credentials in st.secrets: {', '.join(missing)}"}

    access_token = secrets["META_SYSTEM_USER_TOKEN"]
    app_id = secrets["META_APP_ID"]
    app_secret = secrets["META_APP_SECRET"]
    ad_account_id = secrets["META_AD_ACCOUNT_ID"]
    page_id = secrets["META_PAGE_ID"]

    try:
        FacebookAdsApi.init(app_id=app_id, app_secret=app_secret, access_token=access_token)
        account = AdAccount(f"act_{ad_account_id}")

        objective = map_goal_to_meta_objective(goal)
        optimization_goal = map_goal_to_meta_optimization(goal)

        # CAMPAIGN
        campaign_params = {
            "name": f"Sully {goal.title()} – {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            "objective": objective,
            "status": "PAUSED",
            "special_ad_categories": [],
        }
        campaign = account.create_campaign(params=campaign_params)

        # AD SET
        daily_budget_cents = int(max(1, budget / 30) * 100)  # very rough USD → cents
        adset_params = {
            "name": "Sully Auto Ad Set",
            "campaign_id": campaign["id"],
            "daily_budget": daily_budget_cents,
            "billing_event": "IMPRESSIONS",
            "optimization_goal": optimization_goal,
            "status": "PAUSED",
            "promoted_object": {"page_id": page_id},
            "targeting": {
                "geo_locations": {
                    "countries": [country_code] if country_code and country_code != "WORLDWIDE" else [],
                },
            },
        }
        adset = account.create_ad_set(params=adset_params)

        # AD CREATIVE (simple link ad)
        primary_text = f"Discover {', '.join(plan_keywords[:3])} – powered by Sully's strategy."
        creative_params = {
            "name": "Sully Auto Creative",
            "object_story_spec": {
                "page_id": page_id,
                "link_data": {
                    "message": primary_text[:200],
                    "link": landing_url or "https://example.com",
                    "call_to_action": {
                        "type": "LEARN_MORE",
                        "value": {"link": landing_url or "https://example.com"},
                    },
                },
            },
        }
        creative = account.create_ad_creative(params=creative_params)

        # AD
        ad_params = {
            "name": "Sully Auto Ad 1",
            "adset_id": adset["id"],
            "creative": {"creative_id": creative["id"]},
            "status": "PAUSED",
        }
        ad = account.create_ad(params=ad_params)

        return {
            "ok": True,
            "details": {
                "campaign_id": campaign["id"],
                "adset_id": adset["id"],
                "creative_id": creative["id"],
                "ad_id": ad["id"],
            },
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ==========================
# Sidebar (inputs)
# ==========================

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)

    st.markdown("### Planner Settings")

    niche = st.selectbox("Main niche", ["Music", "Clothing brand", "Local Home Care"], index=0)
    goal = st.selectbox("Primary goal", ["Awareness", "Traffic", "Leads", "Sales/Conversions"], index=0)
    budget = st.number_input("Monthly budget (USD)", min_value=100.0, value=1500.0, step=50.0)

    st.markdown("### Country / Geo")
    geo_mode = st.radio("Targeting mode", ["Worldwide", "Single Country"], index=0)
    if geo_mode == "Worldwide":
        country_code = "WORLDWIDE"
    else:
        country_code = st.text_input("2-letter country code (e.g. US, GB, CA)", value="US")

    st.markdown("### Landing page URL")
    landing_url = st.text_input("Main landing URL", value="https://example.com")

    st.markdown("### Competitor URLs")
    comp_text = st.text_area(
        "One per line",
        placeholder="https://competitor1.com\nhttps://competitor2.com",
        height=100,
    )
    competitors = [c.strip() for c in comp_text.split("\n") if c.strip()]

    st.markdown("### Google Trends")
    use_trends = st.checkbox("Use Google Trends to boost keywords", value=True)
    trend_timeframe = st.selectbox("Trends timeframe", ["now 7-d", "today 3-m", "today 12-m", "today 5-y"], index=2)
    trend_geo = "US" if country_code == "WORLDWIDE" else country_code
    trend_seeds_raw = st.text_area(
        "Trend seed terms (optional, comma/line separated)",
        placeholder="streetwear, spotify playlists, home care services",
        height=80,
    )

    run_plan = st.button("Generate Strategy", type="primary")


# ==========================
# Main app
# ==========================

render_header()

st.markdown("")

# --- Trends + plan generation ---

trends_info = {}
trend_seeds = []

if trend_seeds_raw.strip():
    for chunk in trend_seeds_raw.replace(",", "\n").split("\n"):
        v = chunk.strip()
        if v:
            trend_seeds.append(v)
else:
    # auto seeds based on niche
    if "music" in niche.lower():
        trend_seeds = ["new music", "independent artist", "spotify playlist"]
    elif "cloth" in niche.lower():
        trend_seeds = ["streetwear", "hoodies", "graphic tees"]
    else:
        trend_seeds = ["home care", "senior care"]

if run_plan:
    st.info("Building plan with AI + trends…")

if run_plan and use_trends and trend_seeds:
    trends_info = get_trends(trend_seeds, geo=trend_geo, timeframe=trend_timeframe)
    if "error" in trends_info and trends_info["error"]:
        st.warning(f"Trends error: {trends_info['error']}")
        trends_info = {}

plan = {}
if run_plan:
    geo_label = "Worldwide" if country_code == "WORLDWIDE" else country_code
    plan = generate_simple_strategy(
        niche=niche,
        budget=budget,
        goal=goal,
        geo=geo_label,
        competitors=competitors,
        trends_info=trends_info,
    )

# --- Show plan ---

st.subheader("🧠 Strategy Overview")

if not run_plan:
    st.info("Set your niche, goal, budget and click **Generate Strategy** in the sidebar.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Niche**")
        st.write(niche)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Goal**")
        st.write(goal)
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Budget (monthly)**")
        st.write(f"${budget:,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 🔑 Keyword & Topic Ideas")
    if plan.get("keywords"):
        st.dataframe(pd.DataFrame({"Keyword / Topic": plan["keywords"][:100]}))
    else:
        st.write("No keywords yet – try enabling Google Trends or adding seeds.")

    if trends_info and trends_info.get("interest_over_time") is not None:
        st.markdown("### 📈 Google Trends – Interest Over Time")
        st.line_chart(trends_info["interest_over_time"])

    if trends_info and trends_info.get("by_region") is not None:
        st.markdown("### 🌍 Top Regions by Interest")
        st.dataframe(trends_info["by_region"].head(20))


# ==========================
# Meta Campaign Builder
# ==========================

st.markdown("---")
st.subheader("📣 Meta (Facebook + Instagram) Auto Campaign Builder")

if not HAS_META_SDK:
    st.error("facebook_business SDK not installed. Add `facebook-business` to your requirements.txt and redeploy.")
else:
    with st.expander("Meta campaign + ad setup", expanded=True):
        st.markdown(
            "This will create a **campaign, ad set, and ad** in your Meta ad account, "
            "in *PAUSED* status so you can review before spending."
        )
        if st.button("Create Meta Campaign Now"):
            with st.spinner("Creating campaign via Meta API…"):
                keywords_for_ad = plan.get("keywords", []) if plan else trend_seeds
                result = create_meta_campaign_flow(
                    goal=goal,
                    budget=budget,
                    country_code=None if country_code == "WORLDWIDE" else country_code,
                    landing_url=landing_url,
                    plan_keywords=keywords_for_ad,
                )
            if result.get("ok"):
                d = result["details"]
                st.success(
                    f"Meta objects created (PAUSED):\n\n"
                    f"- Campaign ID: `{d['campaign_id']}`\n"
                    f"- Ad Set ID: `{d['adset_id']}`\n"
                    f"- Creative ID: `{d['creative_id']}`\n"
                    f"- Ad ID: `{d['ad_id']}`"
                )
                st.info("Go to Meta Ads Manager, locate these IDs, review settings & turn on when ready.")
            else:
                st.error(f"Meta create error: {result.get('error')}")


st.markdown("---")
st.caption(
    "Next ideas: we can add TikTok Creative Center links, YouTube keyword suggestions, and more once "
    "your Meta + Trends flows feel solid."
)
