def generate_hashtags(seed: str, niche: str):
    base = seed.lower().replace(" ", "")

    if niche == "Music":
        return {
            "instagram": [
                f"#{base}",
                "#newmusic",
                "#independentartist",
                "#musicmarketing",
                "#artistsoninstagram",
                "#musicreels",
            ],
            "tiktok": [
                f"#{base}",
                "#musicdiscovery",
                "#newartist",
                "#fyp",
                "#undergroundmusic",
            ],
            "youtube": [
                f"#{base}",
                "#musicvideo",
                "#newrelease",
                "#indiemusic",
            ],
            "twitter": [
                f"#{base}",
                "#NewMusicFriday",
                "#MusicPromo",
            ],
        }

    if niche == "Clothing":
        return {
            "instagram": [
                f"#{base}",
                "#streetwearbrand",
                "#fashionreels",
                "#outfitinspo",
                "#streetwearstyle",
                "#brandowner",
            ],
            "tiktok": [
                f"#{base}",
                "#streetwear",
                "#fashiontok",
                "#outfitideas",
                "#brandtok",
            ],
            "youtube": [
                f"#{base}",
                "#streetwearbrand",
                "#fashionhaul",
            ],
            "twitter": [
                f"#{base}",
                "#Streetwear",
                "#FashionBrand",
            ],
        }

    if niche == "Homecare":
        return {
            "instagram": [
                "#homecare",
                "#seniorcare",
                "#caregiverlife",
                "#homehealth",
                "#agingparents",
            ],
            "tiktok": [
                "#homecare",
                "#caregiving",
                "#healthtok",
            ],
            "youtube": [
                "#homecare",
                "#seniorhealth",
            ],
            "twitter": [
                "#HomeCare",
                "#SeniorCare",
            ],
        }

    return {}