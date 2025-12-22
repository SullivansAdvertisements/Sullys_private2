def generate_ad_copy(niche: str, goal: str, platform: str):
    niche = niche.lower()
    goal = goal.lower()
    platform = platform.lower()

    hooks = {
        "music": [
            "New release just dropped",
            "Fans can’t stop playing this",
            "Your next favorite track"
        ],
        "clothing": [
            "Limited drop just landed",
            "Streetwear done right",
            "This won’t restock"
        ],
        "homecare": [
            "Care your family deserves",
            "Trusted local caregivers",
            "Support starts today"
        ]
    }

    ctas = {
        "awareness": "Learn More",
        "traffic": "Visit Now",
        "leads": "Get a Quote",
        "sales": "Shop Now"
    }

    headlines = hooks.get(niche, ["Discover more"])[:3]

    return {
        "platform": platform.title(),
        "headlines": headlines,
        "primary_text": headlines,
        "cta": ctas.get(goal, "Learn More")
    }