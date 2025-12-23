# core/common_ai.py
# Phase E – Creative Intelligence Engine

from typing import List
import random


def generate_headlines(platform: str, niche: str, goal: str) -> List[str]:
    base_hooks = {
        "music": [
            "This song is blowing up",
            "You haven’t heard this yet",
            "The sound everyone’s using",
        ],
        "clothing": [
            "This drop is almost gone",
            "Streetwear done right",
            "Your next favorite fit",
        ],
        "homecare": [
            "Care your family can trust",
            "Support when it matters most",
            "Reliable home care starts here",
        ],
    }

    hooks = base_hooks.get(niche.lower(), ["Don’t miss this"])
    return [
        f"{hook} | {platform}" for hook in random.sample(hooks, min(3, len(hooks)))
    ]


def generate_primary_text(
    platform: str,
    niche: str,
    goal: str,
    offer: str = "Learn more today",
) -> List[str]:
    templates = [
        f"Looking for {niche}? {offer}. Tap to see why people are switching.",
        f"This is for anyone serious about {niche}. {offer}.",
        f"{niche.title()} made simple. {offer}.",
    ]
    return templates


def generate_ctas(platform: str, goal: str) -> List[str]:
    ctas = {
        "awareness": ["Learn More", "Watch Now"],
        "traffic": ["Learn More", "Visit Site"],
        "leads": ["Sign Up", "Get Quote"],
        "sales": ["Shop Now", "Buy Now"],
    }
    return ctas.get(goal.lower(), ["Learn More"])


def generate_full_creative(
    platform: str,
    niche: str,
    goal: str,
    offer: str,
):
    return {
        "headlines": generate_headlines(platform, niche, goal),
        "primary_text": generate_primary_text(platform, niche, goal, offer),
        "ctas": generate_ctas(platform, goal),
    }