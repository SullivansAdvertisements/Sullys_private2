# ==========================
# Sully's Super Media Planner Bot
# ==========================

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import streamlit as st
import pandas as pd
import requests

# Optional: Google Trends
try:
    from pytrends.request import TrendReq
    HAS_TRENDS = True
except ImportError:
    HAS_TRENDS = False

# -------------
# Meta secrets
# -------------
# Set these in .streamlit/secrets.toml or Streamlit Cloud Secrets:
# META_SYSTEM_USER_TOKEN = "EAAX..."
# META_AD_ACCOUNT_ID     = "act_1234567890"
# META_BUSINESS_ID       = "1234567890"
# META_APP_ID            = "..."
# META_APP_SECRET        = "..."
META_TOKEN = st.secrets.get("META_SYSTEM_USER_TOKEN", None)
META_AD_ACCOUNT = st.secrets.get("META_AD_ACCOUNT_ID", None)
META_BUSINESS_ID = st.secrets.get("META_BUSINESS_ID", None)
META_APP_ID = st.secrets.get("META_APP_ID", None)
META_APP_SECRET = st.secrets.get("META_APP_SECRET", None)

# -------------
# Page setup
# -------------
st.set_page_config(
    page_title="Sully's Super Media Planner",
    page_icon="🧠",
    layout="wide",
)

# -------------
# Logo header
# -------------
LOGO_PATH = Path(__file__).with_name("sullivans_logo.png")

