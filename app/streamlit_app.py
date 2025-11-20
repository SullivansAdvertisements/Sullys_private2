# ==========================
# Sully's Meta Super Bot (Meta-only)
# Campaign + Ad Set + Ad Creator
# ==========================

import os
import json
from datetime import datetime

import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Facebook Business SDK
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad

# =========== CONFIG / SECRETS ===========

st.set_page_config(page_title="Sully's Meta Campaign Builder", page_icon="🌺", layout="wide")

# Load .env locally if present (optional)
load_dotenv()

def get_secret(key: str, fallback: str = "") -> str:
    # Prefer Streamlit secrets, fallback to environment vars for local dev
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key, fallback)

META_APP_ID = get_secret("META_APP_ID")
META_APP_SECRET = get_secret("META_APP_SECRET")
META_SYSTEM_USER_TOKEN = get_secret("META_SYSTEM_USER_TOKEN")
META_AD_ACCOUNT_ID = get_secret("META_AD_ACCOUNT_ID")  # should look like "act_123..."
META_PAGE_ID = get_secret("META_PAGE_ID")

missing = []
for k, v in [
    ("META_APP_ID", META_APP_ID),
    ("META_APP_SECRET", META_APP_SECRET),
    ("META_SYSTEM_USER_TOKEN", META_SYSTEM_USER_TOKEN),
    ("META_AD_ACCOUNT_ID", META_AD_ACCOUNT_ID),
    ("META_PAGE_ID", META_PAGE_ID),
]:
    if not v:
        missing.append(k)

if missing:
    st.error(
        "❌ Missing Meta credentials: "
        + ", ".join(missing)
        + ".\n\nSet them in Streamlit secrets or environment variables before using the bot."
    )

# =========== INIT META API ===========

def init_meta():
    """Initialize Facebook Marketing API."""
    if not META_SYSTEM_USER_TOKEN or not META_APP_ID or not META_APP_SECRET:
        raise RuntimeError("Meta credentials missing.")
    FacebookAdsApi.init(
        app_id=META_APP_ID,
        app_secret=META_APP_SECRET,
        access_token=META_SYSTEM_USER_TOKEN,
    )
    return AdAccount(META_AD_ACCOUNT_ID)


# =========== HELPERS ===========

OBJECTIVE_MAP = {
    "Awareness": "OUTCOME_AWARENESS",
    "Traffic": "OUTCOME_TRAFFIC",
    "Engagement": "OUTCOME_ENGAGEMENT",
    "Leads": "OUTCOME_LEADS",
    "Sales": "OUTCOME_SALES",
    "App promotion": "OUTCOME_APP_PROMOTION",
}

OPTIMIZATION_MAP = {
    "Awareness": "REACH",
    "Traffic": "LINK_CLICKS",
    "Engagement": "POST_ENGAGEMENT",
    "Leads": "LEAD_GENERATION",
    "Sales": "OFFSITE_CONVERSIONS",
    "App promotion": "APP_INSTALLS",
}


def usd_to_cents(usd: float) -> int:
    """Meta wants daily budget in *cents*."""
    return int(round(usd * 100))


# =========== STREAMLIT UI ===========

st.title("🌺 Sully’s Meta Campaign Builder")
st.caption("Build real Meta (Facebook + Instagram) campaigns with Campaign + Ad Set + Ad in one flow.")

st.markdown("---")

col_main, col_side = st.columns([2, 1])

with col_main:
    st.subheader("1️⃣ Campaign Setup")

    campaign_name = st.text_input("Campaign Name", value="Sully Auto Campaign")
    objective_label = st.selectbox(
        "Primary Objective",
        ["Awareness", "Traffic", "Engagement", "Leads", "Sales", "App promotion"],
        index=0,
    )
    objective = OBJECTIVE_MAP[objective_label]

    buying_type = st.selectbox("Buying Type", ["AUCTION"], index=0)

with col_side:
    st.subheader("2️⃣ Budget & Schedule")

    daily_budget_usd = st.number_input("Daily Budget (USD)", min_value=1.0, value=20.0, step=1.0)
    start_date = st.date_input("Start Date", datetime.utcnow())
    # For now we’ll make ad sets with no end date (you can pause in UI)

st.markdown("---")

st.subheader("3️⃣ Targeting")

col_t1, col_t2 = st.columns(2)
with col_t1:
    countries_raw = st.text_input("Countries (comma separated)", value="US")
    min_age = st.number_input("Min Age", 13, 65, 18)
    max_age = st.number_input("Max Age", 13, 65, 55)
with col_t2:
    genders_label = st.selectbox("Genders", ["All", "Male", "Female"], index=0)
    detailed_targeting = st.text_area(
        "Interests / Keywords (optional, comma separated)",
        placeholder="streetwear, hip hop, independent artist, home care services",
    )

if genders_label == "All":
    genders = []
elif genders_label == "Male":
    genders = [1]
else:
    genders = [2]

countries = [c.strip().upper() for c in countries_raw.split(",") if c.strip()]

interests_list = [
    x.strip() for x in detailed_targeting.split(",") if x.strip()
]


st.markdown("---")

