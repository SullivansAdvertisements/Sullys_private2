# ==========================
# Sullivan's Advertisements – Marketing Bot
# Clean light-theme Streamlit app with logo, ROI + reach estimator
# ==========================

import sys
from pathlib import Path
from datetime import datetime
import io
import json

import streamlit as st
import pandas as pd

# Optional: Google Trends (pytrends)
try:
    from pytrends.request import TrendReq
    HAS_TRENDS = True
except ImportError:
    HAS_TRENDS = False

# Optional: connect to your old strategy engine if available
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
try:
    from bot.core import generate_strategy  # type: ignore
except Exception:
    generate_strategy = None  # app still works without it

# ==========================
# Page config (light look)
# ==========================
st.set_page_config(
    page_title="Sullivan's Marketing Bot",
    page_icon="📊",
    layout="wide",
)

# Small CSS tweak to keep things light and readable
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f7f7f9;
    }
    .main > div {
        padding-top: 0rem;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #123 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================
# Header with logo
# ==========================

logo_path = Path(__file__).with_name("sullivans_logo.png")

header_cols = st.columns([1, 4])
with header_cols[0]:
    if logo_path.exists():
        st.image(str(logo_path), use_column_width=True)
    else:
        st.write("🔺 Upload `sullivans_logo.png` next to this file.")

with header_cols[1]:
    st.title("Sullivan's Marketing Bot")
    st.caption("Planning & estimating for Google/YouTube, Meta, TikTok, and X (Twitter).")


# ==========================
# Sidebar – inputs
# ==========================
with st.sidebar:
    st.header("Campaign Inputs")

    niche = st.selectbox(
        "Business type",
        ["Clothing brand", "Consignment store", "Musician / Artist", "Home care (elderly / special needs)"],
    )

    primary_goal = st.selectbox(
        "Primary goal",
        ["Awareness", "Traffic", "Leads", "Sales"],
    )

    monthly_budget = st.number_input(
        "Monthly ad budget (USD)",
        min_value=100.0,
        value=2500.0,
        step=100.0,
    )

    avg_order_value = st.number_input(
        "Average revenue per conversion (USD)",
        min_value=5.0,
        value=80.0,
        step=5.0,
    )

    country = st.text_input("Main country / market", value="US")

    st.markdown("---")
    st.subheader("Google Trends (optional)")

    use_trends = st.checkbox("Use Google Trends insights", value=True)
    trend_seed_text = st.text_area(
        "Trend seed keywords (comma or new line)",
        placeholder="streetwear, vintage clothing, trap beats, caregiver services",
    )
    trends_timeframe = st.selectbox(
        "Trends timeframe",
        ["now 7-d", "today 3-m", "today 12-m", "today 5-y"],
        index=2,
    )

    st.markdown("---")
    st.subheader("Competitor URLs (optional)")
    comp_text = st.text_area(
        "One URL per line",
        placeholder="https://competitor1.com\nhttps://competitor2.com",
    )
    competitors = [c.strip() for c in comp_text.splitlines() if c.strip()]

    st.markdown("---")
    run_button = st.button("🚀 Run Estimator", type="primary")


# ==========================
# Helper functions
# ==========================

def parse_trend_seeds(raw: str) -> list[str]:
    if not raw:
        return []
    parts = []
    for chunk in raw.replace(",", "\n").splitlines():
        v = chunk.strip()
        if v:
            parts.append(v)
    # dedupe while preserving order
    seen = set()
    uniq = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq[:5]  # keep it small for Trends


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_trends(seed_terms: list[str], geo: str, timeframe: str):
    """Small wrapper around pytrends for interest + related queries."""
    if not HAS_TRENDS or not seed_terms:
        return {}

    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(seed_terms, timeframe=timeframe, geo=geo or "")
        out: dict = {}

        iot = pytrends.interest_over_time()
        if isinstance(iot, pd.DataFrame) and not iot.empty:
            if "isPartial" in iot.columns:
                iot = iot.drop(columns=["isPartial"])
            out["interest_over_time"] = iot

        related = pytrends.related_queries()
        suggestions = []
        if isinstance(related, dict):
            for term, buckets in related.items():
                for key in ("top", "rising"):
                    df = buckets.get(key)
                    if isinstance(df, pd.DataFrame) and "query" in df.columns:
                        suggestions.extend(df["query"].dropna().astype(str).tolist())
        # dedupe suggestions
        seen = set()
        uniq = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                uniq.append(s)
        out["related_suggestions"] = uniq[:50]
        return out
    except Exception as e:
        return {"error": str(e)}


def estimate_performance(goal: str, budget: float, aov: float) -> pd.DataFrame:
    """
    Very simplified estimator using typical CPM/CPC and conversion assumptions.
    These are NOT live platform numbers – just planning heuristics.
    """
    # budget allocation per platform
    allocation = {
        "Google / YouTube": 0.40,
        "Meta (Facebook / IG)": 0.35,
        "TikTok": 0.15,
        "X (Twitter)": 0.10,
    }

    # baseline channel metrics by primary goal
    # all values are "reasonable defaults", change as needed
    assumptions = {
        "Awareness": {
            "Google / YouTube": {"cpm": 12.0, "ctr": 0.01, "conv_rate": 0.002},
            "Meta (Facebook / IG)": {"cpm": 8.0, "ctr": 0.012, "conv_rate": 0.002},
            "TikTok": {"cpm": 6.0, "ctr": 0.013, "conv_rate": 0.0015},
            "X (Twitter)": {"cpm": 7.0, "ctr": 0.009, "conv_rate": 0.001},
        },
        "Traffic": {
            "Google / YouTube": {"cpc": 1.2, "conv_rate": 0.02},
            "Meta (Facebook / IG)": {"cpc": 0.9, "conv_rate": 0.018},
            "TikTok": {"cpc": 0.7, "conv_rate": 0.015},
            "X (Twitter)": {"cpc": 0.8, "conv_rate": 0.012},
        },
        "Leads": {
            "Google / YouTube": {"cpc": 1.8, "conv_rate": 0.10},
            "Meta (Facebook / IG)": {"cpc": 1.5, "conv_rate": 0.09},
            "TikTok": {"cpc": 1.2, "conv_rate": 0.08},
            "X (Twitter)": {"cpc": 1.3, "conv_rate": 0.07},
        },
        "Sales": {
            "Google / YouTube": {"cpc": 2.0, "conv_rate": 0.04},
            "Meta (Facebook / IG)": {"cpc": 1.7, "conv_rate": 0.035},
            "TikTok": {"cpc": 1.4, "conv_rate": 0.03},
            "X (Twitter)": {"cpc": 1.5, "conv_rate": 0.025},
        },
    }

    rows = []

    for platform, share in allocation.items():
        spend = budget * share
        metrics = assumptions[goal][platform]

        if goal == "Awareness":
            cpm = metrics["cpm"]           # cost per 1000 impressions
            ctr = metrics["ctr"]           # click-through rate
            conv_rate = metrics["conv_rate"]

            impressions = (spend / cpm) * 1000
            clicks = impressions * ctr
            conversions = clicks * conv_rate

        else:
            cpc = metrics["cpc"]
            conv_rate = metrics["conv_rate"]

            clicks = spend / cpc if cpc else 0
            impressions = clicks * 40      # crude guess (25–40 views per click)
            conversions = clicks * conv_rate

        est_revenue = conversions * aov
        roi = ((est_revenue - spend) / spend * 100) if spend > 0 else 0.0

        rows.append(
            {
                "Platform": platform,
                "Budget (USD)": round(spend, 2),
                "Est. Impressions": int(impressions),
                "Est. Clicks": int(clicks),
                "Est. Conversions": round(conversions, 1),
                "Est. Revenue (USD)": round(est_revenue, 2),
                "Est. ROI %": round(roi, 1),
            }
        )

    df = pd.DataFrame(rows)
    return df


# ==========================
# Main body
# ==========================

st.markdown("### Overview")
st.write(
    f"""
    **Niche:** {niche}  
    **Goal:** {primary_goal}  
    **Monthly Budget:** ${monthly_budget:,.0f}  
    **Average Value per Conversion:** ${avg_order_value:,.2f}  
    **Market:** {country}
    """
)

results_df: pd.DataFrame | None = None
trend_info: dict | None = None

if run_button:
    # 1) Performance estimation
    results_df = estimate_performance(primary_goal, monthly_budget, avg_order_value)

    st.subheader("📊 Estimated Reach, Conversions & ROI by Platform")
    st.dataframe(results_df, use_container_width=True)

    total_spend = results_df["Budget (USD)"].sum()
    total_revenue = results_df["Est. Revenue (USD)"].sum()
    total_conversions = results_df["Est. Conversions"].sum()
    blended_roi = (total_revenue - total_spend) / total_spend * 100 if total_spend > 0 else 0

    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Total spend (est.)", f"${total_spend:,.0f}")
    kpi_cols[1].metric("Total conversions (est.)", f"{total_conversions:,.1f}")
    kpi_cols[2].metric("Total revenue (est.)", f"${total_revenue:,.0f}")
    kpi_cols[3].metric("Blended ROI (est.)", f"{blended_roi:,.1f}%")

    st.markdown("#### Platform ROI comparison")
    roi_chart_df = results_df.set_index("Platform")[["Est. ROI %"]]
    st.bar_chart(roi_chart_df)

    # 2) Optional Google Trends
    if use_trends and HAS_TRENDS:
        st.subheader("📈 Google Trends Insights")

        seeds = parse_trend_seeds(trend_seed_text)
        if not seeds:
            st.info("Enter 1–5 trend seed keywords in the sidebar to pull Google Trends data.")
        else:
            trend_info = fetch_trends(seeds, country, trends_timeframe)

            if trend_info.get("error"):
                st.warning(f"Trends error (often 429 = too many requests): {trend_info['error']}")
            else:
                iot = trend_info.get("interest_over_time")
                if isinstance(iot, pd.DataFrame) and not iot.empty:
                    st.write("**Interest over time**")
                    st.line_chart(iot)

                sugg = trend_info.get("related_suggestions", [])
                if sugg:
                    st.write("**Related search queries (top + rising)**")
                    st.dataframe(pd.DataFrame({"Query": sugg}))

                    st.caption(
                        "Use these ideas to expand your keyword lists for Google, Meta interests, "
                        "TikTok interests/hashtags, and X (Twitter) topics."
                    )

    elif use_trends and not HAS_TRENDS:
        st.warning("pytrends is not installed. Add `pytrends==4.9.2` to requirements.txt to enable Trends.")

    # 3) Optional: call your advanced generator if available
    if generate_strategy is not None and competitors:
        st.subheader("🧠 Extra: Strategy notes from competitor URLs")
        try:
            # geo string is just the country here
            plan = generate_strategy(
                niche=niche,
                budget=float(monthly_budget),
                goal=primary_goal,
                geo=country,
                competitors=competitors,
            )
            # we don't rely on its schema – just show whatever summary it returns
            plan_json = json.dumps(plan, indent=2)
            st.code(plan_json, language="json")
        except Exception as e:
            st.warning(f"Strategy engine error (bot.core): {e}")

else:
    st.info("Set your inputs on the left and click **🚀 Run Estimator** to see reach, conversions, and ROI per platform.")
