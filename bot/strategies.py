from typing import Dict
from .audiences import AUDIENCE_BANK, DEFAULT_COUNTRY_EXCLUSIONS

def campaign_dev_meta(niche: str, insights: Dict) -> Dict:
    bank = AUDIENCE_BANK[niche]
    kws = insights.get("keywords", [])
    locs = insights.get("locations", ["{geo}"])
    return {
        "platform": "meta",
        "objective": "Sales/Leads",
        "campaigns": [
            {
                "name": f"{niche}_conv_{'{month}'}_{'{geo}'}",
                "objective": "Sales",
                "daily_budget_rule": "Scale +20% when ROAS > 2.5 for 3 days",
                "ad_sets": [
                    {"name": "INT_Interests", "targeting": {"interests": bank["interests"], "geo": locs, "exclusions": bank["exclusions"]}},
                    {"name": "LLA_Lookalikes", "targeting": {"lookalikes": bank["lookalikes"], "geo": locs}},
                    {"name": "RT_Retargeting", "targeting": {"custom_audiences": ["site_visitors_30","engagers_30"], "geo": locs}},
                ],
                "creatives": {"formats": ["Reels 9:16","Carousel 1:1","Static 1:1"], "brief": "Hook in 2s • Benefit • Proof • CTA • Captions"},
                "tracking": {"pixel": True, "events": ["Lead","Purchase","ViewContent"], "utm": "utm_source=meta&utm_medium=paid&utm_campaign={campaign}"},
                "optimizations": ["Consolidate low-spend ad sets","Test 3 hooks/week","Rotate creatives weekly"],
                "keywords_hints": kws[:15],
            }
        ],
        "kpis": ["CPA","ROAS","CTR","Thumbstop"],
    }

def campaign_dev_google(niche: str, insights: Dict) -> Dict:
    bank = AUDIENCE_BANK[niche]
    kws = insights.get("keywords", []) or bank.get("keywords_positive", [])
    locs = insights.get("locations", ["{geo}"])
    return {
        "platform": "google",
        "objective": "Sales/Leads",
        "search": {
            "brand": {"keywords": ["{brand}","{brand} site"], "negatives": []},
            "nonbrand": {"keywords": kws[:25], "negatives": bank.get("keywords_negative", [])},
            "geo": locs,
            "bidding": "Max Conversions → tROAS after 30+ conversions",
            "rsa_headlines": ["{brand} Official Site","{value_prop}","Local {niche} {product}","Call Today"],
            "rsa_descriptions": ["Trusted {niche}. Licensed & insured. Call now.","Fast response. Friendly team. {offer}"],
        },
        "youtube": {"sequence": ["6s Bumper","15s Skippable"], "targeting": ["In-market","Custom segments from keywords"]},
        "kpis": ["Conversions","CPA","ROAS","Impr. Share","VTR"],
    }

def campaign_dev_tiktok(niche: str, insights: Dict) -> Dict:
    bank = AUDIENCE_BANK[niche]
    locs = insights.get("locations", ["{geo}"])
    return {
        "platform": "tiktok",
        "objective": "Sales/Leads",
        "ad_groups": [
            {"name": "INT_Interests", "targeting": {"interests": bank["interests"], "geo": locs}},
            {"name": "BROAD", "targeting": {"geo": locs}},
            {"name": "RT_VC7_ATC14", "targeting": {"custom": ["viewers_7","atc_14"], "geo": locs}},
        ],
        "creatives": {"specs": "9:16 • 7–12s • native • captions", "ideas": ["Before/After","Testimonial","Day-in-the-life"]},
        "kpis": ["CPA","CTR","Thumbstop","View time"],
    }

def campaign_dev_twitter(niche: str, insights: Dict) -> Dict:
    bank = AUDIENCE_BANK[niche]
    kws = insights.get("keywords", []) or bank.get("keywords_positive", [])
    return {
        "platform": "twitter",
        "objective": "Awareness/Traffic",
        "targeting": {"keywords": kws[:20], "interests": bank["interests"][:10]},
        "formats": ["Image","Video","Carousel"],
        "copy_template": "{hook}\n{benefit}\n{cta} #YourHashtag",
        "kpis": ["Engagement rate","CPM","Site visits"],
    }

PLATFORM_DEVELOPMENT = {
    "meta": campaign_dev_meta,
    "google": campaign_dev_google,
    "tiktok": campaign_dev_tiktok,
    "twitter": campaign_dev_twitter,
}
