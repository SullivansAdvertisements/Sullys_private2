from pytrends.request import TrendReq
import pandas as pd


def get_google_trends(seed: str, geo: str = "US", timeframe="today 12-m"):
    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload([seed], timeframe=timeframe, geo=geo)

    df = pytrends.interest_over_time()
    if df.empty:
        return pd.DataFrame({"message": ["No trend data found"]})

    if "isPartial" in df.columns:
        df = df.drop(columns=["isPartial"])

    return df.reset_index()


def get_related_queries(seed: str):
    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload([seed])

    rq = pytrends.related_queries()
    if seed not in rq or rq[seed]["top"] is None:
        return []

    return rq[seed]["top"]["query"].tolist()
