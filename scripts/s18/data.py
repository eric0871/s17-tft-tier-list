import json,sys
core=sys.argv[1]
s=open(core).read().split('\n')
K=json.loads(s[3][len('window.__TFT_PACK = '):].rstrip(';'))
tids=K['tids'];dates=K['dates'];tours={t['id']:t for t in K['tours']}
P={pr[0]:pr[1] for pr in K['players']}
def n(x,i,w): return int(x[i:i+w],36)
# key, display, team tag, region, iso, cn alias
R=[('Broseph','Broseph','GLE','AMER','ca',''),('bopster','bopster','','AMER','ca',''),('Upsetmax','Upsetmax','FL','AMER','ca',''),
('ego','ego','TFTLAB','AMER','br',''),('JosueDeleted','Deleted','MJS','AMER','pe',''),('Dishsoap','Dishsoap','ACAD','AMER','us',''),
('wigwugg','wigwugg','FL','AMER','ca',''),('Cambulee','Cambulee','FL','AMER','us',''),('Chunington','Chunington','FL','AMER','us',''),
('wasianiverson','wasianiverson','ACAD','AMER','ca',''),
('L3SCoco','L3S Coco','M8','EMEA','fr',''),('Yakumo','Yakumo','','EMEA','kg',''),('Cynarr','Cynarr','','EMEA','tr',''),('oskuu','oskuu','','EMEA','fi',''),
('whyyoumadpro','whyyoumadpro','','EMEA','de',''),('bensac','Bensac','MIH','EMEA','fr',''),('Skipaeus','Skipaeus','','EMEA','cz',''),('ZyK0o','ZyK0o','MIH','EMEA','fr',''),
('Jazlatte','JazLatte','','APAC','tw',''),('AQ1H','AQ1H','FW','APAC','hk',''),('Milo','Milo','VP','APAC','vn',''),('pigpig','pigpig','','APAC','tw',''),
('title','title','ZETA','APAC','jp',''),('Maris','Maris','VP','APAC','vn',''),('iCeEmperoz','iCeEmperoz','','APAC','vn',''),('Iron Bog','Iron Bog','FW','APAC','hk',''),
('steppy','steppy','','APAC','sg',''),('WithoutYou','WithoutYou','','APAC','tw',''),('seoill','seoill','','APAC','kr',''),
('Baizhi','Baizhi','','CN','cn','白纸'),('ACE','Ace','','CN','cn',''),('Rue','Rue','','CN','cn',''),('Myyz','Myyz','','CN','cn',''),
('CSFX','Cangshan','','CN','cn','苍山'),('HuiYuan','HuiYuan','','CN','cn',''),('HangHang','HangHang','','CN','cn',''),
('Linshen','linshen','SCG','CN','cn',''),('Hexi','hexi','SCG','CN','cn',''),('Hanxing','Hanxing','YSG','CN','cn','寒星'),('diaomei','diaomei','TLG','CN','cn','雕妹')]
PROPTS={'Dishsoap':'AMER 积分第一','bensac':'EMEA 积分第一','Iron Bog':'APAC 积分第一'}
WORLD_SETNAME={}
out=[]
for key,disp,team,reg,iso,cn in R:
  p=P[key]; g=p.get('$g','')
  games=[]
  for i in range(0,len(g),12):
    tid=tids[n(g,i,2)]; t=tours.get(tid,{})
    games.append(dict(t=tid,d=dates[n(g,i+2,2)],day=n(g,i+4,1),gm=n(g,i+5,2),p=n(g,i+7,1),set=t.get('set'),ev=t.get('short_name') or t.get('name')))
  games.sort(key=lambda x:(x['d'],x['t'],x['day'],x['gm']))
  def st(L):
    pl=[x['p'] for x in L]
    if not pl: return None
    return dict(gp=len(pl),avp=round(sum(pl)/len(pl),2),top4=round(sum(q<=4 for q in pl)/len(pl),3),win=round(sum(q==1 for q in pl)/len(pl),3),eighth=round(sum(q==8 for q in pl)/len(pl),3))
  th=[]
  for r in p.get('$t',[]):
    tid=tids[r[0]]; t=tours.get(tid,{})
    th.append(dict(id=tid,name=t.get('name'),short=t.get('short_name'),series=t.get('series'),set=t.get('set'),tier=t.get('tier'),reg=t.get('tournament_region'),place=r[1],n=t.get('num_players'),date=t.get('date_start')))
  worlds=sorted([dict(set=x['set'],series=x['series'],place=x['place'],n=x['n']) for x in th if x['reg']=='GLOBAL' and ('Championship' in x['name'] or 'Crown' in x['name'])],key=lambda w:w['set'])
  s18=[x for x in th if x['set']==18]
  cups=[x for x in s18 if x['place']==1 and ('Cup' in (x['name'] or '') or 'Pro Circuit' in (x['name'] or ''))]
  rf=[x for x in s18 if 'Regional Finals' in (x['name'] or '') or 'National Finals' in (x['name'] or '')]
  if key in PROPTS: q=PROPTS[key]
  elif cups:
    c=cups[0]; nm=c['name'].split(' - ')[-1] if ' - ' in c['name'] else c['short']; q=nm.replace('TFT Pro Circuit','TPC')+' 冠军'
  elif rf:
    r0=sorted(rf,key=lambda x:x['place'])[0]; q=(r0['short'] or r0['name'])+f" 第{r0['place']}"
  else: q=''
  track='JOC' if any('JOC' in (x['name'] or '') for x in s18) else ('TOC' if reg=='CN' else '')
  best=sorted([x for x in s18 if x['tier']=='1'],key=lambda x:x['place'])[:3]
  out.append(dict(key=key,name=disp,team=team,region=reg,iso=iso,cn=cn,track=track,qual=q,
    s18=st([x for x in games if x['set']==18]),career=st(games),
    last20=[dict(p=x['p'],ev=x['ev'],d=x['d']) for x in games[-20:]],
    worlds=worlds,titles=sum(1 for x in th if x['place']==1 and x['tier'] in ('0','1')),
    best=[dict(ev=x['name'].replace('Enchanted Wilds: ','').replace('TFT Pro Circuit - ','TPC '),place=x['place']) for x in best],
    gid=p.get('id'),names=p.get('names_seen'),
    s18ev=[dict(name=x['name'],short=x['short'],place=x['place'],n=x['n'],date=x['date'],end=tours.get(x['id'],{}).get('date_end')) for x in s18 if x['tier']=='1']))
# ranks among 40
for k,rev in [('avp',False),('top4',True),('win',True),('eighth',False)]:  # eighth: lower is better
  vals=sorted([o['s18'][k] for o in out if o['s18']],reverse=rev)
  for o in out: o['s18']['r_'+k]=vals.index(o['s18'][k])+1
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False)
for o in out: print(f"{o['name']:14s}{o['region']} {o['track']:3s} q={o['qual']:28s} worlds={[(w['set'],w['place']) for w in o['worlds']]} titles={o['titles']} names={o['names'][:4]}")
