# streamlit_app.py

import base64
import io
from pathlib import Path

import pandas as pd
import streamlit as st

# Optional: Google Trends support via pytrends
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False


# -----------------------------
# Config
# -----------------------------
st.set_page_config(
    page_title="Sullivan’s Advertisements – Growth Console",
    page_icon="📈",
    layout="wide",
)

LOGO_PATH = Path("sullivan_logo.png")


# -----------------------------
# Helpers
# -----------------------------
def get_logo_base64(path: Path) -> str | None:
    """Return base64 string for logo file if it exists."""
    if not path.exists():
        return None
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return encoded


def inject_global_css():
    """Inject global styles: background with stars + logo watermark."""
    logo_b64 = get_logo_base64(LOGO_PATH)
    logo_background = ""
    if logo_b64:
        logo_background = f"url('data:image/png;base64,{logo_b64}') no-repeat center 130px / 260px"

    st.markdown(
        f"""
        <style>
        /* Global background with subtle stars + logo watermark */
        .stApp {{
            background:
              radial-gradient(circle at 20% 10%, rgba(0,179,179,0.24), transparent 60%),
              radial-gradient(circle at 80% 0%, rgba(255,209,102,0.20), transparent 55%),
              radial-gradient(circle at 50% 100%, rgba(0,179,179,0.10), transparent 60%),
              #071016;
            color: #ffffff;
            {'background-image:' + logo_background + ';' if logo_background else ''}
        }}

        /* Card feel for main containers */
        .block-container {{
            padding-top: 2rem;
        }}

        /* Sidebar styling */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #04181b 0%, #081f24 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }}

        /* Sidebar logo centering */
        .sully-sidebar-logo {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
        }}

        .sully-sidebar-logo img {{
            border-radius: 999px;
            box-shadow: 0 0 30px rgba(0,179,179,0.4);
            border: 2px solid rgba(255,255,255,0.35);
        }}

        .sully-sidebar-title {{
            font-size: 1.1rem;
            font-weight: 700;
            margin-top: 0.5rem;
            text-align: center;
        }}

        /* Buttons */
        .stButton>button {{
            border-radius: 999px;
            background: #00b3b3;
            color: #04181b;
            border: 1px solid rgba(255,255,255,0.25);
            font-weight: 600;
        }}
        .stButton>button:hover {{
            background: #10d4c6;
            border-color: #ffd166;
            color: #04181b;
        }}

        /* Metric cards */
        .metric-card {{
            padding: 1rem 1.2rem;
            border-radius: 16px;
            background: rgba(8,26,32,0.95);
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 14px 40px rgba(0,0,0,0.45);
        }}
        .metric-label {{
            font-size: 0.85rem;
            color: #cde7ea;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}
        .metric-value {{
            font-size: 1.7rem;
            font-weight: 700;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def estimate_performance(spend, cpc, cvr, aov):
    """Basic funnel math."""
    if spend <= 0 or cpc <= 0:
        return 0, 0, 0, 0

    clicks = spend / cpc
    conversions = clicks * (cvr / 100.0)
    revenue = conversions * aov
    roas = revenue / spend if spend > 0 else 0
    return clicks, conversions, revenue, roas


def build_google_trends_section():
    st.subheader("Google Trends – Interest Over Time")

    if not PYTRENDS_AVAILABLE:
        st.info(
            "To enable live Google Trends, install `pytrends`:\n\n"
            "```bash\npip install pytrends\n```"
        )
        return

    keyword = st.text_input("Keyword / Topic", value="google ads")
    region = st.text_input("Region code (e.g. US, GB, DE)", value="US")
    timeframe = st.selectbox(
        "Timeframe",
        ["now 7-d", "today 1-m", "today 3-m", "today 12-m", "today 5-y"],
        index=2,
    )

    if st.button("Fetch Trends", use_container_width=True):
        try:
            pytrends = TrendReq(hl="en-US", tz=360)
            pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=region, gprop="")
            data = pytrends.interest_over_time()

            if data.empty:
                st.warning("No data returned. Try a broader term or different region/timeframe.")
                return

            data = data.reset_index().rename(columns={keyword: "interest"})
            st.line_chart(
                data.set_index("date")["interest"],
                height=220,
            )
            st.caption("Google Trends: Interest over time (0–100 index).")
        except Exception as e:
            st.error(f"Error fetching Google Trends: {e}")


# -----------------------------
# App layout
# -----------------------------
inject_global_css()

# Sidebar ---------------------
with st.sidebar:
    st.markdown('<div class="sully-sidebar-logo">', unsafe_allow_html=True)
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=140)
    else:
        st.write("Upload `sullivan_logo.png` to show your logo here.")
    st.markdown(
        '<div class="sully-sidebar-title">Sullivan’s Advertisements</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### Google Trends")
    build_google_trends_section()
    st.markdown("---")
    st.caption("💡 Use this console to model ad performance and spot demand spikes.")

# Main ------------------------
st.title("Growth Console – Google & Meta Performance Estimator")

tab_estimator, tab_downloads = st.tabs(
    ["📊 Ad Performance Estimator", "📥 Export & Notes"]
)

with tab_estimator:
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("Input Assumptions")

        st.markdown("#### Google Ads")
        g_spend = st.number_input("Google monthly ad spend ($)", min_value=0.0, value=3000.0, step=100.0)
        g_cpc = st.number_input("Google average CPC ($)", min_value=0.01, value=1.80, step=0.05)
        g_cvr = st.slider("Google conversion rate (%)", min_value=0.1, max_value=20.0, value=3.5, step=0.1)
        g_aov = st.number_input("Google average order value ($)", min_value=1.0, value=80.0, step=5.0)

        st.markdown("---")
        st.markdown("#### Meta (Facebook / Instagram)")
        m_spend = st.number_input("Meta monthly ad spend ($)", min_value=0.0, value=2000.0, step=100.0)
        m_cpc = st.number_input("Meta average CPC ($)", min_value=0.01, value=1.20, step=0.05)
        m_cvr = st.slider("Meta conversion rate (%)", min_value=0.1, max_value=20.0, value=2.8, step=0.1)
        m_aov = st.number_input("Meta average order value ($)", min_value=1.0, value=70.0, step=5.0)

    with col_right:
        st.subheader("Modeled Results")

        g_clicks, g_conv, g_rev, g_roas = estimate_performance(g_spend, g_cpc, g_cvr, g_aov)
        m_clicks, m_conv, m_rev, m_roas = estimate_performance(m_spend, m_cpc, m_cvr, m_aov)

        total_spend = g_spend + m_spend
        total_rev = g_rev + m_rev
        blended_roas = total_rev / total_spend if total_spend > 0 else 0

        col_g, col_m = st.columns(2)
        with col_g:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Google Ads</div>', unsafe_allow_html=True)
            st.markdown(
                f"<div class='metric-value'>{g_conv:,.0f}</div><div>est. conversions / month</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='margin-top:0.5rem;'>ROAS: <b>{g_roas:,.2f}×</b><br/>Revenue: <b>${g_rev:,.0f}</b></div>",
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col_m:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Meta Ads</div>', unsafe_allow_html=True)
            st.markdown(
                f"<div class='metric-value'>{m_conv:,.0f}</div><div>est. conversions / month</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='margin-top:0.5rem;'>ROAS: <b>{m_roas:,.2f}×</b><br/>Revenue: <b>${m_rev:,.0f}</b></div>",
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### Blended Performance")
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="metric-label">Google + Meta</div>
            <div class="metric-value">${total_rev:,.0f}</div>
            <div>est. revenue from ${total_spend:,.0f} spend / month</div>
            <div style="margin-top:0.4rem;">Blended ROAS: <b>{blended_roas:,.2f}×</b></div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

with tab_downloads:
    st.subheader("Export Scenario")

    data = {
        "channel": ["Google", "Meta"],
        "spend": [g_spend, m_spend],
        "cpc": [g_cpc, m_cpc],
        "cvr_%": [g_cvr, m_cvr],
        "aov": [g_aov, m_aov],
        "clicks": [g_clicks, m_clicks],
        "conversions": [g_conv, m_conv],
        "revenue": [g_rev, m_rev],
        "roas": [g_roas, m_roas],
    }
    df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=True)

    csv_bytes = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download scenario as CSV",
        data=csv_bytes,
        file_name="sullivans_advertisements_estimates.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown(
        """
        #### How to use this with clients
        - Run through assumptions on a call (CPC, CVR, AOV).
        - Show modeled conversions & ROAS live.
        - Export the CSV and drop it into their deck or email recap.
        """
    )
