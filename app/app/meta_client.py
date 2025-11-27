"""
meta_client.py

Thin wrapper around the Meta (Facebook/Instagram) Marketing API
for Sully's Media Planner / Campaign Builder.

- Reads credentials from environment variables by default:
    META_SYSTEM_USER_TOKEN
    META_AD_ACCOUNT_ID        (numbers only, no "act_")
    META_BUSINESS_ID
    META_PAGE_ID
    META_PIXEL_ID
    META_IG_ACTOR_ID

- Exposes MetaClient with:
    .connection_status()
    .create_campaign(...)
    .create_adset(...)
    .create_ad(...)

You can also pass credentials explicitly to MetaClient(...) if you
don't want to rely on env vars.
"""

from __future__ import annotations

import os
import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, Tuple, Optional

import requests


DEFAULT_META_API_VERSION = "v18.0"


@dataclass
class MetaCredentials:
    system_user_token: Optional[str] = None
    ad_account_id: Optional[str] = None  # numeric only, no "act_"
    business_id: Optional[str] = None
    page_id: Optional[str] = None
    pixel_id: Optional[str] = None
    ig_actor_id: Optional[str] = None

    @classmethod
    def from_env(cls) -> "MetaCredentials":
        return cls(
            system_user_token=os.getenv("META_SYSTEM_USER_TOKEN"),
            ad_account_id=os.getenv("META_AD_ACCOUNT_ID"),
            business_id=os.getenv("META_BUSINESS_ID"),
            page_id=os.getenv("META_PAGE_ID"),
            pixel_id=os.getenv("META_PIXEL_ID"),
            ig_actor_id=os.getenv("META_IG_ACTOR_ID"),
        )


