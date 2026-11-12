"""Fully decode GanglyStats data/core.js (mirrors the JS unpacker at the bottom of core.js).

Usage: python3 gangly_decode.py <core.js> -> returns dict via load(); run as script to print summary.
"""
import json, sys

def load(path):
    lines = open(path, encoding='utf-8').read().split('\n')
    meta = json.loads(lines[2][len('window.TFT_META = '):].rstrip(';'))
    K = json.loads(lines[3][len('window.__TFT_PACK = '):].rstrip(';'))
    tids, dates, lobs, strs, keys = K['tids'], K['dates'], K.get('lobs'), K['strs'], K['keys']
    n = lambda s, i, w: int(s[i:i + w], 36)
    tours = []
    for t in K['tours']:
        o = {}
        for k, v in t.items():
            if k == '$fs':
                if v is None:
                    continue
                fs = []
                for r in v:
                    f = {}
                    for i, fk in enumerate(keys['fs']):
                        f[fk] = strs[r[i]] if fk in ('player', 'displayname', 'player_page', 'team', 'region') else r[i]
                    fs.append(f)
                o['final_standings'] = fs
            else:
                o[k] = v
        tours.append(o)
    players = {}
    for key, rec in K['players']:
        p = {}
        for k, v in rec.items():
            if k == '$g':
                gh = []
                for i in range(0, len(v), 12):
                    g = dict(tournament_id=tids[n(v, i, 2)], date=dates[n(v, i + 2, 2)], day=n(v, i + 4, 1),
                             game=n(v, i + 5, 2), placement=n(v, i + 7, 1), points=n(v, i + 8, 2))
                    l = n(v, i + 10, 2)
                    if l:
                        g['lobby'] = lobs[l]
                    gh.append(g)
                p['game_history'] = gh
            elif k == '$t':
                th = []
                for r in v:
                    d = K['thdef'][str(r[0])]
                    over = r[4] if len(r) > 4 and r[4] else {}
                    h = {'tournament_id': tids[r[0]]}
                    for i, dk in enumerate(keys['thd']):
                        h[dk] = over[dk] if dk in over else d[i]
                    h['placement'] = r[1]; h['total_points'] = r[2]
                    h['is_home_region'] = bool(r[3] & 1); h['is_cross_regional'] = bool(r[3] & 2)
                    th.append({tk: h.get(tk) for tk in keys['th']})
                p['tournament_history'] = th
            elif k.startswith('$s'):
                p[k[2:]] = {sk: v[i] for i, sk in enumerate(keys['st'])}
            else:
                p[k] = v
        players[key] = p
    return dict(meta=meta, tours=tours, players=players, keys=keys)

if __name__ == '__main__':
    D = load(sys.argv[1])
    print('keys', json.dumps(D['keys']))
    print('n tours', len(D['tours']), 'n players', len(D['players']))
    print('tour fields', sorted({k for t in D['tours'] for k in t}))
