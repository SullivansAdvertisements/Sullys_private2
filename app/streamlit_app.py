import io
import base64
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd

# -------------------------
# SAFE IMPORTS (won't crash app if missing)
# -------------------------
COMMON_AI_OK = True
try:
    from clients.common_ai import (
        run_full_research,
        generate_headlines,
        generate_descriptions,
        generate_hashtags,
        generate_email_outreach,
    )
except Exception as e:
    COMMON_AI_OK = False
    COMMON_AI_ERR = str(e)

# Optional platform clients (shell status)
def _safe_import(module_path: str, func_name: str):
    try:
        mod = __import__(module_path, fromlist=[func_name])
        return True, getattr(mod, func_name), ""
    except Exception as e:
        return False, None, str(e)

META_OK, meta_connection_status, META_ERR = _safe_import("clients.meta_client", "meta_connection_status")
GOOGLE_OK, google_connection_status, GOOGLE_ERR = _safe_import("clients.google_client", "google_connection_status")
TIKTOK_OK, tiktok_connection_status, TIKTOK_ERR = _safe_import("clients.tiktok_client", "tiktok_connection_status")
SPOTIFY_OK, spotify_connection_status, SPOTIFY_ERR = _safe_import("clients.spotify_client", "spotify_connection_status")

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(
    page_title="Sully’s Media Planner",
    page_icon="🌺",
    layout="wide",
)

APP_DIR = Path(__file__).resolve().parent
ASSETS = APP_DIR / "assets"
LOGO = ASSETS / "sullivans_logo.png"
BG = ASSETS / "sidebar_bg.png"  # used as main app background (mobile-safe)

def _b64_image(path: Path) -> str | None:
    if not path.exists():
        return None
    data = path.read_bytes()
    return base64.b64encode(data).decode("utf-8")

# -------------------------
# STYLES (Light theme + mobile-friendly background)
# -------------------------
bg64 = _b64_image(BG)
logo64 = _b64_image(LOGO)

bg_css = ""
if bg64:
    # Mobile-friendly: cover + fixed off on small screens (fixed causes weird iOS behavior sometimes)
    bg_css = f"""
    .stApp {{
        background-image: url("data:image/png;base64,{bg64}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        background-attachment: scroll;
        background-color: #f7f7fb;
    }}
    @media (min-width: 768px) {{
        .stApp {{
            background-attachment: fixed;
        }}
    }}
    """

