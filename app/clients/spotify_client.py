def spotify_connection_status(secrets):
    if "SPOTIFY_API_KEY" not in secrets:
        return False, "Missing Spotify API key"
    return True, "Spotify Ads creative planner ready"