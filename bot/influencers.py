# bot/influencers.py

from typing import List, Dict


def score_influencer(
    followers: int,
    engagement_rate: float,
    niche_match: bool,
) -> int:
    """
    Simple influencer score (0–100)
    """
    score = 0

    if followers >= 100000:
        score += 40
    elif followers >= 25000:
        score += 25
    else:
        score += 10

    if engagement_rate >= 5:
        score += 40
    elif engagement_rate >= 2:
        score += 25
    else:
        score += 10

    if niche_match:
        score += 20

    return min(score, 100)


def build_influencer_list(raw_creators: List[Dict]) -> List[Dict]:
    """
    Normalizes and scores influencers
    """
    results = []

    for c in raw_creators:
        score = score_influencer(
            followers=c.get("followers", 0),
            engagement_rate=c.get("engagement_rate", 0),
            niche_match=c.get("niche_match", False),
        )

        results.append({
            "name": c.get("name"),
            "platform": c.get("platform"),
            "followers": c.get("followers"),
            "engagement_rate": c.get("engagement_rate"),
            "score": score,
            "contact": c.get("email") or c.get("dm"),
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)


def generate_outreach_email(
    creator_name: str,
    brand: str,
    offer: str,
    platform: str,
) -> str:
    """
    Email / DM template
    """
    return f"""
Hi {creator_name},

I’m reaching out from {brand}. We’ve been following your content on {platform}
and love your style and audience.

We’d love to collaborate and offer:
{offer}

If you’re interested, let’s chat details!

Best,
{brand}
"""