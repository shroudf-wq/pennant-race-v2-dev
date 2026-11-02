# v1 → v2 の「同じ乱数で結果が一致」の確認(同期手順の 4)。v1 の tests_v11w/par_n.py を写したもの。
# python3 par_v2.py <v1のURL> <v2のURL>   … 4通り(スキルあり/なし相当・アメリカ式・特色の上乗せ)で2年回して順位表が一致するか
#   v2.1.g:5通りめ。初期の設定(銀河杯・世界大会あり)で4年(2年目の開幕前に世界大会、4年目に銀河杯。h.py の SEASON が大会を自動で進める)
import sys
from h import *
ST="()=>league.map(t=>[t.name,t.w,t.l,t.t||0])"
VER="()=>[typeof APP_VERSION!=='undefined'?APP_VERSION:null, typeof BASE_V1!=='undefined'?BASE_V1:null, (document.getElementById('settingsVersion')||{}).textContent]"
with sync_playwright() as p:
    br=p.chromium.launch()
    for sel in [{"numTeams":"6","importSel":"off","traitSel":"off"},{"numTeams":"10","leagueFormat":"twodiv","importSel":"off","traitSel":"off"},{"numTeams":"6","rulesSel":"us","importSel":"off","traitSel":"off"},{"numTeams":"6","importSel":"off","archSel":"on","traitSel":"off"},{"numTeams":"6","importSel":"off","traitSel":"off","_years":4}]:
        res=[]; ny=sel.pop("_years",2)
        for u in sys.argv[1:3]:
            pg=open_page(br,u,seed=21); ver=pg.evaluate(VER); create(pg,sel); o=[]
            for y in range(ny): pg.evaluate(SEASON); o.append(pg.evaluate(ST)); pg.evaluate(OFF)
            res.append((o,pg.errs,ver)); pg.context.close()
        print(sel,"一致" if res[0][0]==res[1][0] else "不一致","errs",res[0][1][:2],res[1][1][:2],"ver",res[0][2],res[1][2],flush=True)
