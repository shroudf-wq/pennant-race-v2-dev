# 3D(v2.1.b〜)の観戦を撮る。python3 hl3d_shots.py <URL> <three.min.js の写し> <幅> <セーブ.json> <撮る先> [場面の数]
#   設定「立体:3D」にして、cdnjs への読み込みを手元の写しに差し替える。自チームの次の試合の場面を「プレー前」「プレーの途中(1.1秒)」「プレーの終わり(2.9秒)」で撮る
#   確かめること:3D の舞台(.hl3d と canvas)で描けたか・エラーがないか・札が枠からはみ出していないか
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h import *
URL, LOCAL, W, SV, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]; NMAX=int(sys.argv[6]) if len(sys.argv)>6 else 6
CDN="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
os.makedirs(OUT, exist_ok=True); body=open(LOCAL,"rb").read()
def open3d(br,url,body,seed=9,w=390,h=844,mode="3d"):
    # open_page と同じだが、cdnjs の差し替えを開く前に入れる(「3D」の設定は起動のときに読み込みを始めるため)
    ctx=br.new_context(viewport={"width":w,"height":h}); pg=ctx.new_page(); pg.errs=[]
    pg.on("pageerror",lambda e: pg.errs.append(str(e))); pg.on("dialog",lambda d:(pg.errs.append("DIALOG:"+d.message),d.dismiss()))
    pg.route(CDN,lambda route: route.fulfill(status=200,content_type="application/javascript",body=body))
    pg.add_init_script(SEED_JS%(seed,f"localStorage.setItem('pennantHl3d','{mode}');"))
    pg.goto(url,wait_until="domcontentloaded"); pg.wait_for_timeout(400); return pg
INFO="""()=>{ const st=document.querySelector('#hlSvg .hlStage.hl3'); if(!st) return null; const B=st.getBoundingClientRect();
  const outs=[...st.querySelectorAll('.hl3tag')].filter(t=>{ const r=t.getBoundingClientRect(); return parseFloat(getComputedStyle(t.closest('.hl3bb')).opacity)>=.1 && getComputedStyle(t.closest('.hl3bb')).visibility!=='hidden' && (r.left<B.left-2||r.top<B.top-2||r.right>B.right+2||r.bottom>B.bottom+2); }).map(t=>t.textContent);
  return {d3: st.classList.contains('hl3d'), cv: !!st.querySelector('canvas.hl3dCv'), cam: st.dataset.to, tags: st.querySelectorAll('.hl3dLab .hl3tag').length, outs}; }"""
with sync_playwright() as p:
    br=p.chromium.launch()
    pg=open3d(br,URL,body,w=W,h=844 if W<700 else 700)
    pg.click("text=はじめる"); pg.wait_for_timeout(200); pg.evaluate("(t)=>loadFromText(t)",open(SV,encoding="utf-8").read())
    pg.wait_for_function("()=>hl3dOk===true",timeout=15000)
    q=pg.evaluate("""()=>{ for(;;){ while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); }
        setManageMode(false); playNextGameHighlight(); if(highlightQueue.length>=3 || gameIdx>=schedule.length) break; closeHighlights(); }
      hlClearTimers(); return highlightQueue.length; }""")
    bad=0
    for i in range(min(q,NMAX)):
        PT=[float(x) for x in os.environ.get("SHOT_T","1.1,2.9").split(",")]   # v2.1.c:プレーを撮る時刻(秒)。例 SHOT_T=0.5,0.9,1.3,1.8,2.9
        for stage,waits in (("pre",[900]),("play",[int(round((b-a)*1000)) for a,b in zip([0]+PT,PT)])):
            ok=pg.evaluate("""([i,stage])=>{ hlClearTimers(); highlightIdx=i; const ev=highlightQueue[i], r=highlightGameResult;
                if(stage==='pre'){ if(!Array.isArray(ev.pn)) return false; hlRenderPre(r,ev); } else hlRenderPlay(r,ev); return true; }""",[i,stage])
            if not ok: continue
            tot=0
            for k,wt in enumerate(waits):
                pg.wait_for_timeout(wt); tot+=wt
                m=pg.evaluate(INFO)
                if not m or not m["d3"] or not m["cv"] or (m["outs"] and k==len(waits)-1): bad+=1   # はみ出しは最後のコマだけ見る(本塁打でカメラが打球を追う間は、内野の札が枠の外に出る)
                pg.locator("#hlStage").screenshot(path=f"{OUT}/s{i+1}_{stage}_{tot/1000:.1f}_{m['cam'] if m else 'x'}.png")
                print(f"#{i+1} {stage} {tot/1000:.1f}s", m, flush=True)
    print("errs",pg.errs[:3]); print("NG",bad)
    pg.context.close(); br.close()
