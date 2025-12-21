def google_connection_status(secrets):
    if "GOOGLE_DEVELOPER_TOKEN" not in secrets:
        return False, "Missing Google Ads credentials"
    return True, "Google Ads credentials loaded"


def youtube_connection_status(secrets):
    if "GOOGLE_DEVELOPER_TOKEN" not in secrets:
        return False, "Missing YouTube credentials"
    return True, "YouTube credentials loaded"


def google_sample_call():
    return {
        "search_volume": "High",
        "avg_cpc": "$1.80",
        "competition": "Medium",
    }