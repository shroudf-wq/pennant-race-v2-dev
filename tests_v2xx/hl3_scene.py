# 1場面を撮る:python3 hl3_scene.py <URL> <幅> <セーブ> <場面の番号(1から)> <pre/play> <出力.png>
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h import *
URL,W,SV,I,STG,OUT=sys.argv[1],int(sys.argv[2]),sys.argv[3],int(sys.argv[4])-1,sys.argv[5],sys.argv[6]
with sync_playwright() as p:
    br=p.chromium.launch(); pg=open_page(br,URL,seed=9,w=W,h=844 if W<700 else 700,extra="localStorage.setItem('pennantHl3d','on');")
    pg.click("text=はじめる"); pg.wait_for_timeout(200); pg.evaluate("(t)=>loadFromText(t)",open(SV,encoding="utf-8").read())
    pg.evaluate("""()=>{ let n=0; for(;;){ while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); }
        setManageMode(false); playNextGameHighlight(); if(highlightQueue.length>=3 || ++n>5 || gameIdx>=schedule.length) break; closeHighlights(); } hlClearTimers(); }""")
    pg.evaluate("""([i,stage])=>{ hlClearTimers(); highlightIdx=i; const ev=highlightQueue[i], r=highlightGameResult; if(stage==='pre') hlRenderPre(r,ev); else hlRenderPlay(r,ev); }""",[I,STG])
    pg.wait_for_timeout(900 if STG=="pre" else 2900)
    pg.locator("#hlSvg").screenshot(path=OUT); print("errs",pg.errs[:3]); br.close()
