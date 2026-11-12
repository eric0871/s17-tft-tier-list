import json,re,os
H=os.path.dirname(os.path.abspath(__file__))
D=json.load(open(os.path.join(H,'players.json')))
CNQ={'Baizhi':('端游国服决赛 冠军','TOC'),'ACE':('端游国服决赛 亚军','TOC'),'Rue':('端游国服决赛 季军','TOC'),'Myyz':('端游国服决赛 第4','TOC'),
'CSFX':('CN TPC 冠军',''),'HuiYuan':('金铲铲国服决赛 冠军','JOC'),'HangHang':('金铲铲国服决赛 亚军','JOC'),'Linshen':('金铲铲国服决赛 季军','JOC'),
'Hexi':('金铲铲国服决赛 第4','JOC'),'Hanxing':('CN Elderwood Cup 冠军',''),'diaomei':('CN 赛区代表','')}
CNNAME={'Baizhi':'白纸','Rue':'之忧参上','Myyz':'没有预兆','CSFX':'苍山','Linshen':'林神','Hexi':'鹤曦','Hanxing':'寒星','diaomei':'雕妹'}
TEAMS={'FL':'Final Lobby Gaming','ACAD':'Academy','TFTLAB':'TFTLAB','MJS':'Team Majoris','M8':'Gentle Mates','MIH':'Mihos eSport','FW':'Flash Wolves','VP':'Virtus.pro','ZETA':'ZETA DIVISION','SCG':'SCG','YSG':'YSG','TLG':'TLG','GLE':'GodLike Esports'}
SETN={3:'Galaxies',4:'Fates',5:'Reckoning',6:'Gizmos & Gadgets',7:'Dragonlands',8:'Monsters Attack!',9:'Runeterra Reforged',10:'Remix Rumble',11:'Inkborn Fables',12:"Magic n' Mayhem",13:'Into the Arcane',14:'Cyber City',15:'K.O. Coliseum',16:'Lore & Legends',17:'Space Gods'}
PH={'AQ1H','Cambulee','Dishsoap','Hanxing','Iron Bog','Jazlatte','Milo','Upsetmax','ZyK0o','title','wasianiverson'}
def zh(q):
    q=q.replace('Regional Finals','赛区决赛').replace(' Cup',' Cup')
    q=re.sub(r'^(AMER|EMEA|APAC) (Riftbeast|Elderwood|Blossom) Cup 冠军$',lambda m:f'{m.group(1)} {m.group(2)} Cup 冠军',q)
    return q
out=[]
for o in D:
    k=o['key']; q,tr=o['qual'],o['track']
    if k in CNQ: q,tr=CNQ[k]
    if k=='wigwugg': q='Elderwood Cup 冠军'
    q=zh(q)
    pid=re.sub(r'[^A-Za-z0-9]','_',k)
    out.append(dict(id=pid,n=o['name'],cn=CNNAME.get(k,''),t=o['team'],tf=TEAMS.get(o['team'],''),r=o['region'],c=o['iso'],tr=tr,q=q,
      ph=f'photos/s18/{pid}.jpg',gs=o['gid'],
      s=o['s18'],cr=o['career'],l20=[[g['p'],g['ev'],g['d']] for g in o['last20']],
      w=[[x['set'],x['place'],x['n'],SETN.get(x['set'],'')] for x in o['worlds']],ti=o['titles'],
      b=[[x['ev'],x['place']] for x in o['best']]))
json.dump(out,open(os.path.join(H,'site_players.json'),'w'),ensure_ascii=False,separators=(',',':'))
print(len(out), len(json.dumps(out,ensure_ascii=False)))
for x in out: print(x['n'],'|',x['q'],'|',x['tr'],'|',x['ph'])
