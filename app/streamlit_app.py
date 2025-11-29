# 🌺 Sully's Multi-Platform Media Planner
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
from pytrends.request import TrendReq

from clients.google_client import (
    google_connection_status,
    youtube_connection_status,
    google_sample_call,
)
from clients.tiktok_client import (
    tiktok_connection_status,
    tiktok_sample_call,
)
from clients.spotify_client import (
    spotify_connection_status,
    spotify_sample_call,
)
from clients.meta_client import (
    meta_connection_status,
    meta_sample_call,
)

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
    """Safely check if a file exists."""
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
    ["🧠 Strategy", "🔍 Google / YouTube", "🎵 TikTok", "🎧 Spotify", "📣 Meta"]
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
        goal = st.selectbox("Primary Goal", ["Awareness", "Traffic", "Leads", "Conversions", "Sales"])
    with c3:
        budget = st.number_input("Monthly Ad Budget (USD)", min_value=100.0, value=2500.0, step=50.0)

    c4, c5 = st.columns(2)
    with c4:
        country = st.selectbox("Main Country / Region", ["Worldwide", "US", "UK", "CA", "EU"])
    with c5:
        geo_detail = st.text_input("Key city/region focus (optional)", value="")

    st.markdown("#### Competitor URLs (for context only)")
    comp_text = st.text_area("One per line", placeholder="https://competitor1.com\nhttps://competitor2.com", height=80)
    competitors = parse_multiline(comp_text)

    st.markdown("#### Google Trends (optional, for keyword ideas)")
    trends_col1, trends_col2 = st.columns([2, 1])
    with trends_col1:
        use_trends = st.checkbox("Use Google Trends", value=False)
        trend_seeds_raw = st.text_input("Trend seed terms (comma/newline)", placeholder="streetwear, trap beats, home care services")
    with trends_col2:
        timeframe = st.selectbox("Timeframe", ["now 7-d", "today 3-m", "today 12-m", "today 5-y"], index=2)
        gprop_choice = st.selectbox("Search Source", ["(Web)", "news", "images", "youtube", "froogle"], index=0)
        gprop = "" if gprop_choice == "(Web)" else gprop_choice

    if use_trends and st.button("Pull Google Trends"):
        seeds = parse_multiline(trend_seeds_raw)
        if not seeds:
            st.warning("Add at least one trend seed term.")
        else:
            with st.spinner("Contacting Google Trends..."):
                td = get_trends(seeds, geo="US" if country == "US" else "", timeframe=timeframe, gprop=gprop)
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
        plan = generate_strategy(niche=niche, budget=budget, goal=goal, geo=geo_label, competitors=competitors)
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
