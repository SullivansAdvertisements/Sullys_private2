# research/meta_library.py
"""
Meta Ad Library research helper.
Uses Meta Ad Library public API.
NO Streamlit UI code here.
"""

import requests
from typing import Dict, List

META_AD_LIBRARY_URL = "https://graph.facebook.com/v18.0/ads_archive"


def search_meta_ads(
    query: str,
    country: str = "US",
    limit: int = 10,
    access_token: str | None = None,
) -> Dict:
    """
    Search Meta Ad Library for ads related to a keyword.
    Returns safe JSON for Streamlit display.
    """

    if not query:
        return {"error": "No search query provided", "results": []}

    if not access_token:
        return {
            "error": "Meta Ad Library requires a public access token",
            "results": [],
        }

    params = {
        "search_terms": query,
        "ad_reached_countries": country,
        "ad_active_status": "ALL",
        "fields": ",".join(
            [
                "id",
                "page_name",
                "ad_creative_body",
                "ad_creative_link_title",
                "ad_creative_link_description",
                "publisher_platforms",
                "spend",
                "impressions",
            ]
        ),
        "limit": limit,
        "access_token": access_token,
    }

    try:
        resp = requests.get(META_AD_LIBRARY_URL, params=params, timeout=15)
        data = resp.json()

        if resp.status_code != 200:
            return {
                "error": f"Meta API error {resp.status_code}",
                "response": data,
            }

        return {
            "results": data.get("data", []),
        }

    except Exception as e:
        return {
            "error": str(e),
            "results": [],
        }