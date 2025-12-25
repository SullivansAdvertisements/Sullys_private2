from research.google_trends import get_google_trends
from research.youtube_trends import get_youtube_trends
from research.tiktok_trends import get_tiktok_trends
from research.meta_library import search_meta_ads

def run_full_research(keyword: str, timeframe: str):
    return {
        "google": get_google_trends(keyword, timeframe),
        "youtube": get_youtube_trends(keyword),
        "tiktok": get_tiktok_trends(keyword),
        "meta": search_meta_ads(keyword)
    }