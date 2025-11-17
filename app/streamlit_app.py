# ==========================
# Sully's Marketing Bot
# Full replacement: light theme, logo header, multi-platform estimates, Trends
# ==========================

import os
import sys
from pathlib import Path
from datetime import datetime
import io
import json

import streamlit as st
import pandas as pd

# Try to import Google Trends, but don't crash if missing
try:
    from pytrends.request import TrendReq
    HAS_TRENDS = True
except ImportError:
    HAS_TRENDS = False

# ---- Make repo root importable so we can import /bot/core.py ----
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# Import your strategy generator
# Expecting bot/core.py to have: def generate_strategy(niche, budget, goal, geo, competitors) -> dict
from bot.core import generate_strategy  # type: ignore


# ==========================
# Basic helpers
# ==========================

LOGO_PATH = Path(__file__).with_name("sullivan_logo.png")


def _split_list(raw: str):
    """Split comma/newline-separated text into a clean unique list."""
    if not raw:
        return []
    parts = []
    for chunk in raw.replace(",", "\n").split("\n"):
        v = chunk.strip()
        if v:
            parts.append(v)
    # Keep order but unique
    seen = set()
    out = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def estimate_platform_metrics(platform: str, goal: str, budget: float, avg_value: float):
    """
    Very rough heuristic estimator for reach, clicks, conversions, and ROI.
    These are NOT live platform numbers – just planning estimates.
    """

    # Baseline CPM and CTR per platform (very rough typical ranges)
    platform_cpm = {
        "Meta": 8.0,
        "Google": 12.0,  # assume search/display mix
        "TikTok": 6.0,
        "X (Twitter)": 7.0,
    }

    platform_ctr = {
        "Meta": 0.015,
        "Google": 0.03,
        "TikTok": 0.012,
        "X (Twitter)": 0.01,
    }

    # Conversion rate multipliers by goal
    # awareness < traffic/engagement < conversion/sales
    goal_cvr = {
        "awareness": 0.002,
        "traffic": 0.004,
        "leads": 0.015,
        "conversions": 0.02,
        "sales": 0.02,
    }

    # Normalize goal key
    gkey = goal.lower()
    if gkey not in goal_cvr:
        gkey = "conversions"

    cpm = platform_cpm.get(platform, 10.0)
    ctr = platform_ctr.get(platform, 0.015)
    base_cvr = goal_cvr[gkey]

    # Impressions, reach, clicks
    impressions = (budget / cpm) * 1000.0
    # For planning, treat reach ~ 0.7 * impressions (frequency ~1.4)
    reach = impressions * 0.7
    clicks = impressions * ctr
    conversions = clicks * base_cvr

    revenue = conversions * avg_value
    profit = revenue - budget
    roi_pct = (profit / budget * 100.0) if budget > 0 else 0.0

    return {
        "platform": platform,
        "goal": gkey,
        "budget": budget,
        "impressions": round(impressions),
        "reach": round(reach),
        "clicks": round(clicks),
        "conversions": round(conversions, 2),
        "revenue": round(revenue, 2),
        "profit": round(profit, 2),
        "roi_pct": round(roi_pct, 1),
    }


# ==========================
# Google Trends helper
# ==========================

@st.cache_data(ttl=3600, show_spinner=False)
def get_trends(seed_terms, geo="US", timeframe="today 12-m", gprop=""):
    """
    Google Trends wrapper for Sully's bot.
    Returns dict with (may be empty if Trends not available):
      - interest_over_time (DataFrame)
      - by_region (DataFrame)
      - related_suggestions (list[str])
    """
    if not HAS_TRENDS or not seed_terms:
        return {}

    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(seed_terms, timeframe=timeframe, geo=geo, gprop=gprop)

        out = {}

        # Interest Over Time
        iot = pytrends.interest_over_time()
        if isinstance(iot, pd.DataFrame) and not iot.empty:
            if "isPartial" in iot.columns:
                iot = iot.drop(columns=["isPartial"])
            out["interest_over_time"] = iot

        # Region Interest
        reg = pytrends.interest_by_region(resolution="REGION", inc_low_vol=True, inc_geo_code=True)
        if isinstance(reg, pd.DataFrame) and not reg.empty:
            first = seed_terms[0]
            if first in reg.columns:
                reg = reg.sort_values(first, ascending=False)
            out["by_region"] = reg

        # Related Queries
        rq = pytrends.related_queries()
        suggestions = []
        if isinstance(rq, dict):
            for term, buckets in rq.items():
                for key in ("top", "rising"):
                    df = buckets.get(key)
                    if isinstance(df, pd.DataFrame) and "query" in df.columns:
                        suggestions.extend(df["query"].dropna().astype(str).tolist())

        # De-dupe
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


