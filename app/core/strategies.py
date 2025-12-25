"""
Phase 2 – Strategy & Budget Engine
Handles:
- Budget allocation
- Platform weighting
- Scaling logic
"""

def validate_budget(monthly_budget: float, minimum: float = 500) -> float:
    """
    Enforce minimum monthly budget.
    """
    if monthly_budget < minimum:
        raise ValueError(f"Minimum monthly budget is ${minimum}")
    return float(monthly_budget)


def allocate_budget(monthly_budget: float, goal: str) -> dict:
    """
    Allocate budget across platforms based on primary goal.
    """
    goal = goal.lower()
    monthly_budget = validate_budget(monthly_budget)

    if goal in ["sales", "conversions"]:
        weights = {
            "Meta": 0.35,
            "Google": 0.30,
            "TikTok": 0.15,
            "YouTube": 0.15,
            "Spotify": 0.05,
        }
    elif goal == "leads":
        weights = {
            "Meta": 0.40,
            "Google": 0.35,
            "TikTok": 0.10,
            "YouTube": 0.10,
            "Spotify": 0.05,
        }
    elif goal == "awareness":
        weights = {
            "Meta": 0.30,
            "TikTok": 0.25,
            "YouTube": 0.25,
            "Spotify": 0.10,
            "Google": 0.10,
        }
    else:  # traffic / default
        weights = {
            "Meta": 0.30,
            "Google": 0.30,
            "TikTok": 0.20,
            "YouTube": 0.15,
            "Spotify": 0.05,
        }

    allocation = {
        platform: round(monthly_budget * pct, 2)
        for platform, pct in weights.items()
    }

    return allocation


def scaling_recommendations(monthly_budget: float) -> dict:
    """
    Suggest how to scale when budget increases.
    """
    monthly_budget = validate_budget(monthly_budget)

    if monthly_budget < 2000:
        return {
            "focus": "Validation",
            "recommendation": "Test creatives & audiences before scaling.",
        }
    elif monthly_budget < 5000:
        return {
            "focus": "Optimization",
            "recommendation": "Double down on best-performing platform.",
        }
    else:
        return {
            "focus": "Scale",
            "recommendation": "Expand to new platforms + retargeting layers.",
        }