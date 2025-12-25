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