# ==========================
# Streamlit page config & style
# ==========================

st.set_page_config(page_title="Sully's Marketing Bot", page_icon="💼", layout="wide")

# Light theme / readable font
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f5f5;
    }
    html, body, [class*="css"] {
        color: #111111;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-size: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================
# Sidebar inputs
# ==========================

with st.sidebar:
    st.header("Inputs")

    niche = st.selectbox("Niche", ["clothing", "consignment", "musician", "homecare"])
    budget = st.number_input("Monthly Budget (USD)", min_value=100.0, value=2500.0, step=50.0)
    avg_value = st.number_input("Avg Conversion Value (USD)", min_value=1.0, value=80.0, step=5.0)

    goal = st.selectbox(
        "Primary Goal",
        ["awareness", "traffic", "leads", "conversions", "sales"],
        index=3,
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
        st.caption("Enter city names (commas or new lines)")
        cities_raw = st.text_area("Cities list", value="")
    elif loc_mode == "ZIPs":
        st.caption("Enter ZIPs (commas or new lines)")
        zips_raw = st.text_area("ZIP list", value="")
    elif loc_mode == "Radius":
        radius_center = st.text_input("Center address (e.g. city or full address)")
        radius_miles = st.number_input("Radius (miles)", min_value=1, max_value=100, value=15)

    st.markdown("### Competitor URLs")
    comp_text = st.text_area(
        "One per line",
        placeholder="https://example.com\nhttps://competitor.com/locations",
    )
    competitors = [c.strip() for c in comp_text.split("\n") if c.strip()]

    st.markdown("### Google Trends")
    use_trends = st.checkbox("Use Google Trends insights", value=True)
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
    trend_seeds_raw = st.text_area(
        "Trend seed terms (comma/newline)",
        placeholder="streetwear, trap music, caregiver services",
        value="",
    )

    run = st.button("Generate Plan", type="primary")


# ==========================
# Build strategy plan
# ==========================

if run:
    # Derive human-readable geo
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
        selected_zips = [z.strip()[:5] if z and z[0].isdigit() else z for z in selected_zips]
        geo = ", ".join(selected_zips) if selected_zips else country
    else:  # Radius
        geo = f"{radius_miles}mi around {radius_center}" if radius_center else country

    plan = generate_strategy(niche, float(budget), goal, geo, competitors)
    st.success("✅ Plan generated!")
else:
    # Safe empty default
    geo = country
    plan = {"insights": {}, "keywords": []}

# Rebuild target lists for main section
selected_states = _split_list(states_raw) if loc_mode == "States" else []
selected_cities = _split_list(cities_raw) if loc_mode == "Cities" else []
selected_zips = _split_list(zips_raw) if loc_mode == "ZIPs" else []


# ==========================
# Header with logo
# ==========================

header_cols = st.columns([1, 3])
with header_cols[0]:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), caption="", use_column_width=False, width=180)
with header_cols[1]:
    st.title("Sully's Marketing Bot")
    st.write(
        f"Smart planning for **{niche}** campaigns in **{geo}** with a monthly budget of "
        f"**${budget:,.0f}** and goal **{goal.title()}**."
    )


# ==========================
# Target Locations
# ==========================

st.subheader("🎯 Target Locations")

ins = plan.get("insights", {})
ranked_cities = ins.get("cities_ranked", []) or []
ranked_states = ins.get("states_ranked", []) or []
ranked_zips = ins.get("zips_ranked", []) or []

if loc_mode == "Country":
    chosen_locs = [country]
elif loc_mode == "States":
    chosen_locs = selected_states or ranked_states[:10]
elif loc_mode == "Cities":
    chosen_locs = selected_cities or ranked_cities[:15]
