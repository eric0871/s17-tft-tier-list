"""Compare our page's 晋级方式 (q / tr fields) with the official Riot list (competetft.com) and Liquipedia.

Sources:
 - Riot official: raw/competetft/qual_parsed.json (from competetft_qual.py) + event names resolved from each qualifierEsportsId page title
 - Liquipedia: raw/liquipedia/crown_qualification_wikitext.txt (Enchanted Wilds/Tacticians Crown/Qualification)
   + event pages for CN (JOC TPC / TOC TPC / TOC RF prize pools) in raw/liquipedia/event_wikitext.json
 - GanglyStats (for CN JOC RF order, source toc.qq.com)
Output: raw/qual_check.json
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "..", "raw")
SITE = {s["id"]: s for s in json.load(open(os.path.join(R, "site_players_from_index.json"), encoding="utf-8"))}
OFF = json.load(open(os.path.join(R, "competetft", "qual_parsed.json"), encoding="utf-8"))
EV = {  # competetft qualifierEsportsId -> event title (from <title> of competetft.com/en-US/tournament/<id>/overview, 2026-11-12)
    "116917714996825423": "Riftbeast Cup AMER", "116917726412134723": "Riftbeast Cup APAC", "116917732296294434": "Riftbeast Cup EMEA",
    "116917739410358414": "Elderwood Cup AMER Home Cup", "116917808055257065": "Elderwood Cup APAC Home Cup",
    "116917834277455889": "Elderwood Cup EMEA Home Cup", "116917848897620003": "Elderwood Cup CN Home Cup",
    "116917873644865592": "Blossom Cup AMER", "116917882326747206": "Blossom Cup APAC", "116917892270458972": "Blossom Cup EMEA",
    "116912912421782425": "Regional Finals AMER", "116912974691526392": "Regional Finals EMEA", "116912935942959610": "Regional Finals APAC",
}
OFF2SITE = {"ACAD wasian": "wasianiverson", "seoill": "seoill", "MIH ZyK0o": "ZyK0o", "WithoutYou": "WithoutYou", "YSG Hanxing": "Hanxing",
            "FL wigwugg": "wigwugg", "FL Chunington": "Chunington", "steppy": "steppy", "Skipaeus": "Skipaeus", "FL Cambulee": "Cambulee",
            "mih bensac": "bensac", "ACAD Dishsoap": "Dishsoap", "FW Iron Bog": "Iron_Bog", "Broseph": "Broseph", "bopster": "bopster",
            "FL Upsetmax": "Upsetmax", "TFTLAB ego": "ego", "MJS Deleted": "JosueDeleted", "M8 L3SCoco": "L3SCoco", "yakumo": "Yakumo",
            "Cynarr": "Cynarr", "oskuu": "oskuu", "whyyoumadpro": "whyyoumadpro", "ROC JazLatte": "Jazlatte", "FW AQ1H": "AQ1H",
            "Milo": "Milo", "pigpig": "pigpig", "ZETA title": "title", "Maris": "Maris", "iCeEmperoz": "iCeEmperoz"}
# Liquipedia qualification page (participant name -> note), plus regional-finals rank where given
lpq = open(os.path.join(R, "liquipedia", "crown_qualification_wikitext.txt"), encoding="utf-8").read()
LPNAME2SITE = {"wasian": "wasianiverson", "Iron Bog": "Iron_Bog", "Bensac": "bensac", "Steppy": "steppy", "baizhi": "Baizhi", "Ace": "ACE",
               "JazLatte": "Jazlatte"}
lp = {}
for sec in re.finditer(r"\{\{ParticipantSection\|title=(.*?)\|count=\d+(.*?)\n\}\}", lpq, re.S):
    title = re.sub(r"\{\{[^}]*\}\}\s*", "", sec.group(1)).strip()
    for m in re.finditer(r"\n\|([^|\n=]+?)\s*\|p(\d+)note=(\[\[[^\]]+\]\]|\{\{[^}]+\}\}|[^|\n]+)[ \t]*(\|p\d+dq=1)?", sec.group(2)):
        name, note, dq = m.group(1).strip(), re.sub(r"\[\[[^|\]]*\|([^\]]*)\]\]", r"\1", m.group(3)).strip(), bool(m.group(4))
        sid = LPNAME2SITE.get(name, name)
        if name == "TBD":
            continue
        lp.setdefault(sid, []).append(dict(section=title, note=note, slot_passed_down=dq))
rows = []
for o in OFF:
    sid = OFF2SITE[o["trDisplayName"]]
    if o["qualifierType"] == "PRO_POINTS":
        ev = "Pro Points " + {"NA1": "AMER", "EUW1": "EMEA", "TW2": "APAC"}[o["shard"]] + " 第一"
    else:
        ev = EV[o["qualifierEsportsId"]]
    rows.append(dict(id=sid, official=ev))
seen = {r["id"] for r in rows}
CN_OFFICIAL = {  # CN slots are run by Tencent; Riot's page doesn't list them. Evidence = Liquipedia event pages (+ GanglyStats/toc.qq.com order)
    "CSFX": "TOC TPC 冠军（LP: Enchanted Wilds/TFT Pro Circuit/CN/TOC 第1，¥100,000，qualified1=Crown）",
    "diaomei": "JOC TPC 冠军（LP: Enchanted Wilds/TFT Pro Circuit/CN/JOC 第1，¥100,000，qualified1=Crown；赛期 2026-09-04~13）",
    "Baizhi": "TOC 2026 秋季赛区决赛 第1（LP prize pool）", "ACE": "TOC 2026 秋季赛区决赛 第2（LP prize pool）",
    "Rue": "TOC 2026 秋季赛区决赛 第3（LP prize pool）", "Myyz": "TOC 2026 秋季赛区决赛 第4（LP prize pool）",
    "HuiYuan": "JOC 2026 秋季赛区决赛 前4（LP 名单在列；名次 LP 未录，GanglyStats/toc.qq.com 记第1）",
    "HangHang": "JOC 2026 秋季赛区决赛 前4（LP 名单在列；GanglyStats 记第2）",
    "Linshen": "JOC 2026 秋季赛区决赛 前4（LP 名单在列；GanglyStats 记第3）",
    "Hexi": "JOC 2026 秋季赛区决赛 前4（LP 名单在列；GanglyStats 记第4）",
}
for sid, txt in CN_OFFICIAL.items():
    rows.append(dict(id=sid, official=txt))
out = []
for r in rows:
    s = SITE[r["id"]]
    out.append(dict(id=r["id"], site_q=s["q"], site_tr=s["tr"], official_or_best=r["official"], liquipedia=lp.get(r["id"], [])))
json.dump(out, open(os.path.join(R, "qual_check.json"), "w"), ensure_ascii=False, indent=1)
for x in out:
    print(f"{x['id']:14s} | site: {x['site_q']:22s} {x['site_tr']:3s} | official: {x['official_or_best']:40s} | LP: {[(l['section'][:28], l['note'], 'deferred' if l['slot_passed_down'] else '') for l in x['liquipedia']]}")
print(len(out))
