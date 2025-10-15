import re
from typing import List, Dict
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from collections import Counter

STOPWORDS = set("""a an the and or but if then else when at by for in of on to from with without into over under near not no yes is are was were be been being have has had do does did can could should would you your we our they them this that these those it's its i'm we're there's as it's it's's
care service services near me best top local provider clinic hospital free job jobs hiring wholesale pattern download mp3 wav mp4 pdf""".split())

US_STATES = [
    "alabama","alaska","arizona","arkansas","california","colorado","connecticut","delaware","florida","georgia",
    "hawaii","idaho","illinois","indiana","iowa","kansas","kentucky","louisiana","maine","maryland","massachusetts","michigan","minnesota",
    "mississippi","missouri","montana","nebraska","nevada","new hampshire","new jersey","new mexico","new york","north carolina","north dakota",
    "ohio","oklahoma","oregon","pennsylvania","rhode island","south carolina","south dakota","tennessee","texas","utah","vermont","virginia",
    "washington","west virginia","wisconsin","wyoming"
]
STATE_ABBR = ["al","ak","az","ar","ca","co","ct","de","fl","ga","hi","id","il","in","ia","ks","ky","la","me","md","ma","mi","mn","ms","mo","mt","ne","nv","nh","nj","nm","ny","nc","nd","oh","ok","or","pa","ri","sc","sd","tn","tx","ut","vt","va","wa","wv","wi","wy"]

def fetch_text(url: str, timeout: int = 12) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SullyBot/1.0)"}
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, "html.parser")
        for t in soup(["script","style","noscript"]):
            t.extract()
        texts = [t.get_text(" ", strip=True) for t in soup.find_all(["h1","h2","h3","p","li","meta"])]
        return " ".join(texts).lower()
    except Exception:
        return ""

def extract_keywords(text: str, top_n: int = 30):
    tokens = re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", text.lower())
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) <= 30]
    bigrams = [" ".join([tokens[i], tokens[i+1]]) for i in range(len(tokens)-1)]
    from collections import Counter
    counts = Counter(tokens + bigrams)
    common = [w for w,_ in counts.most_common(200)]
    filtered = [w for w in common if not w.isdigit() and len(w) > 2]
    prefer = [w for w in filtered if any(k in w for k in ["care","home","senior","elder","in home","assistance","therapy","music","clothing","consignment","store","sell","buy","near me","video","tickets","brand","vintage","thrift"])]
    uniques = []
    for w in prefer + filtered:
        if w not in uniques:
            uniques.append(w)
        if len(uniques) >= top_n:
            break
    return uniques

def extract_locations(text: str, host: str):
    locs = set()
    for s in US_STATES:
        if f" {s} " in f" {text} ":
            locs.add(s.title())
    for ab in STATE_ABBR:
        import re
        if re.search(rf"\b{ab}\b", text):
            locs.add(ab.upper())
    parts = (host or "").split(".")
    if len(parts) >= 3:
        locs.add(parts[0].title())
    return sorted(locs)

def analyze_competitors(urls: List[str]) -> Dict[str, list]:
    all_text = ""
    locs = set()
    for u in urls:
        u = u.strip()
        if not u:
            continue
        txt = fetch_text(u)
        host = urlparse(u).hostname or ""
        all_text += " " + txt
        for l in extract_locations(txt, host):
            locs.add(l)
    keywords = extract_keywords(all_text, top_n=40) if all_text.strip() else []
    return {"keywords": keywords, "locations": sorted(locs)}
