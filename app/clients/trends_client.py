from pytrends.request import TrendReq
import requests

def google_trends(seed_terms, geo="US", timeframe="today 12-m"):
    pt = TrendReq(hl="en-US", tz=360)
    pt.build_payload(seed_terms, geo=geo, timeframe=timeframe)
    return pt.related_queries()

def tiktok_trends():
    # Public trending hashtags example
    url = "https://www.tiktok.com/api/discover/item_list/?region=US&count=10"
    try:
        return requests.get(url, timeout=10).json()
    except Exception as e:
        return {"error": str(e)}

def youtube_trends():
    return {"trending": ["music videos", "streetwear vlogs", "home care tips"]}

def spotify_trends():
    return {"trending": ["hip hop playlists", "lofi beats", "relaxing acoustic"]}

def aggregate_trends(seed_terms):
    out = {}
    try:
        out["google"] = google_trends(seed_terms)
        out["tiktok"] = tiktok_trends()
        out["youtube"] = youtube_trends()
        out["spotify"] = spotify_trends()
    except Exception as e:
        out["error"] = str(e)
    return out