st.subheader("4️⃣ Creative (Ad)")

col_c1, col_c2 = st.columns(2)
with col_c1:
    ad_name = st.text_input("Ad Name", value="Sully Auto Ad 1")
    primary_text = st.text_area(
        "Primary Text",
        value="Tap to discover the latest drops and campaigns powered by Sully’s Marketing Bot.",
    )
    headline = st.text_input("Headline", value="Discover What Sully Can Do For You")
with col_c2:
    description = st.text_input("Description", value="Smart marketing across Meta with one bot.")
    website_url = st.text_input("Destination URL", value="https://example.com")
    image_url = st.text_input(
        "Image URL (for link ad)",
        value="https://via.placeholder.com/1080x1080.png?text=Sully+Ad",
    )

st.info("ℹ️ Your Meta Page ID is read from secrets and used as the Facebook Page for this ad.")

st.markdown("---")

do_create = st.button("🚀 Create Campaign + Ad Set + Ad")


# =========== META CREATION LOGIC ===========

def build_targeting():
    targeting = {
        "geo_locations": {"countries": countries},
        "age_min": int(min_age),
        "age_max": int(max_age),
    }
    if genders:
        targeting["genders"] = genders

    if interests_list:
        # NOTE: For real interest targeting, you must look up interest IDs first.
        # Here we only attach them as flexible_spec keywords for you to refine later.
        targeting["flexible_spec"] = [
            {"interests": [{"id": "6000000000000", "name": kw} for kw in interests_list]}
        ]
    return targeting


def create_meta_campaign(ad_account: AdAccount):
    params = {
        Campaign.Field.name: campaign_name,
        Campaign.Field.objective: objective,
        Campaign.Field.status: Campaign.Status.paused,  # start paused
        "special_ad_categories": [],
        "buying_type": buying_type,
    }
    campaign = ad_account.create_campaign(params=params)
    return campaign[Campaign.Field.id]


def create_meta_adset(ad_account: AdAccount, campaign_id: str):
    optimization_goal = OPTIMIZATION_MAP[objective_label]
    today = start_date.strftime("%Y-%m-%d")

    targeting = build_targeting()

    params = {
        AdSet.Field.name: f"{campaign_name} - AdSet",
        AdSet.Field.campaign_id: campaign_id,
        AdSet.Field.daily_budget: usd_to_cents(daily_budget_usd),
        AdSet.Field.billing_event: AdSet.BillingEvent.impressions,
        AdSet.Field.optimization_goal: optimization_goal,
        AdSet.Field.bid_strategy: "LOWEST_COST_WITHOUT_CAP",
        AdSet.Field.status: AdSet.Status.paused,
        AdSet.Field.start_time: f"{today}T00:00:00",
        AdSet.Field.targeting: targeting,
    }
    adset = ad_account.create_ad_set(params=params)
    return adset[AdSet.Field.id]


def create_meta_creative(ad_account: AdAccount):
    """
    Simplest possible link ad creative:
    - Uses your Page ID
    - Single image + link
    """
    link_data = {
        "message": primary_text,
        "link": website_url,
        "caption": website_url,
        "name": headline,
        "description": description,
        "picture": image_url,
    }

    object_story_spec = {
        "page_id": META_PAGE_ID,
        "link_data": link_data,
    }

    params = {
        AdCreative.Field.name: f"{ad_name} Creative",
        AdCreative.Field.object_story_spec: object_story_spec,
    }
    creative = ad_account.create_ad_creative(params=params)
    return creative[AdCreative.Field.id]


def create_meta_ad(ad_account: AdAccount, adset_id: str, creative_id: str):
    params = {
        Ad.Field.name: ad_name,
        Ad.Field.adset_id: adset_id,
        Ad.Field.creative: {"creative_id": creative_id},
        Ad.Field.status: Ad.Status.paused,  # start paused
    }
    ad = ad_account.create_ad(params=params)
    return ad[Ad.Field.id]


if do_create:
    if missing:
        st.error("❌ You must fix the missing Meta secrets above before creating campaigns.")
    else:
        try:
            acct = init_meta()
            with st.spinner("Creating campaign on Meta..."):
                campaign_id = create_meta_campaign(acct)
            st.success(f"✅ Campaign created: {campaign_id}")

            with st.spinner("Creating ad set..."):
                adset_id = create_meta_adset(acct, campaign_id)
            st.success(f"✅ Ad Set created: {adset_id}")

            with st.spinner("Creating ad creative..."):
                creative_id = create_meta_creative(acct)
            st.success(f"✅ Ad Creative created: {creative_id}")

            with st.spinner("Creating ad..."):
                ad_id = create_meta_ad(acct, adset_id, creative_id)
            st.success(f"🎉 Ad created: {ad_id}")

            result = {
                "campaign_id": campaign_id,
                "adset_id": adset_id,
                "creative_id": creative_id,
                "ad_id": ad_id,
            }
            st.subheader("Meta Objects Created")
            st.json(result)

            st.info("Everything is created in **PAUSED** status. Review & enable inside Meta Ads Manager.")
        except Exception as e:
            st.error(f"❌ Meta API error: {e}")
