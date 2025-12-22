def tiktok_connection_status(secrets):
    if "TIKTOK_ACCESS_TOKEN" not in secrets:
        return False, "Missing TikTok access token"
    return True, "TikTok Ads credentials detected"