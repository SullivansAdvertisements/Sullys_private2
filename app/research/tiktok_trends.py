def get_tiktok_trends(seed: str):
    """
    Simulated TikTok Creative Center insights.
    Used for hooks, formats, and content direction.
    """
    if not seed:
        return {"error": "No seed keyword"}

    return {
        "top_hooks": [
            f"POV: You found the best {seed}",
            f"This {seed} changed everything",
            f"Nobody talks about this {seed}",
        ],
        "formats": [
            "UGC selfie video",
            "Before / After",
            "Problem → Solution",
            "Storytime",
        ],
        "cta_styles": [
            "Watch till the end",
            "Don’t scroll",
            "You need this",
        ],
        "note": "Based on TikTok Creative Center patterns",
    }