def find_influencers(niche: str, country: str, platform: str = "instagram"):
    base = {
        "music": [
            {"handle": "@musicplugdaily", "followers": 120000, "type": "playlist page"},
            {"handle": "@unsignedheat", "followers": 85000, "type": "music blog"},
        ],
        "clothing": [
            {"handle": "@streetwearhub", "followers": 200000, "type": "fashion page"},
            {"handle": "@dailyfits", "followers": 95000, "type": "UGC creator"},
        ],
        "homecare": [
            {"handle": "@caregiverlife", "followers": 60000, "type": "educational"},
            {"handle": "@eldercaretips", "followers": 45000, "type": "authority page"},
        ],
    }

    results = base.get(niche.lower(), [])

    for r in results:
        r["platform"] = platform
        r["country_focus"] = country
        r["estimated_cost"] = estimate_influencer_cost(r["followers"])

    return results


def estimate_influencer_cost(followers: int):
    if followers < 25000:
        return "$50–$150"
    if followers < 100000:
        return "$150–$500"
    return "$500–$2,000+"