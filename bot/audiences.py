from typing import Dict, List

AUDIENCE_BANK: Dict[str, Dict] = {
    "clothing": {
        "demographics": {"age": "18-44", "genders": ["all"]},
        "interests": ["Streetwear","Sneakers","Hypebeast","Athleisure","Urban culture","Celebrity style"],
        "lookalikes": ["site_visitors_180","ig_engagers_365","purchasers_365"],
        "exclusions": ["recent_purchasers_30","employees"],
        "keywords_positive": [
            "buy streetwear online","graphic tees","urban clothing","streetwear brand","hoodies","caps","new collection"
        ],
        "keywords_negative": ["free","job","wholesale","knitting pattern"]
    },
    "consignment": {
        "demographics": {"age": "21-65", "genders": ["all"]},
        "interests": ["Thrifting","Second-hand","Vintage fashion","Sustainability","Minimalism"],
        "lookalikes": ["store_visitors_180","fb_page_engagers_365","sellers_365"],
        "exclusions": ["recent_sellers_30","employees"],
        "keywords_positive": [
            "consignment store near me","sell clothes near me","thrift store",
            "buy used designer","resale shop"
        ],
        "keywords_negative": ["donation center","free","dumpster"]
    },
    "musician": {
        "demographics": {"age": "16-39","genders":["all"]},
        "interests": ["Spotify","Apple Music","SoundCloud","Live music","Music festivals"],
        "lookalikes": ["video_viewers_365","profile_engagers_365","listeners_180"],
        "exclusions": ["recent_listeners_7","employees"],
        "keywords_positive": [
            "new {genre} artist","{genre} album","stream {artist}","music video","upcoming tour dates"
        ],
        "keywords_negative": ["free download","instrument lessons"]
    },
    "homecare": {
        "demographics": {"age": "35-75", "genders": ["all"]},
        "interests": [
            "Elder care","Caregiving","Home health care","Alzheimer's & dementia support",
            "Disability services","Medicare","Veterans benefits"
        ],
        "lookalikes": ["lead_form_submitters_365","site_visitors_180","call_inquiries_180"],
        "exclusions": ["current_clients","employees"],
        "keywords_positive": [
            "home care near me","in home care for seniors","caregiver for special needs",
            "alzheimers home care","respite care","non medical home care"
        ],
        "keywords_negative": ["nursing jobs","free","hospital inpatient"]
    },
}
DEFAULT_COUNTRY_EXCLUSIONS: List[str] = []
