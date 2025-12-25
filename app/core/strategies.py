# core/strategies.py

def validate_budget(monthly_budget: float):
    if monthly_budget < 500:
        return False, "Minimum monthly budget is $500."
    if monthly_budget < 1500:
        return True, "⚠️ Budget is low — limit platforms to 1–2."
    return True, None


def allowed_platforms(goal: str, budget: float):
    goal = goal.lower()

    if budget < 1500:
        return ["Meta"]

    if goal == "awareness":
        return ["Meta", "TikTok", "YouTube"]

    if goal in ["leads", "sales", "conversions"]:
        return ["Meta", "Google"]

    return ["Meta"]


def allocate_budget(budget: float, goal: str, platforms: list):
    goal = goal.lower()

    splits = {
        "awareness": {
            "Meta": 0.35,
            "TikTok": 0.30,
            "YouTube": 0.25,
            "Google": 0.10,
        },
        "traffic": {
            "Meta": 0.40,
            "Google": 0.30,
            "TikTok": 0.20,
            "YouTube": 0.10,
        },
        "leads": {
            "Meta": 0.45,
            "Google": 0.35,
            "TikTok": 0.10,
            "YouTube": 0.10,
        },
        "sales": {
            "Meta": 0.45,
            "Google": 0.40,
            "TikTok": 0.10,
            "YouTube": 0.05,
        },
    }

    allocation = {}
    for platform in platforms:
        allocation[platform] = round(budget * splits[goal].get(platform, 0), 2)

    return allocation


def strategy_warnings(goal: str, budget: float, platforms: list):
    warnings = []

    if goal in ["sales", "leads"] and budget < 2000:
        warnings.append("Conversion goals may underperform with this budget.")

    if len(platforms) > 3 and budget < 3000:
        warnings.append("Too many platforms selected for this budget.")

    if "Meta" not in platforms:
        warnings.append("No Meta campaigns detected — remarketing may be limited.")

    return warnings


def generate_strategy(niche, goal, budget, platforms):
    """
    Generates a high-level marketing strategy plan
    """

    allocation = {}
    per_platform_budget = budget / max(len(platforms), 1)

    for platform in platforms:
        allocation[platform] = {
            "monthly_budget": round(per_platform_budget, 2),
            "primary_goal": goal,
            "recommended_objective": (
                "Conversions" if goal.lower() in ["sales", "leads"] else "Awareness"
            ),
            "notes": f"Focus on {niche} audience with {goal} objective."
        }

    return {
        "niche": niche,
        "goal": goal,
        "total_budget": budget,
        "platforms": platforms,
        "allocation": allocation,
        "scaling_rule": "Increase budget 20% after 7 days if CPA is below target"
    }