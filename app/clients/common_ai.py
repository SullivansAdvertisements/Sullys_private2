import pandas as pd

def generate_strategy(niche, budget, platforms):
    split = budget / max(len(platforms),1)
    return {
        "niche": niche,
        "total_budget": budget,
        "platforms": {
            p: round(split,2) for p in platforms
        }
    }

def generate_ad_copy(seed, goal):
    data = [
        {"Headline": f"{seed} — Don’t Miss This", "CTA": "Learn More"},
        {"Headline": f"Why {seed} Is Trending", "CTA": "Shop Now"},
    ]
    return pd.DataFrame(data)

def estimate_reach(daily_budget):
    # transparent math model
    cpm = 10  # assumed avg CPM
    impressions = (daily_budget / cpm) * 1000
    return {
        "daily_budget": daily_budget,
        "estimated_impressions": int(impressions),
        "note": "Estimate based on avg CPM – not platform-guaranteed"
    }