# ==========================
# Sully's Super Media Planner
# Clean, light theme – logo in header + sidebar
# Multi-platform estimates + optional Google Trends
# ==========================

import os
import sys
import io
import json
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd

# Try to import Google Trends (pytrends), but don't crash if missing
try:
    from pytrends.request import TrendReq
    HAS_TRENDS = True
except ImportError:
    HAS_TRENDS = False

# ==========
# CONFIG
# ==========
st.set_page_config(
    page_title="Sully's Super Media Planner",
    page_icon="🌺",
    layout="wide",
)

APP_DIR = Path(__file__).resolve().parent
LOGO_PATH = APP_DIR / "sullivans_logo.png"


# ==========
# STYLING
# ==========

def inject_global_css():
    """Light, tropical / floral-inspired theme (no background logo)."""
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #ffffff 0%, #fdf7ff 40%, #f5fff8 100%);
            color: #222222;
            font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        /* Tweak sidebar */
        section[data-testid="stSidebar"] {
            background: #ffffffcc;
            border-right: 1px solid #e2e8f0;
        }

        /* Cards look */
        .sully-card {
            background: #ffffffcc;
            border-radius: 18px;
            padding: 1rem 1.2rem;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
            border: 1px solid #e2e8f0;
            margin-bottom: 1rem;
        }

        h1, h2, h3, h4 {
            color: #111827;
        }

        .sully-pill {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 999px;
            background: #ecfdf5;
            color: #047857;
            font-size: 0.75rem;
            font-weight: 600;
            margin-right: 6px;
        }

        /* Make tables easier to read */
        .stDataFrame table tbody tr:nth-child(odd) {
            background-color: #f9fafb !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_logo_header():
    """Show logo in main header + sidebar."""
    # Main header: logo + title
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_column_width=True)
        else:
            st.write("Sully's")
    with col_title:
        st.markdown("### 🌺 Sully's Super Media Planner")
        st.caption("Music • Clothing Brands • Local Home Care – Multi-platform strategy & estimates.")

    # Sidebar logo
    with st.sidebar:
        st.markdown("#### ")
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_column_width=True)
        else:
            st.write("Sully's Planner")


inject_global_css()
show_logo_header()


# ==========
# HELPERS
# ==========

def safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0


def get_trends(seed_terms, geo="US", timeframe="today 12-m"):
    """Wrapper around pytrends; returns dict with possible keys."""
    if not HAS_TRENDS or not seed_terms:
        return {"error": "pytrends not installed or no seed terms."}
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(seed_terms, timeframe=timeframe, geo=geo)

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
        # De-dupe
        seen = set()
        uniq = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                uniq.append(s)
        out["related_suggestions"] = uniq[:50]
        return out
    except Exception as e:
        msg = str(e)
        if "429" in msg:
            return {"error": "Google Trends rate-limited this IP (429). Try again later or with fewer seeds."}
        return {"error": msg}


def platform_baselines(niche: str, goal: str):
    """
    Return simple CPM/CTR/CVR baselines for each platform.
    Values are heuristic, not live from APIs.
    """
    niche = niche.lower()
    goal = goal.lower()

    # Base numbers by platform (CPM in USD, CTR %, CVR %)
    base = {
        "Meta (FB/IG)":      {"cpm": 8,   "ctr": 1.4, "cvr": 2.5},
        "TikTok":            {"cpm": 7,   "ctr": 1.8, "cvr": 2.0},
        "Google Search":     {"cpm": 20,  "ctr": 4.0, "cvr": 5.0},
        "YouTube":           {"cpm": 10,  "ctr": 0.8, "cvr": 1.5},
        "Spotify":           {"cpm": 12,  "ctr": 0.5, "cvr": 1.0},
        "Twitter / X":       {"cpm": 9,   "ctr": 1.0, "cvr": 1.5},
        "Snapchat":          {"cpm": 6.5, "ctr": 1.6, "cvr": 2.0},
    }

    # Niche adjustments
    if "music" in niche:
        for p in ["TikTok", "YouTube", "Spotify", "Twitter / X"]:
            base[p]["ctr"] *= 1.2
        base["Spotify"]["cvr"] *= 1.3

    if "clothing" in niche or "brand" in niche:
        for p in ["Meta (FB/IG)", "TikTok", "Snapchat"]:
            base[p]["ctr"] *= 1.25
            base[p]["cvr"] *= 1.15

    if "home" in niche or "care" in niche:
        # Local lead gen – lower CTR, higher CVR on search
        base["Google Search"]["ctr"] *= 0.9
        base["Google Search"]["cvr"] *= 1.4
        base["Meta (FB/IG)"]["cvr"] *= 1.1

    # Goal adjustments
    if "awareness" in goal:
        for p in base.values():
            p["cvr"] *= 0.7
    elif "traffic" in goal:
        for p in base.values():
            p["ctr"] *= 1.1
    elif "leads" in goal or "conversions" in goal or "sales" in goal:
        for p in base.values():
            p["cvr"] *= 1.2

    return base


