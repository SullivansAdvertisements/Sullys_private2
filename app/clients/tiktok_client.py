import requests

# Placeholder for TikTok Ads integration.
# Real integration needs:
# - TikTok for Business account
# - TikTok Ads API access + OAuth credentials


def tiktok_connection_status(secrets):
    required = ["TIKTOK_ACCESS_TOKEN", "TIKTOK_ADVERTISER_ID"]
    missing = [k for k in required if not secrets.get(k)]
    if missing:
        return False, f"Missing TikTok credentials in secrets: {', '.join(missing)}"
    return True, "TikTok creds present (but no live API call wired yet)."


def tiktok_sample_call():
    return {"note": "TODO: implement TikTok Ads API call here."}
