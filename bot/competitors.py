import re
from typing import List, Dict, Tuple
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from collections import Counter, defaultdict

# Common stopwords and noise
STOPWORDS = set("""
a an the and or but if then else when at by for in of on to from with without into over under near not no yes is are was were be been being have has had do does did can could should would you your we our they them this that these those
care service services near me best top local provider clinic hospital free job jobs hiring wholesale pattern download mp3 wav mp4 pdf
""".split())

# US state full names and postal abbreviations
US_STATES = [
    "alabama","alaska","arizona","arkansas","california","colorado","connecticut","delaware","florida","georgia",
    "hawaii","idaho","illinois","indiana","iowa","kansas","kentucky","louisiana","maine","maryland",
    "massachusetts","michigan","minnesota","mississippi","missouri","montana","nebraska","nevada",
    "new hampshire","new jersey","new mexico","new york","north carolina","north dakota","ohio","oklahoma",
    "oregon","pennsylvania","rhode island","south carolina","south dakota","tennessee","texas","utah","vermont",
    "virginia","washington","west virginia","wisconsin","wyoming"
]
STATE_ABBR = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME",
              "MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA",
              "RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]

ZIP_RE = re.compile(r"\b\d{5}(?:-\d{4})?\b")  # 12345 or 12345-6789

def fetch_text(url: str, timeout: int = 12) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SullyBot/1.1)"}
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, "html.parser")
        # Prefer structured address if available
        parts = []
        for adr in soup.select('[itemtype*="PostalAddress"], [itemprop*="address"]'):
            parts.append(adr.get_text(" ", strip=True))
        # Main textual content
        for t in soup(["script", "style", "noscript"]):
            t.extract()
        parts += [t.get_text(" ", strip=True) for t in soup.find_all(["h1","h2","h3","p","li","address","td","meta"])]
        text = " ".join(parts)
        return text
    except Exception:
        return ""

def extract_locations_block(text: str, host: str) -> Dict[str, Counter]:
    # Normalize spacing, keep case for city detection
    raw = text
    low = raw.lower()

    cities = Counter()
    states = Counter()
    zips = Counter()

    # ZIP codes
    for m in ZIP_RE.finditer(raw):
        z = m.group(0)
        zips[z] += 1

    # State names and abbreviations
    for s in US_STATES:
        if f" {s} " in f" {low} ":
            states[s.title()] += 1
    for ab in STATE_ABBR:
        # word boundary to avoid matching parts of words
        if re.search(rf"\b{ab}\b", raw):
            states[ab.upper()] += 1

    # City patterns: “City”, “County”, “Metro”, etc.
    for m in re.finditer(r"\b([A-Z][a-zA-Z\-]{2,}(?:\s[A-Z][a-zA-Z\-]{2,})?)\s+(City|County|Metro|Area|Region)\b", raw):
        cities[m.group(1)] += 1

    # Comma patterns like "Springfield, IL" or "Austin, Texas"
    for m in re.finditer(r"\b([A-Z][a-zA-Z\-]{2,}(?:\s[A-Z][a-zA-Z\-]{2,})?),\s*([A-Z]{2}|[A-Z][a-z]+)\b", raw):
        cities[m.group(1)] += 1
        states[m.group(2).upper() if len(m.group(2))==2 else m.group(2).title()] += 1

    # Host subdomain often hints a city: austin.example.com
    parts = (host or "").split(".")
    if len(parts) >= 3 and parts[0].istitle():
        cities[parts[0]] += 1

    return {"cities": cities, "states": states, "zips": zips}

def extract_keywords(text: str, top_n: int = 40) -> List[str]:
    low = text.lower()
    tokens = re.findall(r"[a-z][a-z\-]{2,}", low)
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) <= 30]
    bigrams = [" ".join([tokens[i], tokens[i+1]]) for i in range(len(tokens)-1)]
    counts = Counter(tokens + bigrams)
    common = [w for w,_ in counts.most_common(300)]
    focus = [w for w in common if any(k in w for k in [
        "home","care","senior","elder","alzheim","respite","disability","therapy","music","clothing",
        "consignment","vintage","thrift","brand","store","near me","service","pricing","appointment","licensed","insured"
    ])]
    seen, out = set(), []
    for w in focus + common:
        if w not in seen:
            out.append(w); seen.add(w)
        if len(out) >= top_n: break
    return out

def analyze_competitors(urls: List[str]) -> Dict[str, List[str] | Dict[str, int]]:
    totals_cities = Counter()
    totals_states = Counter()
    totals_zips = Counter()
    all_text = ""

    for u in urls:
        u = u.strip()
        if not u: continue
        txt = fetch_text(u)
        all_text += " " + txt
        host = urlparse(u).hostname or ""
        locs = extract_locations_block(txt, host)
        totals_cities.update(locs["cities"])
        totals_states.update(locs["states"])
        totals_zips.update(locs["zips"])

    # Rank by frequency
    top_cities = [c for c,_ in totals_cities.most_common(50)]
    top_states = [s for s,_ in totals_states.most_common(50)]
    top_zips = [z for z,_ in totals_zips.most_common(100)]
    keywords = extract_keywords(all_text, top_n=40) if all_text.strip() else []

    return {
        "keywords": keywords,
        "cities_ranked": top_cities,
        "states_ranked": top_states,
        "zips_ranked": top_zips,
        "cities_counts": dict(totals_cities),
        "states_counts": dict(totals_states),
        "zips_counts": dict(totals_zips),
    }