def allocate_budget(budget: float, goal: str):
    """Return budget shares per platform based on high-level priors."""
    goal = goal.lower()
    if "awareness" in goal:
        weights = {
            "Meta (FB/IG)": 0.30,
            "TikTok": 0.20,
            "YouTube": 0.20,
            "Google Search": 0.10,
            "Spotify": 0.10,
            "Twitter / X": 0.05,
            "Snapchat": 0.05,
        }
    elif "traffic" in goal or "engagement" in goal:
        weights = {
            "Meta (FB/IG)": 0.30,
            "TikTok": 0.20,
            "Google Search": 0.20,
            "YouTube": 0.10,
            "Spotify": 0.05,
            "Twitter / X": 0.10,
            "Snapchat": 0.05,
        }
    else:  # sales, conversions, leads
        weights = {
            "Meta (FB/IG)": 0.30,
            "TikTok": 0.15,
            "Google Search": 0.30,
            "YouTube": 0.10,
            "Spotify": 0.05,
            "Twitter / X": 0.05,
            "Snapchat": 0.05,
        }

    allocs = {}
    for k, w in weights.items():
        allocs[k] = budget * w
    return allocs


def build_strategy(niche: str, budget: float, goal: str, geo: str,
                   avg_revenue: float,
                   trend_seeds: list[str],
                   trends: dict | None):
    """
    Core 'brain' to estimate reach, clicks, conversions and ROI per platform.
    """
    baselines = platform_baselines(niche, goal)
    allocs = allocate_budget(budget, goal)

    # Use related suggestions from Trends as bonus keyword hints
    trend_keywords = []
    top_regions = []
    if trends:
        trend_keywords = trends.get("related_suggestions", []) or []
        reg = trends.get("by_region")
        if isinstance(reg, pd.DataFrame) and not reg.empty:
            top_regions = [str(idx) for idx in reg.head(10).index.tolist()]

    rows = []
    total_conv = 0.0
    total_rev = 0.0

    for platform, base in baselines.items():
        spend = allocs.get(platform, 0.0)
        cpm = base["cpm"]
        ctr = base["ctr"] / 100.0
        cvr = base["cvr"] / 100.0

        impressions = safe_div(spend, cpm) * 1000.0
        clicks = impressions * ctr
        conversions = clicks * cvr
        revenue = conversions * avg_revenue
        roi_pct = (safe_div(revenue - spend, spend) * 100.0) if spend else 0.0

        total_conv += conversions
        total_rev += revenue

        rows.append({
            "Platform": platform,
            "Monthly Spend ($)": round(spend, 2),
            "Est. Impressions": int(impressions),
            "Est. Clicks": int(clicks),
            "Est. Conversions": int(conversions),
            "Est. Revenue ($)": round(revenue, 2),
            "Est. ROI (%)": round(roi_pct, 1),
        })

    overall_roi = (safe_div(total_rev - budget, budget) * 100.0) if budget else 0.0

    summary = {
        "niche": niche,
        "goal": goal,
        "geo": geo,
        "budget": budget,
        "avg_revenue": avg_revenue,
        "trend_seeds": trend_seeds,
        "trend_keywords": trend_keywords,
        "trend_regions": top_regions,
        "total_conversions": int(total_conv),
        "total_revenue": round(total_rev, 2),
        "overall_roi_pct": round(overall_roi, 1),
    }

    return pd.DataFrame(rows), summary


# ==========
# SIDEBAR
# ==========

with st.sidebar:
    st.subheader("📋 Campaign Inputs")

    niche = st.selectbox(
        "Niche",
        ["Music / Artists", "Clothing Brand", "Local Home Care"],
        index=0,
    )

    monthly_budget = st.number_input(
        "Total Monthly Ad Budget ($)",
        min_value=100.0,
        value=2500.0,
        step=50.0,
    )

    goal = st.selectbox(
        "Primary Goal",
        ["Sales / Conversions", "Leads", "Traffic", "Awareness"],
        index=0,
    )

    avg_revenue = st.number_input(
        "Avg Revenue per Conversion ($)",
        min_value=1.0,
        value=80.0,
        step=5.0,
    )

    st.markdown("### Targeting")
    country = st.selectbox(
        "Main Country",
        ["Worldwide", "United States", "United Kingdom", "Canada", "Australia", "Germany", "France"],
        index=0,
    )
    city_hint = st.text_input("Optional City / Region Focus", value="")

    # Google Trends controls
    st.markdown("### Google Trends (optional)")
    use_trends = st.checkbox("Use Google Trends to enrich plan", value=False)
    trends_timeframe = st.selectbox(
        "Trends timeframe",
        ["now 7-d", "today 3-m", "today 12-m", "today 5-y"],
        index=2,
    )
    trend_seed_text = st.text_area(
        "Trend seeds (comma or line separated)",
        placeholder="trap beats, drill music, streetwear, home care services",
        value="",
    )

    generate = st.button("🚀 Generate Strategy")


