# 1場面の流れ(つなぎ→プレー前→プレー)を待って撮る。python3 hl3_flow.py <URL> <セーブ> <出力> [幅] [立体] [anim]
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h import *
URL, SAVE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; W=int(sys.argv[4]) if len(sys.argv)>4 else 390
H3=sys.argv[5] if len(sys.argv)>5 else "on"; ANIM=sys.argv[6] if len(sys.argv)>6 else "on"
os.makedirs(OUT, exist_ok=True); txt=open(SAVE,encoding="utf-8").read()
with sync_playwright() as p:
    br=p.chromium.launch(); pg=open_page(br,URL,seed=9,w=W,h=844 if W<700 else 700,extra=f"localStorage.setItem('pennantHl3d','{H3}');localStorage.setItem('pennantAnim','{ANIM}');localStorage.setItem('pennantHlOpt',JSON.stringify({{fx:'on',inter:'on',pre:'on',flow:'on',speed:'fast'}}));")
    errs=pg.errs; pg.on("console",lambda m: errs.append("CONSOLE:"+m.text) if m.type=="error" and "ERR_" not in m.text else None)
    pg.click("text=はじめる"); pg.wait_for_timeout(200); pg.evaluate("(t)=>loadFromText(t)",txt)
    r=pg.evaluate("""()=>{ while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); }
      setManageMode(false); playNextGameHighlight(); return {q:highlightQueue.length, kinds:highlightQueue.map(e=>e.kind)}; }""")
    print("queue",r, flush=True)
    k=0
    for i in range(min(r["q"],4)):
        # fast: inter .9s → pre 1.1s → play
        pg.wait_for_timeout(1000); pg.screenshot(path=f"{OUT}/{i+1:02d}_1pre.png"); a=pg.evaluate("()=>({cam:hl3Cam,st:hlStageName})")
        pg.wait_for_timeout(1300); pg.screenshot(path=f"{OUT}/{i+1:02d}_2play.png"); b=pg.evaluate("()=>({cam:hl3Cam,st:hlStageName,k:(highlightQueue[highlightIdx]||{}).kind})")
        pg.wait_for_timeout(1800); pg.screenshot(path=f"{OUT}/{i+1:02d}_3end.png")
        print(i+1,a,b,flush=True); pg.evaluate("()=>nextHighlight()")
    print("errs",errs[:5]); br.close()
