"""
common_ai.py
-------------
Shared AI-style logic for:
- Headlines
- Primary text
- Descriptions
- CTAs
- Platform-specific ad copy variants

NO Streamlit UI code allowed here.
"""

import random


# -----------------------------
# CORE COPY GENERATORS
# -----------------------------
def generate_headlines(niche: str, goal: str, brand: str = "Your Brand"):
    niche = niche.lower()
    goal = goal.lower()

    base = {
        "music": [
            f"New music dropping now",
            f"Tap in — {brand} just released something special",
            f"This sound is blowing up",
            f"Your next favorite track is here",
        ],
        "clothing": [
            f"New drop just landed",
            f"Limited pieces — don’t miss this",
            f"Streetwear done right",
            f"{brand} just leveled up",
        ],
        "homecare": [
            f"Care your family can trust",
            f"Support your loved ones at home",
            f"Professional care starts here",
            f"Peace of mind begins today",
        ],
    }

    goal_mod = {
        "awareness": ["Discover", "Introducing", "Now trending"],
        "traffic": ["Learn more", "See why", "Find out how"],
        "leads": ["Get a free quote", "Schedule today", "Talk to us"],
        "sales": ["Shop now", "Order today", "Limited availability"],
        "conversions": ["Get started", "Sign up now", "Don’t wait"],
    }

    headlines = []
    for h in base.get(niche, []):
        headlines.append(h)

    for g in goal_mod.get(goal, []):
        headlines.append(f"{g} with {brand}")

    return list(set(headlines))[:10]


def generate_primary_text(niche: str, goal: str, offer: str = ""):
    texts = []

    if niche == "music":
        texts.extend([
            "If you love discovering new sounds, this one’s for you.",
            "Streaming everywhere now — tap in.",
            "Fans can’t stop replaying this.",
        ])

    elif niche == "clothing":
        texts.extend([
            "Designed for those who stand out.",
            "Limited quantities available — once it’s gone, it’s gone.",
            "Quality, fit, and culture in one drop.",
        ])

    elif niche == "homecare":
        texts.extend([
            "Professional caregivers when your family needs it most.",
            "Trusted support right at home.",
            "Licensed, compassionate, reliable care.",
        ])

    if offer:
        texts.append(f"{offer}")

    goal_tail = {
        "awareness": "See what everyone’s talking about.",
        "traffic": "Tap to learn more.",
        "leads": "Get started in seconds.",
        "sales": "Order today before it’s gone.",
        "conversions": "Sign up now.",
    }

    texts = [f"{t} {goal_tail.get(goal, '')}".strip() for t in texts]
    return texts[:10]


def generate_descriptions(niche: str):
    return {
        "music": [
            "Available on all platforms.",
            "Listen now.",
        ],
        "clothing": [
            "Fast shipping available.",
            "Limited stock.",
        ],
        "homecare": [
            "Serving your local area.",
            "Care you can rely on.",
        ],
    }.get(niche, [])


def generate_ctas(goal: str):
    return {
        "awareness": ["Learn More", "Watch Now"],
        "traffic": ["Learn More", "Visit Website"],
        "leads": ["Sign Up", "Get Quote"],
        "sales": ["Shop Now", "Buy Now"],
        "conversions": ["Get Started", "Apply Now"],
    }.get(goal, ["Learn More"])


# -----------------------------
# PLATFORM-SPECIFIC PACKS
# -----------------------------
def generate_meta_creatives(niche, goal, brand="Your Brand", offer=""):
    return {
        "headlines": generate_headlines(niche, goal, brand),
        "primary_texts": generate_primary_text(niche, goal, offer),
        "descriptions": generate_descriptions(niche),
        "ctas": generate_ctas(goal),
    }


def generate_google_ads(niche, goal, brand="Your Brand"):
    headlines = generate_headlines(niche, goal, brand)
    descriptions = generate_descriptions(niche)

    return {
        "headlines": headlines[:15],
        "descriptions": descriptions[:4],
    }


def generate_tiktok_hooks(niche):
    hooks = {
        "music": [
            "Wait for the drop 🎧",
            "This song is stuck in my head",
            "POV: you just found your new favorite artist",
        ],
        "clothing": [
            "This fit goes crazy",
            "Outfit check 👀",
            "Would you wear this?",
        ],
        "homecare": [
            "When family needs real support",
            "Care that actually matters",
            "Here’s how we help families",
        ],
    }
    return hooks.get(niche, [])


def generate_spotify_script(brand="Your Brand"):
    return [
        f"Hey, it’s {brand}. If you’re listening right now, you’re exactly who we made this for.",
        f"Tap now to learn more about {brand}.",
    ]


# -----------------------------
# UTILITY
# -----------------------------
def pick_random(items, k=3):
    return random.sample(items, min(k, len(items)))