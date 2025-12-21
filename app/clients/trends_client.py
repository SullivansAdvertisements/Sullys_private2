from pytrends.request import TrendReq

def get_advanced_trends(seed, geo="US", timeframe="today 12-m"):
    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload([seed], timeframe=timeframe, geo=geo)

    results = {}

    try:
        iot = pytrends.interest_over_time()
        if not iot.empty:
            results["interest_over_time"] = iot
    except:
        results["interest_over_time"] = None

    try:
        regions = pytrends.interest_by_region(resolution="REGION")
        results["regions"] = regions.sort_values(seed, ascending=False).head(20)
    except:
        results["regions"] = None

    try:
        rq = pytrends.related_queries()
        results["related_queries"] = rq.get(seed, {})
    except:
        results["related_queries"] = None

    return results