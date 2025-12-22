def allocate_budget(total_budget, platforms):
    if total_budget < 5000:
        raise ValueError("Minimum monthly budget is $5,000")

    weights = {
        "Meta": 0.35,
        "Google": 0.30,
        "TikTok": 0.20,
        "Spotify": 0.15,
    }

    active_weights = {p: weights[p] for p in platforms if p in weights}
    total_weight = sum(active_weights.values())

    allocation = {}
    for platform, weight in active_weights.items():
        allocation[platform] = round((weight / total_weight) * total_budget, 2)

    return allocation