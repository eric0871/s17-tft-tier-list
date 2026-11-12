import json,sys,os
H=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,H)
import subset_fonts
subset_fonts.main()  # 先按页面用到的字重新子集化中文字体（fonts/smiley-sub.woff2）
t=open(os.path.join(H,'template.html')).read()
P=open(os.path.join(H,'site_players.json')).read()
t=t.replace('__PLAYERS__',P).replace('__META__',json.dumps({"updated":"2026-11-11"}))
open(sys.argv[1],'w').write(t)
print(len(t))
