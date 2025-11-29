# Sully's Multi-Platform Media Planner
# Tabs:
# - Strategy Planner (Music, Clothing, Home Care) + optional Google Trends
# - Google / YouTube campaign planner (API shell)
# - TikTok campaign planner (API shell)
# - Spotify campaign planner (API shell)
# - Meta shell (connection test, future wiring)

import io
import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

from pytrends.request import TrendReq # optional, but in requirements
from clients.google_client import (
google_connection_status,
youtube_connection_status,
google_sample_call,
)
from clients.tiktok_client import tiktok_connection_status, tiktok_sample_call
from clients.spotify_client import spotify_connection_status, spotify_sample_call
from clients.meta_client import meta_connection_status, meta_sample_call

# -------------------------
# Basic config + styling
# -------------------------
st.set_page_config(
page_title="Sully's Multi-Platform Planner",
page_icon="🌺",
layout="wide",
)

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
[data-testid="stSidebar"] {
background-color: #151826;
}
[data-testid="stSidebar"] * {
color: #ffffff !important;
}
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
# Strategy brain
# -------------------------
def generate_strategy(niche, budget, goal, geo, competitors):
niche = niche.lower()
goal = goal.lower()
budget = float(budget)

if goal in ["sales", "conversions"]:
split = {"meta": 0.4, "google": 0.35, "tiktok": 0.15, "youtube": 0.1}
elif goal in ["leads"]:
split = {"meta": 0.45, "google": 0.3, "tiktok": 0.15, "youtube": 0.1}
elif goal in ["awareness"]:
split = {"meta": 0.35, "tiktok": 0.3, "youtube": 0.25, "google": 0.1}
else:
split = {"meta": 0.35, "google": 0.3, "tiktok": 0.2, "youtube": 0.15}

def alloc(p):
return round(budget * split.get(p, 0), 2)

if niche == "music":
audiences = [
"Fans of similar artists",
"Recent listeners of your genre",
"Lookalike of engaged fans",
"Retarget video viewers 25%+",
]
hooks = [
"New single out now",
"Behind-the-scenes studio clips",
"Countdown to release",
]
elif niche == "clothing":
audiences = [
"Streetwear & sneakerheads",
"Online fashion shoppers",
"Lookalike of purchasers",
"Cart abandoners & product viewers",
]
hooks = [
"Limited drop – low stock",
"New collection live",
"Bundle / fit ideas",
]
elif niche == "homecare":
audiences = [
"Adults 35–65 with parents 65+",
"Caregiving / nursing interests",
"Local radius around service area",
"Retarget service page visitors",
]
hooks = [
"Free consultation for home care",
"Trusted care for your loved ones",
"Licensed, insured caregivers in your area",
]
else:
audiences = ["Broad + remarketing"]
hooks = ["Strong core offer"]

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
"ideas": {
"audiences": audiences,
"hooks": hooks,
"formats": ["Reels", "Feed video", "Carousel", "Stories"],
},
},
"google": {
"budget": alloc("google"),
"ideas": {
"campaign_types": ["Search", "Performance Max"],
"keywords": ["brand + niche", "purchase intent queries"],
},
},
"tiktok": {
"budget": alloc("tiktok"),
"ideas": {
"audiences": audiences,
"hooks": hooks,
"formats": ["In-feed video 9:16", "Spark ads"],
},
},
"youtube": {
"budget": alloc("youtube"),
"ideas": {
"audiences": [
"Custom segments using keywords / competitors",
"Remarketing to site visitors",
],
"formats": ["Skippable in-stream", "In-feed video"],
},
},
},
}
return plan


@st.cache_data(ttl=3600, show_spinner=False)
def get_trends(seed_terms, geo="US", timeframe="today 12-m", gprop=""):
if not seed_terms:
return {"error": "No seed terms."}
try:
pytrends = TrendReq(hl="en-US", tz=360)
pytrends.build_payload(seed_terms, timeframe=timeframe, geo=geo, gprop=gprop)
out = {}
iot = pytrends.interest_over_time()
if isinstance(iot, pd.DataFrame) and not iot.empty:
if "isPartial" in iot.columns:
iot = iot.drop(columns=["isPartial"])
out["interest_over_time"] = iot
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
seen = set()
result = []
for v in out:
if v not in seen:
seen.add(v)
result.append(v)
return result


# -------------------------
# Header + sidebar logo
# -------------------------
header_cols = st.columns([1, 3])
with header_cols[0]:
if _file_exists(LOGO_PATH):
st.image(str(LOGO_PATH), use_column_width=True)
with header_cols[1]:
st.markdown("## Sully’s Multi-Platform Planner")
st.caption(
"Strategy + cross-platform campaign planning for Music, Clothing Brands, and Local Home Care."
)

