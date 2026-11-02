# 3D の守備の形を確かめる(v2.1.e)。python3 hl3d_pose.py <URL> <three.min.js の写し> <セーブ.json> <撮る先>
#   作った場面(送りバント・併殺・外野フライ)を 3D で描き、時刻ごとに野手の位置と腕の角度を読む。途中のコマを撮る
#   確かめること:バントで投・捕・一・三が前へ出て、いちばん近い野手が捕って投げる(腕を引いて振る)・二塁手が一塁へ入って受ける(腕を上げる)
#                併殺で、捕る→投げる→二塁で受けて投げる→一塁で受ける。外野フライで捕る野手が腕を上げる
#   v2.1.f:腕が2本。グラブの腕(glv)も読む。走者・追う野手は左右の腕を交互に振る(左右の差が開く)こと、捕る野手はグラブの腕を上げること
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["HL3D_LOCAL"]=sys.argv[2]
from h3 import *
URL, SV, OUT = sys.argv[1], sys.argv[3], sys.argv[4]
os.makedirs(OUT, exist_ok=True)
CASES={
 "sh":  {"kind":"SH","pn":["一走",None,None],"po":0,"outs":1,"runs":0,"mv":[[1,2]],"af":[0,1,0]},
 "dp":  {"kind":"OUT","dp":1,"bp":"G遊","pn":["一走",None,None],"po":0,"outs":2,"runs":0,"mv":[],"af":[0,0,0]},
 "fly": {"kind":"OUT","bp":"F中","pn":[None,None,None],"po":1,"outs":2,"runs":0,"mv":[],"af":[0,0,0]},
}
SAMPLE="""()=>{ const S=hl3dCur; if(!S) return null; const t=(performance.now()-S.t0)/1000;
  return {t:+t.toFixed(2), f:S.items.filter(it=>it.fld && it.man).map(it=>({p:it.b.dataset.pos, x:+it.man.position.x.toFixed(0), z:+it.man.position.z.toFixed(0), arm:+it.man.userData.arm.rotation.x.toFixed(2), glv:+it.man.userData.glv.rotation.x.toFixed(2), poses:(it.poses||[]).map(o=>o.k+o.t.toFixed(2)).join(' ')})).filter(o=>o.poses || Math.abs(o.arm-.15)>.01 || true),
    r:S.items.filter(it=>it.man && !it.fld).map(it=>({arm:+it.man.userData.arm.rotation.x.toFixed(2), glv:+it.man.userData.glv.rotation.x.toFixed(2)}))}; }"""
bad=0
with sync_playwright() as p:
    br=p.chromium.launch(); pg=open_page3(br,URL,seed=9,w=390,h=844)
    pg.click("text=はじめる"); pg.wait_for_timeout(200); pg.evaluate("(t)=>loadFromText(t)",open(SV,encoding="utf-8").read())
    pg.evaluate("""()=>{ for(;;){ while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); }
        setManageMode(false); playNextGameHighlight(); if(highlightQueue.length) break; closeHighlights(); } hlClearTimers(); }""")
    for name,e in CASES.items():
        pg.evaluate("""([e])=>{ hlClearTimers(); const base=highlightQueue[0], r=highlightGameResult;
            const ev=Object.assign({},base,e,{bases:[null,null,null],rn:(e.af||[0,0,0]).map(Boolean),fw:undefined,fwLast:undefined}); hl3Cam="B"; hlRenderPlay(r,ev);
            window.__sw=0; window.__sp=0; window.__gu=0; const tk=()=>{ const S=hl3dCur; if(S){ S.items.forEach(it=>{ if(it.man && it.fld) window.__gu=Math.min(window.__gu,it.man.userData.glv.rotation.x); if(it.man && !(it.poses||[]).length){ window.__sw=Math.max(window.__sw,Math.abs(it.man.userData.arm.rotation.x-it.man.userData.glv.rotation.x)); window.__sp=Math.max(window.__sp,it.sp||0); } }); } if(performance.now()-t00<2000) requestAnimationFrame(tk); }; const t00=performance.now(); requestAnimationFrame(tk); }""",[e])
        seen={}; t0=0; swing=0; gup=0
        for t in (300,650,950,1150,1450):
            pg.wait_for_timeout(t-t0); t0=t
            m=pg.evaluate(SAMPLE)
            pg.locator("#hlStage").screenshot(path=f"{OUT}/{name}_{t/1000:.2f}.png")
            moved=[f"{o['p']}({o['x']},{o['z']}) 腕{o['arm']}/{o['glv']}" for o in m["f"] if o["poses"] or abs(o["arm"]-.15)>.01]
            print(name, m["t"], " / ".join(moved), "| 走者", m["r"], flush=True)
            swing=max([swing]+[abs(o["arm"]-o["glv"]) for o in m["r"]]+[abs(o["arm"]-o["glv"]) for o in m["f"] if not o["poses"]])
            gup=min([gup]+[o["glv"] for o in m["f"]])
            for o in m["f"]:
                if o["poses"]: seen[o["p"]]=o["poses"]
        swing=max(swing,pg.evaluate("()=>window.__sw")); gup=min(gup,pg.evaluate("()=>window.__gu")); print(name,"速さの最大",round(pg.evaluate("()=>window.__sp"),1))
        print(name,"形:",seen,"振りの最大",round(swing,2),"グラブの最も上",gup, flush=True)
        if name in ("sh","dp") and swing<.3: bad+=1; print("  NG 腕を振っていない")
        if gup>-2.0: bad+=1; print("  NG グラブの腕が上がっていない")
        if name=="sh" and not (any("t" in v for v in seen.values()) and seen.get("二","").count("c")): bad+=1
        if name=="dp" and not (sum(v.count("t") for v in seen.values())>=2 and sum(v.count("c") for v in seen.values())>=3): bad+=1
        if name=="fly" and not any(v.startswith("c0.90") for v in seen.values()): bad+=1
    print("errs",pg.errs[:3]); print("NG",bad); br.close()
