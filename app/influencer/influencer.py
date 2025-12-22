import pandas as pd


def find_influencers(topic: str):
    return pd.DataFrame({
        "creator": [
            f"{topic.title()} Creator 1",
            f"{topic.title()} Creator 2",
            f"{topic.title()} Creator 3"
        ],
        "platform": ["Instagram", "TikTok", "YouTube"],
        "followers": ["120K", "85K", "240K"]
    })
