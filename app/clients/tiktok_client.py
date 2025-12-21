def tiktok_research(niche):
    return {
        "age_focus": "18–34" if niche in ["Music", "Clothing"] else "30–55",
        "content_formats": [
            "POV",
            "UGC testimonials",
            "Storytelling",
        ],
        "hooks": [
            "You need to see this",
            "This changed everything",
            "No one talks about this",
        ],
        "interest_clusters": [
            f"{niche.lower()} lifestyle",
            f"{niche.lower()} tips",
            f"{niche.lower()} trends",
        ],
    }