# research/youtube_trends.py
# Phase C – YouTube Search & Video Research Engine

from typing import List, Dict


def get_youtube_trends(
    seed_terms: List[str],
    region: str = "US",
) -> Dict:
    """
    Structured YouTube keyword + content research.
    Designed to feed Google Ads & YouTube campaigns.
    """

    if not seed_terms:
        return {"error": "No seed terms provided"}

    expanded_queries = []
    content_formats = []

    for term in seed_terms:
        expanded_queries.extend(
            [
                f"{term} review",
                f"{term} tutorial",
                f"{term} explained",
                f"{term} vs competitors",
                f"best {term}",
            ]
        )

        content_formats.extend(
            [
                "Skippable in-stream (5s hook)",
                "In-feed video",
                "Shorts (repurpose TikTok)",
            ]
        )

    return {
        "platform": "YouTube",
        "region": region,
        "seed_terms": seed_terms,
        "expanded_queries": list(set(expanded_queries)),
        "content_formats": list(set(content_formats)),
        "audience_strategies": [
            "Custom intent (search keywords)",
            "Channel placements (competitors)",
            "Remarketing (site + video viewers)",
        ],
        "notes": [
            "Hook must land before skip",
            "Use subtitles for mobile",
            "Retarget viewers into Search or Meta",
        ],
    }
import pandas as pd

def get_youtube_trends(keyword: str, region: str = "US"):
    data = [
        {
            "video_title": f"{keyword} explained",
            "estimated_views": 1200000,
            "category": "Education",
            "platform": "YouTube"
        },
        {
            "video_title": f"{keyword} viral breakdown",
            "estimated_views": 890000,
            "category": "Entertainment",
            "platform": "YouTube"
        }
    ]

    return pd.DataFrame(data)
