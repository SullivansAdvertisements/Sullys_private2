# ==========================
# Sully's Super Media Planner (Meta-first)
# Light theme, header + sidebar background, logo, Meta API
# ==========================

import os
import sys
import base64
from pathlib import Path
from datetime import datetime
import json
import io

import streamlit as st
import pandas as pd
import requests

# Optional: Google Trends (pytrends)
try:
    from pytrends.request import TrendReq
    HAS_TRENDS = True
except ImportError:
    HAS_TRENDS = False

# ---------- PATHS / ASSETS ----------
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

APP_DIR = Path(__file__).resolve().parent
LOGO_PATH = APP_DIR / "sullivans_logo.png"
HEADER_BG_PATH = APP_DIR / "header_bg.png"
SIDEBAR_BG_PATH = APP_DIR / "sidebar_bg.png"


# ---------- META CONFIG HELPERS ----------

def get_meta_config():
    """
    Read Meta credentials from Streamlit secrets or env.
    """
    token = None
    ad_account = None
    app_id = None
    app_secret = None
    business_id = None

    # Prefer st.secrets
    try:
        token = st.secrets.get("META_SYSTEM_USER_TOKEN", None)
        ad_account = st.secrets.get("META_AD_ACCOUNT_ID", None)
        app_id = st.secrets.get("META_APP_ID", None)
        app_secret = st.secrets.get("META_APP_SECRET", None)
        business_id = st.secrets.get("META_BUSINESS_ID", None)
    except Exception:
        pass

    # Fallback to env vars (for local dev)
    token = token or os.getenv("META_SYSTEM_USER_TOKEN")
    ad_account = ad_account or os.getenv("META_AD_ACCOUNT_ID")
    app_id = app_id or os.getenv("META_APP_ID")
    app_secret = app_secret or os.getenv("META_APP_SECRET")
    business_id = business_id or os.getenv("META_BUSINESS_ID")

    return {
        "token": token,
        "ad_account": ad_account,
        "app_id": app_id,
        "app_secret": app_secret,
        "business_id": business_id,
    }


# ---------- STYLING HELPERS ----------

