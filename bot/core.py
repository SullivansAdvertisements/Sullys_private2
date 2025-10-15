from typing import Dict, List, Any
from .budget import allocation_by_budget, funnel_split
from .strategies import PLATFORM_DEVELOPMENT
from .audiences import AUDIENCE_BANK
from .competitors import analyze_competitors

def generate_strategy(niche: str, budget: float, goal: str, geo: str, competitors: List[str]) -> Dict[str, Any]:
    niche = niche.lower()
    if niche not in AUDIENCE_BANK:
        raise ValueError(f"Unsupported niche: {niche}")
    allocation = allocation_by_budget(budget, goal)
    funnel = funnel_split(budget)

    insights = {"keywords": [], "locations": [geo]}
    try:
        if competitors:
            res = analyze_competitors(competitors)
            if res.get("keywords"):
                insights["keywords"] = res["keywords"]
            if res.get("locations"):
                insights["locations"] = res["locations"]
    except Exception:
        pass

    plans = {}
    for platform, pct in allocation.items():
        if platform in PLATFORM_DEVELOPMENT:
            plan = PLATFORM_DEVELOPMENT[platform](niche, insights)
            plan["budget_pct"] = pct
            plan["notes"] = {"geo": geo, "goal": goal, "competitors": competitors}
            plans[platform] = plan

    return {
        "niche": niche,
        "budget": budget,
        "goal": goal,
        "geo": geo,
        "allocation": allocation,
        "funnel_split": funnel,
        "insights": insights,
        "platforms": plans,
    }
