def tiktok_connection_status(secrets):
    if "TIKTOK_ACCESS_TOKEN" not in secrets:
        return False, "Missing TikTok token"
    return True, "TikTok credentials loaded"


def tiktok_sample_call():
    return {
        "trend_strength": "High",
        "avg_watch_time": "6.2s",
        "recommended_format": "UGC 9:16",
    }