class MetaClient:
    """
    Simple Meta Marketing API client for campaigns, ad sets and ads.

    Usage:

        from meta_client import MetaClient

        meta = MetaClient()  # uses env vars
        ok, msg, missing = meta.connection_status()

        if ok:
            camp = meta.create_campaign("Test", "OUTCOME_AWARENESS")
            ...
    """

    def __init__(
        self,
        credentials: Optional[MetaCredentials] = None,
        api_version: str = DEFAULT_META_API_VERSION,
    ) -> None:
        if credentials is None:
            credentials = MetaCredentials.from_env()
        self.creds = credentials
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    # -----------------------------
    # Metadata / health
    # -----------------------------
    def connection_status(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Returns (ok, message, details) about whether all required credentials exist.
        """
        missing = []
        if not self.creds.system_user_token:
            missing.append("META_SYSTEM_USER_TOKEN")
        if not self.creds.ad_account_id:
            missing.append("META_AD_ACCOUNT_ID")
        if not self.creds.business_id:
            missing.append("META_BUSINESS_ID")
        if not self.creds.page_id:
            missing.append("META_PAGE_ID")
        if not self.creds.pixel_id:
            missing.append("META_PIXEL_ID")
        if not self.creds.ig_actor_id:
            missing.append("META_IG_ACTOR_ID")

        details: Dict[str, Any] = {
            "creds": asdict(self.creds),
            "missing": missing,
        }

        if missing:
            msg = (
                "Missing Meta credentials: "
                + ", ".join(missing)
                + ". Set them as environment variables or pass MetaCredentials explicitly."
            )
            return False, msg, details

        return True, "Meta credentials are present.", details

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 20,
    ) -> Dict[str, Any]:
        """
        Internal helper to send a request to the Graph API.

        Returns:
            {
                "ok": bool,
                "status": int,
                "url": str,
                "data": <response JSON or raw text>,
                "error": <optional error string>
            }
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            if method.upper() == "GET":
                resp = requests.get(url, params=params, timeout=timeout)
            else:
                resp = requests.post(url, params=params, data=data, timeout=timeout)

            try:
                payload = resp.json()
            except ValueError:
                payload = resp.text

            result: Dict[str, Any] = {
                "ok": resp.status_code == 200,
                "status": resp.status_code,
                "url": url,
                "data": payload,
            }

            if resp.status_code != 200:
                result["error"] = f"HTTP {resp.status_code}"
            return result

        except Exception as e:
            return {
                "ok": False,
                "status": 0,
                "url": url,
                "data": None,
                "error": f"Exception: {e}",
            }

    # -----------------------------
    # Campaigns
    # -----------------------------
    def create_campaign(
        self,
        name: str,
        objective: str,
        status: str = "PAUSED",
        buying_type: str = "AUCTION",
        special_ad_categories: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Create a campaign.

        objective: OUTCOME_AWARENESS, OUTCOME_TRAFFIC, OUTCOME_ENGAGEMENT,
                   OUTCOME_LEADS, OUTCOME_SALES, OUTCOME_APP_PROMOTION, etc.
        """
        ok, msg, _ = self.connection_status()
        if not ok:
            return {"ok": False, "error": msg}

        if special_ad_categories is None:
            special_ad_categories = []

        payload = {
            "name": name,
            "objective": objective,
            "status": status,
            "buying_type": buying_type,
            "special_ad_categories": json.dumps(special_ad_categories),
            "access_token": self.creds.system_user_token,
        }

        path = f"act_{self.creds.ad_account_id}/campaigns"
        result = self._request("POST", path, data=payload)
        return result

    # -----------------------------
    # Ad sets
    # -----------------------------
    @staticmethod
    def _map_optimization_goal(objective: str) -> tuple:
        """
        Map high-level objective string to optimization_goal + billing_event.
        """
        o = objective.upper()
        if "AWARENESS" in o:
            return "REACH", "IMPRESSIONS"
        if "TRAFFIC" in o:
            return "LINK_CLICKS", "IMPRESSIONS"
        if "ENGAGEMENT" in o:
            return "ENGAGED_USERS", "IMPRESSIONS"
        if "LEADS" in o:
            return "LEAD_GENERATION", "IMPRESSIONS"
        if "SALES" in o or "CONVERSION" in o:
            return "CONVERSIONS", "IMPRESSIONS"
        return "REACH", "IMPRESSIONS"

    def create_adset(
        self,
        name: str,
        campaign_id: str,
        daily_budget_usd: float,
        objective: str,
        country: str = "US",
        age_min: int = 18,
        age_max: int = 65,
        interests: Optional[list[str]] = None,
        status: str = "PAUSED",
    ) -> Dict[str, Any]:
        """
        Create an ad set under a campaign.

        - Budget is set at the ad set level (no campaign budget sharing).
        - For conversion-style objectives, pixel is attached if available.
        """
        ok, msg, _ = self.connection_status()
        if not ok:
            return {"ok": False, "error": msg}
        if not campaign_id:
            return {"ok": False, "error": "campaign_id is required"}

        optimization_goal, billing_event = self._map_optimization_goal(objective)
        daily_budget_minor = int(float(daily_budget_usd) * 100)  # USD -> cents

        if country.upper() == "WORLDWIDE":
            geo = {"geo_locations": {"location_types": ["home", "recent"]}}
        else:
            geo = {
                "geo_locations": {
                    "countries": [country.upper()],
                    "location_types": ["home", "recent"],
                }
            }

        targeting: Dict[str, Any] = {
            **geo,
            "age_min": age_min,
            "age_max": age_max,
        }

        if interests:
            targeting["flexible_spec"] = [
                {
                    "interests": [{"name": i, "id": i} for i in interests]
                    # NOTE: properly, you should pass real interest IDs
                }
            ]

        payload: Dict[str, Any] = {
            "name": name,
            "campaign_id": campaign_id,
            "daily_budget": str(daily_budget_minor),
            "billing_event": billing_event,
            "optimization_goal": optimization_goal,
            "status": status,
            "targeting": json.dumps(targeting),
            "access_token": self.creds.system_user_token,
        }

        if optimization_goal == "CONVERSIONS" and self.creds.pixel_id:
            payload["promoted_object"] = json.dumps({"pixel_id": self.creds.pixel_id})

        path = f"act_{self.creds.ad_account_id}/adsets"
        result = self._request("POST", path, data=payload)
        return result

    # -----------------------------
    # Ads (creative + ad)
    # -----------------------------
    def create_ad(
        self,
        name: str,
        adset_id: str,
        link_url: str,
        primary_text: str,
        headline: str,
        description: str,
        image_url: Optional[str] = None,
        call_to_action: str = "LEARN_MORE",
        status: str = "PAUSED",
    ) -> Dict[str, Any]:
        """
        Create an ad creative and then an ad under an existing ad set.

        NOTE: This uses Page ID and IG actor ID from credentials for placements.
        For image_url, you typically need to upload the image first and reference
        an image_hash. This helper instead uses link_data (page post) with a URL.
        """
        ok, msg, _ = self.connection_status()
        if not ok:
            return {"ok": False, "error": msg}
        if not adset_id:
            return {"ok": False, "error": "adset_id is required"}

        if not self.creds.page_id:
            return {"ok": False, "error": "META_PAGE_ID is missing"}

        # 1) Create ad creative
        creative_path = f"act_{self.creds.ad_account_id}/adcreatives"
        object_story_spec: Dict[str, Any] = {
            "page_id": self.creds.page_id,
            "link_data": {
                "message": primary_text,
                "name": headline,
                "description": description,
                "link": link_url,
                "call_to_action": {
                    "type": call_to_action,
                    "value": {"link": link_url},
                },
            },
        }
        if self.creds.ig_actor_id:
            object_story_spec["instagram_actor_id"] = self.creds.ig_actor_id.strip()

        creative_payload = {
            "name": f"{name} – Creative",
            "object_story_spec": json.dumps(object_story_spec),
            "access_token": self.creds.system_user_token,
        }

        creative_resp = self._request("POST", creative_path, data=creative_payload)
        if not creative_resp.get("ok") or "id" not in (creative_resp.get("data") or {}):
            return {
                "ok": False,
                "step": "creative",
                "error": "Failed to create creative",
                "response": creative_resp,
            }

        creative_id = creative_resp["data"]["id"]

        # 2) Create ad
        ad_path = f"act_{self.creds.ad_account_id}/ads"
        ad_payload = {
            "name": name,
            "adset_id": adset_id,
            "creative": json.dumps({"creative_id": creative_id}),
            "status": status,
            "access_token": self.creds.system_user_token,
        }

        ad_resp = self._request("POST", ad_path, data=ad_payload)
        if not ad_resp.get("ok"):
            return {
                "ok": False,
                "step": "ad",
                "error": "Failed to create ad",
                "response": ad_resp,
            }

        return {
            "ok": True,
            "creative": creative_resp,
            "ad": ad_resp,
        }


# Optional convenience function if you prefer a singleton-style client
def get_default_client() -> MetaClient:
    return MetaClient()
