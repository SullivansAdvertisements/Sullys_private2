# research/trends_client.py
# Phase B – Google / YouTube Trends Research Engine

from typing import List, Dict, Any

import pandas as pd

try:
    from pytrends.request import TrendReq
    HAS_TRENDS = True
except ImportError:
    HAS_TRENDS = False


def get_google_trends(
    seed_terms: List[str],
    geo: str = "US",
    timeframe: str = "today 12-m",
    gprop: str = "",
) -> Dict[str, Any]:
    """
    Pulls Google Trends data safely.
    Returns dict with:
    - interest_over_time (DataFrame)
    - related_queries (list)
    - by_region (DataFrame)
    """

    if not HAS_TRENDS:
        return {"error": "pytrends not installed"}

    if not seed_terms:
        return {"error": "No seed terms provided"}

    try:
        pytrends = TrendReq(hl="en-US", tz=360)

        pytrends.build_payload(
            seed_terms,
            timeframe=timeframe,
            geo=geo,
            gprop=gprop,
        )

        result: Dict[str, Any] = {}

        # Interest over time
        iot = pytrends.interest_over_time()
        if isinstance(iot, pd.DataFrame) and not iot.empty:
            if "isPartial" in iot.columns:
                iot = iot.drop(columns=["isPartial"])
            result["interest_over_time"] = iot

        # Region data
        try:
            region_df = pytrends.interest_by_region(
                resolution="COUNTRY",
                inc_low_vol=True,
                inc_geo_code=True,
            )
            if isinstance(region_df, pd.DataFrame) and not region_df.empty:
                result["by_region"] = region_df.sort_values(
                    by=region_df.columns[0], ascending=False
                )
        except Exception:
            pass

        # Related queries
        related_queries = []
        rq = pytrends.related_queries()
        if isinstance(rq, dict):
            for term, buckets in rq.items():
                for bucket in ["top", "rising"]:
                    df = buckets.get(bucket)
                    if isinstance(df, pd.DataFrame) and "query" in df.columns:
                        related_queries.extend(
                            df["query"].dropna().astype(str).tolist()
                        )

        # De-duplicate while preserving order
        seen = set()
        cleaned = []
        for q in related_queries:
            if q not in seen:
                seen.add(q)
                cleaned.append(q)

        result["related_queries"] = cleaned[:100]

        return result

    except Exception as e:
        return {"error": str(e)}


def expand_keywords(
    base_keywords: List[str],
    trends_output: Dict[str, Any],
    limit: int = 50,
) -> List[str]:
    """
    Combines seed keywords + related queries into an expanded list.
    """
    expanded = list(base_keywords)

    rq = trends_output.get("related_queries", [])
    for q in rq:
        if q not in expanded:
            expanded.append(q)

    return expanded[:limit]