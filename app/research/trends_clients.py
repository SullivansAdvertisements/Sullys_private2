# research/trends_client.py
"""
Google Trends + basic research utilities.
NO Streamlit UI code in this file.
"""

from typing import List, Dict
import pandas as pd

try:
    from pytrends.request import TrendReq
    HAS_PYTRENDS = True
except ImportError:
    HAS_PYTRENDS = False


def get_google_trends(
    keywords: List[str],
    geo: str = "US",
    timeframe: str = "today 12-m",
) -> Dict:
    """
    Fetch Google Trends data for keywords.
    Returns safe JSON-like dict for Streamlit display.
    """

    if not HAS_PYTRENDS:
        return {
            "error": "pytrends not installed",
            "interest_over_time": None,
            "related_queries": [],
        }

    if not keywords:
        return {
            "error": "No keywords provided",
            "interest_over_time": None,
            "related_queries": [],
        }

    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(
            keywords,
            timeframe=timeframe,
            geo=geo,
        )

        data = {}

        iot = pytrends.interest_over_time()
        if isinstance(iot, pd.DataFrame) and not iot.empty:
            if "isPartial" in iot.columns:
                iot = iot.drop(columns=["isPartial"])
            data["interest_over_time"] = iot
        else:
            data["interest_over_time"] = None

        related = pytrends.related_queries()
        queries = []

        if isinstance(related, dict):
            for kw, blocks in related.items():
                for section in ("top", "rising"):
                    df = blocks.get(section)
                    if df is not None and "query" in df.columns:
                        queries.extend(df["query"].tolist())

        data["related_queries"] = list(dict.fromkeys(queries))[:50]

        return data

    except Exception as e:
        return {
            "error": str(e),
            "interest_over_time": None,
            "related_queries": [],
        }