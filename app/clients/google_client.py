def google_connection_status(secrets):
    if "GOOGLE_DEVELOPER_TOKEN" not in secrets:
        return False, "Missing Google Ads developer token"
    return True, "Google Ads credentials detected"


def youtube_connection_status(secrets):
    if "GOOGLE_REFRESH_TOKEN" not in secrets:
        return False, "Missing YouTube OAuth token"
    return True, "YouTube credentials detected"