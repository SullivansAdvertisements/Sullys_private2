# app/meta_client.py

import os
from typing import Optional, Dict, Any

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

META_TOKEN = os.getenv("META_SYSTEM_USER_TOKEN")
META_AD_ACCOUNT = os.getenv("META_AD_ACCOUNT_ID")  # numeric, e.g. 123456789012345

def get_ad_account() -> Optional[AdAccount]:
    """Return an AdAccount instance if env vars are set, otherwise None."""
    if not META_TOKEN or not META_AD_ACCOUNT:
        return None

    # Initialize the SDK with just the access token (simple mode)
    FacebookAdsApi.init(access_token=META_TOKEN)
    return AdAccount(f"act_{META_AD_ACCOUNT}")

def test_meta_connection() -> Dict[str, Any]:
    """
    Try a simple call to Meta Marketing API:
    - Gets ad account name and currency.
    """
    account = get_ad_account()
    if account is None:
        return {"ok": False, "error": "META_TOKEN or META_AD_ACCOUNT not set."}

    try:
        fields = ["name", "currency", "account_id"]
        data = account.api_get(fields=fields)
        return {
            "ok": True,
            "name": data.get("name"),
            "currency": data.get("currency"),
            "account_id": data.get("account_id"),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
