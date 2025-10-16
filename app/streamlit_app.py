import os
from datetime import datetime
from pathlib import Path
import streamlit as st
import pandas as pd
# --- make the repo root importable so Streamlit can see /bot folder ---
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bot.core import generate_strategy

st.set_page_config(page_title="Sullivan's Advertisements Bot", page_icon="🌿", layout="wide")

APP_PASS = os.getenv("SULLY_APP_PASSWORD","").strip()
if APP_PASS:
    if "auth_ok" not in st.session_state:
        st.session_state["auth_ok"] = False
    if not st.session_state["auth_ok"]:
        with st.form("login"):
            st.subheader("🔒 Private access")
            pw = st.text_input("Enter password", type="password")
            ok = st.form_submit_button("Enter")
        if ok:
            if pw == APP_PASS:
                st.session_state["auth_ok"] = True
                st.experimental_rerun()
            else:
                st.error("Incorrect password")
        st.stop()

logo_path = Path(__file__).parent / "../data" / "sullivans_logo.png"
if logo_path.exists():
    st.image(str(logo_path), width=220)
st.markdown("<h2 style='text-align:center;margin-top:0;'>Sully’s New & Improved Marketing Bot</h2>", unsafe_allow_html=True)
st.caption("Campaign Development System + Competitor Intelligence")
st.divider()

from bot.core import generate_strategy
with st.sidebar:
    st.header("Inputs")
    niche = st.selectbox("Niche", ["clothing", "consignment", "musician", "homecare"])
    budget = st.number_input("Monthly Budget (USD)", min_value=100.0, value=2500.0, step=50.0)
    goal = st.selectbox("Primary Goal", ["sales", "conversions", "leads", "awareness", "traffic"])

    st.markdown("### Location mode")
    loc_mode = st.radio("Choose how to target", ["Country", "States", "Cities", "ZIPs", "Radius"], horizontal=True)

    default_country = "US"
    country = st.text_input("Country (ISO code or name)", value=default_country)

    selected_states = []
    selected_cities = []
    selected_zips = []
    radius_center = ""
    radius_miles = 10

    if loc_mode == "States":
        st.caption("Type states or abbreviations, press Enter after each (e.g., CA, TX, Florida)")
        selected_states = st.tags_input("States", ["CA","TX"])
    elif loc_mode == "Cities":
        st.caption("Type city names, press Enter after each (e.g., Austin, Miami)")
        selected_cities = st.tags_input("Cities", ["Austin","Miami"])
    elif loc_mode == "ZIPs":
        st.caption("Paste ZIP codes or upload a CSV with a 'zip' column")
        zip_text = st.text_area("ZIPs (comma or newline separated)", "")
        uploaded = st.file_uploader("Optional: upload ZIP CSV", type=["csv"])
        if uploaded is not None:
            import pandas as pd
            try:
                df = pd.read_csv(uploaded)
                if "zip" in df.columns:
                    selected_zips = [str(z).strip() for z in df["zip"].dropna().astype(str).tolist()]
                    st.success(f"Loaded {len(selected_zips)} ZIPs from CSV")
            except Exception as e:
                st.error(f"CSV read error: {e}")
        if zip_text.strip():
            for piece in re.split(r"[,\s]+", zip_text.strip()):
                if piece.isdigit() and len(piece) in (5,9):
                    selected_zips.append(piece[:5])
        selected_zips = sorted(set(selected_zips))
    elif loc_mode == "Radius":
        radius_center = st.text_input("Center address (e.g., 123 Main St, Austin, TX)")
        radius_miles = st.number_input("Radius (miles)", min_value=1, max_value=100, value=15)

    st.markdown("### Competitor URLs")
    comp_text = st.text_area("One per line", placeholder="https://example.com\nhttps://competitor.com/locations")
    competitors = [c.strip() for c in comp_text.split("\n") if c.strip()]

    run = st.button("Generate Plan", type="primary")



if run:
    plan = generate_strategy(niche, budget, goal, geo, competitors)

    st.subheader("📌 Competitor Insights")
    colA, colB = st.columns(2)
    colA.write("**Keyword ideas**")
    colA.write(", ".join(plan.get("insights",{}).get("keywords", [])[:30]) or "—")
    colB.write("**Location hints**")
    colB.write(", ".join(plan.get("insights",{}).get("locations", [])[:20]) or "—")

    st.subheader("📊 Budget Allocation & Funnel Split")
    c1, c2 = st.columns(2)
    c1.bar_chart(pd.DataFrame(plan["allocation"], index=["%"]).T)
    c2.bar_chart(pd.DataFrame(plan["funnel_split"], index=["%"]).T)

    st.subheader("🧩 Campaign Development System — Platform Plans")
    for platform, cfg in plan["platforms"].items():
        with st.expander(f"{platform.upper()} — Development Plan", expanded=False):
            st.json(cfg)

    st.subheader("⬇️ Export")
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    md = f"# Strategy — {niche.title()} ({geo}) — ${budget:,.0f}/mo\n*Goal:* {goal}\n"
    md += "\n## Competitor Insights\n"
    md += "- Keywords: " + (", ".join(plan['insights'].get('keywords', [])[:30]) or "—") + "\n"
    md += "- Locations: " + (", ".join(plan['insights'].get('locations', [])[:20]) or "—") + "\n"
    md += "\n## Allocation\n" + "\n".join([f"- **{k}**: {v}%" for k,v in plan['allocation'].items()])
    md += "\n\n## Funnel Split\n" + "\n".join([f"- **{k}**: {v}%" for k,v in plan['funnel_split'].items()])
    md += "\n\n## Platforms\n"
    for p,cfg in plan["platforms"].items():
        md += f"\n### {p.upper()}\n- Objective: {cfg.get('objective','')}\n- Budget %: {cfg.get('budget_pct','?')}%\n"              f"- KPIs: {', '.join(cfg.get('kpis', []))}\n"
    st.download_button("Download plan.md", data=md.encode("utf-8"), file_name="plan.md", mime="text/markdown")
else:
    st.info("Select a niche, add budget & goal, paste competitor links (optional), then click **Generate Plan**.")
