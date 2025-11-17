# ==========================
# Sully's Marketing Bot
# Light theme + top logo + multi-platform research
# ==========================

import sys
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

# ---------- Make /bot importable ----------
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# Expecting: bot/core.py -> def generate_strategy(niche, budget, goal, geo, competitors) -> dict
from bot.core import generate_strategy  # type: ignore


# ==========================
# Helpers
# ==========================

LOGO_PATH = Path(__file__).with_name("sullivan_logo.png")


def _split_list(raw: str) -> list[str]:
    """Split comma/newline separated text into a clean unique list."""
    if not raw:
        return []
    parts = []
    for chunk in raw.replace(",", "\n").split("\n"):
        v = chunk.strip()
        if v:
            parts.append(v)
    # de-duplicate, keep order
    seen = set()
    out = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


if HAS_TRENDS:

    @st.cache_data(ttl=3600, show_spinner=False)
    def get_trends(seed_terms, geo="US", timeframe="today 12-m", gprop=""):
        """
        Google Trends wrapper.
        Returns dict with:
          - interest_over_time: DataFrame
          - by_region: DataFrame
          - related_suggestions: list[str]
        """
        if not seed_terms:
            return {}

        try:
            pytrends = TrendReq(hl="en-US", tz=360)
            pytrends.build_payload(seed_terms, timeframe=timeframe, geo=geo, gprop=gprop)

            out: dict[str, object] = {}

            # Interest over time
            iot = pytrends.interest_over_time()
            if isinstance(iot, pd.DataFrame) and not iot.empty:
                if "isPartial" in iot.columns:
                    iot = iot.drop(columns=["isPartial"])
                out["interest_over_time"] = iot

            # By region
            reg = pytrends.interest_by_region(
                resolution="REGION", inc_low_vol=True, inc_geo_code=True
            )
            if isinstance(reg, pd.DataFrame) and not reg.empty:
                first = seed_terms[0]
                if first in reg.columns:
                    reg = reg.sort_values(first, ascending=False)
                out["by_region"] = reg

            # Related queries
            rq = pytrends.related_queries()
            suggestions: list[str] = []
            if isinstance(rq, dict):
                for _, buckets in rq.items():
                    for key in ("top", "rising"):
                        df = buckets.get(key)
                        if isinstance(df, pd.DataFrame) and "query" in df.columns:
                            suggestions.extend(
                                df["query"].dropna().astype(str).tolist()
                            )

            # de-dupe suggestions
            seen = set()
            uniq: list[str] = []
            for s in suggestions:
                if s not in seen:
                    seen.add(s)
                    uniq.append(s)
            out["related_suggestions"] = uniq[:100]

            return out
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)}
else:

    def get_trends(seed_terms, geo="US", timeframe="today 12-m", gprop=""):
        return {"error": "pytrends not installed on this server."}


def build_platform_insights(plan: dict, trends: dict | None, niche: str) -> dict:
    """
    Build simple research-style insights for:
      - Google (Trends + keywords)
      - Meta (interest & creative angles)
      - TikTok (hashtags and hook ideas)
      - X/Twitter (topic & keyword angles)
    No external scraping, just transforms your data.
    """
    keywords = [str(k) for k in plan.get("keywords", [])][:50]
    trends = trends or {}
    related = [str(x) for x in trends.get("related_suggestions", [])][:50]

    # Google
    google_keywords = keywords + related

    # Meta – treat as interest categories / hooks
    meta_interests = []
    for k in keywords[:20]:
        meta_interests.append(k.title())
    for r in related[:10]:
        meta_interests.append(r.title())
    # de-dupe
    meta_seen = set()
    meta_interests = [m for m in meta_interests if not (m in meta_seen or meta_seen.add(m))]

    # TikTok – generate hashtag-style strings
    tiktok_tags = []
    for k in keywords[:25]:
        base = k.replace("#", "").strip().lower()
        if not base:
            continue
        tag = "#" + base.replace(" ", "")
        tiktok_tags.append(tag[:24])
    for r in related[:10]:
        base = r.replace("#", "").strip().lower()
        if not base:
            continue
        tag = "#" + base.replace(" ", "")
        tiktok_tags.append(tag[:24])
    # de-dupe
    seen_tags = set()
    tiktok_tags = [t for t in tiktok_tags if not (t in seen_tags or seen_tags.add(t))]

    # Twitter / X – shorter phrases + trend queries
    twitter_terms = []
    for k in keywords[:25]:
        twitter_terms.append(k)
    for r in related[:20]:
        twitter_terms.append(r)
    tw_seen = set()
    twitter_terms = [t for t in twitter_terms if not (t in tw_seen or tw_seen.add(t))]

    return {
        "google_keywords": google_keywords,
        "meta_interests": meta_interests,
        "tiktok_tags": tiktok_tags,
        "twitter_terms": twitter_terms,
    }


