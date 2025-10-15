import os
from datetime import datetime
from pathlib import Path
import streamlit as st
import pandas as pd

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
    niche = st.selectbox("Niche", ["clothing","consignment","musician","homecare"])
    budget = st.number_input("Monthly Budget (USD)", min_value=100.0, value=2500.0, step=50.0)
    goal = st.selectbox("Primary Goal", ["sales","conversions","leads","awareness","traffic"])
    geo = st.text_input("Geo (country/city or radius)", "US")
    comp_text = st.text_area("Competitor URLs (one per line)", placeholder="https://example.com
https://competitor.com/locations")
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
