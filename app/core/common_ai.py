import random


# -------------------------
# HEADLINES
# -------------------------
def generate_headlines(platform: str, niche: str, goal: str, brand: str = ""):
    base = {
        "music": [
            "New music you can’t ignore",
            "This artist is next up",
            "You’ll want to hear this",
        ],
        "clothing": [
            "New drop just landed",
            "Streetwear done right",
            "Limited stock available",
        ],
        "homecare": [
            "Care you can trust",
            "Support for your loved ones",
            "Professional home care services",
        ],
    }

    headlines = base.get(niche.lower(), ["Discover something new"])

    platform_mods = {
        "meta": ["Shop now", "Learn more", "See why people love this"],
        "google": ["Near you", "Top-rated", "Affordable options"],
        "tiktok": ["This blew up", "TikTok made me buy this"],
        "youtube": ["Watch now", "Don’t miss this"],
        "spotify": ["Listen now", "Tap to hear more"],
    }

    results = []
    for h in headlines:
        mod = random.choice(platform_mods.get(platform.lower(), [""]))
        line = f"{h} {mod}".strip()
        if brand:
            line = f"{brand}: {line}"
        results.append(line)

    return results[:5]


# -------------------------
# PRIMARY TEXT / AD COPY
# -------------------------
def generate_primary_text(platform: str, niche: str, goal: str, offer: str = ""):
    templates = {
        "music": [
            "If you love new sounds, this one’s for you.",
            "Fans of this genre are loving this release.",
        ],
        "clothing": [
            "Designed for comfort, built for style.",
            "This drop won’t last long.",
        ],
        "homecare": [
            "Compassionate care when it matters most.",
            "Trusted caregivers in your area.",
        ],
    }

    texts = templates.get(niche.lower(), ["Discover something worth your time."])

    ctas = {
        "awareness": "Learn more today.",
        "traffic": "Tap to explore.",
        "leads": "Get a free consultation.",
        "sales": "Shop now.",
        "conversions": "Get started today.",
    }

    results = []
    for t in texts:
        line = f"{t} {ctas.get(goal.lower(), '')}"
        if offer:
            line += f" {offer}"
        results.append(line)

    return results[:5]


# -------------------------
# CTA GENERATOR
# -------------------------
def generate_ctas(platform: str, goal: str):
    base = {
        "awareness": ["Learn More", "Watch Now"],
        "traffic": ["Visit Site", "See More"],
        "leads": ["Sign Up", "Get Quote"],
        "sales": ["Shop Now", "Buy Now"],
        "conversions": ["Get Started", "Apply Now"],
    }
    return base.get(goal.lower(), ["Learn More"])


# -------------------------
# HASHTAG GENERATOR
# -------------------------
def generate_hashtags(niche: str, platform: str):
    base = {
        "music": ["#newmusic", "#unsignedartist", "#musicdiscovery"],
        "clothing": ["#streetwear", "#fashionbrand", "#newdrop"],
        "homecare": ["#homecare", "#caregivers", "#seniorcare"],
    }

    platform_tags = {
        "tiktok": ["#fyp", "#foryou"],
        "instagram": ["#reels", "#explore"],
        "youtube": ["#shorts"],
    }

    tags = base.get(niche.lower(), ["#trending"])
    tags += platform_tags.get(platform.lower(), [])

    return list(dict.fromkeys(tags))[:10]


# -------------------------
# AUDIENCE TARGETING ENGINE
# -------------------------
def generate_audience(niche: str, country: str):
    if niche.lower() == "music":
        return {
            "age_range": "18–34",
            "interests": ["Music streaming", "Live concerts", "Similar artists"],
            "locations": [country],
        }

    if niche.lower() == "clothing":
        return {
            "age_range": "18–44",
            "interests": ["Streetwear", "Sneakers", "Online shopping"],
            "locations": [country],
        }

    if niche.lower() == "homecare":
        return {
            "age_range": "35–65+",
            "interests": ["Caregiving", "Elder care", "Healthcare services"],
            "locations": [country],
        }

    return {
        "age_range": "18–65+",
        "interests": ["General interest"],
        "locations": [country],
    }