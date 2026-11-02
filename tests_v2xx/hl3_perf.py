# 観戦の重さを測る:CPU を遅くして(CDP の Emulation.setCPUThrottlingRate)、プレーの場面の 3.2 秒のコマの間隔を集める
#   python3 hl3_perf.py <URL> <セーブ> [遅くする倍率…]   立体あり/なし(2D)を比べる。幅 390
#   v2.1.b:環境変数 HL3D_LOCAL(three.min.js の写し)があれば「3D」も測る。この作業場所の 3D はソフトウェアで描く(GPU なし)ので、3D の数は実機より重く出る
import sys, os, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h import *
from h3 import open_page3
URL, SV = sys.argv[1], sys.argv[2]; RATES=[float(x) for x in sys.argv[3:]] or [1,4,6]
txt=open(SV,encoding="utf-8").read()
FR="""(i)=>new Promise(res=>{ hlClearTimers(); highlightIdx=i; const ts=[]; let t0=performance.now();
  const f=t=>{ ts.push(t); if(t-t0<3200) requestAnimationFrame(f); else res(ts); }; hlRenderPlay(highlightGameResult,highlightQueue[i]); requestAnimationFrame(f); })"""
with sync_playwright() as p:
    br=p.chromium.launch()
    for mode in (("3d","on","off") if os.environ.get("HL3D_LOCAL") else ("on","off")):
        for rate in RATES:
            if mode=="3d": pg=open_page3(br,URL,seed=9,w=390,h=844)
            else:
                pg=open_page(br,URL,seed=9,w=390,h=844,extra=f"localStorage.setItem('pennantHl3d','{mode}');")
            pg.click("text=はじめる"); pg.wait_for_timeout(200); pg.evaluate("(t)=>loadFromText(t)",txt)
            q=pg.evaluate("""()=>{ while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); }
                setManageMode(false); playNextGameHighlight(); hlClearTimers(); return highlightQueue.length; }""")
            cdp=pg.context.new_cdp_session(pg); cdp.send("Emulation.setCPUThrottlingRate",{"rate":rate})
            gaps=[]; worst=0
            for i in range(min(q,5)):
                ts=pg.evaluate(FR,i); d=[b-a for a,b in zip(ts,ts[1:])]; gaps+=d; worst=max(worst,max(d) if d else 0)
            gaps.sort(); n=len(gaps)
            print(f"立体={mode:3s} CPU×{rate:g}  コマ数/秒 {1000/statistics.mean(gaps):5.1f}  中央 {statistics.median(gaps):5.1f}ms  遅い5% {gaps[int(n*.95)]:6.1f}ms  最悪 {worst:6.1f}ms  33ms超 {sum(g>33.4 for g in gaps)/n*100:4.1f}%", flush=True)
            pg.context.close()
    br.close()
