def build_client_summary(
    brand: str,
    niche: str,
    goal: str,
    budget: float,
    platforms: dict,
):
    return {
        "brand": brand,
        "niche": niche,
        "goal": goal,
        "monthly_budget": budget,
        "platforms": platforms,
        "status": "Read-only client view",
    }


def export_client_report(data: dict):
    """
    Used for PDF / JSON / shareable link later
    """
    return {
        "title": f"{data['brand']} Media Plan",
        "content": data,
        "timestamp": "auto-generated",
    }