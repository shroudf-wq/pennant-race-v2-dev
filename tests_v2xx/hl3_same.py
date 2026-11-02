# 2.5D の舞台が2つの版で同じかを確かめる(v2.1.a:動きの台本を取り出しても絵が変わらないこと)。
#   python3 hl3_same.py <前の版のURL> <新しい版のURL> <セーブ.json> [セーブ.json ...]
#   ・観戦:セーブを読み、自チームの次の試合の場面を1つずつ「プレー前」「プレー」で描いた直後の #hlSvg の HTML
#   ・采配:新しいリーグ(作戦と走塁・球場の個性あり)で采配の試合を4つ進め、結果の場面ごとの #mgField の HTML
#   描いた直後(動かす前)に取るので、時間に左右されない。違う場面があれば、最初に違う所を出す
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h import *
A, B = sys.argv[1], sys.argv[2]; SAVES=sys.argv[3:]
REEL="""()=>{ const out=[]; for(let k=0;k<3;k++){
    while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); }
    if(gameIdx>=schedule.length) break;
    setManageMode(false); playNextGameHighlight(); hlClearTimers();
    for(let i=0;i<highlightQueue.length;i++){ const ev=highlightQueue[i], r=highlightGameResult; highlightIdx=i;
      if(Array.isArray(ev.pn)){ hl3Cam="B"; hlRenderPre(r,ev); out.push("pre "+i+" "+document.getElementById("hlSvg").innerHTML); hlClearTimers(); }
      hlRenderPlay(r,ev); out.push("play "+i+" "+document.getElementById("hlSvg").innerHTML); hlClearTimers(); }
    closeHighlights(); }
  return out; }"""
MG="""()=>{ const out=[]; for(let k=0;k<4;k++){ startManagedGame();
    for(let n=0;n<400 && mg;n++){ const d=mg.dec; let ans=null; if(d.kind==="bunt") ans={bunt:false}; else if(d.kind==="steal") ans={steal:true};
      stepManaged(ans); if(mg && mg.dec.kind==="result"){ const f=document.getElementById("mgField"); out.push("mg "+k+" "+n+" "+(f? f.innerHTML : "")); } }
    try{ closeModal(); }catch(e){} try{ closeHighlights(); }catch(e){} } return out; }"""
def collect(url):
    res={}
    with sync_playwright() as p:
        br=p.chromium.launch()
        for sv in SAVES:
            pg=open_page(br,url,seed=9,w=390,h=844,extra="localStorage.setItem('pennantHl3d','on');")
            pg.click("text=はじめる"); pg.wait_for_timeout(200); pg.evaluate("(t)=>loadFromText(t)",open(sv,encoding="utf-8").read())
            res[os.path.basename(sv)]=(pg.evaluate(REEL),pg.errs[:]); pg.context.close()
        pg=open_page(br,url,seed=21,w=390,h=844,extra="localStorage.setItem('pennantHl3d','on');")
        create(pg,{"numTeams":"6","importSel":"off","traitSel":"off"})
        pg.evaluate("()=>{ for(let k=0;k<12;k++) simScheduledGame(); setManageMode(true); }")
        res["采配"]=(pg.evaluate(MG),pg.errs[:]); pg.context.close(); br.close()
    return res
ra, rb = collect(A), collect(B)
bad=0; n=0
for k in ra:
    a,ea=ra[k]; b,eb=rb[k]; n+=len(a)
    if len(a)!=len(b): print(k,"場面の数が違う",len(a),len(b)); bad+=1; continue
    for x,y in zip(a,b):
        if x!=y:
            bad+=1; i=next(j for j in range(min(len(x),len(y))) if x[j]!=y[j]) if any(x[j]!=y[j] for j in range(min(len(x),len(y)))) else min(len(x),len(y))
            print(k,x[:12],"違う:",x[max(0,i-80):i+80],"\n   →",y[max(0,i-80):i+80]); break
    print(k,"場面",len(a),"errs",ea[:2],eb[:2])
print("比べた場面",n,"違い",bad)
