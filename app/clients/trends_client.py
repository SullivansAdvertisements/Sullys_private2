from pytrends.request import TrendReq
import pandas as pd

def get_advanced_trends(
    keywords,
    geo="US",
    timeframe="today 12-m",
    gprop=""
):
    """
    Returns:
    - interest_over_time (DataFrame)
    - interest_by_region (DataFrame)
    - related_queries (dict)
    """

    if not keywords:
        return {"error": "No keywords provided"}

    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload(
        kw_list=keywords,
        timeframe=timeframe,
        geo=geo,
        gprop=gprop,
    )

    results = {}

    # Interest over time
    iot = pytrends.interest_over_time()
    if not iot.empty and "isPartial" in iot.columns:
        iot = iot.drop(columns=["isPartial"])
    results["interest_over_time"] = iot

    # Interest by region
    region = pytrends.interest_by_region(
        resolution="COUNTRY",
        inc_low_vol=True,
        inc_geo_code=True,
    )
    results["interest_by_region"] = region

    # Related queries
    rq = pytrends.related_queries()
    cleaned = {}

    for kw, data in rq.items():
        cleaned[kw] = {
            "top": data["top"] if data["top"] is not None else pd.DataFrame(),
            "rising": data["rising"] if data["rising"] is not None else pd.DataFrame(),
        }

    results["related_queries"] = cleaned
    return results
