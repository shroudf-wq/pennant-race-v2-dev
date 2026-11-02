# 球場の個性の見本(v2.0.f):新しいリーグ(球場の個性:あり)を作り、自チームの試合の観戦で、同じ場面を球場の型ごとに撮る
#   python3 hl3_park.py <URL> <出力フォルダ> [幅]
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h import *
URL, OUT = sys.argv[1], sys.argv[2]; W=int(sys.argv[3]) if len(sys.argv)>3 else 390
os.makedirs(OUT, exist_ok=True)
VAR=[("狭い・天然芝",0,False,False),("標準・天然芝",1,False,False),("広い・天然芝",2,False,False),("狭い・人工芝",0,True,False),("標準・人工芝・屋根",1,True,True),("広い・人工芝・屋根",2,True,True)]
with sync_playwright() as p:
    br=p.chromium.launch(); pg=open_page(br,URL,seed=31,w=W,h=844 if W<700 else 700,extra="localStorage.setItem('pennantHl3d','on');")
    errs=pg.errs; pg.on("console",lambda m: errs.append("CONSOLE:"+m.text) if m.type=="error" and "ERR_" not in m.text else None)
    create(pg,{"numTeams":"6"})
    info=pg.evaluate("""()=>{ for(let i=0;i<40;i++) simScheduledGame();
      return {park:parkEnabled, teams:league.map(t=>[t.name, t.park? t.park.s : null, t.park? t.park.turf : null, JSON.stringify(hl3ParkFor(t.name))])}; }""")
    print("parkEnabled",info["park"]); [print("  ",t) for t in info["teams"]]
    # 本塁打のある自チームの試合まで進める
    q=pg.evaluate("""()=>{ for(let n=0;n<40;n++){ while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); }
        setManageMode(false); playNextGameHighlight(); hlClearTimers(); if(highlightQueue.some(e=>e.kind==="HR") && highlightQueue.some(e=>e.kind==="2B"||e.kind==="1B")) break; closeHighlights(); }
      return {home:highlightGameResult.homeTeam.name, park:JSON.stringify(hl3Park), kinds:highlightQueue.map(e=>e.kind)}; }""")
    print("試合",q)
    for stage,kind in (("pre","HR"),("play","HR"),("play","hit")):
        for nm,sz,turf,dome in VAR:
            pg.evaluate("""([sz,turf,dome,stage,kind])=>{ hlClearTimers(); hl3Park={s:sz,R:HL3_PARK_R[sz],turf,dome};
                const i=highlightQueue.findIndex(e=> kind==="HR"? e.kind==="HR" : (e.kind==="2B"||e.kind==="1B"||e.kind==="3B")); highlightIdx=i; hl3Cam="B";
                const ev=highlightQueue[i], r=highlightGameResult; if(stage==="pre") hlRenderPre(r,ev); else hlRenderPlay(r,ev); }""",[sz,turf,dome,stage,kind])
            pg.wait_for_timeout(900 if stage=="pre" else 2900)
            pg.locator("#hlSvg").screenshot(path=f"{OUT}/{stage}_{kind}_{nm}.png")
    print("errs",errs[:5]); br.close()
