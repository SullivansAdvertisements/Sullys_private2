# core/strategies.py
# Budget allocation + scaling logic (Phase 3 stable)

from typing import Dict


MIN_MONTHLY_BUDGET = 500  # enforced minimum


def allocate_budget(
    monthly_budget: float,
    goal: str,
    enabled_platforms: list[str] | None = None,
) -> Dict[str, float]:
    """
    Allocates monthly budget across platforms based on goal.
    Returns dict: {platform: budget_amount}
    """

    if monthly_budget < MIN_MONTHLY_BUDGET:
        raise ValueError(
            f"Monthly budget must be at least ${MIN_MONTHLY_BUDGET}"
        )

    goal = goal.lower()
    enabled_platforms = enabled_platforms or [
        "Meta",
        "Google",
        "TikTok",
        "Spotify",
    ]

    # Default allocation logic
    if goal in ["sales", "conversions"]:
        weights = {
            "Meta": 0.4,
            "Google": 0.35,
            "TikTok": 0.15,
            "Spotify": 0.10,
        }
    elif goal in ["leads"]:
        weights = {
            "Meta": 0.45,
            "Google": 0.30,
            "TikTok": 0.15,
            "Spotify": 0.10,
        }
    elif goal in ["awareness"]:
        weights = {
            "Meta": 0.35,
            "TikTok": 0.30,
            "Spotify": 0.20,
            "Google": 0.15,
        }
    else:  # traffic / default
        weights = {
            "Meta": 0.35,
            "Google": 0.30,
            "TikTok": 0.20,
            "Spotify": 0.15,
        }

    # Normalize for enabled platforms only
    active_weights = {
        k: v for k, v in weights.items() if k in enabled_platforms
    }
    total_weight = sum(active_weights.values())

    allocation = {}
    for platform, weight in active_weights.items():
        allocation[platform] = round(
            monthly_budget * (weight / total_weight), 2
        )

    return allocation


def recommend_scaling(
    performance: Dict[str, float],
    current_budget: Dict[str, float],
    scale_factor: float = 0.2,
) -> Dict[str, float]:
    """
    Simple auto-scaling recommendation engine.
    performance: {platform: ROAS or CPA score}
    """

    updated_budget = current_budget.copy()

    if not performance:
        return updated_budget

    avg_perf = sum(performance.values()) / len(performance)

    for platform, perf in performance.items():
        if perf > avg_perf:
            updated_budget[platform] *= (1 + scale_factor)
        else:
            updated_budget[platform] *= (1 - scale_factor / 2)

        updated_budget[platform] = round(updated_budget[platform], 2)

    return updated_budget