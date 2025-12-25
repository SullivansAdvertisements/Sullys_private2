mimport pandas as pd

def get_youtube_trends(keyword: str, region: str = "US"):
    data = [
        {
            "video_title": f"{keyword} explained",
            "estimated_views": 1200000,
            "category": "Education",
            "platform": "YouTube"
        },
        {
            "video_title": f"{keyword} viral breakdown",
            "estimated_views": 890000,
            "category": "Entertainment",
            "platform": "YouTube"
        }
    ]

    return pd.DataFrame(data)