cols = st.columns([1, 4])
with cols[0]:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)
with cols[1]:
    st.markdown(
        """
        # Sully's Super Media Planner 🧠  
        *Multi-platform strategy brain for Music, Clothing, and Home Care.*
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# -------------
# Helpers
# -------------
PLATFORMS = [
    "Meta (FB + IG)",
    "TikTok Ads",
    "Google Search",
    "YouTube Ads",
    "Spotify Ads",
    "Twitter/X Ads",
    "Snapchat Ads",
]

GOALS = [
    "awareness",
    "traffic",
    "leads",
    "sales",
]

NICHES = [
    "Music (Artists / Musicians)",
    "Clothing / Streetwear Brands",
    "Local Home Care Services",
    "Other",
]


def safe_split_list(raw: str) -> List[str]:
    if not raw:
        return []
    raw = raw.replace(",", "\n")
    out = []
    seen = set()
    for line in raw.split("\n"):
        v = line.strip()
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def get_default_keywords_for_niche(niche: str) -> List[str]:
    niche = niche.lower()
    if "music" in niche:
        return ["trap beats", "drill music", "spotify playlist", "rap artist", "independent artist"]
    if "clothing" in niche or "streetwear" in niche:
        return ["streetwear", "graphic tees", "hoodies", "sneakerheads", "vintage clothing"]
    if "home care" in niche:
        return ["home care", "senior care", "caregiver services", "in home nursing", "alzheimers care"]
    return ["brand awareness", "online store", "book services online"]


# ---- Google Trends wrapper ----
def fetch_trends(seed_terms: List[str], geo_code: str, timeframe: str = "today 12-m") -> Dict:
    """
    Uses Google Trends via pytrends if installed.
    Returns a dict with keys: interest_over_time (df), by_region (df), related_suggestions (list), error (str|None)
    """
    if not HAS_TRENDS:
        return {"error": "pytrends not installed", "interest_over_time": None, "by_region": None, "related_suggestions": []}
    if not seed_terms:
        return {"error": "No seed terms provided", "interest_over_time": None, "by_region": None, "related_suggestions": []}

    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(seed_terms, timeframe=timeframe, geo=geo_code or "")

        result: Dict = {"error": None}

        iot = pytrends.interest_over_time()
        if isinstance(iot, pd.DataFrame) and not iot.empty:
            if "isPartial" in iot.columns:
                iot = iot.drop(columns=["isPartial"])
            result["interest_over_time"] = iot
        else:
            result["interest_over_time"] = None

        by_region = pytrends.interest_by_region(resolution="REGION", inc_low_vol=True, inc_geo_code=True)
        if isinstance(by_region, pd.DataFrame) and not by_region.empty:
            seed = seed_terms[0]
            if seed in by_region.columns:
                by_region = by_region.sort_values(seed, ascending=False)
            result["by_region"] = by_region
        else:
            result["by_region"] = None

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
        result["related_suggestions"] = uniq[:100]
        return result
    except Exception as e:
        return {"error": str(e), "interest_over_time": None, "by_region": None, "related_suggestions": []}


# ---- Estimation logic ----
CPM_MAP = {  # approximate CPM (USD) for awareness
    "Meta (FB + IG)": 8.0,
    "TikTok Ads": 6.0,
    "Google Search": 12.0,  # we fudge CPM from CPC
    "YouTube Ads": 7.0,
    "Spotify Ads": 9.0,
    "Twitter/X Ads": 7.0,
    "Snapchat Ads": 5.0,
}

# CTR and CVR guesses by goal and platform
CTR_MAP = {
    "awareness": 0.01,
    "traffic": 0.02,
    "leads": 0.015,
    "sales": 0.012,
}

PLATFORM_CTR_BOOST = {
    "Meta (FB + IG)": 1.1,
    "TikTok Ads": 1.2,
    "Google Search": 1.8,
    "YouTube Ads": 1.0,
    "Spotify Ads": 0.7,
    "Twitter/X Ads": 0.9,
    "Snapchat Ads": 1.0,
}

CVR_MAP = {
    "awareness": 0.002,  # conversions/landing-page views
    "traffic": 0.01,
    "leads": 0.05,
    "sales": 0.03,
}

PLATFORM_CVR_BOOST = {
    "Meta (FB + IG)": 1.2,
    "TikTok Ads": 1.1,
    "Google Search": 1.6,
    "YouTube Ads": 0.8,
    "Spotify Ads": 0.7,
    "Twitter/X Ads": 0.7,
    "Snapchat Ads": 0.9,
}


def estimate_platform_metrics(
    platform: str,
    monthly_budget: float,
    goal: str,
    avg_revenue: float,
) -> Dict:
    """
    Estimate reach, clicks, conversions, CPA, ROAS for one platform.
    """
    cpm = CPM_MAP.get(platform, 8.0)
    ctr_base = CTR_MAP.get(goal, 0.01)
    cvr_base = CVR_MAP.get(goal, 0.01)

    ctr = ctr_base * PLATFORM_CTR_BOOST.get(platform, 1.0)
    cvr = cvr_base * PLATFORM_CVR_BOOST.get(platform, 1.0)

    # Avoid ridiculous values
    ctr = min(max(ctr, 0.002), 0.25)
    cvr = min(max(cvr, 0.003), 0.5)

    impressions = (monthly_budget / cpm) * 1000 if cpm > 0 else 0
    clicks = impressions * ctr
    conversions = clicks * cvr

    spent = monthly_budget
    revenue = conversions * avg_revenue
    profit = revenue - spent
    roi = (profit / spent) if spent > 0 else 0.0
    roas = (revenue / spent) if spent > 0 else 0.0

    return {
        "platform": platform,
        "budget": spent,
        "impressions": round(impressions),
        "reach_estimate": round(impressions * 0.6),  # rough: 60% unique
        "clicks": round(clicks),
        "conversions": round(conversions, 1),
        "revenue": round(revenue, 2),
        "profit": round(profit, 2),
        "roi": round(roi, 2),
        "roas": round(roas, 2),
    }


def build_strategy(
    niche: str,
    monthly_budget: float,
    goal: str,
    country: str,
    platforms: List[str],
    avg_revenue: float,
    competitors: List[str],
    trends: Dict,
) -> Dict:
    # Simple budget split per platform by niche
    niche_l = niche.lower()
    weights = {}
    for p in platforms:
        w = 1.0
        if "music" in niche_l:
            if "Spotify" in p or "YouTube" in p or "TikTok" in p or "Meta" in p:
                w = 1.4
        elif "clothing" in niche_l:
            if "Meta" in p or "TikTok" in p or "Snapchat" in p:
                w = 1.4
        elif "home care" in niche_l:
            if "Google Search" in p or "Meta" in p:
                w = 1.5
        weights[p] = w

    total_w = sum(weights.values()) or 1.0
    platform_rows = []
    for p in platforms:
        share = weights[p] / total_w
        platform_budget = monthly_budget * share
        est = estimate_platform_metrics(p, platform_budget, goal, avg_revenue)
        est["budget_share_pct"] = round(share * 100, 1)
        platform_rows.append(est)

    df_platforms = pd.DataFrame(platform_rows)

    overall = {
        "monthly_budget": monthly_budget,
        "niche": niche,
        "goal": goal,
        "country": country,
        "platforms": platforms,
        "total_impressions": int(df_platforms["impressions"].sum()) if not df_platforms.empty else 0,
        "total_conversions": float(df_platforms["conversions"].sum()) if not df_platforms.empty else 0.0,
        "total_revenue": float(df_platforms["revenue"].sum()) if not df_platforms.empty else 0.0,
        "total_profit": float(df_platforms["profit"].sum()) if not df_platforms.empty else 0.0,
    }

    plan = {
        "overall": overall,
        "platform_df": df_platforms,
        "trends": trends,
        "competitors": competitors,
    }
    return plan


# ---- Meta API hook ----
def meta_api_available() -> bool:
    return bool(META_TOKEN and META_AD_ACCOUNT)


def create_meta_campaign(
    name: str,
    objective: str,
    daily_budget_usd: float,
    country: str,
) -> Dict:
    """
    Creates a basic Meta campaign via Marketing API.
    Uses new OUTCOME_* objectives from your error message.
    """
    if not meta_api_available():
        return {"ok": False, "error": "Meta token or ad account missing"}

    ad_account_id = META_AD_ACCOUNT  # e.g. "act_1234567890"
    token = META_TOKEN

    url = f"https://graph.facebook.com/v19.0/{ad_account_id}/campaigns"

    # Convert USD to minor currency units (e.g. cents)
    daily_budget_minor = int(daily_budget_usd * 100)

    payload = {
        "name": name,
        "objective": objective,  # must be one of: OUTCOME_LEADS, OUTCOME_SALES, etc.
        "status": "PAUSED",
        "special_ad_categories": [],
        "daily_budget": daily_budget_minor,
    }

    params = {"access_token": token}

    resp = requests.post(url, data=payload, params=params, timeout=30)
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}

    if resp.status_code >= 300:
        return {"ok": False, "status": resp.status_code, "response": data}
    return {"ok": True, "status": resp.status_code, "response": data}


# ==========================
# Sidebar — Inputs
# ==========================
with st.sidebar:
    st.header("Planning Inputs")

    niche = st.selectbox("Niche", NICHES, index=0)
    primary_goal = st.selectbox("Primary Goal", GOALS, index=0)
    monthly_budget = st.number_input("Monthly Ad Budget (USD)", min_value=100.0, value=2500.0, step=50.0)
    avg_revenue = st.number_input("Avg Revenue Per Customer (USD)", min_value=1.0, value=80.0, step=1.0)

    st.markdown("### Geography")
    country_choice = st.selectbox(
        "Main Country",
        ["Worldwide", "United States", "Canada", "United Kingdom", "Australia", "Other"],
        index=0,
    )
    custom_country = st.text_input("If 'Other', type country/region", value="")

    if country_choice == "Worldwide":
        country_label = "Worldwide"
        trends_geo = ""  # worldwide for pytrends
    elif country_choice == "Other":
        country_label = custom_country or "Custom Region"
        trends_geo = custom_country[:2].upper() if len(custom_country) >= 2 else ""
    else:
        country_label = country_choice
        # rough ISO guess
        mapping = {
            "United States": "US",
            "Canada": "CA",
            "United Kingdom": "GB",
            "Australia": "AU",
        }
        trends_geo = mapping.get(country_choice, "")

    st.markdown("### Platforms")
    selected_platforms = st.multiselect("Platforms to include", PLATFORMS, default=PLATFORMS)

    st.markdown("### Competitor URLs")
    comp_text = st.text_area(
        "One per line",
        placeholder="https://example.com\nhttps://competitor.com\nhttps://artist.com",
        height=80,
    )
    competitors = [c.strip() for c in comp_text.splitlines() if c.strip()]

    st.markdown("### Research Seeds (Google/TikTok/YouTube)")
    seed_text = st.text_area(
        "Trend seed terms (comma/newline). Leave blank to auto-fill by niche.",
        placeholder="trap beats, drill music\nstreetwear\nhome care services",
        height=80,
    )

    trends_timeframe = st.selectbox(
        "Trends timeframe",
        ["now 7-d", "today 3-m", "today 12-m", "today 5-y"],
        index=2,
    )

    st.markdown("---")
    run = st.button("🚀 Generate Strategic Plan", type="primary")


# ==========================
# Main logic
# ==========================
if run:
    # Build seed terms
    seed_terms = safe_split_list(seed_text)
    if not seed_terms:
        seed_terms = get_default_keywords_for_niche(niche)

    trends_data = fetch_trends(seed_terms, trends_geo, timeframe=trends_timeframe)

    plan = build_strategy(
        niche=niche,
        monthly_budget=float(monthly_budget),
        goal=primary_goal,
        country=country_label,
        platforms=selected_platforms or PLATFORMS,
        avg_revenue=float(avg_revenue),
        competitors=competitors,
        trends=trends_data,
    )

    # ==========================
    # Tabs
    # ==========================
    tab_summary, tab_platforms, tab_trends, tab_meta = st.tabs(
        ["📋 Summary", "📊 Platforms", "📈 Trends & Research", "🧷 Meta API"]
    )

    # --- Summary tab ---
    with tab_summary:
        overall = plan["overall"]
        st.subheader("High-Level Plan")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Monthly Budget (USD)", f"${overall['monthly_budget']:,.0f}")
        col2.metric("Estimated Conversions", f"{overall['total_conversions']:.1f}")
        col3.metric("Estimated Revenue", f"${overall['total_revenue']:,.0f}")
        col4.metric("Estimated Profit", f"${overall['total_profit']:,.0f}")

        st.markdown(
            f"""
            **Niche:** {overall['niche']}  
            **Primary Goal:** {overall['goal'].title()}  
            **Country / Region:** {overall['country']}  
            **Platforms:** {", ".join(overall['platforms'])}
            """
        )

        st.markdown("### ROI Snapshot by Platform")
        st.dataframe(plan["platform_df"][[
            "platform", "budget_share_pct", "impressions", "reach_estimate",
            "clicks", "conversions", "revenue", "profit", "roi", "roas"
        ]])

    # --- Platforms tab ---
    with tab_platforms:
        st.subheader("Channel-Level Breakdown")

        st.dataframe(plan["platform_df"])

        st.markdown("""
        **How to use this:**
        - Use reach + conversions to decide which platforms to scale.
        - If ROI is negative for a platform, consider:
          - Improving creative/landing page.
          - Tightening audience.
          - Increasing average revenue per customer (upsells, bundles).
        """)

    # --- Trends & Research tab ---
    with tab_trends:
        st.subheader("Google Trends & Keyword Ideas")

        if trends_data.get("error"):
            st.warning(f"Trends error: {trends_data['error']}")
        else:
            iot = trends_data.get("interest_over_time")
            if isinstance(iot, pd.DataFrame):
                st.write("**Interest Over Time**")
                st.line_chart(iot)

            by_region = trends_data.get("by_region")
            if isinstance(by_region, pd.DataFrame):
                st.write("**Top Regions by Interest**")
                st.dataframe(by_region.head(20))

            suggestions = trends_data.get("related_suggestions", [])
            if suggestions:
                st.write("**Related Rising/Top Queries (use as ad keywords, interests, or video topics)**")
                st.dataframe(pd.DataFrame({"Query": suggestions[:50]}))

        st.markdown("---")
        st.markdown("### Practical Use")
        st.markdown("""
        - **Meta / TikTok / Snapchat**:  
          Use Trends queries as **interest keywords**, reel themes, hook ideas.
        - **Google Search / YouTube**:  
          Use them as **search keywords** and **video titles**.
        - **Spotify / Music**:  
          Use music-related trends to choose **genres**, **moods**, and **playlist themes**.
        """)

    # --- Meta API tab ---
    with tab_meta:
        st.subheader("Meta (FB + IG) Campaign Creator (API Hook)")

        if not meta_api_available():
            st.warning(
                "Meta API not fully configured. Set `META_SYSTEM_USER_TOKEN` and "
                "`META_AD_ACCOUNT_ID` in your Streamlit secrets to enable live campaign creation."
            )
        else:
            st.success("Meta API token and ad account detected.")

        st.markdown("#### Campaign Setup")
        default_campaign_name = f"Sully_{primary_goal}_{niche.replace(' ', '')}_{datetime.utcnow().strftime('%Y%m%d')}"
        mc_name = st.text_input("Campaign Name", value=default_campaign_name)

        objective = st.selectbox(
            "Meta Outcome Objective",
            [
                "OUTCOME_AWARENESS",
                "OUTCOME_TRAFFIC",
                "OUTCOME_ENGAGEMENT",
                "OUTCOME_LEADS",
                "OUTCOME_SALES",
                "OUTCOME_APP_PROMOTION",
            ],
            index=0,
        )

        daily_budget_meta = st.number_input(
            "Daily Budget for this Meta Campaign (USD)",
            min_value=5.0,
            value=float(max(5.0, monthly_budget / 30.0)),
            step=1.0,
        )

        if st.button("🧷 Create Meta Campaign via API"):
            if not meta_api_available():
                st.error("Meta token or Ad Account ID missing in secrets. Cannot call API.")
            else:
                with st.spinner("Calling Meta API..."):
                    result = create_meta_campaign(
                        name=mc_name,
                        objective=objective,
                        daily_budget_usd=daily_budget_meta,
                        country=country_label,
                    )
                if result.get("ok"):
                    st.success(f"Campaign created! Response: {result['response']}")
                else:
                    st.error(f"Meta create error: {result}")

else:
    st.info("👈 Set your inputs in the sidebar and click **'🚀 Generate Strategic Plan'** to get started.")
