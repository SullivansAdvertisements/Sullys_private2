"""
common_ai.py
Central intelligence layer for Sully's Media Planner

USED BY:
- Research & Trends tab
- Strategy Engine
- Meta / Google / TikTok creative planners

DOES NOT:
- Scrape restricted platforms
- Call ad APIs directly
"""

from typing import List, Dict
from collections import defaultdict

try:
    from pytrends.request import TrendReq
    HAS_TRENDS = True
except ImportError:
    HAS_TRENDS = False


# -------------------------
# CORE TREND RESEARCH
# -------------------------
def google_trends_research(
    seed_terms: List[str],
    geo: str = "US",
    timeframe: str = "today 12-m"
) -> Dict:
    """
    Pulls interest, regions, and related queries from Google Trends
    """
    if not HAS_TRENDS:
        return {"error": "pytrends not installed"}

    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload(seed_terms, geo=geo, timeframe=timeframe)

    results = {}

    # Interest over time
    iot = pytrends.interest_over_time()
    if not iot.empty:
        if "isPartial" in iot.columns:
            iot = iot.drop(columns=["isPartial"])
        results["interest_over_time"] = iot

    # Interest by region
    regions = pytrends.interest_by_region(
        resolution="REGION",
        inc_low_vol=True
    )
    if not regions.empty:
        results["top_regions"] = regions.sort_values(
            seed_terms[0], ascending=False
        ).head(25)

    # Related queries
    rq = pytrends.related_queries()
    queries = []
    if isinstance(rq, dict):
        for term, data in rq.items():
            for t in ["top", "rising"]:
                df = data.get(t)
                if df is not None and "query" in df.columns:
                    queries.extend(df["query"].tolist())

    results["related_queries"] = list(dict.fromkeys(queries))[:100]

    return results


# -------------------------
# DEMOGRAPHIC INTELLIGENCE
# -------------------------
def infer_demographics(niche: str) -> Dict:
    """
    Heuristic-based demographic inference
    (Used when APIs do not expose demographics directly)
    """
    niche = niche.lower()

    if niche == "music":
        return {
            "age": "18–34",
            "gender": "All",
            "interests": [
                "Music streaming",
                "Live concerts",
                "Hip hop / Pop / Indie",
            ],
        }

    if niche == "clothing":
        return {
            "age": "18–40",
            "gender": "All",
            "interests": [
                "Streetwear",
                "Sneakers",
                "Online shopping",
            ],
        }

    if niche == "homecare":
        return {
            "age": "35–65+",
            "gender": "All",
            "interests": [
                "Caregiving",
                "Healthcare",
                "Elder care",
            ],
        }

    return {
        "age": "18–65",
        "gender": "All",
        "interests": ["General consumer interests"],
    }


# -------------------------
# LOCATION INTELLIGENCE
# -------------------------
def expand_locations(base_geo: str) -> Dict:
    """
    Expands country → states → metro logic
    """
    geo_map = {
        "US": {
            "states": [
                "California", "Texas", "Florida",
                "New York", "Illinois", "Georgia"
            ],
            "metros": [
                "Los Angeles", "New York City",
                "Houston", "Atlanta", "Chicago"
            ],
        },
        "Worldwide": {
            "countries": [
                "United States", "United Kingdom",
                "Canada", "Australia", "Germany"
            ]
        },
    }

    return geo_map.get(base_geo, {"countries": [base_geo]})


# -------------------------
# HASHTAG GENERATOR
# -------------------------
def generate_hashtags(seed: str, niche: str) -> Dict:
    """
    Platform-specific hashtag logic
    """
    seed = seed.replace(" ", "")
    niche = niche.replace(" ", "")

    return {
        "instagram": [
            f"#{seed}",
            f"#{niche}",
            "#explorepage",
            "#trending",
        ],
        "tiktok": [
            f"#{seed}",
            "#fyp",
            "#viral",
            "#foryou",
        ],
        "youtube": [
            seed,
            f"{niche} marketing",
            "how to",
        ],
    }


# -------------------------
# CREATIVE COPY GENERATION
# -------------------------
def generate_headlines(niche: str, goal: str) -> List[str]:
    return [
        f"{niche.title()} That Actually Converts",
        f"The Smarter Way to Grow Your {niche.title()}",
        f"Built for {goal.title()} — Not Guesswork",
    ]


def generate_descriptions(niche: str, goal: str) -> List[str]:
    return [
        f"High-performing {niche} campaigns engineered for {goal}.",
        f"Reach the right audience with data-backed {niche} marketing.",
    ]


# -------------------------
# EMAIL & INFLUENCER OUTREACH
# -------------------------
def generate_email_outreach(
    outreach_type: str,
    sender: str,
    offer: str,
    niche: str
) -> str:
    return f"""
Hi,

My name is {sender} and I work with a {niche} brand.

We’re reaching out regarding a {outreach_type.lower()} opportunity.
We believe your audience aligns perfectly with our current campaign.

Offer:
{offer}

Let me know if you're interested.

Best,
{sender}
"""


# -------------------------
# MASTER RESEARCH PIPELINE
# -------------------------
def run_full_research(seed: str, niche: str, geo: str = "US") -> Dict:
    """
    Used by Research tab
    """
    data = {}

    data["demographics"] = infer_demographics(niche)
    data["locations"] = expand_locations(geo)
    data["hashtags"] = generate_hashtags(seed, niche)

    if HAS_TRENDS:
        data["google_trends"] = google_trends_research([seed], geo=geo)
    else:
        data["google_trends"] = {"error": "pytrends unavailable"}

    return data