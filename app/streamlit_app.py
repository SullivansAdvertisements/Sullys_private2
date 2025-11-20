# ==========================
# Sully's Super Media Planner (Meta + Research)
# ==========================

import os
import sys
import base64
from pathlib import Path
from datetime import datetime
import json
import io

import requests
import streamlit as st
import pandas as pd

# ---------- Optional: Google Trends (if installed) ----------
try:
    from pytrends.request import TrendReq
    HAS_TRENDS = True
except ImportError:
    HAS_TRENDS = False

# ---------- Assets ----------
APP_DIR = Path(__file__).resolve().parent
HEADER_BG = APP_DIR / "header_bg.png"
SIDEBAR_BG = APP_DIR / "sidebar_bg.png"
LOGO_PATH = APP_DIR / "sullivans_logo.png"

# ---------- Meta API config (Streamlit secrets or env) ----------
META_TOKEN = st.secrets.get("META_SYSTEM_USER_TOKEN", os.getenv("META_SYSTEM_USER_TOKEN"))
META_AD_ACCOUNT_ID = st.secrets.get("META_AD_ACCOUNT_ID", os.getenv("META_AD_ACCOUNT_ID"))
META_BUSINESS_ID = st.secrets.get("META_BUSINESS_ID", os.getenv("META_BUSINESS_ID"))
META_APP_ID = st.secrets.get("META_APP_ID", os.getenv("META_APP_ID"))
META_APP_SECRET = st.secrets.get("META_APP_SECRET", os.getenv("META_APP_SECRET"))

# ==========================
# Helpers
# ==========================

