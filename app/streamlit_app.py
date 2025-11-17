# ==========================
# Sully's Marketing Bot
# Clean full replacement with logo placements + background
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
# Logo + Background helpers
# ==========================

LOGO_PATH = Path(__file__).with_name("sullivan_logo.png")

def set_background_from_logo():
    """Use the logo as a subtle tiled background if file exists."""
    if not LOGO_PATH.exists():
        return
    try:
        img_bytes = LOGO_PATH.read_bytes()
        encoded = base64.b64encode(img_bytes).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded}");
                background-repeat: no-repeat;
                background-size: contain;
                background-position: center;
                background-attachment: fixed;
                background-color: #050810;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        # Fail silently if anything goes wrong
        pass


def show_logo_header():
    """Top row: logo on the left, title on the right."""
    col_logo, col_title = st.columns([1, 3])
    if LOGO_PATH.exists():
        col_logo.image(str(LOGO_PATH), use_column_width=True)
    else:
        col_logo.write("🔲 (sullivan_logo.png missing)")
    col_title.markdown(
        "<h1 style='margin-bottom:0;'>Sully's New & Improved Marketing Bot</h1>"
        "<p style='color:#cccccc;'>Cross-platform strategy builder for Clothing, Consignment, Musicians & Home Care.</p>",
        unsafe_allow_html=True,
    )


# ==========================
# Optional: Google Trends helper
# ==========================

@st.cache_data(ttl=3600, show_spinner=False)
def get_trends(seed_terms, geo="US", timeframe="today 12-m", gprop=""):
    """
    Wrapper around Google Trends (pytrends).
    Returns dict with:
      - interest_over_time (DataFrame) or None
      - by_region (DataFrame) or None
      - related_suggestions (list[str])
    Never raises an exception to Streamlit.
    """
    if not HAS_TRENDS or not seed_terms:
        return {}

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
    except Exception:
        return {}


# ==========================
# Streamlit page config
# ==========================

st.set_page_config(
    page_title="Sully's Marketing Bot",
    page_icon="💼",
    layout="wide",
)

# Set background based on logo
set_background_from_logo()


# ==========================
# Sidebar
# ==========================

with st.sidebar:
    # Logo in sidebar
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)
    else:
        st.write("🔲 Upload app/sullivan_logo.png to show logo here.")

    st.header("Inputs")

    niche = st.selectbox("Niche", ["clothing", "consignment", "musician", "homecare"])
    budget = st.number_input("Monthly Budget (USD)", min_value=100.0, value=2500.0, step=50.0)
    goal = st.selectbox("Primary Goal", ["sales", "conversions", "leads", "awareness", "traffic"])

    st.markdown("### Location mode")
    loc_mode = st.radio("Choose how to target", ["Country", "States", "Cities", "ZIPs", "Radius"], horizontal=True)

    country = st.text_input("Country (ISO code or name)", value="US")

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
        st.caption("Enter ZIP codes separated by commas or new lines")
        zips_raw = st.text_area("ZIP list", value="")
    elif loc_mode == "Radius":
        radius_center = st.text_input("Center address (e.g., Bridgeport, CT)")
        radius_miles = st.number_input("Radius (miles)", min_value=1, max_value=100, value=15)

    st.markdown("### Competitor URLs")
    comp_text = st.text_area(
        "One per line",
        placeholder="https://example.com\nhttps://competitor.com/locations",
    )
    competitors = [c.strip() for c in comp_text.split("\n") if c.strip()]

    st.markdown("### Google Trends (optional)")
    use_trends = st.checkbox("Use Google Trends boost", value=False if not HAS_TRENDS else True)
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
    )

    run = st.button("Generate Plan", type="primary")


# ==========================
# Helpers
# ==========================

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
# Main Layout
# ==========================

show_logo_header()

st.markdown("---")

# --- build plan when button pressed ---
if run:
    # derive geo string
    if loc_mode == "Country":
        geo = country
    elif loc_mode == "States":
        selected_states = split_list(states_raw)
        geo = ", ".join(selected_states) if selected_states else country
    elif loc_mode == "Cities":
        selected_cities = split_list(cities_raw)
        geo = ", ".join(selected_cities) if selected_cities else country
    elif loc_mode == "ZIPs":
        selected_zips = split_list(zips_raw)
        selected_zips = [z.strip()[:5] if z and z[0].isdigit() else z for z in selected_zips]
        geo = ", ".join(selected_zips) if selected_zips else country
    else:
        geo = f"{radius_miles}mi around {radius_center}" if radius_center else country

    plan = generate_strategy(niche, float(budget), goal, geo, competitors)
    st.success("✅ Plan generated!")

