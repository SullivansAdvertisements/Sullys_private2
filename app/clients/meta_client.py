def meta_connection_status(secrets):
    required = [
        "META_SYSTEM_USER_TOKEN",
        "META_AD_ACCOUNT_ID",
        "META_PAGE_ID",
        "META_PIXEL_ID"
    ]

    missing = [k for k in required if k not in secrets]
    if missing:
        return False, f"Missing Meta secrets: {', '.join(missing)}"

    return True, "Meta Ads credentials detected"


def meta_reach_estimate_shell(budget: float, country: str):
    """
    Meta reach estimates require live Graph API calls.
    This is a safe placeholder that Streamlit can display.
    """
    return {
        "daily_budget": budget,
        "country": country,
        "estimated_reach_range": "Use Meta Reach Estimate API"
    }