# ==========================
# Page config & Light styling
# ==========================

st.set_page_config(
    page_title="Sully's Marketing Bot",
    page_icon="📈",
    layout="wide",
)

# Light theme / readable text tweaks (no background image)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f5f7;
        color: #111111;
    }
    .stSidebar {
        background-color: #ffffff !important;
    }
    h1, h2, h3, h4 {
        color: #111111;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================
# Header with logo + title
# ==========================

header_col1, header_col2 = st.columns([1, 3])
with header_col1:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)
    else:
        st.write("⚠️ `sullivan_logo.png` not found")

with header_col2:
    st.title("Sully's Cross-Platform Marketing Bot")
    st.caption(
        "Strategic planning + trends research for Google, Meta, TikTok, and X."
    )


# ==========================
# Sidebar – inputs
# ==========================

with st.sidebar:
    st.header("Inputs")

    niche = st.selectbox(
        "Niche",
        ["clothing", "consignment", "musician", "homecare"],
        index=0,
    )
    budget = st.number_input(
        "Monthly Budget (USD)",
        min_value=100.0,
        value=2500.0,
        step=50.0,
    )
    goal = st.selectbox(
        "Primary Goal",
        ["sales", "conversions", "leads", "awareness, traffic"],
        index=0,
    )

    st.markdown("### Location mode")
    loc_mode = st.radio(
        "Choose how to target",
        ["Country", "States", "Cities", "ZIPs", "Radius"],
        horizontal=True,
    )

    country = st.text_input("Country (ISO/name)", value="US")

    states_raw = ""
    cities_raw = ""
    zips_raw = ""
    radius_center = ""
    radius_miles = 15

    if loc_mode == "States":
        st.caption("Enter states separated by commas or new lines")
        states_raw = st.text_area("States list", value="")
    elif loc_mode == "Cities":
        st.caption("Enter city names separated by commas or new lines")
        cities_raw = st.text_area("Cities list", value="")
    elif loc_mode == "ZIPs":
        st.caption("Enter ZIPs separated by commas or new lines")
        zips_raw = st.text_area("ZIP list", value="")
    elif loc_mode == "Radius":
        radius_center = st.text_input("Center address")
        radius_miles = st.number_input(
            "Radius (miles)", min_value=1, max_value=100, value=15
        )

    st.markdown("### Competitor URLs")
    comp_text = st.text_area(
        "One per line",
        placeholder="https://example.com\nhttps://competitor.com/locations",
    )
    competitors = [c.strip() for c in comp_text.split("\n") if c.strip()]

    # Google Trends controls
    st.markdown("### Google Trends")
    use_trends = st.checkbox("Use Google Trends boost", value=True)
    timeframe = st.selectbox(
        "Trends timeframe",
        ["now 7-d", "today 3-m", "today 12-m", "today 5-y"],
        index=2,
    )
    gprop_choice = st.selectbox(
        "Search source",
        ["(Web)", "news", "images", "youtube", "froogle"],
        index=0,
    )
    gprop = "" if gprop_choice == "(Web)" else gprop_choice

    trend_seeds_raw = st.text_area(
        "Trend seed terms (comma/newline)",
        placeholder="streetwear, vintage clothing\ntrap beats\ncaregiver services",
        value="",
    )

    run = st.button("Generate Plan", type="primary")


