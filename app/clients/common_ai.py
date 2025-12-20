from typing import List, Dict

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
        "Spotify": [
            f"{brand}: hear the story",
            f"{brand} in 30s — tap to learn more",
            f"New from {brand}: listen & shop",
        ],
    }

def summarize_insights(data) -> str:
    if not isinstance(data, dict): return "No trend data available."
    parts = []
    if "google" in data and data["google"].get("related_suggestions"):
        top = ", ".join(data["google"]["related_suggestions"][:5])
        parts.append(f"Google shows rising interest in: {top}.")
    if "tiktok" in data and data["tiktok"].get("topics"):
        t = ", ".join(data["tiktok"]["topics"][:5])
        parts.append(f"TikTok trending topics: {t}.")
    if "youtube" in data and data["youtube"].get("queries"):
        y = ", ".join(data["youtube"]["queries"][:5])
        parts.append(f"YouTube popular searches: {y}.")
    if "spotify" in data and data["spotify"].get("genres"):
        s = ", ".join(data["spotify"]["genres"][:5])
        parts.append(f"Spotify audiences skew toward: {s}.")
    return " ".join(parts) or "No strong signals yet — add more seed keywords."
