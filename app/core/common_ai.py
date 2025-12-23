# core/common_ai.py
# AI-style generators (safe logic, no external API calls)

import random


def generate_headlines(platform: str, niche: str, goal: str, count: int = 5):
    base = {
        "Music": [
            "New music just dropped",
            "Your next favorite artist",
            "This track is going viral",
            "Sound you haven’t heard before",
        ],
        "Clothing": [
            "Limited drop now live",
            "Streetwear done right",
            "Don’t miss this collection",
            "Built for everyday wear",
        ],
        "Homecare": [
            "Care your family can trust",
            "Support when it matters most",
            "Quality home care near you",
            "Peace of mind starts here",
        ],
    }

    platform_flavor = {
        "Meta": ["Tap to learn more", "Shop now", "See why everyone’s switching"],
        "Google": ["Get started today", "Compare options", "Find out more"],
        "TikTok": ["Wait till the end", "This changed everything", "You need this"],
        "Spotify": ["Listen now", "Discover the sound", "Tap to play"],
    }

    headlines = []
    for _ in range(count):
        h = f"{random.choice(base.get(niche, ['Discover more']))} – {random.choice(platform_flavor.get(platform, ['Learn more']))}"
        headlines.append(h)

    return headlines


def generate_primary_text(platform: str, niche: str, goal: str):
    templates = {
        "Music": "If you love discovering new sounds, this is for you. Tap in and listen now.",
        "Clothing": "Designed for comfort and style. Limited quantities available.",
        "Homecare": "Trusted, compassionate care tailored to your family’s needs.",
    }

    platform_cta = {
        "Meta": "Tap below to learn more.",
        "Google": "Visit our site to get started.",
        "TikTok": "Watch now and see why everyone’s talking.",
        "Spotify": "Listen now.",
    }

    return f"{templates.get(niche, 'Discover something better today.')} {platform_cta.get(platform, '')}"


def generate_cta(platform: str):
    ctas = {
        "Meta": ["Learn More", "Shop Now", "Sign Up"],
        "Google": ["Get Started", "Learn More"],
        "TikTok": ["Learn More", "Shop Now"],
        "Spotify": ["Listen Now"],
    }
    return random.choice(ctas.get(platform, ["Learn More"]))