import os

def tiktok_campaign_generator(brand, objective, budget, keywords):
    kws = [k.strip() for k in keywords.replace(",", "\n").split("\n") if k.strip()]
    hooks = [f"POV: {brand} just dropped {k}" for k in kws[:3]] or [
        "POV: You found your new favorite brand",
        "Watch till the end",
        "This changed my routine"
    ]
    return {
        "brand": brand,
        "objective": objective,
        "daily_budget": budget,
        "hooks": hooks,
        "status": "demo" if not os.getenv("TIKTOK_ACCESS_TOKEN") else "ready",
        "notes": ["Test 3-5 creatives per ad group", "Use Spark Ads where possible"]
    }
