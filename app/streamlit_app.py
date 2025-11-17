# ==========================
# Sully's Marketing Bot
# Light theme, header logo, no background
# ==========================

import os
import sys
from pathlib import Path
from datetime import datetime
import io
import json

import streamlit as st
import pandas as pd

# Optional: Google Trends, guarded so it never breaks the app if missing
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

# -------------------------
# Page config (we design for light theme)
# -------------------------
st.set_page_config(
    page_title="Sully's Marketing Bot",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Note: actual light/dark theme is controlled in .streamlit/config.toml or Streamlit Cloud settings.


# ==========================
# Logo + Header
# ==========================

LOGO_PATH = Path(__file__).with_name("sullivan_logo.png")


def show_header():
    """Top header with transparent logo and clean light look."""
    st.markdown(
        """
        <style>
        /* Remove any dark background tweaks and keep it clean */
        .stApp {
            background-color: #ffffff;
        }
        /* Make text readable and slightly larger */
        html, body, [class*="css"]  {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: #111827;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_logo, col_title = st.columns([1, 4])

    with col_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_column_width=True)
        else:
            st.write("")

    with col_title:
        st.title("Sully's Marketing Bot")
        st.caption("Multi-niche digital marketing strategist for Google Ads, Meta, TikTok, X, and more.")


# ==========================
# Helpers
# ==========================

def _split_list(raw: str):
    """Split comma/newline-separated text into a clean unique list."""
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
# Sidebar Controls
# ==========================

with st.sidebar:
    st.header("Inputs")

    niche = st.selectbox("Niche", ["clothing", "consignment", "musician", "homecare"])
    budget = st.number_input("Monthly Budget (USD)", min_value=100.0, value=2500.0, step=50.0)
    goal = st.selectbox("Primary Goal", ["sales", "conversions", "leads", "awareness", "traffic"])

    st.markdown("### Location mode")
    loc_mode = st.radio(
        "Choose how to target",
        ["Country", "States", "Cities", "ZIPs", "Radius"],
        horizontal=False,
    )

    country = st.text_input("Country (ISO/name)", value="US")

    states_raw = ""
    cities_raw = ""
    zips_raw = ""
    radius_center = ""
    radius_miles = 15

    if loc_mode == "States":
        st.caption("Enter states or abbreviations separated by commas or new lines")
        states_raw = st.text_area("States list", value="")
    elif loc_mode == "Cities":
        st.caption("Enter city names separated by commas or new lines")
        cities_raw = st.text_area("Cities list", value="")
    elif loc_mode == "ZIPs":
        st.caption("Enter ZIPs separated by commas or new lines")
        zips_raw = st.text_area("ZIP list", value="")
    elif loc_mode == "Radius":
        radius_center = st.text_input("Center address")
        radius_miles = st.number_input("Radius (miles)", min_value=1, max_value=100, value=15)

    st.markdown("### Competitor URLs")
    comp_text = st.text_area(
        "One per line",
        placeholder="https://example.com\nhttps://competitor.com/locations",
    )
    competitors = [c.strip() for c in comp_text.split("\n") if c.strip()]

    # --- Google Trends controls (UI only; safe even if pytrends is missing) ---
    st.markdown("### Google Trends (optional)")
    use_trends = st.checkbox("Use Google Trends boost (UI only for now)", value=False)

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
        placeholder="streetwear, vintage clothing\ntrap beats\ncaregiver services",
    )

    run = st.button("Generate Plan", type="primary")


# ==========================
# Build Plan
# ==========================

if run:
    # Derive human-readable geo for strategy logic
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

# Ensure app doesn't crash before clicking the button
if "plan" not in locals():
    plan = {"insights": {}, "keywords": []}


# ==========================
# Main Layout
# ==========================

show_header()  # render header + logo

# ---------- Target Locations ----------
st.subheader("🎯 Target Locations")

ins = plan.get("insights", {})
ranked_cities = ins.get("cities_ranked", []) or []
ranked_states = ins.get("states_ranked", []) or []
ranked_zips = ins.get("zips_ranked", []) or []

# Recreate lists from sidebar
selected_states = _split_list(states_raw) if loc_mode == "States" else []
selected_cities = _split_list(cities_raw) if loc_mode == "Cities" else []
selected_zips = _split_list(zips_raw) if loc_mode == "ZIPs" else []

# Seed from mode or competitor ranks
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

st.caption("Tip: You can paste city/state/ZIP lists directly into Google Ads (bulk add) or Ads Editor.")

colA, colB = st.columns(2)
colA.write("**Keyword ideas**")
colA.dataframe(pd.DataFrame({"Keywords": plan.get("keywords", [])}))

colB.write("**Top competitor locations**")
colB.dataframe(pd.DataFrame({
    "Cities": ranked_cities[:20] if ranked_cities else [],
    "States": ranked_states[:20] if ranked_states else [],
}))


# ---------- Budget Allocation ----------
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


# ---------- Campaign Summary & Export ----------
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

# Locations CSV for Google Ads / Editor
st.markdown("#### Export: Google Ads Locations CSV")
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

st.markdown("---")
st.info("💡 Use the JSON with your Google Ads API uploader, and the CSV for bulk location adds in Ads or Ads Editor.")
