import requests

# Placeholder for Spotify Ads or Spotify data integrations.
# Real integration needs:
# - Spotify Ads or Web API client ID / secret
# - OAuth token flow


def spotify_connection_status(secrets):
    required = ["SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET"]
    missing = [k for k in required if not secrets.get(k)]
    if missing:
        return False, f"Missing Spotify creds in secrets: {', '.join(missing)}"
    return True, "Spotify creds present (but no live API call wired yet)."


def spotify_sample_call():
    return {"note": "TODO: implement Spotify Ads / Discovery call here."}
