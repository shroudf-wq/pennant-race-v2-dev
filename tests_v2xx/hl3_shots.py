# 2.5D の観戦の画面写し:セーブを読み、自チームの試合を観戦で開き、場面を進めながら撮る
#   python3 hl3_shots.py <URL> <セーブ.json> <出力フォルダ> [幅] [立体 on/weak/off] [anim on/off]
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h import *
URL, SAVE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; W=int(sys.argv[4]) if len(sys.argv)>4 else 390
H3=sys.argv[5] if len(sys.argv)>5 else "on"; ANIM=sys.argv[6] if len(sys.argv)>6 else "on"
os.makedirs(OUT, exist_ok=True)
txt=open(SAVE,encoding="utf-8").read()
with sync_playwright() as p:
    br=p.chromium.launch(); pg=open_page(br,URL,seed=9,w=W,h=844 if W<700 else 768,extra=f"localStorage.setItem('pennantHl3d','{H3}');localStorage.setItem('pennantAnim','{ANIM}');")
    errs=pg.errs; pg.on("console",lambda m: errs.append("CONSOLE:"+m.text) if m.type=="error" and "ERR_" not in m.text else None)
    pg.click("text=はじめる"); pg.wait_for_timeout(200); pg.evaluate("(t)=>loadFromText(t)",txt)
    r=pg.evaluate("""()=>{ while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); }
      setManageMode(false); playNextGameHighlight(); return {q:highlightQueue.length, kinds:highlightQueue.map(e=>e.kind)}; }""")
    print("queue",r, flush=True)
    pg.wait_for_timeout(300); pg.screenshot(path=f"{OUT}/00_inter.png")
    shots=[]
    for i in range(min(r["q"],6)):
        # つなぎ・前置きを飛ばして打つ場面へ(次へ)、その 0.5秒後と 2.2秒後を撮る
        st=pg.evaluate("()=>hlStageName")
        if st in ("inter","pre"): pg.evaluate("()=>nextHighlight()")
        pg.wait_for_timeout(500); pg.screenshot(path=f"{OUT}/{i+1:02d}a_play.png")
        info=pg.evaluate("()=>({cam:hl3Cam, st:hlStageName, k:(highlightQueue[highlightIdx]||{}).kind, s:(document.querySelector('.hlStage.hl3')||{}).dataset? document.querySelector('.hlStage.hl3').dataset.cam : '2d', fit:getComputedStyle(document.querySelector('.hlStage')).getPropertyValue('--s')})")
        pg.wait_for_timeout(1700); pg.screenshot(path=f"{OUT}/{i+1:02d}b_end.png")
        print(i+1, info, flush=True)
        pg.evaluate("()=>nextHighlight()"); pg.wait_for_timeout(700); pg.screenshot(path=f"{OUT}/{i+1:02d}c_pre.png")
        print("   pre", pg.evaluate("()=>({cam:hl3Cam, st:hlStageName})"), flush=True)
    # 最後まで
    for k in range(200):
        if pg.evaluate("()=>hlStageName")=="final": break
        pg.evaluate("()=>nextHighlight()"); pg.wait_for_timeout(30)
    pg.screenshot(path=f"{OUT}/99_final.png")
    print("final", pg.evaluate("()=>hlStageName"), "errs", errs[:5])
    br.close()
