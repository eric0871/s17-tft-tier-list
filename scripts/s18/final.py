import json,re,os
H=os.path.dirname(os.path.abspath(__file__))
D=json.load(open(os.path.join(H,'players.json')))
CNQ={'Baizhi':('端游国服决赛 冠军','TOC'),'ACE':('端游国服决赛 亚军','TOC'),'Rue':('端游国服决赛 季军','TOC'),'Myyz':('端游国服决赛 第4','TOC'),
'CSFX':('端游 TPC 冠军','TOC'),'HuiYuan':('金铲铲国服决赛 冠军','JOC'),'HangHang':('金铲铲国服决赛 亚军','JOC'),'Linshen':('金铲铲国服决赛 季军','JOC'),
'Hexi':('金铲铲国服决赛 第4','JOC'),'Hanxing':('CN Elderwood Cup 冠军','JOC'),'diaomei':('金铲铲 TPC 冠军','JOC')}
CNNAME={'HangHang':'杭杭','Baizhi':'白纸','Rue':'之忧参上','Myyz':'没有预兆','CSFX':'苍山','Linshen':'林神','Hexi':'鹤曦','Hanxing':'寒星','diaomei':'雕妹'}
TEAMS={'FL':'Final Lobby Gaming','ACAD':'Academy','TFTLAB':'TFTLAB','MJS':'Team Majoris','M8':'Gentle Mates','MIH':'Mihos eSport','FW':'Flash Wolves','VP':'Virtus.pro','ZETA':'ZETA DIVISION','SCG':'SCG','YSG':'YSG','TLG':'TLG','GLE':'GodLike Esports'}
SETN={3:'Galaxies',4:'Fates',5:'Reckoning',6:'Gizmos & Gadgets',7:'Dragonlands',8:'Monsters Attack!',9:'Runeterra Reforged',10:'Remix Rumble',11:'Inkborn Fables',12:"Magic n' Mayhem",13:'Into the Arcane',14:'Cyber City',15:'K.O. Coliseum',16:'Lore & Legends',17:'Space Gods'}
PH={'AQ1H','Cambulee','Dishsoap','Hanxing','Iron Bog','Jazlatte','Milo','Upsetmax','ZyK0o','title','wasianiverson'}
def zh(q):
    q=q.replace('Regional Finals','赛区决赛').replace(' Cup',' Cup')
    q=re.sub(r'^(AMER|EMEA|APAC) (Riftbeast|Elderwood|Blossom) Cup 冠军$',lambda m:f'{m.group(1)} {m.group(2)} Cup 冠军',q)
    return q
X=json.load(open(os.path.join(H,'extra.json')))['players']
# GanglyStats misplaces bio (bio1uc) in Set 10 Worlds, shifting places 15-32 up by one; Liquipedia + Esports Earnings agree on these
WORLDS_FIX={('Dishsoap',10):21}
UNCOUNTED={'HuiYuan','HangHang'}  # JOC 2026 Fall finals prize not on Liquipedia yet (2026-11-12)
def extra(k,byname):
    x=X.get(re.sub(r'[^A-Za-z0-9]','_',k)) or X.get(k) or {}
    lp=x.get('liquipedia') or {}; gs=x.get('ganglystats') or {}
    e=[lp['total_winnings_usd'],lp['winnings_rank_of_40'],'秋季决赛奖金未计' if k in UNCOUNTED else ''] if lp.get('total_winnings_usd') else None
    wc=gs.get('worlds_career'); wa=[wc['gp'],wc['avp']] if wc else None
    r=(gs.get('most_met_crown_rivals') or [None])[0]
    rv=[byname.get(r['vs_id'],r['vs']),r['lobbies'],r['finished_above']] if r else None
    return e,wa,rv
out=[]
for o in D:
    k=o['key']; q,tr=o['qual'],o['track']
    if k in CNQ: q,tr=CNQ[k]
    if k=='wigwugg': q='EMEA Elderwood Cup 冠军'  # AMER player who took the EMEA slot of the joint AMER/EMEA cup
    q=zh(q)
    pid=re.sub(r'[^A-Za-z0-9]','_',k)
    out.append(dict(id=pid,n=o['name'],cn=CNNAME.get(k,''),t=o['team'],tf=TEAMS.get(o['team'],''),r=o['region'],c=o['iso'],tr=tr,q=q,
      ph=f'photos/s18/{pid}.jpg',gs=o['gid'],
      s=o['s18'],cr=o['career'],l20=[[g['p'],g['ev'],g['d']] for g in o['last20']],
      w=[[x['set'],x['place'],x['n'],SETN.get(x['set'],'')] for x in o['worlds']],ti=o['titles'],
      b=[[x['ev'],x['place']] for x in o['best']]))
    for w in out[-1]['w']:
        if (k,w[0]) in WORLDS_FIX: w[1]=WORLDS_FIX[(k,w[0])]
BYNAME={re.sub(r'[^A-Za-z0-9]','_',o['key']):o['name'] for o in D}
for o,p in zip(D,out):
    p['e'],p['wa'],p['rv']=extra(o['key'],BYNAME)
json.dump(out,open(os.path.join(H,'site_players.json'),'w'),ensure_ascii=False,separators=(',',':'))
print(len(out), len(json.dumps(out,ensure_ascii=False)))
for x in out: print(x['n'],'|',x['q'],'|',x['tr'],'|',x['ph'])