elif loc_mode == "ZIPs":
    chosen_locs = selected_zips or ranked_zips[:50]
else:
    chosen_locs = [f"RADIUS {radius_miles}mi around {radius_center}"] if radius_center else [country]

chosen = st.text_area("Final targets (edit before export)", value="\n".join(chosen_locs))
final_targets = [t.strip() for t in chosen.split("\n") if t.strip()]

st.caption("You can paste these into Google Ads / Meta location targeting or Ads Editor bulk tools.")

loc_cols = st.columns(2)
with loc_cols[0]:
    st.write("**Keyword ideas**")
    st.dataframe(pd.DataFrame({"Keywords": plan.get("keywords", [])}))
with loc_cols[1]:
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
# Multi-platform estimates (Meta, Google, TikTok, X)
# ==========================

st.subheader("📊 Multi-Platform Reach, Conversions & ROI (Estimates)")

platforms = ["Meta", "Google", "TikTok", "X (Twitter)"]
rows = []
for p in platforms:
    rows.append(estimate_platform_metrics(p, goal, float(budget) / len(platforms), float(avg_value)))

df_est = pd.DataFrame(rows)
st.dataframe(
    df_est[["platform", "budget", "impressions", "reach", "clicks", "conversions", "revenue", "profit", "roi_pct"]],
    use_container_width=True,
)

st.caption(
    "These numbers are rough planning estimates using heuristic CPM/CTR/CVR values per platform — "
    "they are not live data from Meta/Google/TikTok/X."
)


# ==========================
# Google Trends Insights
# ==========================

st.subheader("📈 Google Trends Insights")

tr_seed_terms = []
if trend_seeds_raw.strip():
    for chunk in trend_seeds_raw.replace(",", "\n").split("\n"):
        v = chunk.strip()
        if v:
            tr_seed_terms.append(v)
else:
    # Auto-pick from plan keywords
    auto = plan.get("keywords", [])
    for k in auto:
        k = str(k)
        if 1 <= len(k.split()) <= 4:
            tr_seed_terms.append(k)
        if len(tr_seed_terms) >= 5:
            break

if use_trends and HAS_TRENDS and tr_seed_terms:
    geo_for_trends = country if country else "US"
    tr = get_trends(tr_seed_terms, geo=geo_for_trends, timeframe=timeframe, gprop=gprop)

    if tr.get("error"):
        st.warning(f"Trends error: {tr['error']}")
    else:
        iot = tr.get("interest_over_time")
        if isinstance(iot, pd.DataFrame) and not iot.empty:
            st.write("**Interest Over Time**")
            st.line_chart(iot)

        by_region = tr.get("by_region")
        if isinstance(by_region, pd.DataFrame) and not by_region.empty:
            st.write("**Top Regions by Interest**")
            st.dataframe(by_region.head(25))

        sugg = tr.get("related_suggestions", [])
        if sugg:
            st.write("**Related Queries (Top + Rising)**")
            st.dataframe(pd.DataFrame({"Query": sugg[:50]}))
else:
    if not HAS_TRENDS:
        st.info("pytrends is not installed – install it in requirements.txt to enable Google Trends.")
    else:
        st.info("Add trend seed terms in the sidebar or let the bot auto-pick from your plan keywords.")


# ==========================
# Campaign Summary & Export (Plan + ROI overview)
# ==========================

st.subheader("🧾 Campaign Summary & Export")

ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
export_name = f"campaign_export_{ts}.json"

summary = {
    "niche": niche,
    "budget_usd": float(budget),
    "avg_conversion_value": float(avg_value),
    "goal": goal,
    "geo": geo,
    "locations": final_targets,
    "keywords": plan.get("keywords", []),
    "platform_estimates": df_est.to_dict(orient="records"),
    "generated_at_utc": ts,
}

json_buf = io.StringIO()
json.dump(summary, json_buf, indent=2)

st.download_button(
    label="⬇️ Download Campaign Plan (JSON)",
    data=json_buf.getvalue(),
    file_name=export_name,
    mime="application/json",
)

st.markdown("---")
st.info(
    "Use this bot as a planning tool: estimates are directional only and not financial advice. "
    "Always verify performance with real platform data."
)