# ==========
# MAIN APP
# ==========

def parse_seed_terms(txt: str):
    if not txt.strip():
        return []
    parts = []
    for chunk in txt.replace(",", "\n").split("\n"):
        v = chunk.strip()
        if v:
            parts.append(v)
    return parts


if not generate:
    # Intro state
    st.markdown(
        """
        <div class="sully-card">
        <span class="sully-pill">Planner</span>
        <span class="sully-pill">Cross-platform</span>
        <span class="sully-pill">Estimates</span>
        <h3>Tell me your niche, budget, goal and targeting – I’ll build a full-funnel plan for Meta, TikTok, Search, YouTube, Spotify, X and Snapchat.</h3>
        <p>Use the left sidebar to set your inputs, then hit <b>“Generate Strategy”</b>.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Geo string
    if country == "Worldwide":
        geo_str = "Worldwide"
        trends_geo = ""
    else:
        geo_str = country + (f" – {city_hint}" if city_hint.strip() else "")
        # Trends geo: use country code if you want; keep simple as worldwide or US-like
        if "United States" in country:
            trends_geo = "US"
        else:
            trends_geo = ""

    # ---- Google Trends step ----
    trend_seeds = parse_seed_terms(trend_seed_text)
    trends_data = None
    trends_error = None
    if use_trends:
        if not HAS_TRENDS:
            trends_error = "pytrends is not installed in this environment."
        else:
            st.info("Fetching Google Trends data...")
            trends_data = get_trends(trend_seeds or ["online marketing"], geo=trends_geo, timeframe=trends_timeframe)
            if trends_data.get("error"):
                trends_error = trends_data["error"]
                trends_data = None

    # ---- Build strategy "brain" ----
    df, summary = build_strategy(
        niche=niche,
        budget=float(monthly_budget),
        goal=goal,
        geo=geo_str,
        avg_revenue=float(avg_revenue),
        trend_seeds=trend_seeds,
        trends=trends_data,
    )

    # ====== Top summary ======
    st.markdown('<div class="sully-card">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Monthly Budget", f"${summary['budget']:,.0f}")
    with col2:
        st.metric("Est. Conversions (All Platforms)", f"{summary['total_conversions']:,.0f}")
    with col3:
        st.metric("Est. Revenue", f"${summary['total_revenue']:,.0f}")
    with col4:
        st.metric("Overall ROI", f"{summary['overall_roi_pct']:,.1f}%")
    st.markdown("</div>", unsafe_allow_html=True)

    # Explain negative ROI if avg_rev is too low
    if summary["overall_roi_pct"] < 0:
        st.warning(
            "Your estimated ROI is negative. This usually happens when your **average revenue per conversion** "
            "is low relative to CPM/CPC costs. Try increasing prices, improving conversion rate, or lowering CPM with tighter targeting."
        )

    # ====== Platform breakdown ======
    st.markdown("### 📊 Platform Breakdown")
    st.dataframe(df, use_container_width=True)

    # ====== Trends visualization ======
    if use_trends:
        st.markdown("### 📈 Google Trends Insights")
        if trends_error:
            st.error(f"Trends error: {trends_error}")
        elif trends_data:
            iot = trends_data.get("interest_over_time")
            by_region = trends_data.get("by_region")
            sugg = trends_data.get("related_suggestions", [])

            if isinstance(iot, pd.DataFrame) and not iot.empty:
                st.write("**Interest over time**")
                st.line_chart(iot)

            if isinstance(by_region, pd.DataFrame) and not by_region.empty:
                st.write("**Top regions by interest**")
                st.dataframe(by_region.head(15))

            if sugg:
                st.write("**Related trending queries**")
                st.dataframe(pd.DataFrame({"Query": sugg[:30]}))
        else:
            st.info("No Trends data available for these seeds / timeframe.")

    # ====== JSON export ======
    st.markdown("### 🧾 Export Plan")
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    export_name = f"sully_plan_{ts}.json"

    export_payload = {
        "summary": summary,
        "platform_breakdown": df.to_dict(orient="records"),
    }

    buf = io.StringIO()
    json.dump(export_payload, buf, indent=2)
    st.download_button(
        "⬇️ Download JSON Plan",
        data=buf.getvalue(),
        file_name=export_name,
        mime="application/json",
    )

    st.markdown("---")
    st.info(
        "This planner uses heuristic CPM/CTR/CVR assumptions for each platform, "
        "plus optional Google Trends enrichment. It does **not** push directly into ad accounts yet – "
        "use it to design and sanity-check your media plans before building campaigns in Meta, TikTok, Google, etc."
    )
