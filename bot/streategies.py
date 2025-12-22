# bot/strategies.py

from typing import Dict, List


MIN_MONTHLY_BUDGET = 500  # enforced minimum


def validate_budget(budget: float) -> float:
    """Ensure minimum monthly budget"""
    if budget < MIN_MONTHLY_BUDGET:
        raise ValueError(f"Minimum monthly budget is ${MIN_MONTHLY_BUDGET}")
    return budget


def auto_platform_split(
    total_budget: float,
    goal: str,
    enabled_platforms: List[str],
) -> Dict[str, float]:
    """
    Auto-allocates budget across platforms based on goal.
    """
    total_budget = validate_budget(total_budget)
    goal = goal.lower()

    # Default weights
    weights = {
        "meta": 0.4,
        "google": 0.3,
        "tiktok": 0.2,
        "spotify": 0.1,
    }

    if goal in ["sales", "conversions"]:
        weights.update({"meta": 0.45, "google": 0.35, "tiktok": 0.15})
    elif goal in ["awareness"]:
        weights.update({"tiktok": 0.35, "meta": 0.3, "spotify": 0.15})
    elif goal in ["leads"]:
        weights.update({"google": 0.4, "meta": 0.4})

    # Normalize only enabled platforms
    filtered = {p: weights.get(p, 0) for p in enabled_platforms}
    total_weight = sum(filtered.values())

    if total_weight == 0:
        raise ValueError("No platforms selected")

    return {
        p: round((w / total_weight) * total_budget, 2)
        for p, w in filtered.items()
    }


def funnel_allocation(goal: str) -> Dict[str, float]:
    """
    Funnel split inside each platform
    """
    goal = goal.lower()

    if goal in ["sales", "conversions"]:
        return {"TOF": 0.2, "MOF": 0.3, "BOF": 0.5}
    elif goal == "leads":
        return {"TOF": 0.3, "MOF": 0.4, "BOF": 0.3}
    else:
        return {"TOF": 0.6, "MOF": 0.3, "BOF": 0.1}


def scaling_recommendations(platform_metrics: Dict) -> Dict[str, str]:
    """
    Suggests scaling actions based on performance.
    """
    recs = {}

    for platform, metrics in platform_metrics.items():
        cpc = metrics.get("cpc")
        ctr = metrics.get("ctr")

        if cpc and cpc < metrics.get("benchmark_cpc", 2.0):
            recs[platform] = "Increase budget 20–30%"
        elif ctr and ctr < 0.8:
            recs[platform] = "Test new creatives & hooks"
        else:
            recs[platform] = "Maintain & monitor"

    return recs