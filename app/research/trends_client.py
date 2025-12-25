from pytrends.request import TrendReq
import pandas as pd


def get_google_trends(
    keywords: list,
    geo: str = "US",
    timeframe: str = "today 12-m",
):
    """
    Returns:
    - interest over time
    - interest by region
    - related queries
    """
    if not keywords:
        return {"error": "No keywords provided"}

    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(
            keywords,
            timeframe=timeframe,
            geo=geo,
        )

        results = {}

        iot = pytrends.interest_over_time()
        if isinstance(iot, pd.DataFrame) and not iot.empty:
            results["interest_over_time"] = iot.drop(
                columns=["isPartial"], errors="ignore"
            )

        regions = pytrends.interest_by_region(resolution="COUNTRY")
        if isinstance(regions, pd.DataFrame) and not regions.empty:
            results["regions"] = regions.sort_values(
                by=keywords[0], ascending=False
            )

        rq = pytrends.related_queries()
        related = []
        for kw, buckets in rq.items():
            for kind in ["top", "rising"]:
                df = buckets.get(kind)
                if isinstance(df, pd.DataFrame) and "query" in df:
                    related.extend(df["query"].tolist())

        results["related_queries"] = list(dict.fromkeys(related))[:50]

        return results

    except Exception as e:
        return {"error": str(e)}