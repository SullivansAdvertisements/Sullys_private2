# core/common_ai.py
"""
Central AI-style generators for ad copy, headlines, hooks, and scripts.
NO Streamlit code in this file.
Pure Python only.
"""

from typing import List, Dict
import random


# -------------------------
# Meta (Facebook / Instagram)
# -------------------------
def generate_meta_creatives(
    niche: str,
    goal: str,
    offer: str,
    brand_name: str = "Your Brand",
) -> List[Dict[str, str]]:
    headlines = [
        f"{offer}",
        f"{brand_name} Is Changing the Game",
        f"Don’t Miss This Drop",
        f"Why Everyone’s Talking About {brand_name}",
        f"Limited Time Only",
    ]

    primary_texts = [
        f"{offer} — tap to learn more.",
        f"{brand_name} is built for people who want better.",
        f"This is your sign to check out {brand_name}.",
        f"Trusted by people who care about quality.",
    ]

    descriptions = [
        "Learn more today.",
        "Limited availability.",
        "Tap to explore.",
        "See why people love it.",
    ]

    creatives = []
    for _ in range(5):
        creatives.append(
            {
                "headline": random.choice(headlines),
                "primary_text": random.choice(primary_texts),
                "description": random.choice(descriptions),
                "cta": "LEARN_MORE",
            }
        )

    return creatives


# -------------------------
# Google Ads / YouTube
# -------------------------
def generate_google_ads(
    keywords: List[str],
    brand_name: str,
) -> List[Dict[str, str]]:
    ads = []
    for kw in keywords:
        ads.append(
            {
                "headline_1": f"{brand_name} – {kw.title()}",
                "headline_2": "Official Site",
                "headline_3": "Get Started Today",
                "description_1": f"Discover {kw} with {brand_name}.",
                "description_2": "Fast. Reliable. Trusted.",
            }
        )
    return ads


# -------------------------
# TikTok
# -------------------------
def generate_tiktok_hooks(
    niche: str,
    offer: str,
) -> List[str]:
    hooks = [
        f"POV: you just discovered {offer}",
        "Watch this before it’s gone",
        "Nobody is talking about this yet",
        "This changed everything for me",
        "Don’t scroll — you need this",
    ]
    return hooks


# -------------------------
# Spotify
# -------------------------
def generate_spotify_script(
    brand_name: str,
    offer: str,
) -> str:
    return (
        f"Hey, it’s {brand_name}. "
        f"If you’re listening right now, you’ll love this. "
        f"{offer}. Tap now to learn more."
    )


# -------------------------
# Utility (used across tabs)
# -------------------------
def normalize_keywords(raw_keywords: str) -> List[str]:
    return [k.strip().lower() for k in raw_keywords.replace(",", "\n").split("\n") if k.strip()]