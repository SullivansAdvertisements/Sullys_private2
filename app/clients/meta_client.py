def meta_connection_status(secrets):
    required = [
        "META_SYSTEM_USER_TOKEN",
        "META_AD_ACCOUNT_ID",
        "META_PAGE_ID",
    ]

    missing = [k for k in required if k not in secrets]

    if missing:
        return False, f"Missing: {', '.join(missing)}"

    return True, "Meta credentials loaded"


def meta_reach_estimate(daily_budget):
    # Meta does NOT allow free reach API without approvals
    # This is a compliant modeled estimate
    cpm = 12  # conservative average
    reach = int((daily_budget / cpm) * 1000)
    return {
        "estimated_daily_reach": reach,
        "estimated_monthly_reach": reach * 30,
    }


def meta_sample_call(secrets):
    return {
        "status": "connected",
        "note": "Campaign creation requires advanced permissions",
    }