# safe fallback so app loads on first open
if "plan" not in locals():
    plan = {"insights": {}, "keywords": []}

ins = plan.get("insights", {}) or {}
ranked_cities = ins.get("cities_ranked", []) or []
ranked_states = ins.get("states_ranked", []) or []
ranked_zips = ins.get("zips_ranked", []) or []
keywords = plan.get("keywords", []) or []

# ---------- Target Locations ----------
st.subheader("🎯 Target Locations")

selected_states = split_list(states_raw) if loc_mode == "States" else []
selected_cities = split_list(cities_raw) if loc_mode == "Cities" else []
selected_zips = split_list(zips_raw) if loc_mode == "ZIPs" else []

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

st.caption("Tip: Paste this into Google Ads bulk location add or Ads Editor.")

c1, c2 = st.columns(2)
c1.write("**Keyword ideas**")
c1.dataframe(pd.DataFrame({"Keywords": keywords}))

c2.write("**Top competitor locations**")
c2.dataframe(pd.DataFrame({
    "Cities": ranked_cities[:20],
    "States": ranked_states[:20],
}))

# ---------- Google Trends Insights ----------
st.subheader("📈 Google Trends Insights")

trend_seeds = []
if trend_seeds_raw.strip():
    trend_seeds = split_list(trend_seeds_raw)
else:
    for k in keywords:
        k = str(k)
        if 1 <= len(k.split()) <= 3:
            trend_seeds.append(k)
        if len(trend_seeds) >= 5:
            break

if use_trends and HAS_TRENDS and trend_seeds:
    geo_for_trends = country if country else "US"
    tr = get_trends(trend_seeds, geo=geo_for_trends, timeframe=timeframe, gprop=gprop)

    iot = tr.get("interest_over_time")
    if isinstance(iot, pd.DataFrame) and not iot.empty:
        st.write("**Interest over time**")
        st.line_chart(iot)

    by_region = tr.get("by_region")
    if isinstance(by_region, pd.DataFrame) and not by_region.empty:
        st.write("**Top regions by interest**")
        st.dataframe(by_region.head(20))

    sugg = tr.get("related_suggestions", [])
    if sugg:
        st.write("**Related queries**")
        st.dataframe(pd.DataFrame({"Query": sugg[:50]}))
else:
    if not HAS_TRENDS:
        st.info("Install pytrends and add it to requirements.txt to enable Google Trends.")
    else:
        st.info("Add trend seeds in the sidebar or generate a plan to auto-pick keywords.")


# ---------- Budget Allocation ----------
st.subheader("📊 Budget Allocation & Funnel Split")

bc1, bc2 = st.columns(2)
with bc1:
    st.write("### Example Budget Breakdown")
    st.markdown(
        """
| Channel        | % Allocation | Description                |
|----------------|--------------|----------------------------|
| Google Search  | 40%          | High-intent search traffic |
| Meta Ads       | 35%          | Retargeting & awareness    |
| TikTok         | 15%          | Discovery & trends         |
| X (Twitter)    | 10%          | Niche engagement           |
        """
    )
with bc2:
    st.write("### Funnel Split Example")
    st.markdown(
        """
| Funnel Stage   | % Budget | Objective           |
|----------------|----------|---------------------|
| Awareness      | 25%      | Reach, Video Views  |
| Consideration  | 35%      | Traffic, Engagement |
| Conversion     | 40%      | Sales, Leads        |
        """
    )

st.success("✅ Customize these values per niche to fit your audience strategy.")


# ---------- Summary & Export ----------
st.subheader("🧾 Campaign Summary & Export")

ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
export_name = f"campaign_export_{ts}.json"

summary = {
    "niche": niche,
    "budget_usd": float(budget),
    "goal": goal,
    "locations": final_targets,
    "keywords": keywords,
    "competitor_cities": ranked_cities,
    "competitor_states": ranked_states,
    "generated_at": ts,
}

json_buf = io.StringIO()
json.dump(summary, json_buf, indent=2)

st.download_button(
    label="⬇️ Download Campaign Plan (JSON)",
    data=json_buf.getvalue(),
    file_name=export_name,
    mime="application/json",
)

loc_rows = [{"Target": t, "Match Type": "Location Name"} for t in final_targets]
loc_df = pd.DataFrame(loc_rows)
csv_buf = io.StringIO()
loc_df.to_csv(csv_buf, index=False)

st.download_button(
    label="⬇️ Download google_ads_locations.csv",
    data=csv_buf.getvalue().encode("utf-8"),
    file_name="google_ads_locations.csv",
    mime="text/csv",
)

st.markdown("---")
st.info("💡 Logo appears in header, sidebar, and background when app/sullivan_logo.png exists in the repo.")
