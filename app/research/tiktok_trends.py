import pandas as pd


def get_tiktok_trends(seed: str):
    return pd.DataFrame({
        "trend": [
            f"{seed} challenge",
            f"{seed} POV",
            f"{seed} before after"
        ],
        "format": [
            "UGC",
            "Storytime",
            "Hook-based"
        ]
    })
