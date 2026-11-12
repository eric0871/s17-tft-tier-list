"""Tiny polite Liquipedia API client (TFT wiki).

- descriptive User-Agent, gzip (required), >=2.5 s between normal calls, >=32 s between action=parse calls
- on HTTP 429 waits 60 s and retries (max 3)
- caches every response on disk under raw/liquipedia/ so re-runs don't hit the API again
"""
import gzip, hashlib, json, os, time, urllib.parse, urllib.request, urllib.error

UA = "S18TFTTierList/1.0 (fan tier-list site; github.com/eric0871/s17-tft-tier-list)"
API = "https://liquipedia.net/tft/api.php"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "raw", "liquipedia", "cache")
os.makedirs(CACHE, exist_ok=True)
_last = {"normal": 0.0, "parse": 0.0}
GAP = {"normal": 4.0, "parse": 35.0}


def call(params, use_cache=True):
    params = dict(params, format="json", formatversion="2")
    q = urllib.parse.urlencode(sorted(params.items()))
    key = hashlib.sha1(q.encode()).hexdigest()[:16]
    path = os.path.join(CACHE, key + ".json")
    if use_cache and os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    kind = "parse" if params.get("action") == "parse" else "normal"
    for attempt in range(6):
        wait = GAP[kind] - (time.time() - _last[kind])
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(API + "?" + q, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
            _last[kind] = time.time()
            data = json.loads(raw.decode("utf-8"))
            json.dump({"_q": q, **data}, open(path, "w", encoding="utf-8"), ensure_ascii=False)
            return data
        except urllib.error.HTTPError as e:
            _last[kind] = time.time()
            if e.code == 429 and attempt < 5:
                print("429, sleeping %ds" % (60 * (attempt + 1)), flush=True)
                time.sleep(60 * (attempt + 1))
                continue
            raise


def wikitext(titles):
    """titles: list (<=50). returns {requested_title: (resolved_title, wikitext or None)}"""
    d = call({"action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main",
              "redirects": "1", "titles": "|".join(titles)})
    q = d.get("query", {})
    mp = {t: t for t in titles}
    for n in q.get("normalized", []):
        for k, v in mp.items():
            if v == n["from"]:
                mp[k] = n["to"]
    for r in q.get("redirects", []):
        for k, v in mp.items():
            if v == r["from"]:
                mp[k] = r["to"]
    pages = {p["title"]: p for p in q.get("pages", [])}
    out = {}
    for t in titles:
        p = pages.get(mp[t])
        if not p or p.get("missing"):
            out[t] = (mp[t], None)
        else:
            out[t] = (p["title"], p["revisions"][0]["slots"]["main"]["content"])
    return out


def parse_html(page, section=None):
    params = {"action": "parse", "page": page, "prop": "text", "disablelimitreport": "1", "disableeditsection": "1"}
    if section is not None:
        params["section"] = str(section)
    d = call(params)
    return d["parse"]["text"]
