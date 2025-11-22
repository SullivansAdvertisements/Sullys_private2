# ==========================
# Sully Super Planner vB-3
# Clean, light theme, logo + header/sidebar backgrounds
# Strategy + estimates for all major platforms (no broken API calls)
# ==========================

import os
from pathlib import Path
from datetime import datetime
import io
import json

import streamlit as st
import pandas as pd
import base64

# ============= PATHS FOR YOUR ASSETS =============
# Make sure these files exist in the app/ folder:
# 1) app/header_bg.png
# 2) app/sidebar_bg.png
# 3) app/sullivans_logo.png

APP_DIR = Path(__file__).resolve().parent
HEADER_BG = APP_DIR / "header_bg.png"
SIDEBAR_BG = APP_DIR / "sidebar_bg.png"
LOGO_PATH = APP_DIR / "sullivans_logo.png"

# Try to import Google Trends, optional
try:
    from pytrends.request import TrendReq
    HAS_TRENDS = True
except ImportError:
    HAS_TRENDS = False


# ==========================
# Helper: encode image to base64 for CSS
# ==========================
def load_base64(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return base64.b64encode(path.read_bytes()).decode()
    except Exception:
        return None


# ==========================
# Styling (light theme + header/sidebar backgrounds)
# ==========================
def inject_global_style():
    header_b64 = load_base64(HEADER_BG)
    sidebar_b64 = load_base64(SIDEBAR_BG)

    header_css = ""
    if header_b64:
        header_css = f"""
        /* Custom header banner */
        .sully-header {{
            background-image: url("data:image/png;base64,{header_b64}");
            background-size: cover;
            background-position: center;
            border-radius: 16px;
            padding: 32px 24px;
            margin-bottom: 16px;
            color: #ffffff;
        }}
        .sully-header h1 {{
            margin: 0;
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: 0.03em;
        }}
        .sully-header p {{
            margin: 4px 0 0 0;
            font-size: 0.95rem;
            opacity: 0.92;
        }}
        """

    sidebar_css = ""
    if sidebar_b64:
        sidebar_css = f"""
        /* Sidebar background */
        [data-testid="stSidebar"] > div:first-child {{
            background-image: url("data:image/png;base64,{sidebar_b64}");
            background-size: cover;
            background-position: center;
            color: #ffffff;
        }}
        [data-testid="stSidebar"] * {{
            color: #ffffff !important;
        }}
        """

    base_css = f"""
    <style>
    /* Light base */
    .stApp {{
        background-color: #f5f7fb;
    }}
    {header_css}
    {sidebar_css}
    /* Cards */
    .sully-card {{
        background: #ffffff;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.10);
        margin-bottom: 16px;
    }}
    </style>
    """
    st.markdown(base_css, unsafe_allow_html=True)


# ==========================
# Optional: Google Trends helper (safe wrapper)
# ==========================
def get_trends(seed_terms: list[str], geo: str = "US", timeframe: str = "today 12-m") -> dict:
    if not HAS_TRENDS or not seed_terms:
        return {}

    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(seed_terms, timeframe=timeframe, geo=geo)

        out: dict[str, object] = {}

        iot = pytrends.interest_over_time()
        if isinstance(iot, pd.DataFrame) and not iot.empty:
            if "isPartial" in iot.columns:
                iot = iot.drop(columns=["isPartial"])
            out["interest_over_time"] = iot

        by_region = pytrends.interest_by_region(
            resolution="COUNTRY", inc_low_vol=True, inc_geo_code=True
        )
        if isinstance(by_region, pd.DataFrame) and not by_region.empty:
            first = seed_terms[0]
            if first in by_region.columns:
                by_region = by_region.sort_values(first, ascending=False)
            out["by_region"] = by_region

        rq = pytrends.related_queries()
        suggestions: list[str] = []
        if isinstance(rq, dict):
            for term, buckets in rq.items():
                if not buckets:
                    continue
                for key in ("top", "rising"):
                    df = buckets.get(key)
                    if isinstance(df, pd.DataFrame) and "query" in df.columns:
                        suggestions.extend(df["query"].dropna().astype(str).tolist())
        # dedupe
        seen: set[str] = set()
        uniq: list[str] = []
        for q in suggestions:
            if q not in seen:
                seen.add(q)
                uniq.append(q)
        out["related_suggestions"] = uniq[:80]
        return out
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


# ==========================
# Strategy "Brain" (no external APIs)
# ==========================
PLATFORMS = [
    "Meta (Facebook + Instagram)",
    "TikTok Ads",
    "Google Search",
    "YouTube Ads",
    "Spotify Ads",
    "Twitter/X Ads",
    "Snapchat Ads",
]


def estimate_platform_metrics(
    platform: str,
    niche: str,
    goal: str,
    monthly_budget: float,
) -> dict:
    """
    Simple heuristic engine for:
      - estimated reach
      - clicks / listens / views
      - conversions
      - rough ROAS
    These are NOT live API numbers – just planning ballparks.
    """

    # Base CPMs (USD) by platform (very rough)
    base_cpm = {
        "Meta (Facebook + Instagram)": 8.0,
        "TikTok Ads": 6.0,
        "Google Search": 16.0,  # we treat as CPC later
        "YouTube Ads": 7.0,
        "Spotify Ads": 9.0,
        "Twitter/X Ads": 6.5,
        "Snapchat Ads": 5.5,
    }

    # Base CPC by platform (rough)
    base_cpc = {
        "Meta (Facebook + Instagram)": 1.2,
        "TikTok Ads": 1.0,
        "Google Search": 2.5,
        "YouTube Ads": 1.7,
        "Spotify Ads": 1.8,
        "Twitter/X Ads": 1.4,
        "Snapchat Ads": 1.1,
    }

    # Goal modifiers
    goal = goal.lower()
    if "awareness" in goal:
        cpm_factor = 0.8
        cpc_factor = 1.0
        conv_rate = 0.003
    elif "traffic" in goal:
        cpm_factor = 1.0
        cpc_factor = 0.9
        conv_rate = 0.007
    elif "leads" in goal:
        cpm_factor = 1.1
        cpc_factor = 1.1
        conv_rate = 0.04
    elif "sales" in goal or "conversions" in goal:
        cpm_factor = 1.2
        cpc_factor = 1.2
        conv_rate = 0.03
    else:  # fallback
        cpm_factor = 1.0
        cpc_factor = 1.0
        conv_rate = 0.01

    # Niche modifiers
    niche = niche.lower()
    if "music" in niche or "artist" in niche:
        conv_rate *= 0.7
    elif "home" in niche or "care" in niche:
        conv_rate *= 1.4
    elif "clothing" in niche or "brand" in niche:
        conv_rate *= 1.0

    b_cpm = base_cpm.get(platform, 10.0) * cpm_factor
    b_cpc = base_cpc.get(platform, 1.5) * cpc_factor

    # Awareness "reach" vs performance
    if platform == "Google Search":
        # Use CPC model
        clicks = monthly_budget / max(b_cpc, 0.3)
        impressions = clicks * 5  # rough avg
        reach = impressions * 0.6
    else:
        impressions = (monthly_budget / max(b_cpm, 1.0)) * 1000.0
        reach = impressions * 0.55
        clicks = impressions / 30.0  # assume ~3.3% CTR baseline

    conversions = clicks * conv_rate
    avg_revenue_per_conv = 80.0  # you can customize in UI later
    est_revenue = conversions * avg_revenue_per_conv
    roas = est_revenue / monthly_budget if monthly_budget > 0 else 0.0

    return {
        "platform": platform,
        "est_reach": round(reach),
        "est_impressions": round(impressions),
        "est_clicks": round(clicks),
        "est_conversions": round(conversions, 1),
        "est_roas": round(roas, 2),
    }


def build_keywords_from_trends(niche: str, country: str, base_keywords: list[str]) -> list[str]:
    """Use Google Trends to expand keyword ideas (optional)."""
    seeds: list[str] = []
    if base_keywords:
        seeds.extend(base_keywords[:3])
    else:
        # fallback seeds by niche
        if "music" in niche.lower():
            seeds = ["new music", "independent artist", "spotify playlist"]
        elif "clothing" in niche.lower():
            seeds = ["streetwear", "graphic tees", "hoodies"]
        elif "home" in niche.lower() or "care" in niche.lower():
            seeds = ["home care", "senior care", "caregiver services"]
        else:
            seeds = [niche]

    trends = get_trends(seeds, geo="US" if country == "Worldwide" else country)
    suggestions = trends.get("related_suggestions", []) if isinstance(trends, dict) else []
    combined = base_keywords + suggestions
    # dedupe and limit
    seen: set[str] = set()
    out: list[str] = []
    for kw in combined:
        kw = str(kw).strip()
        if not kw or kw.lower() in seen:
            continue
        seen.add(kw.lower())
        out.append(kw)
        if len(out) >= 60:
            break
    return out


# ==========================
# Streamlit UI
# ==========================
st.set_page_config(
    page_title="Sully Super Planner vB-3",
    page_icon="🌺",
    layout="wide",
)

inject_global_style()

# ---- HEADER ----
st.markdown(
    """
<div class="sully-header">
  <h1>Sully Super Planner vB-3</h1>
  <p>Mini media planner brain for Music, Clothing Brands & Local Home Care – across Meta, TikTok, Google, YouTube, Spotify, X & Snapchat.</p>
</div>
""",
    unsafe_allow_html=True,
)

# ---- SIDEBAR ----
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)

    st.markdown("### Campaign Inputs")

    niche = st.selectbox(
        "Niche",
        ["Music / Artist", "Clothing Brand", "Local Home Care"],
    )

    primary_goal = st.selectbox(
        "Primary Objective",
        ["Awareness", "Traffic", "Leads", "Sales / Conversions"],
    )

    monthly_budget = st.number_input(
        "Monthly Budget (USD)",
        min_value=100.0,
        value=1500.0,
        step=50.0,
    )

    country = st.selectbox(
        "Main Country",
        ["Worldwide", "US", "UK", "Canada", "Australia", "EU (multi-country)"],
    )

    st.markdown("### Audience & Offer")
    audience_desc = st.text_area(
        "Who are you trying to reach?",
        placeholder="Example: 18-34 streetwear fans in major US cities who follow hip hop & sneaker culture...",
    )
    offer_desc = st.text_area(
        "Core offer / hook",
        placeholder="Example: New drop every Friday, limited-edition tees and hoodies, free shipping over $75...",
    )

    st.markdown("### Competitors / Inspiration")
    competitor_urls_text = st.text_area(
        "Competitor links (one per line)",
        placeholder="https://competitor1.com\nhttps://instagram.com/artist\nhttps://tiktok.com/@brand",
    )

    use_trends = st.checkbox(
        "Use Google Trends to expand keywords (if available)",
        value=False,
        help="Requires pytrends in requirements.txt and may hit Google rate limits.",
    )

    run = st.button("🚀 Generate Multi-Platform Plan", type="primary")


