import pandas as pd


def get_meta_ad_angles(seed: str):
    return pd.DataFrame({
        "angle": [
            f"{seed} limited offer",
            f"{seed} testimonials",
            f"{seed} problem → solution"
        ],
        "format": [
            "Video",
            "Carousel",
            "Static image"
        ]
    })