st.markdown("---")

with st.sidebar:
if _file_exists(LOGO_PATH):
st.image(str(LOGO_PATH), caption="Sullivan’s Advertisements", use_column_width=True)
st.markdown("### Platforms wired")
st.write("• Google / YouTube (shell)")
st.write("• TikTok (shell)")
st.write("• Spotify (shell)")
st.write("• Meta (shell)")


# -------------------------
# Tabs
# -------------------------
tab_strategy, tab_google, tab_tiktok, tab_spotify, tab_meta = st.tabs(
[
"🧠 Strategy",
"🔍 Google / YouTube",
"🎵 TikTok",
"🎧 Spotify",
"📣 Meta",
]
)

# =========================
# TAB 1 – STRATEGY
# =========================
with tab_strategy:
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

st.markdown("#### Competitor URLs (for context only)")
comp_text = st.text_area(
"One per line",
placeholder="https://competitor1.com\nhttps://competitor2.com",
height=80,
)
competitors = parse_multiline(comp_text)

st.markdown("#### Google Trends (optional, for keyword ideas)")
trends_col1, trends_col2 = st.columns([2, 1])
with trends_col1:
use_trends = st.checkbox("Use Google Trends", value=False)
trend_seeds_raw = st.text_input(
"Trend seed terms (comma/newline)",
placeholder="streetwear, trap beats, home care services",
)
with trends_col2:
timeframe = st.selectbox(
"Timeframe", ["now 7-d", "today 3-m", "today 12-m", "today 5-y"], index=2
)
gprop_choice = st.selectbox(
"Search Source", ["(Web)", "news", "images", "youtube", "froogle"], index=0
)
gprop = "" if gprop_choice == "(Web)" else gprop_choice

if use_trends and st.button("Pull Google Trends"):
seeds = parse_multiline(trend_seeds_raw)
if not seeds:
st.warning("Add at least one trend seed term.")
else:
with st.spinner("Contacting Google Trends..."):
td = get_trends(
seeds,
geo="US" if country == "US" else "",
timeframe=timeframe,
gprop=gprop,
)
if td.get("error"):
st.error(f"Trends error: {td['error']}")
else:
if isinstance(td.get("interest_over_time"), pd.DataFrame):
st.write("**Interest over time**")
st.line_chart(td["interest_over_time"])
sugg = td.get("related_suggestions") or []
if sugg:
st.write("**Related queries (Top + Rising)**")
st.dataframe(pd.DataFrame({"Query": sugg[:50]}))

if st.button("Generate Cross-Platform Strategy Plan"):
geo_label = "Worldwide" if country == "Worldwide" else country
if geo_detail.strip():
geo_label = f"{geo_label} – {geo_detail.strip()}"
plan = generate_strategy(
niche=niche, budget=budget, goal=goal, geo=geo_label, competitors=competitors
)
st.success("Strategy generated.")
st.markdown("### Overview")
st.json(plan["overview"])
st.markdown("### Per-Platform Plan")
for platform_name, cfg in plan["platforms"].items():
st.markdown(f"#### {platform_name.upper()}")
st.write(f"**Monthly Budget**: ${cfg['budget']:,.2f}")
st.write("**Ideas:**")
for key, val in cfg["ideas"].items():
st.write(f"- **{key.title()}**: {', '.join(val)}")


# =========================
# TAB 2 – GOOGLE / YOUTUBE
# =========================
with tab_google:
st.subheader("🔍 Google / YouTube Campaign Planner")

secrets = st.secrets # shorthand
ok_g, msg_g = google_connection_status(secrets)
ok_y, msg_y = youtube_connection_status(secrets)

st.markdown("#### Connection Status")
if ok_g:
st.success(f"Google Ads: {msg_g}")
else:
st.warning(f"Google Ads: {msg_g}")
if ok_y:
st.success(f"YouTube: {msg_y}")
else:
st.warning(f"YouTube: {msg_y}")

if st.button("Run sample Google/YouTube API call (placeholder)"):
st.json(google_sample_call())

st.markdown("#### Plan a Search + YouTube Combo Campaign")
g1, g2 = st.columns(2)
with g1:
g_niche = st.selectbox("Niche", ["Music", "Clothing", "Homecare"], key="g_niche")
g_goal = st.selectbox(
"Goal",
["Awareness", "Traffic", "Leads", "Sales"],
key="g_goal",
)
g_country = st.text_input("Country (ISO)", value="US", key="g_country")
g_daily_budget = st.number_input(
"Daily budget (USD)", min_value=5.0, value=50.0, step=5.0
)
with g2:
g_keywords_raw = st.text_area(
"Core keywords (comma/newline)",
placeholder="home care services near me\nindependent artist marketing\nstreetwear brand",
)
g_url = st.text_input(
"Landing page URL",
value="https://example.com",
)

