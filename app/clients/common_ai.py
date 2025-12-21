def generate_headlines(niche, goal):
    base = niche.lower()

    if niche == "Music":
        return [
            "New music just dropped 🎧",
            "You haven’t heard this yet",
            "Independent but unstoppable",
        ]

    if niche == "Clothing":
        return [
            "Limited drop — don’t miss it",
            "Streetwear done right",
            "Built for the culture",
        ]

    if niche == "Homecare":
        return [
            "Care your family deserves",
            "Trusted home care services",
            "Support when it matters most",
        ]

    return ["Discover something new today"]


def generate_descriptions(niche):
    if niche == "Music":
        return [
            "Stream now on all platforms.",
            "Tap in and support independent artists.",
        ]

    if niche == "Clothing":
        return [
            "Premium quality. Limited quantities.",
            "Designed for everyday wear.",
        ]

    if niche == "Homecare":
        return [
            "Licensed caregivers near you.",
            "Book a free consultation today.",
        ]

    return ["Learn more today"]


def generate_hashtags(seed, niche):
    seed = seed.replace(" ", "").lower()

    if niche == "Music":
        return {
            "instagram": [f"#{seed}", "#newmusic", "#musicreels"],
            "tiktok": [f"#{seed}", "#musicdiscovery", "#fyp"],
            "youtube": [f"#{seed}", "#musicvideo"],
            "twitter": [f"#{seed}", "#NewMusic"],
        }

    if niche == "Clothing":
        return {
            "instagram": [f"#{seed}", "#streetwear", "#fashionbrand"],
            "tiktok": [f"#{seed}", "#streetweartok"],
            "youtube": [f"#{seed}", "#streetwearbrand"],
            "twitter": [f"#{seed}", "#Streetwear"],
        }

    if niche == "Homecare":
        return {
            "instagram": ["#homecare", "#seniorcare"],
            "tiktok": ["#caregiving"],
            "youtube": ["#homecare"],
            "twitter": ["#HomeCare"],
        }

    return {}