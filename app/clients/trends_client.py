from pytrends.request import TrendReq

def google_youtube_trends(keywords, geo="US", timeframe="today 12-m"):
    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload(keywords, geo=geo, timeframe=timeframe)

    interest = pytrends.interest_over_time()
    regions = pytrends.interest_by_region(resolution="REGION", inc_low_vol=True)

    related = pytrends.related_queries()
    rising = []

    for k, v in related.items():
        if v.get("rising") is not None:
            rising += v["rising"]["query"].tolist()

    return {
        "interest_over_time": interest,
        "regions": regions,
        "rising_queries": list(set(rising))[:50],
    }