if st.button("Generate Google / YouTube Plan"):
kws = parse_multiline(g_keywords_raw)
if not kws:
st.warning("Add at least one keyword.")
else:
st.success("Plan generated – copy these into Google Ads / YouTube UI.")
st.write("**Search Campaign:**")
st.write(f"- Country: {g_country}")
st.write(f"- Daily budget: ${g_daily_budget:,.2f}")
st.write(f"- Goal: {g_goal}")
st.write(f"- Keywords: {', '.join(kws)}")
st.write(f"- Landing page: {g_url}")
st.write("**YouTube Campaign:**")
st.write("- Use same keywords in custom segments.")
st.write("- Use skippable in-stream + in-feed video.")
st.write("- Retarget video viewers into search / conversion campaigns.")


# =========================
# TAB 3 – TIKTOK
# =========================
with tab_tiktok:
st.subheader("🎵 TikTok Ads Planner")

secrets = st.secrets
ok_tt, msg_tt = tiktok_connection_status(secrets)
st.markdown("#### Connection Status")
if ok_tt:
st.success(msg_tt)
else:
st.warning(msg_tt)

if st.button("Run sample TikTok API call (placeholder)"):
st.json(tiktok_sample_call())

st.markdown("#### Plan a TikTok Campaign")
t1, t2 = st.columns(2)
with t1:
t_niche = st.selectbox("Niche", ["Music", "Clothing", "Homecare"], key="t_niche")
t_goal = st.selectbox(
"Goal", ["Awareness", "Traffic", "Sales"], key="t_goal"
)
t_country = st.text_input("Country (ISO)", value="US", key="t_country")
t_daily_budget = st.number_input(
"Daily budget (USD)", min_value=5.0, value=30.0, step=5.0
)
with t2:
t_hooks = st.text_area(
"Hooks (comma/newline)",
placeholder="POV: You just found your new favorite brand\nWatch till the end\nThis changed my life",
)
t_url = st.text_input("Destination URL", value="https://example.com")

if st.button("Generate TikTok Plan"):
hooks = parse_multiline(t_hooks)
st.success("Plan generated – plug into TikTok Ads Manager.")
st.write(f"**Country:** {t_country}")
st.write(f"**Daily budget:** ${t_daily_budget:,.2f}")
st.write(f"**Goal:** {t_goal}")
st.write("**Creative Hooks:**")
for h in hooks:
st.write(f"- {h}")
st.write(f"**Destination URL:** {t_url}")


# =========================
# TAB 4 – SPOTIFY
# =========================
with tab_spotify:
st.subheader("🎧 Spotify Campaign Planner")

secrets = st.secrets
ok_sp, msg_sp = spotify_connection_status(secrets)
st.markdown("#### Connection Status")
if ok_sp:
st.success(msg_sp)
else:
st.warning(msg_sp)

if st.button("Run sample Spotify API call (placeholder)"):
st.json(spotify_sample_call())

st.markdown("#### Plan a Spotify Audio Campaign")
s1, s2 = st.columns(2)
with s1:
s_niche = st.selectbox("Niche", ["Music", "Clothing", "Homecare"], key="s_niche")
s_goal = st.selectbox(
"Goal", ["Awareness", "Traffic"], key="s_goal"
)
s_country = st.text_input("Country (ISO)", value="US", key="s_country")
s_daily_budget = st.number_input(
"Daily budget (USD)", min_value=5.0, value=25.0, step=5.0
)
with s2:
s_script = st.text_area(
"30s Audio Script",
placeholder="Hey, it’s [Artist/Brand]. While you’re listening, tap now to check out our latest...",
height=120,
)
s_url = st.text_input("Click-through URL", value="https://example.com")

if st.button("Generate Spotify Plan"):
st.success("Plan generated – plug this script + settings into Spotify Ads Studio.")
st.write(f"**Country:** {s_country}")
st.write(f"**Daily budget:** ${s_daily_budget:,.2f}")
st.write(f"**Goal:** {s_goal}")
st.write("**Script:**")
st.write(s_script)
st.write(f"**URL:** {s_url}")


# =========================
# TAB 5 – META (shell)
# =========================
with tab_meta:
st.subheader("📣 Meta (Facebook + Instagram) – Shell")

secrets = st.secrets
ok_meta, msg_meta = meta_connection_status(secrets)
st.markdown("#### Connection Status")
if ok_meta:
st.success(msg_meta)
else:
st.warning(msg_meta)

if st.button("Test /me with current Meta token (shell)"):
st.json(meta_sample_call(secrets))

st.info(
"This tab is a shell. You can wire full campaign + ad set + ad creation here "
"using the Graph API and your existing Meta access token, ad account, pixel, and IG actor ID."
)
