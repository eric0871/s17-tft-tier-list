"""Fetch rendered infobox (section 0) of each player's Liquipedia page and extract fields.

Re-runnable: responses are cached in raw/liquipedia/cache/, so a second run makes no API calls.
Output: raw/liquipedia/players_infobox.json  {site_id: {...fields..., "lp_page":..., "url":...}}
Polite: action=parse spaced >=35 s apart (Liquipedia API terms ask >=30 s), 429 -> back off 60/120/... s.
"""
import html as H, json, os, re, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "raw", "liquipedia", "players_infobox.json")

# site id -> Liquipedia page (resolved via redirects with action=query on 2026-11-12)
PAGES = {
    "Broseph": "Broseph", "bopster": "BOPSTER", "Upsetmax": "Upsetmax", "ego": "Ego illusions",
    "JosueDeleted": "JosueDeleted", "Dishsoap": "Dishsoap", "wigwugg": "Wigwugg", "Cambulee": "Cambulee",
    "Chunington": "Chunington", "wasianiverson": "Wasianiverson", "L3SCoco": "L3SCoco", "Yakumo": "Yatora",
    "Cynarr": "Cynar", "oskuu": "Oskuu", "whyyoumadpro": "Whyyoumadpro", "bensac": "Bensac",
    "Skipaeus": "Skipaeus", "ZyK0o": "ZyK0o", "Jazlatte": "JazLatte", "AQ1H": "AlphaQi", "Milo": "Miloo",
    "pigpig": "Pigpig", "title": "Title", "Maris": "Maris", "iCeEmperoz": "ICeEmperoz", "Iron_Bog": "Iron Bog",
    "steppy": "Steppy", "WithoutYou": "CantWithoutYou", "seoill": "Seoill", "Baizhi": "Pale", "ACE": "Ace",
    "Rue": "Rue", "Myyz": "Myyz", "CSFX": "CangShan", "HuiYuan": "HuiYuan", "HangHang": "HangHang",
    "Linshen": None, "Hexi": "Hexi", "Hanxing": "HanXing", "diaomei": "Diaomei",
}


def text(s):
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = H.unescape(s).replace("\xa0", " ")
    return re.sub(r"[ \t]+", " ", s).strip()


def infobox_fields(html):
    """Return {label: value} for rows like <div class="infobox-cell-2 infobox-description">Label:</div><div ...>Value</div>"""
    out = {}
    for m in re.finditer(r'infobox-description">\s*(.*?)\s*</div>\s*<div[^>]*>(.*?)</div>\s*</div>', html, re.S):
        k = text(m.group(1)).rstrip(":").strip()
        v = text(m.group(2))
        if k and k not in out:
            out[k] = re.sub(r"\s*\n\s*", " / ", v).strip(" /")
    return out


def history(html):
    rows = []
    for m in re.finditer(r'<tr[^>]*>\s*<td[^>]*class="th-mono"[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*</tr>', html, re.S):
        rows.append([text(m.group(1)).replace("—", "-").replace(" - ", " ~ "), text(m.group(2))])
    if not rows:  # fallback: plain text after "History"
        t = text(html)
        i = t.find("History")
        if i >= 0:
            for d, team in re.findall(r"(\d{4}-[\d?]{2}-[\d?]{2} — (?:\d{4}-[\d?]{2}-[\d?]{2}|Present))\s+([^\d\n]+?)(?=\s+\d{4}-|\s*$|\s{2})", t[i:i + 2000]):
                rows.append([d.replace("—", "~"), team.strip()])
    return rows


def main():
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for sid, page in PAGES.items():
        if not page:
            res[sid] = {"lp_page": None, "note": "no Liquipedia player page (checked Linshen / LinShen / 林神 / Lin Shen)"}
            continue
        try:
            h = lp.parse_html(page, section=0)
        except Exception as e:
            print("[err ]", sid, page, e, flush=True)
            continue
        f = infobox_fields(h)
        f["history"] = history(h)
        f["lp_page"] = page
        f["url"] = "https://liquipedia.net/tft/" + urllib.parse.quote(page.replace(" ", "_"))
        res[sid] = f
        json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)
        print("[ok  ]", sid, page, f.get("Approx. Total Winnings"), f.get("Born"), flush=True)
    json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)
    print("done", len(res))


if __name__ == "__main__":
    main()
