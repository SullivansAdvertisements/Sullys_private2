typing import List, Dict

def generate_headlines(brand: str, objective: str, keywords: str) -> Dict[str, List[str]]:
    k = [w.strip() for w in (keywords or "").replace(",", "\n").split("\n") if w.strip()]
    seed = (k[:3] or ["premium", "official", "new"]).copy()
    o = objective.lower()

    def h(prefix): return [
        f"{prefix}: {brand} {seed[0]} drop",
        f"{prefix}: {brand} — {seed[1]} you’ll actually wear" if len(seed) > 1 else f"{prefix}: {brand} — new release",
        f"{prefix}: {brand} {seed[2]} is live" if len(seed) > 2 else f"{prefix}: {brand} shop now",
    ]

    return {
        "Meta": h("Scroll-stopping"),
        "Google": [
            f"{brand} {seed[0]} | Official Site",
            f"Shop {brand} {seed[1]} Today" if len(seed) > 1 else f"Shop {brand} Today",
            f"{brand} Deals & New Arrivals",
        ],
        "YouTube": h("Watch"),
        "TikTok": h("POV"),