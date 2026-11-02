# Three.js の読み込みと、読めないときに 2.5D に戻るか(v2.1.a〜)。python3 hl3_load.py <URL> <three.min.js の写し>
#   この作業場所からは cdnjs に出られないので、cdnjs の URL への読み込みを Playwright で手元の写し(npm の three@0.128.0 の build/three.min.js)に差し替える
#   ① 「あり」などを選んだ端末では、起動しても cdnjs を読みに行かない(3D のときだけ)
#   ③〜⑤は「あり」を選んだ端末で、読み込みを手で始める(v2.1.c から初めの設定が 3D で、起動のときに読み始めるため)
#   ⑥ v2.1.c:何も選んでいない端末(初めの設定=3D)は、起動のときに読み始め、読めたら 3D が使える
#   ② 読める:hl3dLoad() が true、THREE.REVISION が "128"、小さな絵を WebGL で描いて色が取れる
#   ③ 読めない(つながらない):false がすぐ返る
#   ④ 返事がない:8 秒で false
#   ⑤ WebGL がない(--disable-webgl):読みに行かずに false
#   ④のあと、ページを閉じるときに Playwright が asyncio.CancelledError を出すことがある(返事を待たせたままの読み込みを捨てるため。結果には関係ない)
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h import *
URL, LOCAL = sys.argv[1], sys.argv[2]
CDN="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
body=open(LOCAL,"rb").read()
DRAW="""async()=>{ const ok=await hl3dLoad(); if(!ok) return {ok};
  const cv=document.createElement('canvas'); cv.width=64; cv.height=64; document.body.appendChild(cv);
  const R=new THREE.WebGLRenderer({canvas:cv, preserveDrawingBuffer:true}); const sc=new THREE.Scene(); sc.background=new THREE.Color(0x103020);
  const cam=new THREE.PerspectiveCamera(50,1,.1,100); cam.position.set(0,0,3);
  sc.add(new THREE.Mesh(new THREE.BoxGeometry(1,1,1), new THREE.MeshBasicMaterial({color:0xff0000}))); R.render(sc,cam);
  const gl=R.getContext(), px=new Uint8Array(4); gl.readPixels(32,32,1,1,gl.RGBA,gl.UNSIGNED_BYTE,px);
  return {ok, rev:THREE.REVISION, center:[...px]}; }"""
res=[]
with sync_playwright() as p:
    br=p.chromium.launch()
    # ①② 読める
    pg=open_page(br,URL,seed=9,extra="localStorage.setItem('pennantHl3d','on');"); reqs=[]
    pg.on("request",lambda r: reqs.append(r.url) if "cdnjs" in r.url else None)
    pg.route(CDN,lambda route: route.fulfill(status=200,content_type="application/javascript",body=body))
    pg.click("text=はじめる"); pg.wait_for_timeout(200)
    before=len(reqs)
    r=pg.evaluate(DRAW)
    ok2= r.get("ok") is True and r.get("rev")=="128" and r["center"][0]>200 and r["center"][1]<60
    res.append(("① ふだんは読みに行かない", before==0, f"起動まで {before} 回"))
    res.append(("② 読める・描ける", ok2, str(r)))
    res.append(("②' 2回目は読み直さない", pg.evaluate("async()=>{ const a=hl3dLoad(), b=hl3dLoad(); return a===b && await a; }") and len([u for u in reqs if "three" in u])==1, f"読み込み {len(reqs)} 回"))
    pg.context.close()
    # ⑥ 何も選んでいない端末:起動のときに読み始める(開く前に差し替えを入れる)
    ctx=br.new_context(); pg=ctx.new_page(); pg.errs=[]; reqs=[]
    pg.on("request",lambda r: reqs.append(r.url) if "cdnjs" in r.url else None)
    pg.route(CDN,lambda route: route.fulfill(status=200,content_type="application/javascript",body=body))
    pg.add_init_script(SEED_JS%(9,"localStorage.removeItem('pennantHl3d');")); pg.goto(URL,wait_until="domcontentloaded")
    try: pg.wait_for_function("()=>hl3dOk===true",timeout=10000); ok6=True
    except Exception: ok6=False
    res.append(("⑥ 初めの設定は3D:起動で読み、使える", ok6 and pg.evaluate("()=>HL3D")=="3d" and len(reqs)==1, f"HL3D={pg.evaluate('()=>HL3D')} 読み込み {len(reqs)} 回"))
    pg.context.close()
    # ③ つながらない
    pg=open_page(br,URL,seed=9,extra="localStorage.setItem('pennantHl3d','on');"); pg.route(CDN,lambda route: route.abort())
    t=time.time(); r=pg.evaluate("()=>hl3dLoad()"); dt=time.time()-t
    res.append(("③ つながらない → false", r is False and dt<3, f"{r} {dt:.1f}秒")); pg.context.close()
    # ④ 返事がない
    pg=open_page(br,URL,seed=9,extra="localStorage.setItem('pennantHl3d','on');"); pg.route(CDN,lambda route: None)
    t=time.time(); r=pg.evaluate("()=>hl3dLoad()"); dt=time.time()-t
    res.append(("④ 返事がない → 8秒で false", r is False and 7<dt<11, f"{r} {dt:.1f}秒")); pg.unroute_all(behavior="ignoreErrors"); pg.context.close()
    errs=[]
    br.close()
    # ⑤ WebGL がない
    br=p.chromium.launch(args=["--disable-webgl","--disable-3d-apis"])
    pg=open_page(br,URL,seed=9,extra="localStorage.setItem('pennantHl3d','on');"); reqs=[]
    pg.on("request",lambda r: reqs.append(r.url) if "cdnjs" in r.url else None)
    pg.route(CDN,lambda route: route.fulfill(status=200,content_type="application/javascript",body=body))
    r=pg.evaluate("()=>hl3dLoad()")
    res.append(("⑤ WebGL なし → 読まずに false", r is False and not reqs, f"{r} 読み込み {len(reqs)} 回"))
    errs=pg.errs[:]; pg.context.close(); br.close()
bad=0
for n,ok,info in res:
    print("OK " if ok else "NG ",n,info); bad+= 0 if ok else 1
print("errs",errs[:3]); print("NG",bad)
