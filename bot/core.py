# bot/core.py

from typing import Dict, List
from bot.strategies import (
    auto_platform_split,
    funnel_allocation,
    scaling_recommendations,
)
from bot.influencers import build_influencer_list
from clients.common_ai import generate_ad_copy


def build_master_plan(
    niche: str,
    goal: str,
    monthly_budget: float,
    enabled_platforms: List[str],
) -> Dict:
    """
    High-level orchestration engine
    """
    platform_budgets = auto_platform_split(
        total_budget=monthly_budget,
        goal=goal,
        enabled_platforms=enabled_platforms,
    )

    funnel = funnel_allocation(goal)

    return {
        "niche": niche,
        "goal": goal,
        "monthly_budget": monthly_budget,
        "platform_budgets": platform_budgets,
        "funnel_split": funnel,
    }


def generate_platform_creatives(
    niche: str,
    goal: str,
    platforms: List[str],
) -> Dict:
    """
    Generates ad copy per platform
    """
    creatives = {}

    for platform in platforms:
        creatives[platform] = generate_ad_copy(
            niche=niche,
            platform=platform,
            goal=goal,
        )

    return creatives


def apply_scaling_logic(performance_data: Dict) -> Dict:
    """
    Produces scaling recommendations
    """
    return scaling_recommendations(performance_data)


def influencer_pipeline(raw_creators: List[Dict]) -> Dict:
    """
    Influencer discovery → scoring
    """
    ranked = build_influencer_list(raw_creators)

    return {
        "top_influencers": ranked[:10],
        "all_influencers": ranked,
    }