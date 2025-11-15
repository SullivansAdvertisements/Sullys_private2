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

    # Country (simple text to avoid extra libs)
    country = st.text_input("Country (ISO/name)", value="US")

    # Simple, widely-compatible inputs (avoid non-standard widgets)
    states_raw = cities_raw = zips_raw = ""
    radius_center = ""
    radius_miles = 15

    if loc_mode == "States":
        st.caption("Enter states or abbreviations separated by commas or new lines (e.g., CA, TX, Florida)")
        states_raw = st.text_area("States list", value="")
    elif loc_mode == "Cities":
        st.caption("Enter city names separated by commas or new lines (e.g., Austin, Miami)")
        cities_raw = st.text_area("Cities list", value="")
    elif loc_mode == "ZIPs":
        st.caption("Enter ZIPs separated by commas or new lines (e.g., 78701, 10001)")
        zips_raw = st.text_area("ZIP list", value="")
    elif loc_mode == "Radius":
        radius_center = st.text_input("Center address", value="")
        radius_miles = st.number_input("Radius (miles)", min_value=1, max_value=100, value=15)

    st.markdown("### Competitor URLs")
    comp_text = st.text_area(
        "One per line",
        placeholder="https://example.com\nhttps://competitor.com/locations"
    )
    competitors = [c.strip() for c in comp_text.split("\n") if c.strip()]

    run = st.button("Generate Plan", type="primary")


# -------------------------
# Helpers
# -------------------------
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


# -------------------------
# Build the plan when requested
# -------------------------
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
        # Normalize ZIPs to first 5 if they look like ZIP+4
        selected_zips = [z.strip()[:5] if z and z[0].isdigit() else z for z in selected_zips]
        geo = ", ".join(selected_zips) if selected_zips else country
    else:  # Radius
        geo = f"{radius_miles}mi around {radius_center}" if radius_center else country

    # Generate the plan via your core function
    plan = generate_strategy(niche, float(budget), goal, geo, competitors)
    st.success("✅ Plan generated!")

# Ensure the app doesn't crash before user clicks the button
if 'plan' not in locals():
    plan = {"insights": {}, "keywords": []}


# -------------------------
# Target Locations section
# -------------------------
st.subheader("🎯 Target Locations")

# Pull ranked locations from plan insights if present
ins = plan.get("insights", {})
ranked_cities = ins.get("cities_ranked", []) or []
ranked_states = ins.get("states_ranked", []) or []
ranked_zips = ins.get("zips_ranked", []) or []

# Recreate selection lists from sidebar raw text (for display/edit)
selected_states = _split_list(states_raw) if loc_mode == "States" else []
selected_cities = _split_list(cities_raw) if loc_mode == "Cities" else []
selected_zips = _split_list(zips_raw) if loc_mode == "ZIPs" else []

# Seed from your mode OR fallback to competitor ranks
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

# Let user tweak final list
chosen = st.text_area("Final targets (edit before export)", value="\n".join(chosen_locs))
final_targets = [t.strip() for t in chosen.split("\n") if t.strip()]

st.caption("Tip: You can paste city/state/ZIP lists directly into Google Ads (bulk add) or Ads Editor.")

colA, colB = st.columns(2)
colA.write("**Keyword ideas**")
colA.dataframe(pd.DataFrame({"Keywords": plan.get("keywords", [])}))

colB.write("**Top competitor locations**")
colB.dataframe(pd.DataFrame({
    "Cities": ranked_cities[:20] if ranked_cities else [],
    "States": ranked_states[:20] if ranked_states else []
}))
# ---- Safety: define Trends controls if sidebar wasn't added yet ----
if 'trend_seeds_raw' not in locals(): trend_seeds_raw = ""
if 'use_trends' not in locals(): use_trends = False
if 'timeframe' not in locals(): timeframe = "today 12-m"
if 'gprop' not in locals(): gprop = ""
if 'country' not in locals(): country = "US"

# -------------------------
# Google Trends Enrichment
# -------------------------
st.subheader("📈 Google Trends Insights")

tr_seed_terms = []
if trend_seeds_raw.strip():
    # user-specified seeds
    for chunk in trend_seeds_raw.replace(",", "\n").split("\n"):
        v = chunk.strip()
        if v:
            tr_seed_terms.append(v)
else:
    # auto-pick from plan keywords
    auto = plan.get("keywords", [])
    # pick up to 5 short, high-intent seeds
    for k in auto:
        k = str(k)
        if 2 <= len(k.split()) <= 4:  # avoid super long phrases
            tr_seed_terms.append(k)
        if len(tr_seed_terms) >= 5:
            break
    if not tr_seed_terms and auto:
        tr_seed_terms = [str(auto[0])]

if use_trends and tr_seed_terms:
    geo_for_trends = country if loc_mode == "Country" else "US"  # simple default
    tr = get_trends(tr_seed_terms, geo=geo_for_trends, timeframe=timeframe, gprop=gprop)

    if tr.get("error"):
        st.warning(f"Trends error: {tr['error']}")
    else:
        # Interest over time chart
        iot = tr.get("interest_over_time")
        if isinstance(iot, pd.DataFrame) and not iot.empty:
            st.write("**Interest over time**")
            st.line_chart(iot)

        # Top regions dataframe
        by_region = tr.get("by_region")
        if isinstance(by_region, pd.DataFrame) and not by_region.empty:
            st.write("**Top regions (by interest)**")
            st.dataframe(by_region.head(25))

            # Offer to append top regions to targeting
            add_regions = st.checkbox("Append top regions to targeting", value=False)
            if add_regions:
                # Grab top 10 region names (index)
                top_names = [str(idx) for idx in by_region.head(10).index.tolist()]
                # Merge into final_targets textarea
                merged = final_targets + [n for n in top_names if n not in final_targets]
                final_targets[:] = merged  # mutate the list
                # Re-render the textarea
                st.success("Added top regions to targeting.")

        # Related queries (suggestions)
        sugg = tr.get("related_suggestions", [])
        if sugg:
            st.write("**Related queries (Top + Rising)**")
            st.dataframe(pd.DataFrame({"Query": sugg[:50]}))

            # Offer to append 10 related queries as Broad keywords
            add_kw = st.checkbox("Append 10 related queries to keywords (as Broad)", value=False)
            if add_kw:
                base = plan.get("keywords", [])
                extra = [f"+{q.replace(' ', ' +')}" for q in sugg[:10]]
                plan["keywords"] = base + extra
                st.success("Added related queries to keywords.")
else:
    st.info("Add trend seed terms or let the bot auto-pick from your plan keywords.")

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

# JSON export
json_buf = io.StringIO()
json.dump(summary, json_buf, indent=2)
st.download_button(
    label="⬇️ Download Campaign Plan (JSON)",
    data=json_buf.getvalue(),
    file_name=export_name,
    mime="application/json"
)

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
