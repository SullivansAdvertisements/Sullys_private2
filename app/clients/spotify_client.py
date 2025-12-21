def spotify_connection_status(secrets):
    if "SPOTIFY_API_KEY" not in secrets:
        return False, "Missing Spotify Ads API key"
    return True, "Spotify credentials loaded"


def spotify_sample_call():
    return {
        "audio_completion_rate": "92%",
        "recommended_spot_length": "30s",
    }