"""Download the official S18 Worlds headshots and cut out their backgrounds.

Source: the official Pick'em site (pickem.competetft.com) — every player has a 250x250 headshot
on a flat region colour (CN yellow / AMER blue / EMEA orange / APAC purple). We key that flat
colour out so the page can put the faces on any background.

Writes, for every player id used by index.html:
    photos/s18/<id>.png   transparent cut-out
    photos/s18/<id>.jpg   the same cut-out on a neutral dark grey

Known data error on the Pick'em site (2026-11-12): Maris's entry carries Milo's photo, so Maris
uses his Liquipedia studio portrait instead (cropped to the same framing).

    pip install pillow numpy opencv-python-headless
    python scripts/fetch_photos_s18.py
"""
import io
import json
import os
import urllib.request

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "photos", "s18")
API = "https://api-ggtech.leagueoflegends.com/api/v2/public/showcase/tft-championship/pickem/enchanted-wilds"
UA = "S18TFTTierList/1.0 (fan tier-list site; github.com/eric0871/s17-tft-tier-list)"
# Pick'em display name -> our player id (names not listed map to themselves)
NAME2ID = {
    "SCG hexi": "Hexi", "SCG linshen": "Linshen", "Ace": "ACE", "TLG diaomei": "diaomei", "Cangshan": "CSFX",
    "YSG Hanxing": "Hanxing", "FW Iron Bog": "Iron_Bog", "ZETA title": "title", "FW AQ1H": "AQ1H",
    "ACAD Wasian": "wasianiverson", "FL Chunington": "Chunington", "FL Cambulee": "Cambulee", "FL wigwugg": "wigwugg",
    "ACAD Dishsoap": "Dishsoap", "MJS Deleted": "JosueDeleted", "TFTLAB ego": "ego", "FL Upsetmax": "Upsetmax",
    "Bopster": "bopster", "MIH ZyK0o": "ZyK0o", "MIH bensac": "bensac", "Whyyoumadpro": "whyyoumadpro",
    "Oskuu": "oskuu", "M8 L3S Coco": "L3SCoco",
}
# id -> (image url, crop box in that image) for players whose Pick'em photo is wrong
OVERRIDE = {
    "Maris": ("https://liquipedia.net/commons/images/b/b7/VP_Maris_at_ACL_2025.PNG", (367, 62, 857, 552)),
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://liquipedia.net/tft/"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def cutout(im):
    """Key out a flat background colour that touches the image border; returns RGBA."""
    a = np.array(im.convert("RGB")).astype(np.float32)
    h, w, _ = a.shape
    bg = np.median(np.concatenate([a[:, 0], a[:, -1], a[0, :]]), axis=0)
    dist = np.sqrt(((a - bg) ** 2).sum(2))
    n, lab = cv2.connectedComponents((dist < 70).astype(np.uint8), connectivity=4)
    border = set(np.unique(np.concatenate([lab[:, 0], lab[:, -1], lab[0, :]]))) - {0}
    region = np.isin(lab, list(border))
    core = dist < 20
    for k in range(1, n):  # pockets of background enclosed by an arm, hair, etc.
        if k not in border and ((lab == k) & core).sum() > 6:
            region |= lab == k
    grown = cv2.dilate(region.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    alpha = np.ones((h, w), np.float32)
    ramp = np.clip((dist - 28) / 42, 0, 1)
    alpha[grown] = ramp[grown]
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0.6)
    alpha[region & (dist < 28)] = 0
    al = alpha[..., None]
    rgb = np.clip(np.where(al > 0.02, (a - (1 - al) * bg) / np.maximum(al, 0.02), 0), 0, 255)
    # despill: near the cut, remove colour that leans toward the background hue
    band = cv2.dilate(region.astype(np.uint8), np.ones((13, 13), np.uint8)).astype(bool) & (alpha > 0.02)
    lum = (rgb * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
    bgn = (bg - bg.mean()) / (np.linalg.norm(bg - bg.mean()) + 1e-6)
    chroma = rgb - lum
    lean = np.clip((chroma * bgn).sum(2) / 60.0, 0, 1)[..., None]
    rgb = np.where(band[..., None], rgb - chroma * lean, rgb)
    if bg.min() > 230:  # white studio background: pull the light rim in by a pixel
        er = cv2.erode(alpha, np.ones((3, 3), np.uint8))
        alpha = np.minimum(alpha, cv2.GaussianBlur(er, (3, 3), 0.7))
        rim = (alpha > 0) & (alpha < 0.95)
        rgb[rim] *= 0.75
    return Image.fromarray(np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8), "RGBA")


def save(pid, rgba):
    rgba.save(os.path.join(OUT, pid + ".png"), optimize=True)
    flat = Image.new("RGBA", rgba.size, (24, 26, 29, 255))
    flat.alpha_composite(rgba)
    flat.convert("RGB").save(os.path.join(OUT, pid + ".jpg"), quality=90)


def main():
    os.makedirs(OUT, exist_ok=True)
    data = json.loads(get(API))
    people = [p for p in data["body"]["returnData"]["participants"] if p.get("region")]
    for p in people:
        pid = NAME2ID.get(p["name"], p["name"])
        if pid in OVERRIDE:
            continue
        img = p["image"]["url"] if isinstance(p["image"], dict) else p["image"]
        save(pid, cutout(Image.open(io.BytesIO(get(img)))))
        print("[pickem]", pid)
    for pid, (url, box) in OVERRIDE.items():
        try:  # Liquipedia rate-limits hard (HTTP 429); keep the existing file if it refuses
            im = Image.open(io.BytesIO(get(url))).convert("RGB").crop(box).resize((250, 250), Image.LANCZOS)
        except Exception as e:
            print(f"[skip ] {pid}: {e} (kept the existing photo)")
            continue
        save(pid, cutout(im))
        print("[override]", pid)
    print(f"\n{len(people)} players. Commit photos/s18/ and push; the site picks them up automatically.")


if __name__ == "__main__":
    main()
