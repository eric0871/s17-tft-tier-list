"""Merge everything into /home/user/designs/data/extra.json (key = page player id).

Inputs (all produced by the other scripts in this folder, re-runnable):
  raw/liquipedia/players_infobox.json   <- lp_fetch_players.py  (rendered Liquipedia infobox: winnings, born, team history...)
  raw/liquipedia/player_wikitext.json   <- lp.wikitext()        (local IDs, nicknames from the page source)
  raw/gangly_extras.json                <- gangly_extras.py     (Worlds-only stats, streaks, head-to-head vs the field)
  raw/qual_check.json                   <- qual_check.py        (official / Liquipedia qualification path vs our q)
  raw/worlds_crosscheck.json            <- worlds_crosscheck.py (GanglyStats vs Liquipedia Worlds placements)
Run: python3 -I build_extra.py
"""
import datetime as dt, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "..", "raw")
OUT = os.path.join(HERE, "..", "extra.json")
J = lambda *p: json.load(open(os.path.join(R, *p), encoding="utf-8"))
SITE = J("site_players_from_index.json")
LP = J("liquipedia", "players_infobox.json")
WT = J("liquipedia", "player_wikitext.json")
GX = J("gangly_extras.json")
QC = {x["id"]: x for x in J("qual_check.json")}
WX = J("worlds_crosscheck.json")
CROWN_DAY1 = dt.date(2026, 11, 13)
WT_KEY = {"Broseph": "Broseph", "bopster": "Bopster", "Upsetmax": "Upsetmax", "ego": "Ego", "JosueDeleted": "JosueDeleted", "Dishsoap": "Dishsoap",
          "wigwugg": "Wigwugg", "Cambulee": "Cambulee", "Chunington": "Chunington", "wasianiverson": "Wasianiverson", "L3SCoco": "L3SCoco",
          "Yakumo": "Yakumo", "Cynarr": "Cynarr", "oskuu": "Oskuu", "whyyoumadpro": "Whyyoumadpro", "bensac": "Bensac", "Skipaeus": "Skipaeus",
          "ZyK0o": "ZyK0o", "Jazlatte": "JazLatte", "AQ1H": "AQ1H", "Milo": "Milo", "pigpig": "Pigpig", "title": "Title", "Maris": "Maris",
          "iCeEmperoz": "ICeEmperoz", "Iron_Bog": "Iron Bog", "steppy": "Steppy", "WithoutYou": "WithoutYou", "seoill": "Seoill", "Baizhi": "Baizhi",
          "ACE": "Ace", "Rue": "Rue", "Myyz": "Myyz", "CSFX": "CSFX", "HuiYuan": "HuiYuan", "HangHang": "HangHang", "Linshen": "Linshen",
          "Hexi": "Hexi", "Hanxing": "HanXing", "diaomei": "Diaomei"}
MONTHS = {m: i + 1 for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])}
# Suggested corrections to the page's q / tr / c fields (evidence in REPORT.md)
FIX = {
    "diaomei": dict(q="JOC TPC 冠军", tr="JOC", why="Liquipedia: 赢下 Enchanted Wilds TPC CN JOC（金铲铲 TPC，2026-09-04~13）拿世界赛名额；页面原写「CN 赛区代表」"),
    "wigwugg": dict(q="EMEA Elderwood Cup 冠军", why="Riot 官方名单：Elderwood Cup EMEA Home Cup（这届 Elderwood Cup 是美洲和欧洲合打，他拿的是 EMEA 那一侧的名额）"),
    "CSFX": dict(q="端游 TPC 冠军", tr="TOC", why="Liquipedia: TPC CN TOC（端游 TPC）第1；原写「CN TPC 冠军」不算错，只是不够具体"),
    "Hanxing": dict(tr="JOC", optional=True, why="晋级方式没错；但他打的是金铲铲赛道（Liquipedia: 金铲铲 TPC 第9-12；GanglyStats: 金铲铲国服决赛第52），标签可考虑补 JOC，Eric 定"),
}
NOTES = {
    "bopster": "国籍：Liquipedia 选手页写美国（2024-10 建页时就这么写，无出处），但 Liquipedia 两个赛事页（Set 14 美洲金铲铲冠军赛、Set 16 美洲赛区决赛）手动标了加拿大；GanglyStats 也是加拿大。没有一手来源，倾向保持加拿大",
    "Dishsoap": "Set 10 世界赛应为第 21（Liquipedia 奖金表第 21 格 $5,000；Esports Earnings 也记 21st）。GanglyStats 记 20 是因为它把 bio（bio1uc，实际第 14）排到了第 32，后面的人整体前移一位",
    "Hexi": "中文 ID 不一致：页面用「鹤曦」（GanglyStats，来源 toc.qq.com 赛事数据），Liquipedia 写「云鹤追」（真名 郑惟）。可能改过名，Eric 定用哪个",
    "Linshen": "Liquipedia 没有他的选手页（Linshen / LinShen / 林神 / Lin Shen 都试过），所以没有奖金等数据",
    "HuiYuan": "累计奖金偏低：JOC 2026 秋季赛区决赛（冠军 ¥1,000,000）的奖金 Liquipedia 截至 2026-11-12 还没录",
    "HangHang": "累计奖金偏低：JOC 2026 秋季赛区决赛（亚军 ¥400,000）的奖金 Liquipedia 还没录",
    "ACE": "GanglyStats 的国籍字段写的是 Vietnam（错），Liquipedia 是中国、真名 黄华泰；页面用的 cn 没问题",
}
NOTES["Linshen"] += "；JOC 2026 秋季赛区决赛（季军 ¥100,000）奖金也还没录"
NOTES["Hexi"] += "；累计奖金：Liquipedia 信息框没有奖金行（JOC 2026 秋季赛区决赛第 4 ¥60,000 还没录）"


def lp_born(s):
    if not s:
        return None, None
    m = re.match(r"([A-Z][a-z]+) (\d{1,2}), (\d{4})", s)
    if m:
        d = dt.date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))
        age = CROWN_DAY1.year - d.year - ((CROWN_DAY1.month, CROWN_DAY1.day) < (d.month, d.day))
        return d.isoformat(), age
    m = re.match(r"(\d{4})", s)
    return (m.group(1), None) if m else (None, None)


def money(s):
    m = re.search(r"\$([\d,]+)", s or "")
    return int(m.group(1).replace(",", "")) if m else None


def wt_field(wt, k):
    m = re.search(r"\n\|" + k + r"=([^\n]*)", wt or "")
    v = re.sub(r"<!--.*?-->", "", m.group(1)).strip() if m else ""
    return v.replace("<br>", " / ") or None


out = {}
for s in SITE:
    sid = s["id"]
    lp, gx = LP.get(sid, {}), GX[sid]
    wt = (WT.get(WT_KEY[sid]) or [None, None])[1]
    born, age = lp_born(lp.get("Born"))
    e = dict(name=s["n"])
    e["liquipedia"] = dict(
        page=lp.get("lp_page"), url=lp.get("url"),
        total_winnings_usd=money(lp.get("Approx. Total Winnings")), total_winnings_text=lp.get("Approx. Total Winnings"),
        nationality=lp.get("Nationality"), born=born, age_on_crown_day1=age, real_name=lp.get("Name"),
        local_id=wt_field(wt, "localid"), nicknames=wt_field(wt, "nicknames") or lp.get("Nickname(s)") or lp.get("Nicknames"),
        alternate_ids=lp.get("Alternate IDs"), team_now=lp.get("Team"), team_history=lp.get("history") or [],
        years_active=lp.get("Years Active") or lp.get("Years Active (Player)"), status=lp.get("Status"),
        note=lp.get("note"))
    e["ganglystats"] = dict(source=gx["source"], worlds_career=gx["worlds_stats"], streaks_tier1=gx["streaks_tier1"],
                            most_met_crown_rivals=gx["h2h_vs_crown_field"], best_set=gx["best_set"], placement_mix_career=gx["placement_mix_career"],
                            flag=gx["gs_flag"])
    q = QC[sid]
    e["qualification"] = dict(page_q=s["q"], page_track=s["tr"], official_or_best=q["official_or_best"], liquipedia=q["liquipedia"],
                              suggested_fix=FIX.get(sid),
                              double_qualified=any(l["slot_passed_down"] for l in q["liquipedia"]))
    e["worlds_check"] = [dict(set=w["set"], ganglystats=w["gs"], liquipedia=w["lp"]) for w in WX if w["id"] == sid and w["gs"] != w["lp"]]
    e["notes"] = NOTES.get(sid)
    out[sid] = e
# rank of winnings among the 40
vals = sorted([v["liquipedia"]["total_winnings_usd"] for v in out.values() if v["liquipedia"]["total_winnings_usd"] is not None], reverse=True)
for v in out.values():
    w = v["liquipedia"]["total_winnings_usd"]
    v["liquipedia"]["winnings_rank_of_40"] = vals.index(w) + 1 if w is not None else None
meta = dict(generated=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            sources=["https://liquipedia.net/tft/ (API: action=parse section 0 + action=query wikitext)",
                     "https://ganglystats.com/data/core.js, h2h.js, ratings.js (records only)",
                     "https://competetft.com/en-US/tournament/116918001686340951/qualification"],
            notes="total_winnings = Liquipedia 'Approx. Total Winnings' (USD, prize money Liquipedia has recorded; CN events converted from CNY). "
                  "JOC 2026 Fall Regional Finals prizes were not on Liquipedia yet on 2026-11-12, so HuiYuan/HangHang/Linshen/Hexi are undercounted.")
json.dump(dict(_meta=meta, players=out), open(OUT, "w"), ensure_ascii=False, indent=1)
print("wrote", OUT)
for k, v in sorted(out.items(), key=lambda kv: -(kv[1]["liquipedia"]["total_winnings_usd"] or -1)):
    l = v["liquipedia"]
    print(f"{k:14s} {l['total_winnings_text'] or '-':>10s} #{l['winnings_rank_of_40']} born={l['born']} age={l['age_on_crown_day1']} name={l['real_name']} team={l['team_now']} hist={len(l['team_history'])} local={l['local_id']} nick={l['nicknames']}")
