import requests

def meta_connection_status(secrets):
    """Check if Meta token is present."""
    token = secrets.get("META_SYSTEM_USER_TOKEN", None)
    if not token:
        return False, "Missing META_SYSTEM_USER_TOKEN in secrets."
    return True, "Token detected (connection placeholder)."

def meta_sample_call(secrets):
    """Perform a test Graph API call if credentials are valid."""
    token = secrets.get("META_SYSTEM_USER_TOKEN", None)
    ad_account = secrets.get("META_AD_ACCOUNT_ID", None)
    if not token or not ad_account:
        return {"error": "Missing token or account ID."}

    try:
        resp = requests.get(
            f"https://graph.facebook.com/v18.0/act_{ad_account}",
            params={"access_token": token},
            timeout=10,
        )
        return resp.json()
    except Exception as e:
        return {"error": str(e)}
