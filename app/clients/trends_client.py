import pandas as pd
from pytrends.request import TrendReq

def google_trends(seed: str, timeframe="today 12-m", geo=""):
    seeds = [w.strip() for w in seed.replace(",", "\n").split("\n") if w.strip()]
    if not seeds:
        return {"error": "no seeds"}
    try:
        py = TrendReq(hl="en-US", tz=360)
        py.build_payload(seeds, timeframe=timeframe, geo=geo, gprop="")
        out = {}
        iot = py.interest_over_time()
        if isinstance(iot, pd.DataFrame) and not iot.empty:
            if "isPartial" in iot.columns: iot = iot.drop(columns=["isPartial"])
            out["interest_over_time"] = iot.tail(30).to_dict()
        rq = py.related_queries()
        sug = []
        if isinstance(rq, dict):
            for _, buckets in rq.items():
                for key in ("top", "rising"):
                    df = buckets.get(key)
                    if isinstance(df, pd.DataFrame) and "query" in df.columns:
                        sug += df["query"].dropna().astype(str).tolist()
        out["related_suggestions"] = list(dict.fromkeys(sug))[:100]
        return out
    except Exception as e:
        return {"error": str(e)}

def tiktok_trends(seed: str):
    # Public Creative Center has no stable API; return structured placeholders
    # so UI never breaks. Replace with your backend proxy if you have one.
    seeds = [w.strip() for w in seed.replace(",", "\n").split("\n") if w.strip()]
    topics = [f"{s} aesthetic" for s in seeds][:10] or ["viral outfit", "day in the life"]
    hooks  = [f"POV: You found {s}" for s in seeds][:10] or ["Watch till the end"]
    return {"topics": topics, "hooks": hooks}

def youtube_trends(seed: str):
    seeds = [w.strip() for w in seed.replace(",", "\n").split("\n") if w.strip()]
    q = [f"{s} tutorial" for s in seeds][:10] or ["streetwear lookbook", "mixing tutorial"]
    return {"queries": q}

def spotify_audience(seed: str):
    # Web API discovery requires OAuth; we return genre guesses from seeds.
    seeds = [w.strip() for w in seed.replace(",", "\n").split("\n") if w.strip()]
    genres = [f"{s} fans" for s in seeds][:10] or ["hip hop", "lofi", "trap"]
    return {"genres": genres}

def cross_platform_trends(seed: str, timeframe="today 12-m", geo=""):
    return {
        "google":  google_trends(seed, timeframe=timeframe, geo=geo),
        "tiktok":  tiktok_trends(seed),
        "youtube": youtube_trends(seed),
        "spotify": spotify_audience(seed),
    }
