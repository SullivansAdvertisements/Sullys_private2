from typing import Dict

def allocation_by_budget(total_budget: float, goal: str) -> Dict[str, float]:
    goal = (goal or "sales").lower()
    if total_budget < 500:
        return {"meta": 70, "tiktok": 30} if goal in ("sales","conversions") else {"meta": 60, "tiktok": 40}
    if total_budget < 2500:
        return {"meta": 50, "google": 30, "tiktok": 20}
    if total_budget < 10000:
        return {"meta": 40, "google": 35, "tiktok": 15, "twitter": 10}
    return {"meta": 35, "google": 35, "youtube": 15, "tiktok": 10, "twitter": 5}

def funnel_split(total_budget: float) -> Dict[str, float]:
    if total_budget < 1000:
        return {"prospecting": 75, "retargeting": 25, "retention": 0}
    if total_budget < 5000:
        return {"prospecting": 65, "retargeting": 30, "retention": 5}
    return {"prospecting": 60, "retargeting": 30, "retention": 10}
