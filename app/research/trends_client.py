def run_full_research(niche, goal):
    return {
        "niche": niche,
        "goal": goal,
        "keywords": get_google_keywords(niche),
        "hashtags": get_tiktok_hashtags(niche),
        "locations": get_top_locations(niche),
        "audiences": get_meta_audiences(niche),
        "age_range": "18-34",
        "gender": "All",
        "platform_signals": {
            "google": {...},
            "youtube": {...},
            "tiktok": {...},
            "meta": {...}
        }
    }