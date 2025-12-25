from pytrends.request import TrendReq
import pandas as pd

def fetch_google_trends(keywords, timeframe="today 12-m", geo="US"):
    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)

    data = {}

    # Interest over time
    iot = pytrends.interest_over_time()
    if not iot.empty:
        data["interest_over_time"] = iot.drop(columns=["isPartial"], errors="ignore")

    # Related queries
    rq = pytrends.related_queries()
    related = []

    for kw, blocks in rq.items():
        for block in ["top", "rising"]:
            df = blocks.get(block)
            if df is not None:
                df["keyword"] = kw
                df["type"] = block
                related.append(df)

    if related:
        data["related_queries"] = pd.concat(related)

    return data