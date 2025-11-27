# Sully's Media Planner – Meta + Strategy + Google Trends (clean light theme)
# - Tab 1: Strategy Planner (Music, Clothing, Home Care) + optional Google Trends
# - Tab 2: Meta Campaign Builder (Campaign + Ad Set + Ad via Graph API + creative generator)
# - All Meta credentials pulled from st.secrets (no hardcoded tokens)

import io
import json
from pathlib import Path
from datetime import datetime

import requests
import streamlit as st
import pandas as pd

# Optional: Google Trends (pytrends)
try:
    from pytrends.request import TrendReq
    HAS_TRENDS = True
except ImportError:
    HAS_TRENDS = False

# -------------------------
# Basic config + styling
# -------------------------
st.set_page_config(
    page_title="Sully's Media Planner",
    page_icon="🌺",
    layout="wide",
)

# Light theme + readable fonts, dark sidebar
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f7f7fb;
    }
    body, p, li, span, div, label {
        color: #111111 !important;
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }
    h1, h2, h3, h4, h5 {
        color: #111111 !important;
        font-weight: 700;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #151826;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    /* Tabs text visibility */
    .stTabs [role="tab"] p {
        color: #111111 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

APP_DIR = Path(__file__).resolve().parent
LOGO_PATH = APP_DIR / "sullivans_logo.png"


def _file_exists(path: Path) -> bool:
    try:
        return path.exists()
    except Exception:
        return False


# -------------------------
# Meta credentials (from Streamlit secrets)
# -------------------------
META_TOKEN = st.secrets.get("META_SYSTEM_USER_TOKEN", None)
META_AD_ACCOUNT_ID = st.secrets.get("META_AD_ACCOUNT_ID", None)  # numeric only, no 'act_'
META_BUSINESS_ID = st.secrets.get("META_BUSINESS_ID", None)
META_PAGE_ID = st.secrets.get("META_PAGE_ID", None)
META_PIXEL_ID = st.secrets.get("META_PIXEL_ID", None)
META_IG_ACTOR_ID = st.secrets.get("META_IG_ACTOR_ID", None)

META_API_VERSION = "v18.0"
META_GRAPH_BASE = f"https://graph.facebook.com/{META_API_VERSION}"


# -------------------------
# Strategy "brain" (planner)
# -------------------------
def generate_strategy(niche, budget, goal, geo, competitors):
    """Simple in-app strategy planner that returns per-platform breakdown."""
    niche = niche.lower()
    goal = goal.lower()
    budget = float(budget)

    # Basic budget split assumptions by primary goal
    if goal in ["sales", "conversions"]:
        split = {
            "meta": 0.40,
            "google_search": 0.35,
            "tiktok": 0.15,
            "youtube": 0.10,
        }
    elif goal in ["leads"]:
        split = {
            "meta": 0.45,
            "google_search": 0.30,
            "tiktok": 0.15,
            "youtube": 0.10,
        }
    elif goal in ["awareness"]:
        split = {
            "meta": 0.35,
            "tiktok": 0.30,
            "youtube": 0.25,
            "google_search": 0.10,
        }
    else:  # traffic / default
        split = {
            "meta": 0.35,
            "google_search": 0.30,
            "tiktok": 0.20,
            "youtube": 0.15,
        }

    def alloc(p):
        return round(budget * split.get(p, 0), 2)

    # Audience angle by niche
    if niche == "music":
        core_aud = [
            "Fans of similar artists",
            "Recent listeners of your genre",
            "Lookalike of engaged fans",
            "Retarget video viewers 25%+",
        ]
    elif niche == "clothing":
        core_aud = [
            "Streetwear & sneakerheads",
            "Fashion & online shoppers",
            "Lookalike of purchasers",
            "Retarget product viewers & cart abandoners",
        ]
    elif niche == "homecare":
        core_aud = [
            "Adults 35–65 with parents 65+",
            "People interested in caregiving & nursing",
            "Local radius around service area",
            "Website visitors who viewed services or contact",
        ]
    else:
        core_aud = ["Broad interest + remarketing"]

    plan = {
        "overview": {
            "niche": niche,
            "goal": goal,
            "geo": geo,
            "monthly_budget": budget,
            "competitors": competitors,
        },
        "platforms": {
            "meta": {
                "budget": alloc("meta"),
                "objective": goal,
                "campaign_idea": f"{niche.title()} – {goal.title()} – Meta",
                "suggested_audiences": core_aud,
                "notes": [
                    "Use Advantage+ placements first.",
                    "Build one remarketing ad set once pixel has data.",
                ],
            },
            "google_search": {
                "budget": alloc("google_search"),
                "objective": "high-intent search",
                "campaign_idea": f"{niche.title()} – Core Keywords – Search",
                "notes": [
                    "Use Exact + Phrase for tight control.",
                    "Send to the most relevant landing page.",
                ],
            },
            "tiktok": {
                "budget": alloc("tiktok"),
                "objective": "short-form video discovery",
                "campaign_idea": f"{niche.title()} – UGC hooks – TikTok",
                "notes": [
                    "Use fast hooks in first 2 seconds.",
                    "Test 3–5 creatives per ad group.",
                ],
            },
            "youtube": {
                "budget": alloc("youtube"),
                "objective": "mid-funnel video",
                "campaign_idea": f"{niche.title()} – YouTube In-Stream",
                "notes": [
                    "Hook in first 5 seconds.",
                    "Use custom segments with your core keywords and top competitors.",
                ],
            },
        },
    }
    return plan


# -------------------------
# Google Trends helper
# -------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def get_trends(seed_terms, geo="US", timeframe="today 12-m", gprop=""):
    """Google Trends wrapper. Only used if pytrends is installed."""
    if not HAS_TRENDS or not seed_terms:
        return {"error": "pytrends not installed or no seed terms."}

    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(seed_terms, timeframe=timeframe, geo=geo, gprop=gprop)

        out = {}
        iot = pytrends.interest_over_time()
        if isinstance(iot, pd.DataFrame) and not iot.empty:
            if "isPartial" in iot.columns:
                iot = iot.drop(columns=["isPartial"])
            out["interest_over_time"] = iot

        reg = pytrends.interest_by_region(
            resolution="REGION", inc_low_vol=True, inc_geo_code=True
        )
        if isinstance(reg, pd.DataFrame) and not reg.empty:
            main = seed_terms[0]
            if main in reg.columns:
                reg = reg.sort_values(main, ascending=False)
            out["by_region"] = reg

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
        return {"error": str(e)}


def parse_multiline(raw: str):
    out = []
    for chunk in raw.replace(",", "\n").split("\n"):
        v = chunk.strip()
        if v:
            out.append(v)
    # dedupe keep order
    seen = set()
    result = []
    for v in out:
        if v not in seen:
            seen.add(v)
            result.append(v)
    return result


# -------------------------
# Meta helpers
# -------------------------
def meta_connection_status():
    """Return a human-readable status for Meta credentials."""
    missing = []
    if not META_TOKEN:
        missing.append("META_SYSTEM_USER_TOKEN")
    if not META_AD_ACCOUNT_ID:
        missing.append("META_AD_ACCOUNT_ID")
    if not META_BUSINESS_ID:
        missing.append("META_BUSINESS_ID")
    if not META_PAGE_ID:
        missing.append("META_PAGE_ID")
    if not META_PIXEL_ID:
        missing.append("META_PIXEL_ID")
    if not META_IG_ACTOR_ID:
        missing.append("META_IG_ACTOR_ID")

    if missing:
        return (
            False,
            "Missing Meta credentials: "
            + ", ".join(missing)
            + ". Set them in Streamlit secrets to enable live Meta calls.",
        )
    return True, "Meta credentials are present. You can create campaigns, ad sets, and ads."


def meta_create_campaign(name: str, objective: str):
    """
    Create a Meta campaign via Graph API (campaign-level).
    Budget is set at ad set level, so we keep this simple.
    """
    ok, msg = meta_connection_status()
    if not ok:
        return {"error": msg}

    url = f"{META_GRAPH_BASE}/act_{META_AD_ACCOUNT_ID}/campaigns"
    payload = {
        "name": name,
        "objective": objective,  # e.g. OUTCOME_AWARENESS, OUTCOME_TRAFFIC
        "status": "PAUSED",
        "special_ad_categories": "[]",
        "buying_type": "AUCTION",
        "access_token": META_TOKEN,
    }
    try:
        resp = requests.post(url, data=payload, timeout=20)
        data = resp.json()
        if resp.status_code != 200:
            return {"error": f"{resp.status_code}", "response": data, "url": url}
        return data
    except Exception as e:
        return {"error": str(e)}


def _map_meta_optimization(goal: str):
    goal = goal.upper()
    if "AWARENESS" in goal:
        return "REACH", "IMPRESSIONS"
    if "TRAFFIC" in goal:
        return "LINK_CLICKS", "IMPRESSIONS"
    if "LEADS" in goal:
        return "LEAD_GENERATION", "IMPRESSIONS"
    if "SALES" in goal or "CONVERSION" in goal:
        return "CONVERSIONS", "IMPRESSIONS"
    return "REACH", "IMPRESSIONS"


def meta_create_adset(
    name: str,
    campaign_id: str,
    daily_budget_usd: float,
    country: str,
    age_min: int,
    age_max: int,
    objective: str,
):
    """Create an ad set under a campaign."""
    ok, msg = meta_connection_status()
    if not ok:
        return {"error": msg}

    if not campaign_id:
        return {"error": "campaign_id is required to create an ad set."}

    opt_goal, billing_event = _map_meta_optimization(objective)
    daily_budget_minor = int(float(daily_budget_usd) * 100)  # USD -> cents

    targeting = {
        "geo_locations": {
            "countries": [country] if country and country != "Worldwide" else ["US"]
        },
        "age_min": age_min,
        "age_max": age_max,
    }

    payload = {
        "name": name,
        "campaign_id": campaign_id,
        "daily_budget": str(daily_budget_minor),
        "billing_event": billing_event,
        "optimization_goal": opt_goal,
        "status": "PAUSED",
        "targeting": json.dumps(targeting),
        "access_token": META_TOKEN,
    }

    # For conversion / sales, attach pixel
    if opt_goal == "CONVERSIONS" and META_PIXEL_ID:
        payload["promoted_object"] = json.dumps({"pixel_id": META_PIXEL_ID})

    url = f"{META_GRAPH_BASE}/act_{META_AD_ACCOUNT_ID}/adsets"

    try:
        resp = requests.post(url, data=payload, timeout=20)
        data = resp.json()
        if resp.status_code != 200:
            return {"error": f"{resp.status_code}", "response": data, "url": url}
        return data
    except Exception as e:
        return {"error": str(e)}


def meta_create_ad(
    name: str,
    adset_id: str,
    page_id: str,
    ig_actor_id: str,
    link_url: str,
    primary_text: str,
    headline: str,
    description: str,
):
    """
    Create a creative + ad under an ad set.
    Uses Page ID + IG actor for placements.
    """
    ok, msg = meta_connection_status()
    if not ok:
        return {"error": msg}

    if not adset_id:
        return {"error": "adset_id is required to create an ad."}
    if not page_id:
        return {"error": "META_PAGE_ID is missing."}

    # 1) Create ad creative
    creative_url = f"{META_GRAPH_BASE}/act_{META_AD_ACCOUNT_ID}/adcreatives"
    object_story_spec = {
        "page_id": page_id,
        "link_data": {
            "message": primary_text,
            "name": headline,
            "description": description,
            "link": link_url,
            "call_to_action": {"type": "LEARN_MORE", "value": {"link": link_url}},
        },
    }
    if ig_actor_id:
        object_story_spec["instagram_actor_id"] = ig_actor_id

    creative_payload = {
        "name": f"{name} – Creative",
        "object_story_spec": json.dumps(object_story_spec),
        "access_token": META_TOKEN,
    }

    try:
        c_resp = requests.post(creative_url, data=creative_payload, timeout=20)
        c_data = c_resp.json()
        if c_resp.status_code != 200 or "id" not in c_data:
            return {"error": "creative_error", "response": c_data, "url": creative_url}
        creative_id = c_data["id"]
    except Exception as e:
        return {"error": f"creative_exception: {e}"}

    # 2) Create ad
    ad_url = f"{META_GRAPH_BASE}/act_{META_AD_ACCOUNT_ID}/ads"
    ad_payload = {
        "name": name,
        "adset_id": adset_id,
        "creative": json.dumps({"creative_id": creative_id}),
        "status": "PAUSED",
        "access_token": META_TOKEN,
    }

    try:
        a_resp = requests.post(ad_url, data=ad_payload, timeout=20)
        a_data = a_resp.json()
        if a_resp.status_code != 200:
            return {"error": "ad_error", "response": a_data, "url": ad_url}
        return {"creative": c_data, "ad": a_data}
    except Exception as e:
        return {"error": f"ad_exception: {e}"}


# -------------------------
# Creative generator for Meta
# -------------------------
def generate_meta_creatives(niche, goal, country, states, interests, offer, brand_name="Sully's"):
    """
    Generate a small table of creative ideas (primary text, headline, description, CTA, audience notes).
    This does NOT hit the Meta API; it's planning output for you to copy.
    """
    niche = niche.lower()
    goal = goal.lower()
    base_audience = ", ".join(states) if states else country
    interest_str = ", ".join(interests) if interests else "broad interests"

    if niche == "music":
        vibe = "new releases, unreleased snippets, studio content"
    elif niche == "clothing":
        vibe = "new drops, fit checks, streetwear looks"
    elif niche == "homecare":
        vibe = "trust, safety, family peace of mind"
    else:
        vibe = "your brand story and strongest value"

    if goal == "awareness":
        cta = "LEARN_MORE"
        angle = "introduce the brand and story"
    elif goal == "traffic":
        cta = "LEARN_MORE"
        angle = "drive clicks to key landing pages"
    elif goal == "leads":
        cta = "SIGN_UP"
        angle = "push sign-ups or lead forms"
    elif goal in ["conversions", "sales"]:
        cta = "SHOP_NOW"
        angle = "drive purchases with urgency"
    else:
        cta = "LEARN_MORE"
        angle = "push engagement and discovery"

    rows = []

    # Idea 1 – Social proof
    rows.append({
        "Primary Text": f"{brand_name} is making noise in {base_audience}. Tap in for {vibe}. {offer}",
        "Headline": f"{brand_name} – {goal.title()} in {base_audience}",
        "Description": f"Built for people who live and breathe this culture.",
        "CTA": cta,
        "Suggested Audience": f"{base_audience} – interests in {interest_str}",
        "Suggested Placement": "Feed + Reels (FB & IG)",
    })

    # Idea 2 – Scarcity / urgency
    rows.append({
        "Primary Text": f"Only a few spots / pieces left for {brand_name}. {offer}",
        "Headline": "Don’t sleep on this drop",
        "Description": "Once it’s gone, it’s gone.",
        "CTA": cta,
        "Suggested Audience": f"Engagers in last 30–90 days + Lookalikes",
        "Suggested Placement": "Reels + Stories",
    })

    # Idea 3 – Education / value
    rows.append({
        "Primary Text": f"Here’s why {brand_name} hits different for {niche} in {base_audience}. {offer}",
        "Headline": "Why this matters for you",
        "Description": "Quick breakdown of what makes us different.",
        "CTA": cta,
        "Suggested Audience": f"{base_audience} – interests in {interest_str}",
        "Suggested Placement": "Feed + In-Stream Video",
    })

    df = pd.DataFrame(rows)
    return df


# -------------------------
# Header + sidebar logo
# -------------------------
header_cols = st.columns([1, 3])
with header_cols[0]:
    if _file_exists(LOGO_PATH):
        st.image(str(LOGO_PATH), use_column_width=True)
with header_cols[1]:
    st.markdown("## Sully’s Multi-Platform Media Planner")
    st.caption(
        "Mini media planner for Music, Clothing Brands, and Local Home Care — "
        "with Meta API hooks and optional Google Trends research."
    )

st.markdown("---")

with st.sidebar:
    if _file_exists(LOGO_PATH):
        st.image(str(LOGO_PATH), caption="Sullivan’s Advertisements", use_column_width=True)


# -------------------------
# Tabs: Planner & Meta
# -------------------------
tab_planner, tab_meta = st.tabs(["🧠 Strategy Planner", "📣 Meta Campaign Builder"])


# =========================
# TAB 1 – STRATEGY PLANNER
# =========================
with tab_planner:
    st.subheader("🧠 Strategy Planner")

    c1, c2, c3 = st.columns(3)
    with c1:
        niche = st.selectbox("Niche", ["Music", "Clothing", "Homecare"])
    with c2:
        goal = st.selectbox(
            "Primary Goal",
            ["Awareness", "Traffic", "Leads", "Conversions", "Sales"],
        )
    with c3:
        budget = st.number_input(
            "Monthly Ad Budget (USD)", min_value=100.0, value=2500.0, step=50.0
        )

    c4, c5 = st.columns(2)
    with c4:
        country = st.selectbox(
            "Main Country / Region", ["Worldwide", "US", "UK", "CA", "EU"]
        )
    with c5:
        geo_detail = st.text_input("Key city/region focus (optional)", value="")

    st.markdown("#### Competitor URLs (for research context only)")
    comp_text = st.text_area(
        "One per line",
        placeholder="https://example.com\nhttps://competitor.com\n(optional)",
        height=80,
    )
    competitors = parse_multiline(comp_text)

    st.markdown("#### Google Trends (optional research)")
    trends_col1, trends_col2 = st.columns([2, 1])
    with trends_col1:
        use_trends = st.checkbox("Use Google Trends for keyword ideas", value=False)
        trend_seeds_raw = st.text_input(
            "Trend seed terms (comma/newline)",
            placeholder="streetwear, trap beats, home care services",
        )
    with trends_col2:
        timeframe = st.selectbox(
            "Trends timeframe",
            ["now 7-d", "today 3-m", "today 12-m", "today 5-y"],
            index=2,
        )
        gprop_choice = st.selectbox(
            "Search Source",
            ["(Web)", "news", "images", "youtube", "froogle"],
            index=0,
        )
        gprop = "" if gprop_choice == "(Web)" else gprop_choice

    trends_data = None
    if use_trends and st.button("Pull Google Trends"):
        seeds = parse_multiline(trend_seeds_raw)
        if not seeds:
            st.warning("Add at least one trend seed term.")
        else:
            if not HAS_TRENDS:
                st.error(
                    "pytrends is not installed on the server. "
                    "Ask to add `pytrends` to requirements.txt."
                )
            else:
                with st.spinner("Contacting Google Trends..."):
                    trends_data = get_trends(
                        seeds,
                        geo="US" if country == "US" else "",
                        timeframe=timeframe,
                        gprop=gprop,
                    )
                if trends_data.get("error"):
                    st.error(f"Trends error: {trends_data['error']}")
                else:
                    st.success("Trends data loaded.")

                    if isinstance(trends_data.get("interest_over_time"), pd.DataFrame):
                        st.write("**Interest over time**")
                        st.line_chart(trends_data["interest_over_time"])

                    if isinstance(trends_data.get("by_region"), pd.DataFrame):
                        st.write("**Top regions by interest**")
                        st.dataframe(trends_data["by_region"].head(20))

                    sugg = trends_data.get("related_suggestions") or []
                    if sugg:
                        st.write("**Related queries (Top + Rising)**")
                        st.dataframe(pd.DataFrame({"Query": sugg[:50]}))

    if st.button("Generate Strategy Plan"):
        geo_label = "Worldwide" if country == "Worldwide" else country
        if geo_detail.strip():
            geo_label = f"{geo_label} – {geo_detail.strip()}"

        plan = generate_strategy(
            niche=niche,
            budget=budget,
            goal=goal,
            geo=geo_label,
            competitors=competitors,
        )

        st.success("Strategy generated.")
        st.markdown("### High-Level Plan")
        st.json(plan["overview"])

        st.markdown("### Per-Platform Breakdown")
        plat = plan["platforms"]
        for platform_name, cfg in plat.items():
            st.markdown(f"#### {platform_name.upper()}")
            st.write(f"**Monthly Budget**: ${cfg['budget']:,.2f}")
            st.write(f"**Campaign Idea**: {cfg['campaign_idea']}")
            st.write("**Notes:**")
            for n in cfg.get("notes", []):
                st.write(f"- {n}")
            if cfg.get("suggested_audiences"):
                st.write("**Suggested audiences:**")
                for a in cfg["suggested_audiences"]:
                    st.write(f"- {a}")

        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        export_name = f"sully_strategy_{niche.lower()}_{ts}.json"
        buf = io.StringIO()
        json.dump(plan, buf, indent=2)
        st.download_button(
            "⬇️ Download Strategy JSON",
            data=buf.getvalue(),
            file_name=export_name,
            mime="application/json",
        )


# =========================
# TAB 2 – META CAMPAIGN BUILDER
# =========================
with tab_meta:
    st.subheader("📣 Meta (Facebook + Instagram) Campaign Builder")

    ok_meta, msg_meta = meta_connection_status()
    if ok_meta:
        st.success(msg_meta)
    else:
        st.error(msg_meta)
        st.info(
            "In Streamlit Cloud, go to **Settings → Secrets** and add:\n\n"
            "- `META_SYSTEM_USER_TOKEN`\n"
            "- `META_AD_ACCOUNT_ID` (numbers only)\n"
            "- `META_BUSINESS_ID`\n"
            "- `META_PAGE_ID`\n"
            "- `META_PIXEL_ID`\n"
            "- `META_IG_ACTOR_ID`\n\n"
            "Then redeploy the app."
        )

    # 1) Test connection
    st.markdown("#### 1. Test Meta Connection")
    if ok_meta and st.button("Test /me with current token"):
        test_url = f"{META_GRAPH_BASE}/me"
        try:
            resp = requests.get(test_url, params={"access_token": META_TOKEN}, timeout=20)
            data = resp.json()
            if resp.status_code == 200:
                st.success(f"Connected as: {data}")
            else:
                st.error(f"Meta error {resp.status_code}: {data}")
        except Exception as e:
            st.error(f"Request failed: {e}")

    st.markdown("---")

    # 2) Campaign creator
    st.markdown("#### 2. Create Campaign")

    colc1, colc2 = st.columns(2)
    with colc1:
        camp_name = st.text_input(
            "Campaign Name",
            value=f"Sully Awareness – {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        )
    with colc2:
        objective_label = st.selectbox(
            "Objective",
            [
                "OUTCOME_AWARENESS",
                "OUTCOME_TRAFFIC",
                "OUTCOME_ENGAGEMENT",
                "OUTCOME_LEADS",
                "OUTCOME_SALES",
            ],
        )

    if ok_meta and st.button("Create Campaign via Meta API"):
        with st.spinner("Creating campaign on Meta..."):
            result = meta_create_campaign(
                name=camp_name,
                objective=objective_label,
            )
        if "error" in result and not result.get("id"):
            st.error("Meta API error while creating campaign:")
            st.json(result)
        else:
            st.success("✅ Campaign created with Meta.")
            st.json(result)
            if "id" in result:
                st.session_state["last_campaign_id"] = result["id"]

    st.markdown("---")

    # 3) Ad set creator
    st.markdown("#### 3. Create Ad Set (Audience & Budget)")

    default_campaign_id = st.session_state.get("last_campaign_id", "")
    adset_col1, adset_col2, adset_col3 = st.columns(3)
    with adset_col1:
        adset_name = st.text_input(
            "Ad Set Name",
            value="Sully – Core Audience",
        )
    with adset_col2:
        adset_campaign_id = st.text_input(
            "Campaign ID",
            value=default_campaign_id,
            help="Use the campaign ID returned above.",
        )
    with adset_col3:
        adset_daily_budget = st.number_input(
            "Ad Set Daily Budget (USD)",
            min_value=1.0,
            value=20.0,
            step=1.0,
        )

    adset_country = st.selectbox(
        "Ad Set Country",
        ["US", "CA", "GB", "AU", "Worldwide"],
        index=0,
    )
    adset_age_min, adset_age_max = st.slider(
        "Age range", min_value=18, max_value=65, value=(18, 45)
    )

    st.caption(
        "This will create an ad set with basic geo + age targeting and attach the pixel for conversion objectives."
    )

    if ok_meta and st.button("Create Ad Set via Meta API"):
        with st.spinner("Creating ad set on Meta..."):
            result_as = meta_create_adset(
                name=adset_name,
                campaign_id=adset_campaign_id,
                daily_budget_usd=adset_daily_budget,
                country="US" if adset_country == "Worldwide" else adset_country,
                age_min=adset_age_min,
                age_max=adset_age_max,
                objective=objective_label,
            )
        if "error" in result_as and not result_as.get("id"):
            st.error("Meta API error while creating ad set:")
            st.json(result_as)
        else:
            st.success("✅ Ad set created.")
            st.json(result_as)
            if "id" in result_as:
                st.session_state["last_adset_id"] = result_as["id"]

    st.markdown("---")

    # 4) Ad creator
    st.markdown("#### 4. Create Ad (Creative + Ad)")

    default_adset_id = st.session_state.get("last_adset_id", "")
    adc1, adc2 = st.columns(2)
    with adc1:
        ad_name = st.text_input("Ad Name", value="Sully – Main Creative")
        link_url = st.text_input(
            "Destination URL",
            value="https://example.com",
        )
        primary_text = st.text_area(
            "Primary Text",
            value="Tap in to the latest drop from Sully.",
        )
    with adc2:
        headline = st.text_input("Headline", value="New Collection Live")
        description = st.text_input("Description", value="Limited quantities, don’t sleep.")
    ad_image_hint = st.caption(
        "Image is configured inside the Page post / creative setup. For now, this builder focuses on text + structure."
    )

    adset_id_for_ad = st.text_input(
        "Ad Set ID",
        value=default_adset_id,
        help="Use the ad set ID returned above.",
    )

    st.caption(
        "This will create an ad creative using your Page + IG actor (from secrets), "
        "then create an ad linked to the selected ad set."
    )

    if ok_meta and st.button("Create Ad via Meta API"):
        with st.spinner("Creating ad creative + ad on Meta..."):
            result_ad = meta_create_ad(
                name=ad_name,
                adset_id=adset_id_for_ad,
                page_id=META_PAGE_ID or "",
                ig_actor_id=(META_IG_ACTOR_ID or "").strip(),
                link_url=link_url,
                primary_text=primary_text,
                headline=headline,
                description=description,
            )
        if "error" in result_ad and not result_ad.get("ad"):
            st.error("Meta API error while creating ad/creative:")
            st.json(result_ad)
        else:
            st.success("✅ Ad creative + ad created.")
            st.json(result_ad)

    # 5) Ad set & creative ideas (manual planning)
    st.markdown("---")
    st.markdown("#### 5. Ad Set & Creative Ideas (manual input into Meta)")

    st.caption("Use this section to plan audiences + creatives. Copy/paste into Meta Ads Manager or your own API flow.")

    ac1, ac2 = st.columns(2)
    with ac1:
        creative_niche = st.selectbox(
            "Niche for this ad set",
            ["Music", "Clothing", "Homecare"],
            key="creative_niche"
        )
        creative_goal = st.selectbox(
            "Goal for this ad set",
            ["Awareness", "Traffic", "Leads", "Conversions", "Sales"],
            key="creative_goal"
        )
        creative_country = st.text_input(
            "Target Country (e.g., US, Worldwide)",
            value="US",
            key="creative_country"
        )
        creative_states_raw = st.text_area(
            "Target States / Regions (comma or newline)",
            placeholder="California, New York\nTexas",
            key="creative_states"
        )
    with ac2:
        interests_raw = st.text_area(
            "Interests / Keywords (paste from Google Trends, TikTok, etc.)",
            placeholder="streetwear, hip hop, sneakerheads\ntrap beats\nhome care services",
            height=120,
            key="creative_interests"
        )
        offer_text = st.text_input(
            "Main Offer / Hook",
            value="Limited time offer – tap to learn more.",
            key="creative_offer"
        )

    if st.button("Generate Meta Ad Creative Ideas"):
        states_list = parse_multiline(creative_states_raw)
        interests_list = parse_multiline(interests_raw)

        df_creatives = generate_meta_creatives(
            niche=creative_niche,
            goal=creative_goal,
            country=creative_country,
            states=states_list,
            interests=interests_list,
            offer=offer_text,
            brand_name="Sully's"
        )

        st.success("Here are your ad ideas. Copy/paste into Meta Ads Manager (Ad level).")
        st.dataframe(df_creatives)

        csv_buf = io.StringIO()
        df_creatives.to_csv(csv_buf, index=False)
        st.download_button(
            "⬇️ Download creatives.csv",
            data=csv_buf.getvalue().encode("utf-8"),
            file_name="meta_creatives.csv",
            mime="text/csv"
        )
