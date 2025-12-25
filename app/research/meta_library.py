def search_meta_ads(keyword: str):
    """
    Lightweight Meta Ad Library-style research.
    Does NOT scrape illegally.
    """
    if not keyword:
        return {"error": "No keyword"}

    return {
        "keyword": keyword,
        "common_formats": [
            "Short-form video",
            "Carousel",
            "Static image + headline",
        ],
        "common_angles": [
            "Limited time offer",
            "Social proof",
            "Problem-solution",
        ],
        "cta_examples": [
            "Shop Now",
            "Learn More",
            "Sign Up",
        ],
        "note": "Inspired by public Meta Ad Library patterns",
    }
import pandas as pd

def search_meta_ads(keyword: str, country: str = "US"):
    data = [
        {
            "advertiser": "Brand Alpha",
            "headline": f"{keyword} that converts",
            "cta": "Shop Now",
            "platform": "Instagram"
        },
        {
            "advertiser": "Brand Beta",
            "headline": f"Why everyone loves {keyword}",
            "cta": "Learn More",
            "platform": "Facebook"
        }
    ]

    return pd.DataFrame(data)
