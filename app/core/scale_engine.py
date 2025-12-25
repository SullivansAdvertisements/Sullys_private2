def evaluate_performance(metrics: dict):
    """
    metrics example:
    {
        "meta": {"cpa": 18, "roas": 2.4},
        "google": {"cpa": 25, "roas": 1.8},
        "tiktok": {"cpa": 12, "roas": 3.1}
    }
    """

    recommendations = {}

    for platform, data in metrics.items():
        if data.get("roas", 0) >= 2.5:
            recommendations[platform] = "Scale +20%"
        elif data.get("roas", 0) < 1.5:
            recommendations[platform] = "Reduce -20%"
        else:
            recommendations[platform] = "Maintain budget"

    return recommendations


def rebalance_budget(total_budget: float, scale_actions: dict):
    adjustments = {}
    base = total_budget / len(scale_actions)

    for platform, action in scale_actions.items():
        if "Scale" in action:
            adjustments[platform] = base * 1.2
        elif "Reduce" in action:
            adjustments[platform] = base * 0.8
        else:
            adjustments[platform] = base

    return adjustments