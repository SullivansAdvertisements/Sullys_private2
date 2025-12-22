# core/common_ai.py
"""
AI-style generators for headlines, descriptions, CTAs.
NO Streamlit code here.
"""

from typing import List
import random


def generate_headlines(platform: str, niche: str, goal: str) -> List[str]:
    platform = platform.lower()
    niche = niche.lower()
    goal = goal.lower()

    base = {
        "music": [
            "New music just dropped",
            "This artist is next up",
            "You haven’t heard this yet",
            "Sound you’ll replay all day",
        ],
        "clothing": [
            "Limited drop now live",
            "Your next favorite fit",
            "Streetwear done right",
            "Don’t miss this drop",
        ],
        "homecare": [
            "Care your family can trust",
            "Support when it matters most",
            "Professional home care services",
            "Peace of mind starts here",
        ],
    }

    goal_mod = {
        "awareness": ["Discover", "Introducing", "Now trending"],
        "traffic": ["Tap to learn more", "See why everyone’s talking"],
        "leads": ["Get a free consultation", "Speak with a specialist"],
        "sales": ["Book today", "Limited availability"],
        "conversions": ["Start now", "Apply today"],
    }

    headlines = []
    for h in base.get(niche, ["Discover more"]):
        prefix = random.choice(goal_mod.get(goal, ["Explore"]))
        headlines.append(f"{prefix}: {h}")

    return headlines


def generate_descriptions(niche: str, goal: str) -> List[str]:
    niche = niche.lower()
    goal = goal.lower()

    if niche == "music":
        return [
            "Streaming everywhere. Tap in now.",
            "If you like new sounds, this is for you.",
        ]
    if niche == "clothing":
        return [
            "High-quality streetwear. Limited quantities.",
            "Built for everyday wear. Shop now.",
        ]
    if niche == "homecare":
        return [
            "Trusted caregivers in your area.",
            "Licensed, insured, compassionate care.",
        ]

    return ["Learn more today."]


def generate_ctas(goal: str) -> List[str]:
    goal = goal.lower()

    return {
        "awareness": ["Learn More", "Discover"],
        "traffic": ["Visit Site", "See More"],
        "leads": ["Get Quote", "Contact Us"],
        "sales": ["Book Now", "Shop Now"],
        "conversions": ["Apply Now", "Start Today"],
    }.get(goal, ["Learn More"])