# ==========================
# Main logic – generate plan & research
# ==========================

plan: dict | None = None
trends_data: dict | None = None
platform_insights: dict | None = None

if run:
    # derive geo string
    if loc_mode == "Country":
        geo = country
    elif loc_mode == "States":
        selected_states = _split_list(states_raw)
        geo = ", ".join(selected_states) if selected_states else country
    elif loc_mode == "Cities":
        selected_cities = _split_list(cities_raw)
        geo = ", ".join(selected_cities) if selected_cities else country
    elif loc_mode == "ZIPs":
        selected_zips = _split_list(zips_raw)
        selected_zips = [
            z.strip()[:5] if z and z[0].isdigit() else z for z in selected_zips
        ]
        geo = ", ".join(selected_zips) if selected_zips else country
    else:
        geo = f"{radius_miles}mi around {radius_center}" if radius_center else country

    plan = generate_strategy(niche, float(budget), goal, geo, competitors)

    # build seed terms for trends
    tr_seed_terms: list[str] = []
    if trend_seeds_raw.strip():
        tr_seed_terms = _split_list(trend_seeds_raw)
    else:
        auto_kw = plan.get("keywords", [])
        for k in auto_kw:
            k_str = str(k)
            if 1 <= len(k_str.split()) <= 4:
                tr_seed_terms.append(k_str)
            if len(tr_seed_terms) >= 5:
                break

    if use_trends and tr_seed_terms:
        geo_for_trends = country if country else "US"
        trends_data = get_trends(
            tr_seed_terms,
            geo=geo_for_trends,
            timeframe=timeframe,
            gprop=gprop,
        )

    platform_insights = build_platform_insights(plan, trends_data, niche)
    st.success("✅ Plan and research generated. Scroll down for details.")


# ==========================
# If no plan yet – show hint
# ==========================

if plan is None:
    st.info("Fill the sidebar and click **Generate Plan** to see strategy and insights.")
    st.stop()


# ==========================
# Locations & Keywords Overview
# ==========================

st.subheader("🎯 Locations & Core Keywords")

ins = plan.get("insights", {})
ranked_cities = ins.get("cities_ranked", []) or []
ranked_states = ins.get("states_ranked", []) or []
ranked_zips = ins.get("zips_ranked", []) or []

# derive chosen locations
if loc_mode == "Country":
    chosen_locs = [country]
elif loc_mode == "States":
    chosen_locs = _split_list(states_raw) or ranked_states[:10]
elif loc_mode == "Cities":
    chosen_locs = _split_list(cities_raw) or ranked_cities[:15]
elif loc_mode == "ZIPs":
    chosen_locs = _split_list(zips_raw) or ranked_zips[:50]
else:
    chosen_locs = [f"{radius_miles}mi around {radius_center}"] if radius_center else [country]

chosen_text = st.text_area(
    "Final targets (edit before export)",
    value="\n".join(chosen_locs),
)
final_targets = [t.strip() for t in chosen_text.split("\n") if t.strip()]

st.caption("You can paste these directly into Google Ads location bulk add or Ads Editor.")

c1, c2 = st.columns(2)
with c1:
    st.write("**Keyword ideas**")
    st.dataframe(pd.DataFrame({"Keyword": plan.get("keywords", [])}))
with c2:
    st.write("**Top competitor locations**")
    st.dataframe(
        pd.DataFrame(
            {
                "Cities": ranked_cities[:20] if ranked_cities else [],
                "States": ranked_states[:20] if ranked_states else [],
            }
        )
    )


# ==========================
# Google Trends Insights
# ==========================

st.subheader("📈 Google Trends Insights")

if not use_trends:
    st.info("Google Trends is disabled in the sidebar. Enable it to see trends.")
elif trends_data is None or trends_data.get("error"):
    err = trends_data.get("error") if isinstance(trends_data, dict) else None
    if err:
        st.warning(f"Trends error: {err}")
    else:
        st.info("No trends data available for the current seeds.")
