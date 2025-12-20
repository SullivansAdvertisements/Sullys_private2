import os

def spotify_campaign_generator(brand, objective, budget, keywords):
    script = f"Hey, it’s {brand}. While you’re listening, tap to check out our latest — only for a limited time."
    return {
        "brand": brand,
        "objective": objective,
        "daily_budget": budget,
        "script_30s": script,
        "status": "demo",  # Spotify Ads API is private; wire your vendor creds if available
        "notes": ["Use 24/7 pacing, cap at 30s creative", "Add companion banner"]
    }