def _img_to_base64(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return base64.b64encode(path.read_bytes()).decode("utf-8")
    except Exception:
        return None


def apply_custom_css():
    """
    Light theme + header background + sidebar background + logo placement.
    """
    header_b64 = _img_to_base64(HEADER_BG_PATH)
    sidebar_b64 = _img_to_base64(SIDEBAR_BG_PATH)

    header_bg_css = ""
    if header_b64:
        header_bg_css = f"""
        .sully-header {{
            background-image: url("data:image/png;base64,{header_b64}");
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
            border-radius: 18px;
            padding: 18px 24px;
            display: flex;
            align-items: center;
            gap: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            margin-bottom: 12px;
        }}
        """

    sidebar_bg_css = ""
    if sidebar_b64:
        sidebar_bg_css = f"""
        [data-testid="stSidebar"] > div:first-child {{
            background-image: url("data:image/png;base64,{sidebar_b64}");
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
        }}
        """

    st.markdown(
        f"""
        <style>
        /* Light-ish base */
        .stApp {{
            background-color: #f5f7fb;
        }}

        {header_bg_css}
        {sidebar_bg_css}

        /* Main body cards */
        .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }}

        /* Sidebar overlay for better readability */
        [data-testid="stSidebar"] {{
            color: #ffffff;
        }}
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stTextInput label,
        [data-testid="stSidebar"] .stNumberInput label,
        [data-testid="stSidebar"] .stTextArea label,
        [data-testid="stSidebar"] .stRadio label {{
            font-weight: 600;
        }}

        .sully-logo {{
            height: 56px;
        }}
        .sully-sidebar-logo {{
            height: 48px;
            margin-bottom: 8px;
        }}
        .sully-title {{
            font-size: 1.6rem;
            font-weight: 800;
            color: #ffffff;
            text-shadow: 0 2px 4px rgba(0,0,0,0.4);
        }}
        .sully-subtitle {{
            font-size: 0.95rem;
            color: #f0f4ff;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------- GOOGLE TRENDS (RESEARCH ONLY, NO FAKE CALCS) ----------

@st.cache_data(ttl=3600, show_spinner=False)
def get_trends(seed_terms, geo="US", timeframe="today 12-m", gprop=""):
    if not HAS_TRENDS or not seed_terms:
        return {"error": "pytrends not installed or no seed terms"}

    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(seed_terms, timeframe=timeframe, geo=geo, gprop=gprop)

        out = {}

        iot = pytrends.interest_over_time()
        if isinstance(iot, pd.DataFrame) and not iot.empty:
            if "isPartial" in iot.columns:
                iot = iot.drop(columns=["isPartial"])
            out["interest_over_time"] = iot

        reg = pytrends.interest_by_region(resolution="REGION", inc_low_vol=True, inc_geo_code=True)
        if isinstance(reg, pd.DataFrame) and not reg.empty:
            first = seed_terms[0]
            if first in reg.columns:
                reg = reg.sort_values(first, ascending=False)
            out["by_region"] = reg

        rq = pytrends.related_queries()
        suggestions = []
        if isinstance(rq, dict):
            for _term, buckets in rq.items():
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
        return {"error": str(e)}


# ---------- META MARKETING API (LIVE CAMPAIGN CREATE) ----------

def create_meta_campaign(name: str, objective: str, status: str = "PAUSED") -> dict:
    """
    Create a Meta (Facebook/Instagram) campaign using Marketing API.
    Uses Marketing API "outcome" objectives (e.g. OUTCOME_AWARENESS, OUTCOME_TRAFFIC, etc.)
    """
    cfg = get_meta_config()
    token = cfg["token"]
    ad_account = cfg["ad_account"]

    if not token or not ad_account:
        return {"ok": False, "error": "Meta token or ad account not configured. Set META_SYSTEM_USER_TOKEN and META_AD_ACCOUNT_ID in secrets."}

    # Allow both "act_xxx" and "xxx"
    if not ad_account.startswith("act_"):
        ad_account_id = f"act_{ad_account}"
    else:
        ad_account_id = ad_account

    url = f"https://graph.facebook.com/v19.0/{ad_account_id}/campaigns"

    payload = {
        "name": name,
        "objective": objective,  # e.g. OUTCOME_AWARENESS, OUTCOME_TRAFFIC, etc.
        "status": status,
        "special_ad_categories": json.dumps([]),
    }

    resp = requests.post(url, data=payload, params={"access_token": token}, timeout=30)

    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}

    if resp.status_code >= 400:
        return {"ok": False, "status": resp.status_code, "response": data}

    return {"ok": True, "status": resp.status_code, "response": data}


# ---------- SIMPLE UTIL ----------

def split_list(raw: str):
    if not raw:
        return []
    parts = []
    for chunk in raw.replace(",", "\n").split("\n"):
        v = chunk.strip()
        if v:
            parts.append(v)
    seen = set()
    out = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


# ==========================
# APP LAYOUT
# ==========================

st.set_page_config(
    page_title="Sully's Super Media Planner",
    page_icon="🌺",
    layout="wide",
)

apply_custom_css()

# ----- HEADER -----
header_logo_b64 = _img_to_base64(LOGO_PATH)
header_html = '<div class="sully-header">'
if header_logo_b64:
    header_html += f'<img class="sully-logo" src="data:image/png;base64,{header_logo_b64}" />'
header_html += """
  <div>
    <div class="sully-title">Sully's Super Media Planner</div>
    <div class="sully-subtitle">Meta-first smart planner with live campaign creation & Google Trends research.</div>
  </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# ----- SIDEBAR -----
with st.sidebar:
    # Sidebar logo
    if LOGO_PATH.exists():
        st.markdown(
            f'<div style="text-align:center;"><img class="sully-sidebar-logo" src="data:image/png;base64,{_img_to_base64(LOGO_PATH)}" /></div>',
            unsafe_allow_html=True,
        )

    st.markdown("### Campaign Inputs")

    niche = st.selectbox("Niche", ["Music", "Clothing brand", "Local home care"], index=0)
    budget_monthly = st.number_input("Monthly budget (USD)", min_value=50.0, value=2000.0, step=50.0)
    primary_goal = st.selectbox(
        "Primary goal",
        ["Awareness", "Traffic", "Engagement", "Leads", "Sales", "App promotion"],
        index=0,
    )

    st.markdown("### Geo Targeting")
    country = st.selectbox(
        "Main country",
        ["Worldwide", "United States", "Canada", "United Kingdom", "Australia", "Germany", "France"],
        index=0,
    )
    extra_cities_raw = st.text_area("Key cities or regions (optional)", placeholder="New York\nLos Angeles\nLondon")

    st.markdown("### Research seeds")
    seed_keywords_raw = st.text_area(
        "Seed keywords (comma/newline)",
        placeholder="trap beats, independent artist, streetwear brand, home care agency",
    )
    competitor_urls_raw = st.text_area(
        "Competitor URLs (one per line)",
        placeholder="https://example-artist.com\nhttps://example-home-care.com",
    )

    st.markdown("### Google Trends")
    use_trends = st.checkbox("Use Google Trends for research", value=True)
    trends_timeframe = st.selectbox("Timeframe", ["now 7-d", "today 3-m", "today 12-m", "today 5-y"], index=2)

    use_meta_live = st.checkbox("Enable live Meta campaign creation", value=False)
    st.caption("Requires valid Meta Marketing API credentials in Streamlit secrets.")

    run = st.button("Generate Plan & (optionally) Create Meta Campaign")


# ----- PREP INPUTS -----
seed_keywords = split_list(seed_keywords_raw)
competitor_urls = [u.strip() for u in competitor_urls_raw.split("\n") if u.strip()]
extra_cities = split_list(extra_cities_raw)

if country == "Worldwide":
    geo_label = "Worldwide"
    trends_geo = ""  # worldwide for pytrends
else:
    geo_label = country
    # Use US, CA, GB, etc. for trends geo where possible
    country_code_map = {
        "United States": "US",
        "Canada": "CA",
        "United Kingdom": "GB",
        "Australia": "AU",
        "Germany": "DE",
        "France": "FR",
    }
    trends_geo = country_code_map.get(country, "")


# ==========================
# MAIN BODY
# ==========================
col_left, col_right = st.columns([1.6, 1.4])

with col_left:
    st.subheader("🎯 Strategic Overview")

    if run:
        # Basic strategy text — no fake ROI
        st.write(f"**Niche:** {niche}")
        st.write(f"**Goal:** {primary_goal}")
        st.write(f"**Geo:** {geo_label}")
        st.write(f"**Budget:** ${budget_monthly:,.0f} / month")

        st.markdown("#### Recommended Meta campaign structure")
        st.markdown(
            """
- **1 campaign** per niche/goal (e.g. "Music – Awareness – US – SullyBot")
- **2–3 ad sets** split by:
    - Audience type (interests vs lookalikes vs remarketing)
    - Device / placement if needed
- **3–5 ads** per ad set:
    - Mix of static, Reels, and carousel
    - Creative variations based on Google Trends search language
            """
        )

        # We could later wire Google Ads / TikTok APIs here too

    else:
        st.info("Fill inputs in the sidebar and click **Generate Plan & (optionally) Create Meta Campaign** to start.")


    # ---- Google Trends section ----
    st.subheader("📈 Google Trends (Research only)")

    if use_trends and seed_keywords:
        trends = get_trends(seed_keywords[:5], geo=trends_geo, timeframe=trends_timeframe)

        if trends.get("error"):
            st.warning(f"Trends error: {trends['error']}")
        else:
            iot = trends.get("interest_over_time")
            if isinstance(iot, pd.DataFrame) and not iot.empty:
                st.write("**Interest over time**")
                st.line_chart(iot)

            by_region = trends.get("by_region")
            if isinstance(by_region, pd.DataFrame) and not by_region.empty:
                st.write("**Top regions by interest**")
                st.dataframe(by_region.head(20))

            related = trends.get("related_suggestions", [])
            if related:
                st.write("**Related search queries**")
                st.dataframe(pd.DataFrame({"Query": related[:50]}))
    else:
        st.caption("Enter seed keywords and enable Google Trends in the sidebar to see live research.")


with col_right:
    st.subheader("📡 Meta Campaign Builder (Live API)")

    if use_meta_live and run:
        # Map high-level goal to Meta "outcome" objective
        objective_map = {
            "Awareness": "OUTCOME_AWARENESS",
            "Traffic": "OUTCOME_TRAFFIC",
            "Engagement": "OUTCOME_ENGAGEMENT",
            "Leads": "OUTCOME_LEADS",
            "Sales": "OUTCOME_SALES",
            "App promotion": "OUTCOME_APP_PROMOTION",
        }
        meta_objective = objective_map.get(primary_goal, "OUTCOME_AWARENESS")

        campaign_name = f"{niche} – {primary_goal} – {geo_label} – {datetime.utcnow().strftime('%Y%m%d_%H%M')}"

        st.write(f"Planned campaign name: **{campaign_name}**")
        st.write(f"Meta objective: **{meta_objective}**")

        st.info("When you click the button below, the bot will call the **Meta Marketing API** to create a real campaign in your ad account (status: PAUSED).")

        if st.button("🚀 Create Meta Campaign Now"):
            result = create_meta_campaign(campaign_name, meta_objective, status="PAUSED")
            if result.get("ok"):
                cid = result["response"].get("id")
                st.success(f"✅ Campaign created! ID: {cid}")
                st.json(result["response"])
            else:
                st.error(f"❌ Meta API error (status {result.get('status')}):")
                st.json(result.get("response") or result.get("error"))
    else:
        if not use_meta_live:
            st.warning("Toggle **Enable live Meta campaign creation** in the sidebar to activate real API calls.")
        else:
            st.info("Set your inputs and click **Generate Plan** first, then this section will create the campaign.")

    st.markdown("---")
    st.subheader("🔗 External Research Shortcuts")
    if seed_keywords:
        q = "+".join(seed_keywords[:3])
        st.markdown(f"- TikTok Creative Center: search `{seed_keywords[0]}`")
        st.markdown(f"- YouTube search: https://www.youtube.com/results?search_query={q}")
        st.markdown(f"- Twitter/X search: https://x.com/search?q={q}")
        st.markdown(f"- Reddit search: https://www.reddit.com/search/?q={q}")
        st.caption("These use the live platforms directly in the browser instead of unofficial APIs.")

st.markdown("---")
st.info("⚠️ All calculators/estimators removed unless backed by a real API. Meta campaign creation is live; Google Trends uses live data when enabled (subject to rate limits / 429s).")

