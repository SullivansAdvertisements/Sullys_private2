import requests

# This module is a placeholder shell for Google Ads / YouTube integrations.
# Real calls require:
# - Google Ads / Google Cloud project
# - OAuth or service account credentials
# - google-ads Python SDK (not included yet in requirements.txt)


def google_connection_status(secrets):
    required = ["GOOGLE_DEVELOPER_TOKEN", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"]
    missing = [k for k in required if not secrets.get(k)]
    if missing:
        return False, f"Missing Google credentials in secrets: {', '.join(missing)}"
    return True, "Google creds present (but no live API call wired yet)."


def youtube_connection_status(secrets):
    required = ["YOUTUBE_API_KEY"]
    missing = [k for k in required if not secrets.get(k)]
    if missing:
        return False, f"Missing YouTube credentials in secrets: {', '.join(missing)}"
    return True, "YouTube API key present (but no live API call wired yet)."


def google_sample_call():
    """
    Placeholder that *could* hit a public Google endpoint if you wire an API key.
    For now, returns a static message so the UI doesn't crash.
    """
    return {"note": "TODO: implement Google Ads / YouTube API call here."}
