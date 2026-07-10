import base64, os, glob, re

VAULT = r"C:\Users\ericc\OneDrive\文档\second_brain"
PHOTODIR = os.path.join(VAULT, "tft-crown-photos")
HTML = os.path.join(VAULT, "tft-crown-tier-list.html")

# build base64 data-URI map keyed by filename stem (== JS id())
entries = []
for fp in sorted(glob.glob(os.path.join(PHOTODIR, "*.jpg"))):
    stem = os.path.splitext(os.path.basename(fp))[0]
    with open(fp, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    entries.append('  "' + stem + '":"data:image/jpeg;base64,' + b64 + '"')
photos_js = "const PHOTOS = {\n" + ",\n".join(entries) + "\n};\n"
print(f"embedded {len(entries)} photos, ~{len(photos_js)//1024}KB base64")

html = open(HTML, "r", encoding="utf-8").read()

# 1) inject PHOTOS map right before the PLAYERS declaration (idempotent: strip old one first)
html = re.sub(r'const PHOTOS = \{.*?\n\};\n', '', html, flags=re.S)
marker = "// p:1 = has a downloaded Liquipedia portrait"
assert marker in html, "PLAYERS marker not found"
html = html.replace(marker, photos_js + marker, 1)

# 2) point the portrait src at the embedded data URI (fallback to file path if ever missing)
old_src = 'img.src = `tft-crown-photos/${id(p)}.jpg`;'
new_src = 'img.src = PHOTOS[id(p)] || `tft-crown-photos/${id(p)}.jpg`;'
if old_src in html:
    html = html.replace(old_src, new_src, 1)
elif new_src not in html:
    raise SystemExit("portrait src line not found")

open(HTML, "w", encoding="utf-8").write(html)
print(f"wrote self-contained HTML: {os.path.getsize(HTML)//1024}KB")
