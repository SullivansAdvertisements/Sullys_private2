# research/tiktok_trends.py
# Phase C – TikTok Creative Center Research (API-safe shell)

from typing import Dict, List


def get_tiktok_trends(
    seed_terms: List[str],
    region: str = "US",
) -> Dict:
    """
    TikTok does not provide a fully open public trends API.
    This function prepares structured research output using:
    - Seed keywords
    - Category expansion
    - Creative angle mapping

    Ready to be wired to TikTok Creative Center scraping or API later.
    """

    if not seed_terms:
        return {"error": "No seed terms provided"}

    expanded_keywords = []
    creative_angles = []

    for term in seed_terms:
        expanded_keywords.extend(
            [
                f"{term} tutorial",
                f"{term} before after",
                f"{term} review",
                f"{term} hack",
                f"{term} trend",
            ]
        )

        creative_angles.extend(
            [
                "POV storytelling",
                "Problem → solution",
                "Quick hook in first 2 seconds",
                "UGC-style selfie video",
                "Text-on-screen explainer",
            ]
        )

    return {
        "platform": "TikTok",
        "region": region,
        "seed_terms": seed_terms,
        "expanded_keywords": list(set(expanded_keywords)),
        "creative_angles": list(set(creative_angles)),
        "recommended_formats": [
            "In-Feed Video (9:16)",
            "Spark Ads",
            "Carousel",
        ],
        "notes": [
            "Use trending sounds manually from Creative Center",
            "Test 3–5 creatives per ad group",
            "Fast hooks outperform polished ads",
        ],
    }