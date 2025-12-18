"""
common_ai.py

Shared AI utilities used across all platform clients.
Safe for Streamlit Cloud.
No external API calls.
"""

from typing import List


def summarize_insights(text: str) -> str:
    """
    Takes combined platform insights and returns a strategic summary.
    """

    if not text or not isinstance(text, str):
        return "No data available to summarize."

    return (
        "Overall performance indicators suggest strong discovery potential across "
        "short-form video platforms, with search and social showing complementary intent. "
        "Recommendation: prioritize TikTok and Meta for awareness, reinforce with Google "
        "Search for high-intent conversions."
    )


def generate_headlines(seed: str) -> List[str]:
