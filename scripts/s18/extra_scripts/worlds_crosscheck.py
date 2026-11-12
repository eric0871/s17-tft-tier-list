"""Cross-check GanglyStats Worlds placements of the 40 players against Liquipedia prize-pool order.

Liquipedia: each Worlds page's {{SoloPrizePool}} lists one {{Slot}} per placement, in order (1st, 2nd, ...).
Usage: python3 -I worlds_crosscheck.py  (reads raw/, prints mismatches, writes raw/worlds_crosscheck.json)
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gangly_decode as G
from aliases import aliases_for

R = os.path.join(HERE, "..", "raw")
D = G.load(os.path.join(R, "gangly", "core.js"))
W = json.load(open(os.path.join(R, "liquipedia", "worlds_wikitext.json"), encoding="utf-8"))
SITE = json.load(open(os.path.join(R, "site_players_from_index.json"), encoding="utf-8"))
# LP page title <-> GanglyStats tournament id
LP2GS = {"Space Gods/Tacticians Crown": "Space Gods/Tacticians Crown", "Lore & Legends/Tacticians Crown": "Lore_&_Legends/Tacticians_Crown",
         "K.O. Coliseum/Tacticians Crown": "K.O._Coliseum/Tacticians_Crown", "Cyber City/Tacticians Crown": "Cyber_City/Tacticians_Crown",
         "Into the Arcane/Tacticians Crown": "Into_the_Arcane/Tacticians_Crown", "Magic n' Mayhem/Tacticians Crown": "Magic_n'_Mayhem/Tacticians_Crown",
         "Inkborn Fables/Tacticians Crown": "Inkborn_Fables/Tacticians_Crown"}
for t in ["Remix Rumble", "Runeterra Reforged", "Monsters Attack!", "Dragonlands", "Gizmos & Gadgets", "Reckoning", "Fates", "Galaxies"]:
    LP2GS[t + "/Championship"] = t + "/Championship"


def lp_order(wt):
    i = wt.find("SoloPrizePool")
    if i < 0:
        return []
    depth, j = 0, wt.rfind("{{", 0, i)
    k = j
    while k < len(wt):  # find matching }} of the SoloPrizePool template
        if wt.startswith("{{", k): depth += 1; k += 2; continue
        if wt.startswith("}}", k):
            depth -= 1; k += 2
            if depth == 0: break
            continue
        k += 1
    body = re.sub(r"<!--.*?-->", "", wt[j:k], flags=re.S)
    names = []
    for m in re.finditer(r"\{\{Slot\|(.*?)\}\}\}\}", body, re.S):
        nm = re.findall(r"\{\{(?:Solo|1)Opponent\|(?:flag=\w+\|)?([^|}]+)", m.group(1))
        names.append(nm[0].strip() if nm else None)
    return names


res = []
for lp_title, (resolved, wt) in W.items():
    order = lp_order(wt or "")
    gid = LP2GS[lp_title]
    tour = next(t for t in D["tours"] if t["id"] == gid)
    for sp in SITE:
        key = sp["gs"]
        p = next((q for q in D["players"].values() if q["id"] == key), None)
        if not p:
            continue
        gs_place = next((h["placement"] for h in p["tournament_history"] if h["tournament_id"] == gid), None)
        al = aliases_for(sp["id"], p)
        lp_place = next((i + 1 for i, n in enumerate(order) if n and n.lower().replace(" ", "") in al), None)
        if gs_place is None and lp_place is None:
            continue
        res.append(dict(id=sp["id"], set=tour["set"], event=lp_title, gs=gs_place, lp=lp_place, n=len(order)))
json.dump(res, open(os.path.join(R, "worlds_crosscheck.json"), "w"), ensure_ascii=False, indent=1)
for r in res:
    flag = "" if r["gs"] == r["lp"] else "   <-- MISMATCH"
    print(f"{r['id']:14s} S{r['set']:<3} GS={r['gs']} LP={r['lp']} (LP slots {r['n']}){flag}")
print(len(res), "player-worlds checked;", sum(r['gs'] != r['lp'] for r in res), "mismatches")
