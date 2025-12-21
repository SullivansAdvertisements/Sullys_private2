def generate_headlines(niche, goal):
    return [
        f"{niche} campaign designed for {goal}",
        f"Discover the future of {niche}",
        f"{niche} solutions that convert",
    ]


def generate_descriptions(niche, goal):
    return [
        f"High-performing {niche} ads built for {goal}.",
        f"Reach the right audience with smarter {niche} marketing.",
    ]


def generate_hashtags(seed, niche):
    return {
        "instagram": [f"#{seed}", f"#{niche}", "#trending"],
        "tiktok": [f"#{seed}", "#fyp", "#viral"],
        "youtube": [seed, f"{niche} marketing"],
    }


def generate_email_outreach(email_type, sender, offer, niche):
    return f"""
Hi there,

My name is {sender} and I work with a {niche} brand.

We’re reaching out regarding a {email_type.lower()} opportunity.
We’d love to discuss: {offer}

Let me know if you’re interested.

Best,
{sender}
"""