# ==========================
# Sully — Streamlit App
# Clean full replacement
# ==========================

import os
import sys
from pathlib import Path
from datetime import datetime
import io
import json

import streamlit as st
import pandas as pd

# --- Make repo root importable so we can import bot/core.py ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# Import your strategy function
# Expecting: bot/core.py -> def generate_strategy(niche, budget, goal, geo, competitors:list) -> dict
from bot.core import generate_strategy  # noqa: E402


# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Sully's Marketing Bot", page_icon="💼", layout="wide")


# -------------------------
# Sidebar inputs
# -------------------------
with st.sidebar:
    st.header("Inputs")

    niche = st.selectbox("Niche", ["clothing", "consignment", "musician", "homecare"])
    budget = st.number_input("Monthly Budget (USD)", min_value=100.0, value=2500.0, step=50.0)
    goal = st.selectbox("Primary Goal", ["sales", "conversions", "leads", "awareness", "traffic"])

    st.markdown("### Location mode")
    loc_mode = st.radio("Choose how to target", ["Country", "States", "Cities", "ZIPs", "Radius"], horizontal=True)

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
        st.caption("Enter city names")
        cities_raw = st.text_area("Cities list", value="")
    elif loc_mode == "ZIPs":
        st.caption("Enter ZIPs")
        zips_raw = st.text_area("ZIP list", value="")
    elif loc_mode == "Radius":
        radius_center = st.text_input("Center address")
        radius_miles = st.number_input("Radius (miles)", min_value=1, max_value=100, value=15)

    st.markdown("### Competitor URLs")
    comp_text = st.text_area(
        "One per line",
        placeholder="https://example.com\nhttps://competitor.com/locations"
    )
    competitors = [c.strip() for c in comp_text.split("\n") if c.strip()]

# -------------------------
# Google Trends Insights
# -------------------------
st.subheader("📈 Google Trends Insights")

@st.cache_data(ttl=3600, show_spinner=False)
def get_trends(seed_terms, geo="US", timeframe="today 12-m", gprop=""):
    """
    seed_terms: list[str]
    geo: e.g. "US", "GB", "US-CT", "" for worldwide
    timeframe: "now 7-d", "today 3-m", "today 12-m", "today 5-y"
    gprop: "", "news", "images", "youtube", "froogle"
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
        reg = pytrends.interest_by_region(resolution="REGION", inc_low_vol=True, inc_geo_code=True)
        if isinstance(reg, pd.DataFrame) and not reg.empty:
            first = seed_terms[0]
            if first in reg.columns:
                reg = reg.sort_values(first, ascending=False)
            out["by_region"] = reg

        # Related queries (top + rising)
        rq = pytrends.related_queries()
        suggestions = []
        if isinstance(rq, dict):
            for term, buckets in rq.items():
                for key in ("top", "rising"):
                    df = buckets.get(key)
                    if isinstance(df, pd.DataFrame) and "query" in df.columns:
                        suggestions.extend(df["query"].dropna().astype(str).tolist())

        # De-dupe suggestions
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

# ---- Build seed terms list ----
tr_seed_terms = []
if 'trend_seeds_raw' in locals() and trend_seeds_raw.strip():
    # user-specified seeds from sidebar
    for chunk in trend_seeds_raw.replace(",", "\n").split("\n"):
        v = chunk.strip()
        if v:
            tr_seed_terms.append(v)
else:
    # auto-pick from plan keywords if none typed
    auto = plan.get("keywords", [])
    for k in auto:
        k = str(k)
        if 2 <= len(k.split()) <= 4:
            tr_seed_terms.append(k)
        if len(tr_seed_terms) >= 5:
            break
    if not tr_seed_terms and auto:
        tr_seed_terms = [str(auto[0])]

if use_trends and tr_seed_terms:
    geo_for_trends = country if loc_mode == "Country" else "US"
    tr = get_trends(tr_seed_terms, geo=geo_for_trends, timeframe=timeframe, gprop=gprop)

    if tr.get("error"):
        st.warning(f"Trends error: {tr['error']}")
    else:
        iot = tr.get("interest_over_time")
        if isinstance(iot, pd.DataFrame) and not iot.empty:
            st.write("**Interest over time**")
            st.line_chart(iot)

        by_region = tr.get("by_region")
        if isinstance(by_region, pd.DataFrame) and not by_region.empty:
            st.write("**Top regions (by interest)**")
            st.dataframe(by_region.head(25))

        sugg = tr.get("related_suggestions", [])
        if sugg:
            st.write("**Related queries (Top + Rising)**")
            st.dataframe(pd.DataFrame({"Query": sugg[:50]}))
else:
    st.info("Add trend seed terms in the sidebar or let the bot auto-pick from your keywords.")


# -------------------------
# Budget Allocation (example tables)
# -------------------------
st.subheader("📊 Budget Allocation & Funnel Split")

c1, c2 = st.columns(2)
with c1:
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
with c2:
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
st.success("✅ Customize these values per niche to fit your audience strategy.")


# -------------------------
# Campaign Summary & Export
# -------------------------
st.subheader("🧾 Campaign Summary & Export")

md = f"# Strategy — {niche.title()} ({country}) — ${budget:,.0f}/mo\n*Goal:* {goal}\n"
md += "\n## Competitor Insights\n"
md += "\nTop keywords and target regions derived from competitor data.\n"

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
    "generated_at": ts
}
import os
import sys
from pathlib import Path
from datetime import datetime
import io
import json

import streamlit as st
import pandas as pd
from pytrends.request import TrendReq   # 👈 MOVE IMPORT HERE

# your other imports/helpers like generate_strategy, _split_list, etc.

# ============= GOOGLE TRENDS ENGINE =============
@st.cache_data(ttl=3600, show_spinner=False)
def get_trends(seed_terms, geo="US", timeframe="today 12-m", gprop=""):
    """
    Google Trends wrapper for Sully's bot.
    Returns:
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

        # Related queries
        rq = pytrends.related_queries()
        suggestions = []
        if isinstance(rq, dict):
            for term, buckets in rq.items():
                for key in ("top", "rising"):
                    df = buckets.get(key)
                    if isinstance(df, pd.DataFrame) and "query" in df.columns:
                        suggestions.extend(df["query"].dropna().astype(str).tolist())

        # De-dupe suggestions
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

    """
    Google Trends wrapper for Sully's bot.
    Returns:
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

        # dedupe
        uniq = []
        seen = set()
        for q in suggestions:
            if q not in seen:
                seen.add(q)
                uniq.append(q)
        out["related_suggestions"] = uniq[:100]

        return out

    except Exception as e:
        return {"error": str(e)}

# JSON export
json_buf = io.StringIO()
json.dump(summary, json_buf, indent=2)
st.download_button(
    label="⬇️ Download Campaign Plan (JSON)",
    data=json_buf.getvalue(),
    file_name=export_name,
    mime="application/json"\

# Optional: Locations CSV export for Ads/Editor
st.markdown("#### Export: Google Ads Locations CSV")
loc_rows = [{"Target": t, "Match Type": "Location Name"} for t in final_targets]
loc_df = pd.DataFrame(loc_rows)
csv_buf = io.StringIO()
loc_df.to_csv(csv_buf, index=False)
st.download_button(
    "⬇️ Download google_ads_locations.csv",
    data=csv_buf.getvalue().encode("utf-8"),
    file_name="google_ads_locations.csv",
    mime="text/csv"
)

st.markdown("---")
st.info("💡 Use the JSON with your Google Ads API uploader, and the CSV for bulk location adds in Ads or Ads Editor.")
