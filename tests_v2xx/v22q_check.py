# v2.2.q のテスト(v1.8.f〜u の同期):v1.8.l〜o で増えた場面(暴投・捕逸・ボーク・本盗・重盗・ディレード)と盗塁を、2.5D・3D・2D で観戦して止まらないか。
# 盗塁(SB/CS)は 2D のときだけ v1.8.i の演出(.sbxRun)、2.5D・3D のときは v2 の絵(.sbxRun が出ない)。
#   python3 tests_v2xx/v22q_check.py <v2.2.q の URL> <three.min.js の写し>(リポジトリの一番上で回す)
import sys, os, json
sys.path.insert(0, os.path.join(os.getcwd(), "tests_v2xx"))
from h import *
URL, LOCAL = sys.argv[1], sys.argv[2]
CDN="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"; body=open(LOCAL,"rb").read()
KINDS=["WP","PB","BK","HS","RD","TE","SB","CS"]
bad=0
def ok(n,c,x=""):
    global bad
    if not c: bad+=1
    print(("PASS " if c else "FAIL ")+n, str(x)[:400], flush=True)
COLLECT="""(K)=>{ const out=[]; let r0=null;
  for(let g=0; g<400 && out.length<40; g++){ const h=league[g%league.length], a=league[(g+1)%league.length]; const r=simGame(h,a,true);
    [...((r.log&&r.log.events)||[]),...((r.log&&r.log.rpv)||[])].forEach(ev=>{ if(K.includes(ev.kind) && out.filter(e=>e.kind===ev.kind).length<4){ out.push(ev); if(!r0) r0=r; } }); if(!r0) r0=r; }
  window.__r0=r0; window.__evs=out; return out.map(e=>e.kind); }"""
PLAY="""async ()=>{ const sleep=ms=>new Promise(f=>setTimeout(f,ms)); const res=[];
  for(const ev of __evs){ startHighlightReel(__r0); highlightQueue=[ev]; highlightIdx=0; hlClearTimers(); renderHighlightScene();
    let sbx=false, n=0; for(; n<12; n++){ await sleep(450); if(document.querySelector('#highlightOverlay .sbxRun')) sbx=true; if(hlStageName==="final") break; nextHighlight(); }
    res.push({k:ev.kind, sbx, st:hlStageName, n}); closeHighlights(); await sleep(50); }
  return res; }"""
with sync_playwright() as p:
    br=p.chromium.launch()
    for mode in ["on","3d","off"]:
        ctx=br.new_context(viewport={"width":1200,"height":844}); pg=ctx.new_page(); pg.errs=[]
        pg.on("pageerror",lambda e,pg=pg: pg.errs.append(str(e))); pg.on("dialog",lambda d,pg=pg:(pg.errs.append("DIALOG:"+d.message),d.dismiss()))
        pg.route(CDN,lambda route: route.fulfill(status=200,content_type="application/javascript",body=body))
        pg.add_init_script(SEED_JS%(31,f"localStorage.setItem('pennantHl3d','{mode}');"))
        pg.goto(URL,wait_until="domcontentloaded"); pg.wait_for_timeout(400)
        create(pg)
        if mode=="3d":
            try: pg.wait_for_function("()=>typeof hl3dOk==='undefined' || hl3dOk===true",timeout=15000)
            except Exception as e: print("3d wait",e)
        ks=pg.evaluate(COLLECT,KINDS)
        res=pg.evaluate(PLAY)
        print(mode, "場面", {k:ks.count(k) for k in KINDS}, "3D:", pg.evaluate("()=>[HL3D, hl3Active()]"))
        stuck=[x for x in res if x["st"]!="final"]
        ok(f"{mode}:新しい場面と盗塁を最後まで観戦できる・エラーなし", not stuck and not pg.errs and len(res)>=8, (stuck, pg.errs[:3]))
        sb=[x for x in res if x["k"] in ("SB","CS")]
        if mode=="off": ok("off(2D):盗塁は v1.8.i の演出が出る", sb and all(x["sbx"] for x in sb), sb)
        else: ok(f"{mode}:盗塁は v2 の絵(v1.8.i の 2D の演出は出ない)", sb and not any(x["sbx"] for x in sb), sb)
        pg.context.close()
    br.close()
print("NG", bad)