st.markdown(
    f"""
    <style>
    {bg_css}

    /* Force light readable text */
    body, p, span, label, div, input, textarea {{
        color: #111 !important;
        font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Arial,sans-serif !important;
    }}
    h1,h2,h3,h4 {{
        color: #111 !important;
        font-weight: 800 !important;
    }}

    /* Make content sit on a readable card layer */
    .block-container {{
        padding-top: 4.5rem !important;
    }}
    .sully-card {{
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 18px;
        padding: 16px 16px 6px 16px;
        box-shadow: 0 6px 22px rgba(0,0,0,0.08);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        margin-bottom: 14px;
    }}

    /* Sticky header */
    .sully-sticky {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
        padding: 10px 14px;
        background: rgba(255,255,255,0.92);
        border-bottom: 1px solid rgba(0,0,0,0.08);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }}
    .sully-header {{
        display: flex;
        align-items: center;
        gap: 12px;
        max-width: 1200px;
        margin: 0 auto;
    }}
    .sully-header h2 {{
        margin: 0;
        font-size: 1.2rem;
    }}
    .sully-header small {{
        color: #333 !important;
    }}
    </style>

    <div class="sully-sticky">
      <div class="sully-header">
        {"<img src='data:image/png;base64," + logo64 + "' style='height:34px;width:auto;display:block;' />" if logo64 else ""}
        <div>
          <h2>Sully’s Multi-Platform Media Planner</h2>
          <small>Research → Strategy → Platforms → Influencers → Email</small>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_column_width=True)
    st.markdown("### Quick Status")
    st.write("Light theme ✅  |  Mobile background ✅")
    st.caption("If your background doesn’t show: confirm `app/assets/sidebar_bg.png` exists and is committed to GitHub.")

# -------------------------
# TABS
# -------------------------
tab_strategy, tab_research, tab_platforms, tab_influencers, tab_email = st.tabs(
    ["🧠 Strategy", "📊 Research & Trends", "📣 Platform Tabs", "🤝 Influencers", "✉️ Email Marketing"]
)

# ======================================================
# 🧠 STRATEGY TAB
# ======================================================
with tab_strategy:
    st.markdown("<div class='sully-card'>", unsafe_allow_html=True)
    st.subheader("🧠 Strategy Engine")

    c1, c2, c3 = st.columns(3)
    with c1:
        niche = st.selectbox("Niche", ["Music", "Clothing", "Homecare"], key="s_niche")
    with c2:
        goal = st.selectbox("Primary Goal", ["Awareness", "Traffic", "Leads", "Conversions", "Sales"], key="s_goal")
    with c3:
        monthly_budget = st.number_input("Monthly Budget (USD)", min_value=5000, step=500, value=5000, key="s_budget")

    geo = st.selectbox("Geo", ["Worldwide", "US", "UK", "CA", "EU"], key="s_geo")

    st.caption("This tab generates strategy + copy suggestions. (No fake ROI.)")
    if not COMMON_AI_OK:
        st.error(f"common_ai import error: {COMMON_AI_ERR}")
    else:
        if st.button("Generate Strategy Copy", key="btn_strategy"):
            st.write("### Headline Ideas")
            for h in generate_headlines(niche, goal):
                st.write("•", h)
            st.write("### Description Ideas")
            for d in generate_descriptions(niche, goal):
                st.write("•", d)

    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# 📊 RESEARCH TAB (MATCHES common_ai.py)
# ======================================================
with tab_research:
    st.markdown("<div class='sully-card'>", unsafe_allow_html=True)
    st.subheader("📊 Research & Trends (Seed → Keywords → Locations → Demographics)")

    seed = st.text_input("Seed keyword / interest", placeholder="streetwear, hip hop, home care", key="r_seed")
    r_geo = st.selectbox("Research Geo", ["US", "Worldwide", "UK", "CA", "EU"], index=0, key="r_geo")
    timeframe = st.selectbox("Timeframe", ["now 7-d", "today 3-m", "today 12-m", "today 5-y"], index=2, key="r_timeframe")
    r_niche = st.selectbox("Research Niche", ["Music", "Clothing", "Homecare"], key="r_niche")

    if not COMMON_AI_OK:
        st.error(f"common_ai import error: {COMMON_AI_ERR}")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        if st.button("Run Research", key="btn_research"):
            if not seed.strip():
                st.warning("Enter a seed keyword first.")
            else:
                with st.spinner("Running research..."):
                    data = run_full_research(seed=seed.strip(), niche=r_niche, geo=("Worldwide" if r_geo == "Worldwide" else r_geo))

                st.success("Research ready. This output feeds the platform tabs.")
                st.session_state["research_data"] = data
                st.session_state["research_seed"] = seed.strip()

        data = st.session_state.get("research_data")
        if data:
            st.write("### Demographics (inferred)")
            st.json(data.get("demographics", {}))

            st.write("### Location Targets")
            st.json(data.get("locations", {}))

            st.write("### Hashtags")
            st.json(data.get("hashtags", {}))

            gt = data.get("google_trends", {})
            if isinstance(gt, dict) and gt.get("error"):
                st.warning(f"Google Trends: {gt['error']}")
            else:
                iot = gt.get("interest_over_time")
                if isinstance(iot, pd.DataFrame) and not iot.empty:
                    st.write("### Google Trends: Interest Over Time")
                    st.line_chart(iot)

                regions = gt.get("top_regions")
                if isinstance(regions, pd.DataFrame) and not regions.empty:
                    st.write("### Google Trends: Top Regions")
                    st.dataframe(regions)

                rq = gt.get("related_queries") or []
                if rq:
                    st.write("### Related Queries")
                    st.dataframe(pd.DataFrame({"query": rq[:50]}))

    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# 📣 PLATFORM TABS
# ======================================================
with tab_platforms:
    st.markdown("<div class='sully-card'>", unsafe_allow_html=True)
    st.subheader("📣 Platform Tabs (use research output)")

    data = st.session_state.get("research_data", {})
    seed = st.session_state.get("research_seed", "")

    st.caption("Run Research first to auto-fill keywords/hashtags/locations into these tabs.")

    ptab_google, ptab_tiktok, ptab_spotify, ptab_meta = st.tabs(
        ["🔍 Google / YouTube", "🎵 TikTok", "🎧 Spotify", "📣 Meta"]
    )

    # --- GOOGLE ---
    with ptab_google:
        st.write("### Connection")
        if GOOGLE_OK:
            ok, msg = google_connection_status(st.secrets)
            st.write(msg)
        else:
            st.warning(f"google_client import missing: {GOOGLE_ERR}")

        st.write("### Suggested Inputs (from research)")
        st.write("Seed:", seed)
        st.json(data.get("google_trends", {}).get("related_queries", [])[:25] if data else [])

    # --- TIKTOK ---
    with ptab_tiktok:
        st.write("### Connection")
        if TIKTOK_OK:
            ok, msg = tiktok_connection_status(st.secrets)
            st.write(msg)
        else:
            st.warning(f"tiktok_client import missing: {TIKTOK_ERR}")

        st.write("### Hashtags (from research)")
        tags = (data.get("hashtags", {}) or {}).get("tiktok", [])
        st.write(", ".join(tags) if tags else "Run Research to populate hashtags.")

    # --- SPOTIFY ---
    with ptab_spotify:
        st.write("### Connection")
        if SPOTIFY_OK:
            ok, msg = spotify_connection_status(st.secrets)
            st.write(msg)
        else:
            st.warning(f"spotify_client import missing: {SPOTIFY_ERR}")

        st.write("### Angle (from demographics)")
        st.json(data.get("demographics", {}) if data else {})

    # --- META ---
    with ptab_meta:
        st.write("### Connection")
        if META_OK:
            ok, msg = meta_connection_status(st.secrets)
            st.write(msg)
        else:
            st.warning(f"meta_client import missing: {META_ERR}")

        st.write("### Hashtags + Interests (from research)")
        ig_tags = (data.get("hashtags", {}) or {}).get("instagram", [])
        st.write("IG hashtags:", ", ".join(ig_tags) if ig_tags else "Run Research first.")

    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# 🤝 INFLUENCERS
# ======================================================
with tab_influencers:
    st.markdown("<div class='sully-card'>", unsafe_allow_html=True)
    st.subheader("🤝 Influencer List Builder")

    plat = st.selectbox("Platform", ["Instagram", "TikTok", "YouTube"], key="inf_plat")
    size = st.selectbox("Creator size", ["Nano (1k–10k)", "Micro (10k–100k)", "Mid (100k–500k)", "Macro (500k+)"], key="inf_size")
    st.write("Use your research seed + hashtags to find creators faster:")
    data = st.session_state.get("research_data", {})
    tags = data.get("hashtags", {}).get("instagram" if plat == "Instagram" else "tiktok", [])
    st.write(", ".join(tags) if tags else "Run Research to generate hashtags.")

    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# ✉️ EMAIL MARKETING
# ======================================================
with tab_email:
    st.markdown("<div class='sully-card'>", unsafe_allow_html=True)
    st.subheader("✉️ Email Outreach Generator")

    if not COMMON_AI_OK:
        st.error(f"common_ai import error: {COMMON_AI_ERR}")
    else:
        outreach_type = st.selectbox("Email type", ["Influencer Collaboration", "Brand Partnership", "Press / Promo"], key="e_type")
        sender = st.text_input("Sender / Brand name", value="Sully’s", key="e_sender")
        offer = st.text_input("Offer / pitch", value="Paid collab + long-term partnership opportunity", key="e_offer")
        niche = st.selectbox("Niche", ["Music", "Clothing", "Homecare"], key="e_niche")

        if st.button("Generate Email", key="btn_email"):
            email = generate_email_outreach(outreach_type, sender, offer, niche)
            st.text_area("Email draft", email, height=260)

    st.markdown("</div>", unsafe_allow_html=True)