# ---- SAFETY FOR FIRST LOAD ----
if not run:
    st.info("Configure your inputs in the sidebar and click **“🚀 Generate Multi-Platform Plan”**.")
    st.stop()

# ==========================
# POST-SUBMIT: BUILD STRATEGY
# ==========================
# Simple base keywords by niche
base_keywords: list[str] = []
if "music" in niche.lower():
    base_keywords = ["new music", "spotify artist", "rap songs", "hip hop artist", "trap beats"]
elif "clothing" in niche.lower():
    base_keywords = ["streetwear brand", "hoodies", "graphic tees", "oversized t shirt"]
elif "home care" in niche.lower():
    base_keywords = ["home care", "senior care near me", "in home caregiver", "respite care"]

if use_trends:
    expanded_keywords = build_keywords_from_trends(niche, country, base_keywords)
else:
    expanded_keywords = base_keywords

# Estimate metrics for each platform
platform_rows: list[dict] = []
for p in PLATFORMS:
    row = estimate_platform_metrics(p, niche, primary_goal, monthly_budget / len(PLATFORMS))
    platform_rows.append(row)

metrics_df = pd.DataFrame(platform_rows)

# ==========================
# LAYOUT: SUMMARY + METRICS
# ==========================
col_summary, col_table = st.columns([1.1, 1.6])

