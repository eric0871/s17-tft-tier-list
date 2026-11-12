"""Compute GanglyStats-derived candidate fields for the 40 Crown players (no ratings: Eric doesn't want them).

Usage: python3 -I gangly_extras.py   (reads raw/gangly/*.js + raw/site_players_from_index.json, writes raw/gangly_extras.json)
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gangly_decode as G

R = os.path.join(HERE, "..", "raw")
D = G.load(os.path.join(R, "gangly", "core.js"))
T = {t["id"]: t for t in D["tours"]}
P = {p["id"]: p for p in D["players"].values()}
S = json.load(open(os.path.join(R, "site_players_from_index.json"), encoding="utf-8"))
js = lambda f, pre: json.loads(open(os.path.join(R, "gangly", f), encoding="utf-8").read().split("\n")[1][len(pre):].rstrip(";"))
H2H = js("h2h.js", "window.TFT_H2H = ")
RAT = js("ratings.js", "window.TFT_RATINGS = ")
gs2site = {s["gs"]: s for s in S}


def ordered(gh):  # same order as GanglyStats' tftGamesInOrder (set, event start, event id, day, game)
    g = [x for x in gh if x["placement"]]
    return sorted(g, key=lambda x: (int(T.get(x["tournament_id"], {}).get("set") or 0), str(T.get(x["tournament_id"], {}).get("date_start") or ""),
                                    x["tournament_id"], x["day"] or 0, x["game"] or 0))


def streak(gs, ok):
    best = cur = st = 0; span = (None, None)
    for i, g in enumerate(gs):
        if ok(g["placement"]):
            if not cur: st = i
            cur += 1
            if cur > best: best, span = cur, (st, i)
        else:
            cur = 0
    if not best:
        return dict(best=0, current=cur)
    a, b = T[gs[span[0]]["tournament_id"]], T[gs[span[1]]["tournament_id"]]
    return dict(best=best, current=cur, from_event=a["name"], to_event=b["name"], from_date=gs[span[0]]["date"], to_date=gs[span[1]]["date"])


out = {}
for s in S:
    p = P[s["gs"]]
    gh = p["game_history"]
    t1 = ordered([g for g in gh if str(T.get(g["tournament_id"], {}).get("tier")) == "1"])
    allg = ordered(gh)
    e = {}
    # 1. Worlds-only career stats (GanglyStats global_stats = games at World Championships / Tactician's Crowns)
    gl = p["global_stats"]
    e["worlds_stats"] = None if not gl["gp"] else dict(gp=gl["gp"], avp=gl["avp"], top4=gl["top4_rate"], win=gl["top1_rate"])
    # 2. streaks in Tier 1 games (GanglyStats player-page definition), with site-record context
    if len(t1) >= 20:
        st = {}
        for k, f in [("top4", lambda x: x <= 4), ("win", lambda x: x == 1), ("no8", lambda x: x != 8)]:
            v = streak(t1, f)
            rec = RAT["records"][k]
            v["site_record"] = rec[0][1]; v["site_record_holder"] = rec[0][0]
            v["site_top10_rank"] = next((i + 1 for i, r in enumerate(rec) if r[0] == p["id"]), None)
            st[k] = v
        e["streaks_tier1"] = st
    else:
        e["streaks_tier1"] = None
    e["tier1_games"] = len(t1)
    # 3. head-to-head vs the other 39 Crown players (same-region lobbies only; GanglyStats h2h.js, Tier 1, min 12 shared lobbies)
    m = H2H["matchups"].get(p["id"])
    if m:
        opp = [dict(vs=gs2site[o]["n"], vs_id=gs2site[o]["id"], lobbies=n, finished_above=ab, avp_with=w, avp_without=wo)
               for o, n, ab, w, wo in m["opp"] if o in gs2site]
        e["h2h_vs_crown_field"] = opp[:3]
    else:
        e["h2h_vs_crown_field"] = None
    # 4. career span in the GanglyStats database
    th = [h for h in p["tournament_history"] if h["date"] and not str(h["date"]).startswith("0000")]
    th.sort(key=lambda h: h["date"])
    sets = sorted({int(T[h["tournament_id"]]["set"]) for h in th if T.get(h["tournament_id"], {}).get("set")})
    e["first_event"] = dict(date=th[0]["date"], name=th[0]["tournament_name"], set=int(T[th[0]["tournament_id"]]["set"])) if th else None
    e["sets_played"] = len(sets); e["events_played"] = len(th)
    # 5. placement mix, career (all events)
    c = [0] * 8
    for g in allg:
        c[min(8, g["placement"]) - 1] += 1
    e["placement_mix_career"] = c
    # 6. best set by AVP (min 20 games)
    by = {}
    for g in allg:
        by.setdefault(int(T[g["tournament_id"]]["set"]), []).append(g["placement"])
    best = sorted([(round(sum(v) / len(v), 2), k, len(v)) for k, v in by.items() if len(v) >= 20])
    e["best_set"] = dict(set=best[0][1], avp=best[0][0], gp=best[0][2]) if best else None
    # 7. raw identity fields
    e["gs_flag"] = p.get("flag"); e["gs_server"] = p.get("server"); e["gs_names_seen"] = p.get("names_seen")
    e["source"] = "https://ganglystats.com/player.html?id=" + p["id"]
    out[s["id"]] = e
json.dump(out, open(os.path.join(R, "gangly_extras.json"), "w"), ensure_ascii=False, indent=1)
for k, e in out.items():
    st = e["streaks_tier1"] or {}
    print(f"{k:14s} worlds={e['worlds_stats'] and (e['worlds_stats']['gp'], e['worlds_stats']['avp'])} "
          f"top4streak={st.get('top4', {}).get('best')} no8={st.get('no8', {}).get('best')} win={st.get('win', {}).get('best')} "
          f"first={e['first_event'] and e['first_event']['date']} sets={e['sets_played']} h2h={[(x['vs'], x['lobbies'], x['finished_above']) for x in (e['h2h_vs_crown_field'] or [])]}")