else:
    iot = trends_data.get("interest_over_time")
    if isinstance(iot, pd.DataFrame) and not iot.empty:
        st.write("**Interest over time**")
        st.line_chart(iot)

    by_region = trends_data.get("by_region")
    if isinstance(by_region, pd.DataFrame) and not by_region.empty:
        st.write("**Top regions by interest**")
        st.dataframe(by_region.head(25))

    sugg = trends_data.get("related_suggestions") or []
    if sugg:
        st.write("**Related queries (Top + Rising)**")
        st.dataframe(pd.DataFrame({"Query": sugg[:50]}))


# ==========================
# Platform Research Tabs
# ==========================

st.subheader("🔍 Cross-Platform Research Insights")

tabs = st.tabs(["Google Search", "Meta Ads", "TikTok", "X (Twitter)"])

with tabs[0]:
    st.write("**Search intent & keyword universe**")
    st.dataframe(
        pd.DataFrame(
            {"Keyword / Query": platform_insights.get("google_keywords", [])}
        )
    )

with tabs[1]:
    st.write("**Meta interest & angle ideas**")
    st.dataframe(
        pd.DataFrame(
            {"Interests / Angles": platform_insights.get("meta_interests", [])}
        )
    )
    st.caption("Use these as interest targets, hooks, and creative angles in Meta Ads.")

with tabs[2]:
    st.write("**TikTok hashtag concepts**")
    st.dataframe(
        pd.DataFrame(
            {"Hashtag": platform_insights.get("tiktok_tags", [])}
        )
    )
    st.caption("Pair these with short-form video hooks for cold + warm audiences.")

with tabs[3]:
    st.write("**X (Twitter) topic & keyword angles**")
    st.dataframe(
        pd.DataFrame(
            {"Term": platform_insights.get("twitter_terms", [])}
        )
    )
    st.caption("Use these in X keyword targeting, Lists, and content threads.")


# ==========================
# Budget / Funnel + Export
# ==========================

st.subheader("📊 Budget Allocation & Funnel Split")

bc1, bc2 = st.columns(2)
with bc1:
    st.write("### Example Budget Breakdown")
    st.markdown(
        """
| Channel        | % Allocation | Description                    |
|----------------|--------------|--------------------------------|
| Google Search  | 40%          | High-intent search traffic     |
| Meta Ads       | 35%          | Retargeting & awareness        |
| TikTok         | 15%          | Discovery & trends             |
| X (Twitter)    | 10%          | Niche audience engagement      |
        """
    )
with bc2:
    st.write("### Funnel Split Example")
    st.markdown(
        """
| Funnel Stage   | % Budget | Objective              |
|----------------|----------|------------------------|
| Awareness      | 25%      | Reach, Video Views     |
| Consideration  | 35%      | Traffic, Engagement    |
| Conversion     | 40%      | Sales, Leads           |
        """
    )
st.success("Customize these numbers per niche as needed.")


st.subheader("🧾 Campaign Summary & Export")

ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
export_name = f"campaign_export_{ts}.json"

summary = {
    "niche": niche,
    "budget_usd": float(budget),
    "goal": goal,
    "locations": final_targets,
    "keywords": plan.get("keywords", []),
    "competitor_cities": ranked_cities,
    "competitor_states": ranked_states,
    "generated_at": ts,
}

# JSON export
json_buf = io.StringIO()
json.dump(summary, json_buf, indent=2)
st.download_button(
    label="⬇️ Download Campaign Plan (JSON)",
    data=json_buf.getvalue(),
    file_name=export_name,
    mime="application/json",
)

# Locations CSV export
loc_rows = [{"Target": t, "Match Type": "Location Name"} for t in final_targets]
loc_df = pd.DataFrame(loc_rows)
csv_buf = io.StringIO()
loc_df.to_csv(csv_buf, index=False)
st.download_button(
    "⬇️ Download google_ads_locations.csv",
    data=csv_buf.getvalue().encode("utf-8"),
    file_name="google_ads_locations.csv",
    mime="text/csv",
) 
