"""Download S18 Worlds player portraits from Liquipedia into photos/s18/.

Run this on your own computer (Liquipedia blocks most server IPs):
    pip install pillow
    python scripts/fetch_photos_s18.py

It skips players that already have a photo, so it is safe to re-run.
Liquipedia asks for a descriptive User-Agent and at most one page request every 2 seconds.
"""
import io
import os
import re
import time
import urllib.parse
import urllib.request

from PIL import Image

UA = "S18TFTTierList/1.0 (fan tier-list site; github.com/eric0871/s17-tft-tier-list)"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "photos", "s18")
os.makedirs(OUT, exist_ok=True)

# (file id used by index.html, Liquipedia page name)
PLAYERS = [
    ("Broseph", "Broseph"), ("bopster", "Bopster"), ("Upsetmax", "Upsetmax"), ("ego", "Ego"),
    ("JosueDeleted", "JosueDeleted"), ("Dishsoap", "Dishsoap"), ("wigwugg", "Wigwugg"),
    ("Cambulee", "Cambulee"), ("Chunington", "Chunington"), ("wasianiverson", "Wasianiverson"),
    ("L3SCoco", "L3S_Coco"), ("Yakumo", "Yakumo"), ("Cynarr", "Cynarr"), ("oskuu", "Oskuu"),
    ("whyyoumadpro", "Whyyoumadpro"), ("bensac", "Bensac"), ("Skipaeus", "Skipaeus"), ("ZyK0o", "ZyK0o"),
    ("Jazlatte", "JazLatte"), ("AQ1H", "AQ1H"), ("Milo", "Milo"), ("pigpig", "Pigpig"), ("title", "Title"),
    ("Maris", "Maris"), ("iCeEmperoz", "ICeEmperoz"), ("Iron_Bog", "Iron_Bog"), ("steppy", "Steppy"),
    ("WithoutYou", "WithoutYou"), ("seoill", "Seoill"),
    ("Baizhi", "Baizhi"), ("ACE", "Ace"), ("Rue", "Rue"), ("Myyz", "Myyz"), ("CSFX", "CangShan"),
    ("HuiYuan", "HuiYuan"), ("HangHang", "HangHang"), ("Linshen", "Linshen"), ("Hexi", "Hexi"),
    ("Hanxing", "HanXing"), ("diaomei", "Diaomei"),
]


def get(url, referer=None):
    headers = {"User-Agent": UA}
    if referer:
        headers["Referer"] = referer
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        return r.read()


def square(blob):
    im = Image.open(io.BytesIO(blob)).convert("RGB")
    w, h = im.size
    s = min(w, h)
    x0 = (w - s) // 2
    y0 = 0 if h > w else (h - s) // 2  # portrait shots: keep the top (the face)
    return im.crop((x0, y0, x0 + s, y0 + s)).resize((360, 360), Image.LANCZOS)


for pid, page in PLAYERS:
    dest = os.path.join(OUT, pid + ".jpg")
    if os.path.exists(dest):
        print(f"[have ] {pid}")
        continue
    url = "https://liquipedia.net/tft/" + urllib.parse.quote(page)
    try:
        html = get(url).decode("utf-8", "ignore")
        m = re.search(r'class="infobox-image[^"]*"[^>]*>.*?<img[^>]+src="(/commons/images/[^"]+?\.(?:jpg|jpeg|png))"', html, re.S)
        if not m or any(k in m.group(1).lower() for k in ("logo", "allmode", "flag", "noimage", "icon")):
            print(f"[none ] {pid} (no portrait on {url})")
        else:
            img = "https://liquipedia.net" + m.group(1)
            square(get(img, referer=url)).save(dest, quality=86)
            print(f"[saved] {pid} <- {img}")
    except Exception as e:  # keep going; one bad page should not stop the rest
        print(f"[error] {pid}: {e}")
    time.sleep(2.2)

print("\nDone. Commit photos/s18/ and push; the site picks the new files up automatically.")