def img_to_base64(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        data = path.read_bytes()
        return base64.b64encode(data).decode("utf-8")
    except Exception:
        return None

def inject_theme_css():
    """Light theme, 3D header & sidebar backgrounds, white font in sidebar."""
    header_b64 = img_to_base64(HEADER_BG)
    sidebar_b64 = img_to_base64(SIDEBAR_BG)

    header_css = ""
    if header_b64:
        header_css = f"""
        [data-testid="stHeader"] {{
            background-image: url("data:image/png;base64,{header_b64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            color: #ffffff;
        }}
        [data-testid="stHeader"] * {{
            color: #ffffff !important;
        }}
        """

    sidebar_css = ""
    if sidebar_b64:
        sidebar_css = f"""
        [data-testid="stSidebar"] {{
            background-image: url("data:image/png;base64,{sidebar_b64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-color: #02040a;
        }}
        [data-testid="stSidebar"] * {{
            color: #ffffff !important;
        }}
        """

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: #f5f6fb;
        }}
        {header_css}
        {sidebar_css}

        /* Cards & text */
        .sully-card {{
            background: rgba(255,255,255,0.98);
            border-radius: 18px;
            padding: 18px 20px;
            box-shadow: 0 14px 30px rgba(0,0,0,0.08);
            margin-bottom: 16px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def split_list(raw: str) -> list[str]:
    if not raw:
        return []
    parts = []
    for chunk in raw.replace(",", "\n").split("\n"):
        v = chunk.strip()
        if v:
            parts.append(v)
    seen, out = set(), []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out

# ---------- Meta objective mapping ----------

def map_goal_to_meta_objective(goal: str) -> str:
    """
    Map our primary goal to Meta outcome objective (as per latest error message).
    """
    goal = (goal or "").lower()
    if "lead" in goal:
        return "OUTCOME_LEADS"
    if "sale" in goal or "purchase" in goal or "conversion" in goal:
        return "OUTCOME_SALES"
    if "awareness" in goal or "reach" in goal:
        return "OUTCOME_AWARENESS"
    if "traffic" in goal or "visit" in goal:
        return "OUTCOME_TRAFFIC"
    if "app" in goal:
        return "OUTCOME_APP_PROMOTION"
    if "engagement" in goal or "video" in goal:
        return "OUTCOME_ENGAGEMENT"
    # default:
    return "OUTCOME_AWARENESS"

# ---------- Meta API call (Campaign only for now) ----------

def meta_is_configured() -> bool:
    return bool(META_TOKEN and META_AD_ACCOUNT_ID)

def meta_create_campaign(
    name: str,
    objective: str,
    status: str = "PAUSED",
    special_ad_categories: list[str] | None = None,
) -> dict:
    """
    Create a basic Meta campaign using Outcome-driven objective.
    """
    if not meta_is_configured():
        return {"error": "Meta API credentials not configured."}

    account_id = META_AD_ACCOUNT_ID
    token = META_TOKEN

    url = f"https://graph.facebook.com/v21.0/act_{account_id}/campaigns"

    payload = {
        "name": name,
        "objective": objective,  # one of OUTCOME_*
        "status": status,
    }
    if special_ad_categories:
        payload["special_ad_categories"] = special_ad_categories

    try:
        resp = requests.post(
            url,
            data=payload,
            params={"access_token": token},
            timeout=20,
        )
        data = resp.json()
        if resp.status_code >= 400:
            return {"error": f"{resp.status_code}", "details": data}
        return data
    except Exception as e:
        return {"error": "request_failed", "details": str(e)}

# ---------- Optional: Google Trends helper ----------

if HAS_TRENDS:
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_trends(seed_terms, geo="US", timeframe="today 12-m", gprop=""):
        if not seed_terms:
            return {}
        try:
            pytrends = TrendReq(hl="en-US", tz=360)
            pytrends.build_payload(seed_terms, timeframe=timeframe, geo=geo, gprop=gprop)

            out = {}
            iot = pytrends.interest_over_time()
            if isinstance(iot, pd.DataFrame) and not iot.empty:
                if "isPartial" in iot.columns:
                    iot = iot.drop(columns=["isPartial"])
                out["interest_over_time"] = iot

            by_region = pytrends.interest_by_region(
                resolution="REGION", inc_low_vol=True, inc_geo_code=True
            )
            if isinstance(by_region, pd.DataFrame) and not by_region.empty:
                first = seed_terms[0]
                if first in by_region.columns:
                    by_region = by_region.sort_values(first, ascending=False)
                out["by_region"] = by_region

            rq = pytrends.related_queries()
            suggestions = []
            if isinstance(rq, dict):
                for term, buckets in rq.items():
                    for key in ("top", "rising"):
                        df = buckets.get(key)
                        if isinstance(df, pd.DataFrame) and "query" in df.columns:
                            suggestions.extend(df["query"].dropna().astype(str).tolist())
            seen, uniq = set(), []
            for s in suggestions:
                if s not in seen:
                    seen.add(s)
                    uniq.append(s)
            out["related_suggestions"] = uniq[:100]
            return out
        except Exception as e:
            return {"error": str(e)}
else:
    def get_trends(*args, **kwargs):
        return {"error": "pytrends not installed"}


# ---------- Strategy "brain" (simple heuristic) ----------

def generate_strategy(niche: str, budget: float, goal: str, geo: str, competitors: list[str]) -> dict:
    """
    Simple planner that returns a plan for Meta + other platforms.
    No fake ROI math; just splits & messaging ideas.
    """
    niche = niche.lower()
    goal = goal.lower()

    # Budget split by platform (just used to inform user, not a calculator)
    if niche == "music":
        split = {
            "Meta (FB + IG)": 0.35,
            "TikTok Ads": 0.30,
            "YouTube Ads": 0.20,
            "Spotify Ads": 0.10,
            "X / Twitter Ads": 0.05,
        }
    elif niche == "clothing":
        split = {
            "Meta (FB + IG)": 0.40,
            "TikTok Ads": 0.30,
            "Google Search": 0.15,
            "YouTube Ads": 0.10,
            "X / Twitter Ads": 0.05,
        }
    else:  # home care default
        split = {
            "Google Search": 0.45,
            "Meta (FB + IG)": 0.30,
            "YouTube Ads": 0.15,
            "X / Twitter Ads": 0.10,
        }

    platforms = []
    for name, pct in split.items():
        platforms.append(
            {
                "name": name,
                "monthly_budget": round(budget * pct, 2),
                "objective": goal.title(),
                "geo": geo,
            }
        )

    # Very light "estimates" text, not a calculator:
    est_notes = []
    for p in platforms:
        est_notes.append(
            f"- **{p['name']}**: Use {p['objective']} objective with ~${p['monthly_budget']:.0f}/mo in {p['geo']}."
        )

    plan = {
        "niche": niche,
        "geo": geo,
        "goal": goal,
        "platforms": platforms,
        "meta_objective": map_goal_to_meta_objective(goal),
        "notes": est_notes,
        "competitors": competitors,
    }
    return plan


# ==========================
# UI
# ==========================

st.set_page_config(
    page_title="Sully's Media Brain",
    page_icon="🌺",
    layout="wide",
)

inject_theme_css()

# ---------- Sidebar ----------
with st.sidebar:
    # Logo at top (transparent)
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_column_width=True)

    st.markdown("### 🎛️ Controls")

    niche = st.selectbox(
        "Niche",
        ["Music", "Clothing Brand", "Local Home Care"],
        index=0,
    )

    goal = st.selectbox(
        "Primary Goal",
        ["Awareness", "Traffic", "Leads", "Sales / Purchases", "Engagement"],
        index=0,
    )

    budget = st.number_input(
        "Total Monthly Ad Budget (USD)",
        min_value=50.0,
        value=2000.0,
        step=50.0,
    )

    st.markdown("### 🌍 Geography")
    country = st.selectbox(
        "Main Country",
        ["Worldwide", "United States", "Canada", "United Kingdom", "Australia", "Custom text"],
        index=0,
    )
    if country == "Custom text":
        country = st.text_input("Enter Country/Region", value="Worldwide")

    cities_raw = st.text_area(
        "Priority cities/regions (optional)",
        placeholder="New York\nLos Angeles\nMiami",
    )

    st.markdown("### 🕵️ Competitors (optional)")
    comp_text = st.text_area(
        "Competitor URLs (one per line)",
        placeholder="https://example-competitor.com\nhttps://another-brand.com",
    )
    competitors = [c.strip() for c in comp_text.split("\n") if c.strip()]

    st.markdown("### 📈 Research options")
    use_trends = st.checkbox("Use Google Trends (if available)", value=True)

    st.markdown("### 🧠 Meta API")
    use_meta_api = st.checkbox("Create real Meta campaign when I click Build", value=False)
    if not meta_is_configured():
        st.caption(
            "⚠️ Meta API not configured yet. "
            "Add META_SYSTEM_USER_TOKEN and META_AD_ACCOUNT_ID to Streamlit secrets."
        )

    build = st.button("🚀 Build Strategy & (Optionally) Push to Meta")


# ---------- Main layout ----------
st.markdown("## 🌺 Sullivan’s Super Media Brain")

if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=80)