with col_summary:
    st.markdown("### 🧠 Strategy Snapshot")
    st.markdown(
        f"""
<div class="sully-card">
<b>Niche:</b> {niche}<br>
<b>Goal:</b> {primary_goal}<br>
<b>Budget:</b> ${monthly_budget:,.0f} / month<br>
<b>Country:</b> {country}
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("#### Key Moves")
    bullet_points: list[str] = []

    if "music" in niche.lower():
        bullet_points += [
            "Lean heavier into **TikTok + Spotify + YouTube** for discovery and listening.",
            "Use Meta & X for remarketing fans who engaged with video, clips or playlists.",
        ]
    elif "clothing" in niche.lower():
        bullet_points += [
            "Use **Meta + TikTok + Snapchat** for visual feeds and UGC-style creative.",
            "Support with **Google Search** on branded & high-intent product terms.",
        ]
    elif "home care" in niche.lower():
        bullet_points += [
            "Use **Google Search** + **Local Meta lead ads** for high-intent families.",
            "Run YouTube remarketing for people who visited key service pages.",
        ]

    if "awareness" in primary_goal.lower():
        bullet_points.append("Bias spend towards TikTok, YouTube & Meta Reach/Video campaigns.")
    elif "traffic" in primary_goal.lower():
        bullet_points.append("Use link-click/landing page view campaigns on Meta, TikTok & X.")
    elif "leads" in primary_goal.lower():
        bullet_points.append("Deploy native lead forms on Meta and high-intent Search campaigns.")
    elif "sales" in primary_goal.lower():
        bullet_points.append("Use conversion-optimized campaigns with proper pixel & events configured.")

    st.markdown(
        "<ul>" + "".join(f"<li>{bp}</li>" for bp in bullet_points) + "</ul>",
        unsafe_allow_html=True,
    )

with col_table:
    st.markdown("### 📊 Cross-Platform Estimates (heuristic)")
    st.caption("These are **planning ballparks**, not live API numbers. Always verify inside each ad platform.")
    st.dataframe(
        metrics_df.rename(
            columns={
                "platform": "Platform",
                "est_reach": "Est. Reach",
                "est_impressions": "Est. Impressions",
                "est_clicks": "Est. Clicks/Visits",
                "est_conversions": "Est. Conversions",
                "est_roas": "Est. ROAS (x)",
            }
        ),
        use_container_width=True,
    )

# ==========================
# PLATFORM-BY-PLATFORM PLAN
# ==========================
st.markdown("## 🎯 Per-Platform Strategic Plan")

for p in PLATFORMS:
    with st.expander(p, expanded=(p == "Meta (Facebook + Instagram)")):
        if p == "Meta (Facebook + Instagram)":
            st.markdown(
                """
**Campaign Types:**
- Awareness: Reach / Video Views with broad interest + lookalike audiences.
- Traffic: Link Clicks / Landing Page Views to key landing pages or Linktree.
- Leads: Lead Ads with native lead forms (home care, mailing list, waitlists).
- Sales: Conversions with pixel + standard events configured.

**Audiences:**
- Core interest stacks aligned to your niche (music genres, fashion interests, caregiving).
- Custom audiences from site visitors, IG engagers, FB page engagers.
- Lookalikes based on purchasers / high-value engagers where available.

**Creatives:**
- Short vertical video (9:16) + static carousels.
- Use UGC-style hooks (“I found this brand…”, “Day in the life…”, “Before / after…”).
"""
            )
        elif p == "TikTok Ads":
            st.markdown(
                """
**Campaign Types:**
- Awareness & consideration with video view / traffic objectives.
- Conversion campaigns once you have pixel + events setup.

**Creative Direction:**
- Native-feeling, lo-fi content; hooks in first 2 seconds.
- Lean into trends, sounds, stitch/duet formats for music & fashion.
"""
            )
        elif p == "Google Search":
            st.markdown(
                """
**Campaign Types:**
- High-intent search ads around key queries (brand, service + geo, product names).

**Keywords:**
- Start from the keyword list below, then refine with real search terms and negatives.
"""
            )
        elif p == "YouTube Ads":
            st.markdown(
                """
**Campaign Types:**
- Skippable in-stream for reach.
- In-feed ads around relevant content (music videos, fashion hauls, caregiving tips).

**Creative:**
- 15–30s hooks, highlight brand story or strongest song/offer.
"""
            )
        elif p == "Spotify Ads":
            st.markdown(
                """
**Campaign Types:**
- Audio + companion banner for music & local brand awareness.
- Target by genre, mood, and playlists.

**Creative:**
- 30-second audio spot with a clear CTA and URL mention.
"""
            )
        elif p == "Twitter/X Ads":
            st.markdown(
                """
**Campaign Types:**
- Engagement & traffic for conversation around drops, releases, and news.

**Tactics:**
- Promote best-performing organic posts.
- Use keyword + handle targeting around relevant culture and competitor brands.
"""
            )
        elif p == "Snapchat Ads":
            st.markdown(
                """
**Campaign Types:**
- Story Ads, Spotlight ads for visually led vertical creative.

**Tactics:**
- Fashion & music: lean into AR filters or quick cuts.
- Home care: light-touch awareness, retargeting site visitors.
"""
            )

# ==========================
# EXPORT PLAN
# ==========================
st.markdown("## 📁 Export Plan")

ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
export_name = f"sully_super_plan_{ts}.json"

plan = {
    "niche": niche,
    "primary_goal": primary_goal,
    "budget_usd": monthly_budget,
    "country": country,
    "audience": audience_desc,
    "offer": offer_desc,
    "competitors": [u.strip() for u in competitor_urls_text.splitlines() if u.strip()],
    "keywords": expanded_keywords,
    "platform_estimates": platform_rows,
    "generated_at_utc": ts,
}

buf = io.StringIO()
json.dump(plan, buf, indent=2)
st.download_button(
    "⬇️ Download strategy JSON",
    data=buf.getvalue(),
    file_name=export_name,
    mime="application/json",
)

st.caption("Use this JSON as a brief for building campaigns in Meta, TikTok, Google, YouTube, Spotify, X, and Snapchat.")
