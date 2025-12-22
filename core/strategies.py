def validate_budget(total_budget: float):
    if total_budget < 5000:
        raise ValueError("Minimum monthly budget is $5,000")


def allocate_budget(total_budget: float, platforms: list[str]):
    validate_budget(total_budget)

    base_weights = {
        "Meta": 0.35,
        "Google": 0.30,
        "TikTok": 0.20,
        "Spotify": 0.15,
    }

    active = {p: base_weights[p] for p in platforms if p in base_weights}
    weight_sum = sum(active.values())

    allocation = {}
    for platform, weight in active.items():
        allocation[platform] = round((weight / weight_sum) * total_budget, 2)

    return allocation


def rebalance_budget(performance: dict, current_budget: dict):
    """
    performance = {
        "Meta": 1.2,
        "Google": 0.9,
        "TikTok": 1.1
    }
    >1 means outperforming, <1 underperforming
    """

    total = sum(current_budget.values())
    scores = {k: max(v, 0.5) for k, v in performance.items()}
    score_sum = sum(scores.values())

    new_budget = {}
    for platform, score in scores.items():
        new_budget[platform] = round((score / score_sum) * total, 2)

    return new_budget