# v2 の 3D のテスト用(v2.1.b〜)。h.py は v1 と同じものにしておくので、3D の道具はこちらに置く
#   環境変数 HL3D_LOCAL に three.min.js の写し(npm の three@0.128.0 の build/three.min.js)を入れると、open_page3 は「立体:3D」で開き、
#   cdnjs への読み込みを写しに差し替える(この作業場所からは cdnjs に出られない)。HL3D_LOCAL がなければ open_page と同じ(立体は mode)
#   HL3D_FAIL=1 なら、cdnjs への読み込みを失敗させる(3D を選んでも 2.5D に戻るかを見る)
import os
from h import *
CDN="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
def open_page3(br,url,seed=11,w=390,h=844,mode="on",extra=""):
    local=os.environ.get("HL3D_LOCAL"); fail=os.environ.get("HL3D_FAIL")=="1"
    if local or fail: mode="3d"
    ctx=br.new_context(viewport={"width":w,"height":h}); pg=ctx.new_page(); pg.errs=[]
    pg.on("pageerror",lambda e: pg.errs.append(str(e))); pg.on("dialog",lambda d:(pg.errs.append("DIALOG:"+d.message),d.dismiss()))
    if fail: pg.route(CDN,lambda route: route.abort())
    elif local:
        body=open(local,"rb").read(); pg.route(CDN,lambda route: route.fulfill(status=200,content_type="application/javascript",body=body))
    pg.add_init_script(SEED_JS%(seed,f"localStorage.setItem('pennantHl3d','{mode}');"+extra))
    pg.goto(url,wait_until="domcontentloaded"); pg.wait_for_timeout(400)
    if local and not fail:
        try: pg.wait_for_function("()=>typeof hl3dOk==='undefined' || hl3dOk===true",timeout=15000)
        except Exception as e: pg.errs.append("3D が読めない: "+str(e)[:80])
    return pg
