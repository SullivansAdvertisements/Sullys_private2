# ==========================
# Sullivan's Media Planner Bot
# Clean full replacement - light theme, logo, multi-platform brain
# ==========================

import os
import sys
from pathlib import Path
from datetime import datetime
import io
import json

import requests
import streamlit as st
import pandas as pd

# Optional: Google Trends
try:
    from pytrends.request import TrendReq
    HAS_TRENDS = True
except ImportError:
    HAS_TRENDS = False

# -------------------------
# Streamlit Page Config
# -------------------------
st.set_page_config(
    page_title="Sullivan's Media Planner",
    page_icon="🧠",
    layout="wide"
)

# -------------------------
# Styling (light theme, more extravagant but clean)
# -------------------------
def inject_css():
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #f7f7fb;
            }
            .main-header {
                display: flex;
                align-items: center;
                gap: 1rem;
                padding: 0.75rem 1.25rem;
                background: linear-gradient(90deg, #0f172a, #1d4ed8, #06b6d4);
                border-radius: 0 0 18px 18px;
                color: white;
                box-shadow: 0 4px 16px rgba(15, 23, 42, 0.45);
                margin-bottom: 1.5rem;
            }
            .main-header h1 {
                margin: 0;
                font-size: 1.6rem;
                font-weight: 700;
            }
            .main-header p {
                margin: 0;
                opacity: 0.9;
                font-size: 0.9rem;
            }
            .logo-img {
                height: 52px;
                width: auto;
                object-fit: contain;
            }
            .card {
                background-color: white;
                border-radius: 18px;
                padding: 1rem 1.25rem;
                box-shadow: 0 2px 10px rgba(15, 23, 42, 0.08);
                margin-bottom: 1.2rem;
            }
            .section-title {
                font-weight: 700;
                font-size: 1.1rem;
                margin-bottom: 0.25rem;
            }
            .section-subtitle {
                font-size: 0.85rem;
                color: #64748b;
                margin-bottom: 0.75rem;
            }
            .metric-good {
                color: #16a34a;
                font-weight: 600;
            }
            .metric-bad {
                color: #dc2626;
                font-weight: 600;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


# -------------------------
# Logo helper (top header only, no background)
# -------------------------
def load_logo():
    """
    Look for sullivans_logo.png in the same folder as this file.
    If it exists, return its bytes; otherwise return None.
    """
    logo_path = Path(__file__).with_name("sullivans_logo.png")
    if logo_path.exists():
        return logo_path.read_bytes()
    return None


inject_css()

# -------------------------
# Meta API configuration from secrets
# -------------------------
META_TOKEN = st.secrets.get("META_SYSTEM_USER_TOKEN", "")
META_BUSINESS_ID = st.secrets.get("META_BUSINESS_ID", "")
META_AD_ACCOUNT_ID = st.secrets.get("META_AD_ACCOUNT_ID", "")
META_APP_ID = st.secrets.get("META_APP_ID", "")
META_APP_SECRET = st.secrets.get("META_APP_SECRET", "")

# -------------------------
# Helper: Google Trends wrapper
# -------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def get_trends(seed_terms, geo="", timeframe="today 12-m"):
    """
    Wrap Google Trends via pytrends (if installed).
    geo: "" for worldwide, "US" for United States, etc.
    """
    if not HAS_TRENDS or not seed_terms:
        return {}

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
                for k in ("top", "rising"):
                    df = buckets.get(k)
                    if isinstance(df, pd.DataFrame) and "query" in df.columns:
                        suggestions.extend(df["query"].dropna().astype(str).tolist())
        seen = set()
        uniq = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                uniq.append(s)
        out["related_suggestions"] = uniq[:80]

        return out
    except Exception as e:
        return {"error": str(e)}


# -------------------------
# Helper: simple reach / conv / ROI model per platform
# -------------------------
def platform_benchmarks(goal: str):
    """
    Very rough benchmarks per platform.
    These ARE NOT live API forecasts – just planning heuristics.
    Values: CPC in $, CTR and CVR as decimals.
    """
    # Base values
    base = {
        "Meta (FB/IG)":   {"cpc": 1.00, "ctr": 0.015, "cvr": 0.035},
        "TikTok Ads":     {"cpc": 0.80, "ctr": 0.018, "cvr": 0.022},
        "Google Search":  {"cpc": 1.50, "ctr": 0.04,  "cvr": 0.06},
        "YouTube Ads":    {"cpc": 0.90, "ctr": 0.02,  "cvr": 0.025},
        "Spotify Ads":    {"cpc": 0.75, "ctr": 0.012, "cvr": 0.015},
        "X (Twitter)":    {"cpc": 0.70, "ctr": 0.017, "cvr": 0.018},
        "Snapchat":       {"cpc": 0.60, "ctr": 0.02,  "cvr": 0.02},
    }

    # Adjust for goal type
    goal = goal.lower()
    for p in base:
        if "aware" in goal:
            # Awareness: cheaper clicks, lower CVR
            base[p]["cpc"] *= 0.8
            base[p]["cvr"] *= 0.6
        elif "traffic" in goal:
            base[p]["ctr"] *= 1.2
            base[p]["cvr"] *= 0.9
        elif "lead" in goal or "conversion" in goal or "sales" in goal:
            base[p]["cpc"] *= 1.1
            base[p]["cvr"] *= 1.2
    return base


def estimate_performance(budget: float, share: float, cpc: float, ctr: float, cvr: float, avg_rev: float):
    """Return reach, clicks, conversions, CPA, ROAS, ROI%."""
    spend = budget * share
    if spend <= 0 or cpc <= 0:
        return dict(spend=0, impressions=0, clicks=0, conv=0, cpa=0, roas=0, roi=0)

    clicks = spend / cpc
    impressions = clicks / ctr if ctr > 0 else 0
    conv = clicks * cvr
    revenue = conv * avg_rev
    cpa = spend / conv if conv > 0 else 0
    roas = revenue / spend if spend > 0 else 0
    roi = ((revenue - spend) / spend * 100) if spend > 0 else 0
    return dict(
        spend=spend,
        impressions=impressions,
        clicks=clicks,
        conv=conv,
        cpa=cpa,
        roas=roas,
        roi=roi,
    )


def split_budget(goal: str):
    """
    Budget split per platform based on goal.
    Values sum ~1.0.
    """
    if "aware" in goal.lower():
        return {
            "Meta (FB/IG)":   0.30,
            "TikTok Ads":     0.25,
            "YouTube Ads":    0.20,
            "Spotify Ads":    0.10,
            "X (Twitter)":    0.10,
            "Snapchat":       0.05,
            "Google Search":  0.00,
        }
    elif "traffic" in goal.lower():
        return {
            "Meta (FB/IG)":   0.25,
            "TikTok Ads":     0.20,
            "Google Search":  0.25,
            "YouTube Ads":    0.15,
            "X (Twitter)":    0.10,
            "Snapchat":       0.05,
            "Spotify Ads":    0.00,
        }
    else:  # conversions / sales / leads
        return {
            "Google Search":  0.30,
            "Meta (FB/IG)":   0.30,
            "TikTok Ads":     0.15,
            "YouTube Ads":    0.10,
            "X (Twitter)":    0.05,
            "Snapchat":       0.05,
            "Spotify Ads":    0.05,
        }


# -------------------------
# Meta API helpers (real calls, but guarded)
# -------------------------
def meta_connection_status():
    if not META_TOKEN or not META_AD_ACCOUNT_ID:
        return False, "Meta token or ad account ID is not set in Streamlit secrets."
    try:
        url = f"https://graph.facebook.com/v20.0/act_{META_AD_ACCOUNT_ID}"
        params = {"access_token": META_TOKEN, "fields": "id,account_status,name"}
        r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200:
            return False, f"Meta API error: {r.status_code} – {r.text[:200]}"
        data = r.json()
        return True, f"Connected to Meta Ad Account: {data.get('name','?')} (ID: {data.get('id')})"
    except Exception as e:
        return False, f"Meta connection exception: {e}"


def meta_create_dummy_campaign(name: str, objective: str):
    """
    Example: create a PAUSED awareness campaign in Meta.
    Only runs if token + ad account available.
    """
    if not META_TOKEN or not META_AD_ACCOUNT_ID:
        return False, "Meta token or ad account ID not configured."

    url = f"https://graph.facebook.com/v20.0/act_{META_AD_ACCOUNT_ID}/campaigns"
    payload = {
        "name": name,
        "objective": objective,
        "status": "PAUSED",
        "special_ad_categories": "[]",
        "access_token": META_TOKEN,
    }
    try:
        r = requests.post(url, data=payload, timeout=20)
        if r.status_code != 200:
            return False, f"Meta create error: {r.status_code} – {r.text[:300]}"
        data = r.json()
        return True, f"Campaign created with ID: {data.get('id')}"
    except Exception as e:
        return False, f"Meta exception: {e}"


# =====================================================================
# UI LAYOUT
# =====================================================================

# ---------- Header with logo ----------
logo_bytes = load_logo()
with st.container():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        if logo_bytes:
            st.image(logo_bytes, use_column_width=False, caption=None, output_format="PNG")
        else:
            st.markdown("🧠")
    with col_title:
        st.markdown("<h1>Sullivan's Omni-Channel Media Planner</h1>", unsafe_allow_html=True)
        st.markdown(
            "<p>Music • Clothing Brands • Local Home Care — built-in brain for reach, conversions & ROI estimates.</p>",
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)


# ---------- Sidebar: Inputs ----------
with st.sidebar:
    st.markdown("### 🧩 Setup")

    niche = st.selectbox(
        "Main Vertical",
        ["Music / Artists", "Clothing Brand", "Local Home Care", "Other"],
        index=0
    )
    primary_goal = st.selectbox(
        "Primary Goal",
        ["Awareness", "Traffic", "Leads / Conversions", "Sales"],
        index=0
    )
    monthly_budget = st.number_input("Monthly Ad Budget (USD)", min_value=100.0, value=2500.0, step=50.0)
    avg_revenue = st.number_input(
        "Avg Revenue per Conversion (USD)",
        min_value=1.0,
        value=80.0,
        step=5.0,
        help="Average revenue per sale/lead. Used for ROI estimates."
    )

    st.markdown("### 🌍 Target Geography")
    country_label = st.selectbox(
        "Main Country / Region",
        ["Worldwide", "United States", "Canada", "United Kingdom", "Australia", "European Union"],
        index=0
    )
    country_iso_map = {
        "Worldwide": "",
        "United States": "US",
        "Canada": "CA",
        "United Kingdom": "GB",
        "Australia": "AU",
        "European Union": "EU",
    }
    geo_code = country_iso_map[country_label]

    extra_geo_notes = st.text_input("Optional: Priority cities/regions", value="")

    st.markdown("### 📈 Google Trends")
    use_trends = st.checkbox("Boost with Google Trends (where available)", value=True)
    timeframe = st.selectbox(
        "Trends timeframe",
        ["now 7-d", "today 3-m", "today 12-m", "today 5-y"],
        index=2
    )
    trend_seeds_raw = st.text_area(
        "Trend seed keywords (comma or newline)",
        value="",
        placeholder="trap beats, drill music, underground rapper\nstreetwear, vintage clothing\nhome care services"
    )

    st.markdown("### ⚙️ Meta API (FB/IG)")
    st.caption("Uses Streamlit secrets: META_SYSTEM_USER_TOKEN, META_AD_ACCOUNT_ID, META_BUSINESS_ID, META_APP_ID, META_APP_SECRET.")
    check_meta_api = st.checkbox("Check Meta connection / enable API actions", value=False)

    run_plan = st.button("🧠 Generate Strategic Plan")


# ---------- Helper: figure out Trends seeds ----------
def build_trend_seed_list():
    seeds = []
    if trend_seeds_raw.strip():
        # User-supplied seeds
        for chunk in trend_seeds_raw.replace(",", "\n").split("\n"):
            v = chunk.strip()
            if v:
                seeds.append(v)
    else:
        # Auto seeds based on niche
        if "Music" in niche:
            seeds = ["independent artist", "spotify promotion", "trap beats"]
        elif "Clothing" in niche:
            seeds = ["streetwear", "vintage clothing", "hoodies", "graphic tees"]
        elif "Home Care" in niche:
            seeds = ["home care services", "senior care", "caregiver near me"]
        else:
            seeds = ["online marketing", "digital ads"]
    # Limit to ~5 seeds
    return seeds[:5]


# =====================================================================
# MAIN BODY
# =====================================================================
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Channel Mix & Performance Estimates</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Modeled estimates only — not official forecasts. Use as a planning brain, not exact truth.</div>',
        unsafe_allow_html=True
    )

    if run_plan:
        # ---- Trends (optional) ----
        trends_data = {}
        trend_seeds = build_trend_seed_list()
        if use_trends:
            if not HAS_TRENDS:
                st.warning("Google Trends (pytrends) is not installed in this environment. Skipping trends.")
            else:
                trends_data = get_trends(trend_seeds, geo=geo_code, timeframe=timeframe)
                if "error" in trends_data:
                    st.warning(f"Trends error (rate limiting is common): {trends_data['error']}")
                else:
                    st.write(f"Using trend seeds: {', '.join(trend_seeds)}")
                    if "interest_over_time" in trends_data:
                        st.line_chart(trends_data["interest_over_time"])

        # ---- Build platform estimates ----
        goal_label = primary_goal
        bmarks = platform_benchmarks(goal_label)
        splits = split_budget(goal_label)

        rows = []
        for platform, bench in bmarks.items():
            share = splits.get(platform, 0.0)
            perf = estimate_performance(
                budget=monthly_budget,
                share=share,
                cpc=bench["cpc"],
                ctr=bench["ctr"],
                cvr=bench["cvr"],
                avg_rev=avg_revenue,
            )
            rows.append({
                "Platform": platform,
                "Budget Share": f"{share*100:.0f}%",
                "Spend ($)": round(perf["spend"], 2),
                "Est Reach (impr.)": int(perf["impressions"]),
                "Est Clicks": int(perf["clicks"]),
                "Est Conversions": int(perf["conv"]),
                "Est CPA ($)": round(perf["cpa"], 2) if perf["cpa"] else 0,
                "ROAS (x)": round(perf["roas"], 2) if perf["roas"] else 0,
                "ROI (%)": round(perf["roi"], 1),
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        # Summary: best & worst ROI platforms
        if not df.empty:
            best_row = df.loc[df["ROI (%)"].idxmax()]
            worst_row = df.loc[df["ROI (%)"].idxmin()]

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Best estimated ROI platform**")
                st.markdown(
                    f"- {best_row['Platform']} — "
                    f"<span class='metric-good'>ROI {best_row['ROI (%)']:.1f}%</span>, "
                    f"CPA ${best_row['Est CPA ($)']:.2f}, "
                    f"ROAS {best_row['ROAS (x)']:.2f}x",
                    unsafe_allow_html=True
                )
            with col2:
                st.markdown("**Lowest estimated ROI platform**")
                st.markdown(
                    f"- {worst_row['Platform']} — "
                    f"<span class='metric-bad'>ROI {worst_row['ROI (%)']:.1f}%</span>, "
                    f"CPA ${worst_row['Est CPA ($)']:.2f}, "
                    f"ROAS {worst_row['ROAS (x)']:.2f}x",
                    unsafe_allow_html=True
                )

        # ROI explanation
        st.markdown("---")
        st.markdown(
            "💡 **Why is ROI sometimes negative?**  \n"
            "This bot compares your **avg revenue per conversion** vs. the **estimated CPA** for each platform.  \n"
            "If CPA > revenue, ROI will be negative. Try: increasing lifetime value, tightening targeting, or shifting more budget to the best-ROI channels."
        )

        # Export plan JSON
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        export = {
            "timestamp_utc": ts,
            "niche": niche,
            "primary_goal": primary_goal,
            "monthly_budget": monthly_budget,
            "avg_revenue_per_conversion": avg_revenue,
            "geo_label": country_label,
            "geo_code": geo_code,
            "trend_seeds": trend_seeds,
            "platform_estimates": rows,
        }
        buf = io.StringIO()
        json.dump(export, buf, indent=2)
        st.download_button(
            "⬇️ Download Plan JSON",
            data=buf.getvalue(),
            file_name=f"sullivan_plan_{ts}.json",
            mime="application/json"
        )
    else:
        st.info("Set your niche, goal, budget, and click **🧠 Generate Strategic Plan** to see multi-platform estimates.")

    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# Meta API Section (Real Calls, but Safe + Optional)
# =====================================================================
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧷 Meta (Facebook / Instagram) API</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Connect your Meta Marketing API via Streamlit secrets to inspect accounts and create PAUSED test campaigns.</div>',
        unsafe_allow_html=True
    )

    if check_meta_api:
        ok, msg = meta_connection_status()
        if ok:
            st.success(msg)
        else:
            st.error(msg)

        st.markdown("**Create a PAUSED test campaign (optional)**")
        camp_name = st.text_input("Campaign Name", value="Sully Test Campaign")
        objective = st.selectbox(
            "Meta Campaign Objective",
            ["AWARENESS", "TRAFFIC", "CONVERSIONS", "LEAD_GENERATION"],
            index=0
        )
        if st.button("🚀 Create Meta Campaign (PAUSED)"):
            success, info = meta_create_dummy_campaign(camp_name, objective)
            if success:
                st.success(info)
            else:
                st.error(info)
    else:
        st.info(
            "To enable Meta API: set `META_SYSTEM_USER_TOKEN`, `META_AD_ACCOUNT_ID`, "
            "`META_BUSINESS_ID`, `META_APP_ID`, and `META_APP_SECRET` in your Streamlit secrets, "
            "then tick the checkbox in the sidebar."
        )

    st.markdown('</div>', unsafe_allow_html=True)


# Footer
st.markdown(
    "<p style='text-align:center; color:#94a3b8; font-size:0.8rem;'>"
    "All performance numbers are modeled estimates for planning only — not official forecasts from Meta, Google, or any platform."
    "</p>",
    unsafe_allow_html=True
)
