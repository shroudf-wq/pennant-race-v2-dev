# 2.5D の札の重なりを数える(v2.0.c)。セーブを読み、自チームの次の試合の観戦の場面を1つずつ「プレー前」「プレーの終わり」で止めて測る
#   python3 hl3_overlap.py <URL> <幅> <セーブ.json> [セーブ.json ...]
# 数えるもの:見えている札(.hl3tag と得点の +N)どうしの重なり(6px² より大きい組)・プレー前の打者のカードの下に隠れた札・ボールカウントの表示(v1.2.k〜)の下に隠れた札・舞台からはみ出した札
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h import *
from h3 import open_page3   # v2.1.b:HL3D_LOCAL があれば「立体:3D」で測る
URL, W = sys.argv[1], int(sys.argv[2]); SAVES=sys.argv[3:]
MEASURE="""()=>{ const st=document.querySelector('#hlSvg .hlStage.hl3'); if(!st) return null; const B=st.getBoundingClientRect();
  const ts=[...st.querySelectorAll('.hl3tag,.hl3txt.runs')].filter(t=>{ const b=t.closest('.hl3bb'); return parseFloat(getComputedStyle(b).opacity)>=.1 && getComputedStyle(b).visibility!=='hidden'; })
    .map(t=>{ const r=t.getBoundingClientRect(); return {n:t.textContent, x:r.left, y:r.top, w:r.width, h:r.height}; });
  let pairs=[], outs=[];
  for(let i=0;i<ts.length;i++){ const a=ts[i];
    if(a.x<B.left-2||a.y<B.top-2||a.x+a.w>B.right+2||a.y+a.h>B.bottom+2) outs.push(a.n);
    for(let j=i+1;j<ts.length;j++){ const b=ts[j]; const ix=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x), iy=Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y);
      if(ix>0&&iy>0&&ix*iy>6) pairs.push(a.n+'×'+b.n); } }
  const cut=st.querySelector('.hlCutin:not(.out)'); if(cut){ const c={n:'カード', x:B.left+cut.offsetLeft, y:B.top+cut.offsetTop, w:cut.offsetWidth, h:cut.offsetHeight};
    ts.forEach(a=>{ const ix=Math.min(a.x+a.w,c.x+c.w)-Math.max(a.x,c.x), iy=Math.min(a.y+a.h,c.y+c.h)-Math.max(a.y,c.y); if(ix>0&&iy>0&&ix*iy>6) pairs.push('カード×'+a.n); }); }
  const bcp=st.querySelector('.bcPanel'); if(bcp) bcp.querySelectorAll('.bcList li,.bcBSO').forEach(e=>{ const c={x:B.left+bcp.offsetLeft+e.offsetLeft, y:B.top+bcp.offsetTop+e.offsetTop, w:e.offsetWidth, h:e.offsetHeight};
    ts.forEach(a=>{ const ix=Math.min(a.x+a.w,c.x+c.w)-Math.max(a.x,c.x), iy=Math.min(a.y+a.h,c.y+c.h)-Math.max(a.y,c.y); if(ix>0&&iy>0&&ix*iy>6) pairs.push('カウント×'+a.n); }); });
  return {n:ts.length, pairs, outs, cam:st.dataset.to, d3:st.classList.contains('hl3d')}; }"""
tot={"tags":0,"pairs":0,"outs":0,"scenes":0,"3d":0}
with sync_playwright() as p:
    br=p.chromium.launch()
    for sv in SAVES:
        txt=open(sv,encoding="utf-8").read()
        pg=open_page3(br,URL,seed=9,w=W,h=844 if W<700 else 700)
        pg.click("text=はじめる"); pg.wait_for_timeout(200); pg.evaluate("(t)=>loadFromText(t)",txt)
        q=pg.evaluate("""()=>{ let n=0; for(;;){ while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); }
            setManageMode(false); playNextGameHighlight(); if(highlightQueue.length>=3 || ++n>5 || gameIdx>=schedule.length) break; closeHighlights(); }
          hlClearTimers(); return highlightQueue.length; }""")
        for i in range(q):
            for stage in ("pre","play"):
                ok=pg.evaluate("""([i,stage])=>{ hlClearTimers(); highlightIdx=i; const ev=highlightQueue[i], r=highlightGameResult;
                    if(stage==='pre'){ if(!Array.isArray(ev.pn)) return false; hlRenderPre(r,ev); } else hlRenderPlay(r,ev); return true; }""",[i,stage])
                if not ok: continue
                pg.wait_for_timeout(900 if stage=="pre" else 2900)
                m=pg.evaluate(MEASURE)
                if not m: continue
                tot["scenes"]+=1; tot["3d"]+=1 if m.get("d3") else 0; tot["tags"]+=m["n"]; tot["pairs"]+=len(m["pairs"]); tot["outs"]+=len(m["outs"])
                if m["pairs"] or m["outs"]: print(f"  {os.path.basename(sv)} #{i+1} {stage} cam={m['cam']} 重なり{m['pairs']} はみ出し{m['outs']}")
        print(os.path.basename(sv),"場面",q,"errs",pg.errs[:3], flush=True)
        pg.context.close()
    br.close()
print("合計",tot)
