# 世界大会・銀河杯(v1.2.w〜y)の試合を v2 の絵で観戦・采配できるか(v2.1.g)。python3 hl3_cup.py <URL> <撮る先>
#   環境変数 HL3D_LOCAL=<three.min.js> なら 3D、なければ 2.5D(h3.py)
#   ・世界大会:2年目の開幕前に代表選び → 大会を始める → 自分の国の試合をハイライト観戦(全場面を描く)→ 次の自分の国の試合をじっくり采配(最後まで)
#   ・銀河杯:4年目の7/22 のあと → 自チームの試合をハイライト観戦 → 次の自チームの試合をじっくり采配
#   v2.2.q:采配の合間の見せ場(v1.5.f)はテストの中だけ止める(HLO.mgv="off"。hl3_manage.py と同じ)。開くと試合の終わりで見せ場を流している間に次の一手を進めてしまい止まる
#   確かめること:エラーなし・観戦の場面が描ける(球場を描く場面 st が 3D なら全部 .hl3d。投手交代などは球場を描かない)・采配の結果の場面が描ける・ホームの色と球場が取れる
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h3 import *
URL, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
WATCH="""()=>{ const n0=highlightQueue? highlightQueue.length : 0; playNextGameHighlight(); hlClearTimers(); const out={n:highlightQueue.length, st:0, d3:0, err:null, home:hl3Home||null, col:null};
  try{ out.col=(typeof teamColorMap!=="undefined" && hl3Home)? (teamColorMap[hl3Home]||null) : null;
    for(let i=0;i<highlightQueue.length;i++){ const ev=highlightQueue[i], r=highlightGameResult; highlightIdx=i;
      if(Array.isArray(ev.pn)){ hlRenderPre(r,ev); hlClearTimers(); }
      hlRenderPlay(r,ev); if(document.querySelector('#hlSvg [class*=hl3]')) out.st++; if(document.querySelector('.hl3d')) out.d3++; if(i<highlightQueue.length-1) hlClearTimers(); } }catch(e){ out.err=String(e); }
  return out; }"""
MANAGE="""()=>{ try{ HLO.mgv="off"; }catch(e){} manageMode=true; startManagedGame(); const out={ok:!!mg, series:mg&&mg.series, res:0, d3:0, err:null};
  try{ for(let n=0;n<600 && mg;n++){ const d=mg.dec; let ans=null; if(d.kind==="bunt") ans={bunt:false}; else if(d.kind==="steal") ans={steal:true};
      stepManaged(ans); if(mg && mg.dec.kind==="result"){ out.res++; const f=document.getElementById("mgField"); if(f && f.querySelector('.hl3d')) out.d3++; } } }catch(e){ out.err=String(e); }
  try{ closeModal(); }catch(e){} try{ closeManaged(); }catch(e){} manageMode=false; return out; }"""
bad=0
def ok(n,c,x=""):
    global bad
    if not c: bad+=1
    print(("PASS " if c else "FAIL ")+n, str(x)[:300], flush=True)
d3=bool(os.environ.get("HL3D_LOCAL"))
with sync_playwright() as p:
    br=p.chromium.launch(); pg=open_page3(br,URL,seed=7,w=390,h=844); create(pg,{"numTeams":"6"})
    pg.evaluate(SEASON); pg.evaluate(OFF)
    a=pg.evaluate("()=>({busy:worldBusy(), ph:world&&world.phase})"); ok("世界大会の代表選びで止まる",a["busy"] and a["ph"]=="pick",a)
    pg.evaluate("()=>{ worldStart(); worldSkipToMine(); }")
    w=pg.evaluate(WATCH); ok("世界大会:ハイライト観戦の全場面",w["n"]>0 and not w["err"] and w["st"]>0 and (w["d3"]==w["st"] if d3 else True),w)
    pg.wait_for_timeout(1600); pg.locator("#hlStage").screenshot(path=f"{OUT}/world_watch.png"); pg.evaluate("()=>{ try{ closeHighlights(); }catch(e){} }")
    m=pg.evaluate("()=>{ worldSkipToMine(); return worldActive(); }")
    if m:
        r=pg.evaluate(MANAGE); ok("世界大会:じっくり采配",r["ok"] and r["series"]=="world" and r["res"]>0 and not r["err"] and (r["d3"]==r["res"] if d3 else True),r)
    else: print("SKIP 世界大会の采配(自分の国の試合が残っていない)")
    pg.evaluate("()=>{ while(worldBusy()) worldAuto(); }")
    pg.evaluate(SEASON.replace("cupAuto(); continue;","cupAuto(); continue;")); pg.evaluate(OFF)   # 2年目
    pg.evaluate(SEASON); pg.evaluate(OFF)   # 3年目
    c=pg.evaluate("""()=>{ let n=0; while(!cupDue() && gameIdx<schedule.length && n++<5000) simScheduledGame(); const due=cupDue(); if(due) cupBegin(); if(!cupMine(cupNextMatch())) cupSkipToMine(); return {due, y:year, act:cupActive(), mine:cupActive() && cupMine(cupNextMatch())}; }""")
    ok("4年目に銀河杯が始まる",c["due"] and c["act"],c)
    if c["mine"]:
        w=pg.evaluate(WATCH); ok("銀河杯:ハイライト観戦の全場面",w["n"]>0 and not w["err"] and w["st"]>0 and (w["d3"]==w["st"] if d3 else True),w)
        pg.wait_for_timeout(1600); pg.locator("#hlStage").screenshot(path=f"{OUT}/cup_watch.png"); pg.evaluate("()=>{ try{ closeHighlights(); }catch(e){} }")
        m=pg.evaluate("()=>{ if(!cupActive()) return false; if(!cupMine(cupNextMatch())) cupSkipToMine(); return cupActive() && cupMine(cupNextMatch()); }")
        if m:
            r=pg.evaluate(MANAGE); ok("銀河杯:じっくり采配",r["ok"] and r["series"]=="cup" and r["res"]>0 and not r["err"] and (r["d3"]==r["res"] if d3 else True),r)
        else: print("SKIP 銀河杯の采配(自チームが負けて残っていない)")
    else: print("SKIP 銀河杯(自チームの試合がない)")
    ok("エラーなし",not pg.errs,pg.errs[:3])
    print("3D" if d3 else "2.5D","NG",bad); br.close()
