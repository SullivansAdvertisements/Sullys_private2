import json, requests, os

API_V = "v18.0"
BASE  = f"https://graph.facebook.com/{API_V}"

def _secrets(st_secrets):
    s = st_secrets
    return {
        "token":  s.get("META_SYSTEM_USER_TOKEN"),
        "ad_acct":s.get("META_AD_ACCOUNT_ID"),
        "biz":    s.get("META_BUSINESS_ID"),
        "page":   s.get("META_PAGE_ID"),
        "pixel":  s.get("META_PIXEL_ID"),
        "ig":     s.get("META_IG_ACTOR_ID",""),
    }

def _ok(creds): return all([creds["token"], creds["ad_acct"], creds["biz"], creds["page"]])

def meta_delivery_estimate(st_secrets, country="US", age_min=18, age_max=45):
    c = _secrets(st_secrets)
    if not _ok(c):
        return {"status":"demo","estimated_daily_reach": 120000}
    targeting = {
        "age_min": age_min,
        "age_max": age_max,
        "geo_locations": {"countries": [country]},
    }
    url = f"{BASE}/act_{c['ad_acct']}/delivery_estimate"
    payload = {
        "optimization_goal": "REACH",
        "targeting_spec": json.dumps(targeting),
        "access_token": c["token"],
    }
    r = requests.post(url, data=payload, timeout=20)
    try:
        j = r.json()
    except Exception:
        return {"error": f"bad response {r.status_code}"}
    if r.status_code != 200: return {"error": j}
    data = j.get("data",[{}])[0] if isinstance(j.get("data"), list) else j
    return {"status":"live","raw":j,"estimate": data}

def create_campaign(st_secrets, name, objective):
    c = _secrets(st_secrets)
    if not _ok(c): return {"error":"missing meta secrets"}
    url = f"{BASE}/act_{c['ad_acct']}/campaigns"
    payload = {
        "name": name,
        "objective": objective,   # OUTCOME_AWARENESS / TRAFFIC / LEADS / SALES
        "status": "PAUSED",
        "buying_type": "AUCTION",
        "special_ad_categories": "[]",
        "access_token": c["token"],
    }
    r = requests.post(url, data=payload, timeout=20)
    return r.json()

def create_adset(st_secrets, campaign_id, name, daily_budget_usd, country="US",
                 age_min=18, age_max=45, objective="OUTCOME_AWARENESS"):
    c = _secrets(st_secrets)
    if not _ok(c): return {"error":"missing meta secrets"}
    budget_minor = int(float(daily_budget_usd) * 100)
    goal = "REACH" if "AWARENESS" in objective else ("LINK_CLICKS" if "TRAFFIC" in objective else "CONVERSIONS")
    targeting = {
        "geo_locations": {"countries": [country]},
        "age_min": age_min, "age_max": age_max
    }
    payload = {
        "name": name,
        "campaign_id": campaign_id,
        "daily_budget": str(budget_minor),
        "billing_event": "IMPRESSIONS",
        "optimization_goal": goal,
        "status": "PAUSED",
        "targeting": json.dumps(targeting),
        "access_token": c["token"],
    }
    if goal == "CONVERSIONS" and c["pixel"]:
        payload["promoted_object"] = json.dumps({"pixel_id": c["pixel"]})
    url = f"{BASE}/act_{c['ad_acct']}/adsets"
    r = requests.post(url, data=payload, timeout=20)
    return r.json()

def create_ad(st_secrets, adset_id, name, page_id, ig_actor_id, link_url,
              primary_text, headline, description):
    c = _secrets(st_secrets)
    if not _ok(c): return {"error":"missing meta secrets"}

    creative_url = f"{BASE}/act_{c['ad_acct']}/adcreatives"
    oss = {
        "page_id": page_id,
        "link_data": {
            "message": primary_text,
            "name": headline,
            "description": description,
            "link": link_url,
            "call_to_action": {"type":"LEARN_MORE","value":{"link":link_url}}
        }
    }
    if ig_actor_id: oss["instagram_actor_id"] = ig_actor_id
    cr = requests.post(creative_url, data={
        "name": f"{name} – Creative",
        "object_story_spec": json.dumps(oss),
        "access_token": c["token"]
    }, timeout=20).json()
    if "id" not in cr: return {"creative_error": cr}

    ad_url = f"{BASE}/act_{c['ad_acct']}/ads"
    ad = requests.post(ad_url, data={
        "name": name,
        "adset_id": adset_id,
        "creative": json.dumps({"creative_id": cr["id"]}),
        "status": "PAUSED",
        "access_token": c["token"]
    }, timeout=20).json()
    return {"creative": cr, "ad": ad}

def meta_campaign_generator(brand, objective, budget, keywords):
    # High-level wrapper used by the UI “Generate” button
    plan = {
        "brand": brand,
        "objective": objective,
        "daily_budget": budget,
        "keywords": [k.strip() for k in keywords.replace(",", "\n").split("\n") if k.strip()],
    }
    plan["delivery_estimate"] = {"note": "call meta_delivery_estimate() in UI with your geo"}
    return plan
