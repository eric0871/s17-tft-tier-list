import urllib.request, gzip, re, json, os, time, io

UA = "MoTFTTierList/1.0 (personal wiki tool; contact xiaomo@agentmail.to)"
OUTDIR = r"C:\Users\ericc\OneDrive\文档\second_brain\tft-crown-photos"
os.makedirs(OUTDIR, exist_ok=True)

PLAYERS = [
 ("BruhbruhbruhWHO","ca","AMER"),("Dankmemes01","us","AMER"),("Darth Nub","us","AMER"),
 ("Dishsoap","us","AMER"),("k0nda1","br","AMER"),("k3soju","us","AMER"),
 ("Kaiweng","us","AMER"),("Upsetmax","ca","AMER"),("VCLF","br","AMER"),
 ("Bensac","fr","EMEA"),("Guillosko","es","EMEA"),("HoroX","cn","EMEA"),
 ("Hypno","fr","EMEA"),("Jedusor","fr","EMEA"),("PeepoGlad","pl","EMEA"),
 ("Safo20","es","EMEA"),("Tarteman","fr","EMEA"),("ZyK0o","fr","EMEA"),
 ("A Long","vn","APAC"),("AQ1H","hk","APAC"),("Iron Bog","hk","APAC"),
 ("Maris","vn","APAC"),("Milo","vn","APAC"),("seoill","kr","APAC"),
 ("steelo of bora","kr","APAC"),("steppy","sg","APAC"),("title","jp","APAC"),
 ("YBY1","vn","APAC"),
 ("diaomei","cn","CN"),("Huanmie","cn","CN"),("huanyi","cn","CN"),
 ("jiejie","cn","CN"),("LiShao","cn","CN"),("LiTuChuan","cn","CN"),
 ("QituX","cn","CN"),("Ringo","cn","CN"),("suirenka","cn","CN"),
 ("TianLong","cn","CN"),("XiaoGe","cn","CN"),("XZZ","cn","CN"),
]

def pid(n): return re.sub(r'[^a-zA-Z0-9]','_',n)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":UA,"Accept-Encoding":"gzip"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
        if r.headers.get("Content-Encoding")=="gzip":
            data = gzip.decompress(data)
        return data, r.status, r.geturl()

def fetch_bin(url):
    req = urllib.request.Request(url, headers={"User-Agent":UA,"Referer":"https://liquipedia.net/tft/"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read(), r.status

result = {}
photo_count = 0
for name, code, region in PLAYERS:
    i = pid(name)
    page = "https://liquipedia.net/tft/" + urllib.parse.quote(name.replace(" ","_"))
    entry = {"name":name,"code":code,"region":region,"photo":None}
    try:
        html, status, finalurl = fetch(page)
        html = html.decode("utf-8","ignore")
        # strictly anchor on the portrait container, grab first img (thumb or full)
        m = re.search(r'class="infobox-image lightmode"[^>]*>.*?<img[^>]+src="(/commons/images/[^"]+?\.(?:jpg|jpeg|png))"', html, re.S)
        if m:
            src = m.group(1)
            low = src.lower()
            fname = src.split("/")[-1]
            # skip flags / logos / set icons
            if any(k in low for k in ["_hd.png","logo_filler","allmode","icon_","flag","noimage"]):
                print(f"[SKIP ] {name:20s} matched non-portrait: {fname}")
                m = None
            else:
                print(f"[MATCH] {name:20s} file: {fname}")
        if m:
            imgurl = "https://liquipedia.net" + m.group(1)
            try:
                blob, st = fetch_bin(imgurl)
                ext = ".jpg" if imgurl.lower().split("/")[-1].endswith((".jpg",".jpeg")) else ".png"
                fn = i + ext
                with open(os.path.join(OUTDIR, fn), "wb") as f:
                    f.write(blob)
                entry["photo"] = fn
                photo_count += 1
                print(f"[PHOTO] {name:20s} -> {fn} ({len(blob)//1024}KB)")
            except Exception as e:
                print(f"[DLFAIL] {name:20s} img={imgurl} err={e}")
        else:
            print(f"[FLAG ] {name:20s} (no portrait, status={status})")
    except Exception as e:
        print(f"[ERR  ] {name:20s} url={page} err={e}")
    result[i] = entry
    time.sleep(1.2)

with open(os.path.join(OUTDIR, "_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print(f"\n=== {photo_count}/{len(PLAYERS)} players have photos ===")
