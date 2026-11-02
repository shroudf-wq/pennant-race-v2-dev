# v2 のセーブの互換テスト(同期手順の 2・README の ①〜④)
#   python3 sav_v2.py <v1のURL> <v2のURL> <セーブのフォルダ>
# ① 読み込める  ② 同じ乱数で1シーズン(残り全部+PS)進めて v1 と順位表が一致・エラーなし
# ③ ハイライト観戦:自チームの試合を観戦で進め、「次へ」で最後(final)まで進む(アニメーションあり/なし)
# ④ v2 で20試合進めて保存したものを v1 で読み、さらに20試合進んでエラーなし(逆方向。セーブの形が同じ証拠)
import sys, os, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h import *
from h3 import open_page3   # v2.1.b:HL3D_LOCAL があれば v2 を「立体:3D」で開く(v1 はそのまま)
V1, V2, D = sys.argv[1], sys.argv[2], sys.argv[3]
LOAD="(t)=>{ loadFromText(t); return {ver:APP_VERSION, sv:(JSON.parse(t).version), y:year, idx:gameIdx, n:schedule.length}; }"
ST="()=>league.map(t=>[t.name,t.w,t.l,t.t||0])"
RUN="()=>{ "+SEASON[5:-1]+" return 0; }"   # SEASON の中身(while から)
BACKUP="()=>{ const b=buildSaveText(); return b.text.slice(0,-1)+',\"profile\":'+JSON.stringify(collectProfile())+'}'; }"
HL="""()=>{ // 自チームの次の試合までを進め、観戦を開いて「次へ」で最後まで
  while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); }
  if(gameIdx>=schedule.length) return {skip:"no my game"};
  setManageMode(false); playNextGameHighlight();
  const ov=document.getElementById("highlightOverlay"); if(ov.classList.contains("hidden")) return {err:"overlay not shown"};
  let n=0; const q=highlightQueue.length;
  while(n<400 && hlStageName!=="final"){ nextHighlight(); n++; }
  const txt=(document.getElementById("hlBanner")||{}).textContent||"";
  closeHighlights(); return {scenes:q, clicks:n, stage:hlStageName, banner:txt.slice(0,20)}; }"""
def kv(d): return " ".join(f"{k}={v}" for k,v in d.items())
with sync_playwright() as p:
    br=p.chromium.launch()
    for fn in sorted(glob.glob(os.path.join(D,"save_*.json"))):
        name=os.path.basename(fn); txt=open(fn,encoding="utf-8").read(); out=[]
        # ①②
        res=[]; v2txt=None
        for u in (V1,V2):
            pg=(open_page3 if u==V2 else open_page)(br,u,seed=5); pg.click("text=はじめる"); pg.wait_for_timeout(200)
            info=pg.evaluate(LOAD,txt)
            if u==V2: pg.evaluate("()=>{ for(let i=0;i<20 && gameIdx<schedule.length;i++) simScheduledGame(); }"); v2txt=pg.evaluate(BACKUP); pg.context.close(); pg=(open_page3 if u==V2 else open_page)(br,u,seed=5); pg.click("text=はじめる"); pg.wait_for_timeout(200); pg.evaluate(LOAD,txt)   # ④用に20試合後の保存を取り、②は読み直して同じ条件で
            pg.evaluate(RUN); st=pg.evaluate(ST); y=pg.evaluate("()=>year")
            res.append((info,st,y,pg.errs[:2])); pg.context.close()
        out.append(f"①読込 v1:{kv(res[0][0])} v2:{kv(res[1][0])}")
        out.append(f"②1季 {'一致' if res[0][1]==res[1][1] else '不一致'} errs v1:{res[0][3]} v2:{res[1][3]}")
        # ③ ハイライト(アニメーションあり・なし)
        for anim in ("on","off"):
            pg=open_page3(br,V2,seed=9,extra=f"localStorage.setItem('pennantAnim','{anim}');"); pg.click("text=はじめる"); pg.wait_for_timeout(200)
            pg.evaluate(LOAD,txt); r=pg.evaluate(HL); pg.wait_for_timeout(300)
            out.append(f"③観戦(anim={anim}) {kv(r)} errs {pg.errs[:2]}"); pg.context.close()
        # ④ 逆方向
        pg=open_page(br,V1,seed=5); pg.click("text=はじめる"); pg.wait_for_timeout(200)
        try:
            r=pg.evaluate("(t)=>{ loadFromText(t); const g0=gameIdx; for(let i=0;i<20 && gameIdx<schedule.length;i++) simScheduledGame(); return {ver:APP_VERSION, sv:JSON.parse(t).version, y:year, from:g0, to:gameIdx}; }", v2txt)
            out.append(f"④v2→v1 {kv(r)} errs {pg.errs[:2]}  (v2の保存 {len(v2txt.encode())} bytes)")
        except Exception as e: out.append(f"④v2→v1 ERROR {str(e)[:150]} {pg.errs[:2]}")
        pg.context.close()
        print(name); [print("  "+o) for o in out]; sys.stdout.flush()
    br.close()
