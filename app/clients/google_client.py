from typing import Dict, Any
import os

def google_campaign_generator(brand: str, objective: str, budget: float, keywords: str) -> Dict[str, Any]:
    # If Google Ads credentials exist, you can wire Keyword Plan forecasts here.
    has_creds = all([
        os.getenv("GOOGLE_DEVELOPER_TOKEN") or "",
    ])
    kws = [k.strip() for k in keywords.replace(",", "\n").split("\n") if k.strip()]
    out = {
        "brand": brand,
        "objective": objective,
        "daily_budget": budget,
        "keywords": kws,
        "status": "demo" if not has_creds else "ready",
        "notes": [
            "Search + PMax recommended.",
            "Use Exact/Phrase for core, add DSAs or PMax for discovery."
        ]
    }
    return out