st.write(
    "Mini media planner for **Music**, **Clothing brands**, and **Local Home Care** that plans across "
    "Meta, TikTok, Google, YouTube and more — with optional Google Trends and real Meta API calls."
)

# Build plan on click
if build:
    geo_desc = country
    cities = split_list(cities_raw)
    if cities:
        geo_desc += f" (focus on: {', '.join(cities[:5])})"

    # 1) Base strategy
    plan = generate_strategy(niche, float(budget), goal, geo_desc, competitors)

    # 2) Optional Google Trends enrichment
    trends_block = None
    if use_trends:
        if not HAS_TRENDS:
            st.warning("pytrends is not installed, so Google Trends isn’t available.")
        else:
            # pick seeds based on niche
            if "music" in niche.lower():
                seeds = ["independent artist", "spotify playlist", "trap music"]
            elif "clothing" in niche.lower():
                seeds = ["streetwear", "vintage clothing", "graphic tees"]
            else:
                seeds = ["home care services", "senior care", "caregiver near me"]

            geo_code = "US" if "United States" in geo_desc else ""
            trends_block = get_trends(seeds, geo=geo_code or "US", timeframe="today 12-m")
            if "error" in trends_block and trends_block["error"]:
                st.warning(f"Trends error: {trends_block['error']}")
            else:
                st.subheader("📈 Google Trends (signal only, no fake calculators)")
                iot = trends_block.get("interest_over_time")
                if isinstance(iot, pd.DataFrame) and not iot.empty:
                    st.line_chart(iot)

                rel = trends_block.get("related_suggestions") or []
                if rel:
                    st.write("Top related queries:")
                    st.dataframe(pd.DataFrame({"Query": rel[:25]}))

    # 3) Show per-platform plan
    st.subheader("📊 Platform Plan (no fake ROI, just structured strategy)")

    for plat in plan["platforms"]:
        with st.container():
            st.markdown('<div class="sully-card">', unsafe_allow_html=True)
            st.markdown(f"### {plat['name']}")
            st.markdown(
                f"- **Monthly budget**: `${plat['monthly_budget']:.0f}`\n"
                f"- **Objective**: `{plat['objective']}`\n"
                f"- **Geo**: `{plat['geo']}`"
            )

            if "music" in niche.lower():
                if "Meta" in plat["name"]:
                    st.markdown(
                        "- Use Reels + Feed video targeting fans of similar artists, playlists and genres.\n"
                        "- Stack custom audiences: IG engagers, video viewers, and site visitors."
                    )
                elif "TikTok" in plat["name"]:
                    st.markdown(
                        "- Use sounds from your tracks + creator-style hooks.\n"
                        "- Target interest clusters: ‘indie artists’, ‘trap’, ‘afrobeats’, etc."
                    )
            elif "clothing" in niche.lower():
                if "Meta" in plat["name"]:
                    st.markdown(
                        "- Catalog/advantage+ shopping if available.\n"
                        "- Show bestsellers, UGC try-ons, and seasonal drops."
                    )
                elif "Google Search" in plat["name"]:
                    st.markdown(
                        "- Focus keywords around your brand + ‘streetwear’, ‘graphic tees’, and local modifiers."
                    )
            else:  # home care
                if "Google Search" in plat["name"]:
                    st.markdown(
                        "- Bid on ‘home care near me’, ‘in-home senior care’, ‘caregiver [city]’.\n"
                        "- Use call extensions and local service info."
                    )
                elif "Meta" in plat["name"]:
                    st.markdown(
                        "- Use warm imagery of caregivers + families.\n"
                        "- Layer by age, caregivers, local community groups (where allowed)."
                    )

            st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("📝 Overall Notes")
    for note in plan["notes"]:
        st.write(note)

    # 4) Optional Meta campaign creation (real API call)
    if use_meta_api:
        st.subheader("⚙️ Meta Campaign Creation")
        if not meta_is_configured():
            st.error("Meta API is not configured. Add credentials in Streamlit secrets.")
        else:
            meta_obj = plan["meta_objective"]
            default_name = f"{niche} — {goal.title()} — {datetime.utcnow().strftime('%Y%m%d')}"
            camp_name = st.text_input("Meta Campaign Name", value=default_name)
            if st.button("Create Meta Campaign Now"):
                res = meta_create_campaign(
                    name=camp_name,
                    objective=meta_obj,
                    status="PAUSED",
                )
                if "error" in res:
                    st.error(f"Meta create error: {res.get('error')} – {res.get('details')}")
                else:
                    st.success(f"✅ Meta campaign created with ID: {res.get('id')}")

    # 5) Export summary JSON (no ROI math, just plan)
    st.subheader("⬇️ Export Plan (JSON)")
    summary = {
        "niche": plan["niche"],
        "goal": plan["goal"],
        "geo": plan["geo"],
        "budget_usd": budget,
        "platforms": plan["platforms"],
        "meta_objective": plan["meta_objective"],
        "competitors": plan["competitors"],
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
    buf = io.StringIO()
    json.dump(summary, buf, indent=2)
    st.download_button(
        "Download media_plan.json",
        data=buf.getvalue(),
        file_name="media_plan.json",
        mime="application/json",
    )

else:
    st.info("Use the controls in the left sidebar, then click **“🚀 Build Strategy & (Optionally) Push to Meta”**.")
