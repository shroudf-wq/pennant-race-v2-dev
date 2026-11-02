# hl3d-billboard のテスト。python3 bb_check.py <パッチ後の URL> <元(v2.2.l)の URL> <three.min.js の写し> <撮る先>
#   (リポジトリの一番上で回す。tests_v2xx/h.py と tests_v2xx/saves/save_A.json を使う)
#   ① パッチ後の <script> が node --check を通る
#   ② hl3dMan( を呼ぶ所が残っていない(定義だけ。tests_v2xx/hl3d_bg.py ⑳ が直接呼ぶので関数は残す)
#   ③ 観戦の 3D(幅 390・1366):人が全部絵の板・3D の舞台に名前の札がない・エラーなし・板の絵は使い回し(種類が少ない)
#   ④ 同じ場面・同じ時刻で、人の位置と腕の角度(台本・hl3dArm)が元と1つも違わない(プレー前・プレーを 0.05 秒ごと)
#   ⑤ 姿勢:捕手はプレー前にしゃがむ・打者は立つ絵でバット・走る 2 コマが両方出る・投げる/捕る絵が出る・左向きの左右反転が出る
#   ⑥ 選手 1 人の画面上の高さ(px。プレー前の野手の中央値)が元の 1.6 倍以上。draw call を元と比べる(増えない)
#   ⑦ 3D の絵を作る・描く間に Math.random(試合の乱数)を呼ぶ回数が元と同じ
#   ⑧ 立体「あり」(2.5D)では名前の札が今まで通り出る(絵の板は 3D だけ)
#   ⑨ 試合画面の背景:野手 7・捕手(しゃがむ)・待つ打者 2(バット・リングなし)・ベンチ(しゃがむ・.6 倍・頭が屋根 4.6 より下)・ブルペン 8(2 型とも)が全部板。
#      毎コマ全部の板がカメラのほうを向く。ブルペンの投手は投げる/立つを繰り返す。draw call を元と比べる
import sys, os, re, subprocess, time, json, statistics
sys.path.insert(0, os.path.join(os.getcwd(), "tests_v2xx"))
from h import *
URL, BASE, LOCAL, OUT = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]; os.makedirs(OUT, exist_ok=True)
CDN="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"; body=open(LOCAL,"rb").read()
SAVE=open("tests_v2xx/saves/save_A.json",encoding="utf-8").read()
bad=0
def ok(n,c,x=""):
    global bad
    if not c: bad+=1
    print(("PASS " if c else "FAIL ")+n, str(x)[:400], flush=True)
def path_of(u): return u[7:] if u.startswith("file://") else u

# ①② 文字の確認
src=open(path_of(URL),encoding="utf-8").read()
js="\n;\n".join(re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",src,re.S)); tmp=os.path.join(OUT,"_check.js"); open(tmp,"w",encoding="utf-8").write(js)
r=subprocess.run(["node","--check",tmp],capture_output=True,text=True); os.remove(tmp)
ok("① node --check", r.returncode==0, r.stderr[:300])
calls=[l for l in src.split("\n") if "hl3dMan(" in l and "function hl3dMan(" not in l]
ok("② hl3dMan( を呼ぶ所が残っていない", not calls and src.count("function hl3dMan(")==1, [c[:80] for c in calls])

def open3d(br,url,w,mode="3d"):
    ctx=br.new_context(viewport={"width":w,"height":844 if w<700 else 700}); pg=ctx.new_page(); pg.errs=[]
    pg.on("pageerror",lambda e: pg.errs.append(str(e))); pg.on("dialog",lambda d:(pg.errs.append("DIALOG:"+d.message),d.dismiss()))
    pg.route(CDN,lambda route: route.fulfill(status=200,content_type="application/javascript",body=body))
    pg.add_init_script(SEED_JS%(9,f"localStorage.setItem('pennantHl3d','{mode}');"))
    pg.goto(url,wait_until="domcontentloaded"); pg.wait_for_timeout(400); return pg
QUEUE="""()=>{ for(;;){ while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); }
    setManageMode(false); playNextGameHighlight(); if(highlightQueue.length>=3 || gameIdx>=schedule.length) break; closeHighlights(); }
  hlClearTimers(); return highlightQueue.length; }"""
# 1 場面を描いて、自分で時刻を進める(requestAnimationFrame は止める)。位置・腕・姿勢・反転・高さ・draw call を集める
STEP="""([i,stage])=>{ let nr=0; const MR=Math.random; Math.random=function(){ nr++; return MR.apply(this,arguments); };
  try{ hlClearTimers(); highlightIdx=i; const ev=highlightQueue[i], r=highlightGameResult;
    if(stage==='pre'){ if(!Array.isArray(ev.pn)) return null; hlRenderPre(r,ev); } else hlRenderPlay(r,ev);
    const S=hl3dCur; if(!S) return {no3d:true}; cancelAnimationFrame(S.raf); S.raf=0; S.frame=()=>{};
    const st=S.st, out={pos:[], poses:{}, flips:0, n:0, bills:0, tags:st.querySelectorAll('.hl3tag').length, labTags:st.querySelectorAll('.hl3dLab .hl3tag').length, tex:0, h:[], calls:0, batBat:null, cam:st.dataset.to};
    const V=THREE.Vector3, hpx=it=>{ const m=it.man, B=m.userData.bill; m.updateMatrixWorld(true); let a,b;
      if(B){ a=B.pv.localToWorld(new V(0,0,0)); b=B.pv.localToWorld(new V(0,15.5-HL3D_BILL_TOP[B.pose]/16,0)); }
      else { const bx=new THREE.Box3(); m.children.forEach(c=>{ if(c.geometry && /Circle|Ring/.test(c.geometry.type)) return; bx.expandByObject(c); }); const c=bx.getCenter(new V()); a=new V(c.x,bx.min.y,c.z); b=new V(c.x,bx.max.y,c.z); }
      a.project(S.cam); b.project(S.cam); return Math.abs(a.y-b.y)/2*S.H; };
    const T=[]; if(stage==='pre') T.push(0,.3,1.0); else for(let t=0;t<=S.endT+.001;t+=.05) T.push(+t.toFixed(2));
    const tex=new Set();
    T.forEach(t=>{ hl3dNR(()=>hl3dUpdate(S,t));
      S.items.forEach((it,j)=>{ if(!it.man) return; out.pos.push([j,t,+it.man.position.x.toFixed(3),+it.man.position.z.toFixed(3),+it.man.userData.arm.rotation.x.toFixed(3),+it.man.userData.glv.rotation.x.toFixed(3)]);
        const B=it.man.userData.bill; if(!B) return; const k=B.role+(it.b.dataset.pos==='捕'? 'C' : ''); (out.poses[k]=out.poses[k]||{})[B.pose]=1; if(B.pv.scale.x<0) out.flips++; tex.add(B.pm.map); }); });
    out.n=S.items.filter(it=>it.man).length; out.bills=S.items.filter(it=>it.man && it.man.userData.bill).length; out.tex=tex.size;
    if(stage==='pre'){ hl3dNR(()=>{ hl3dUpdate(S,1.0); hl3dR.render(S.sc,S.cam); }); out.calls=hl3dR.info.render.calls;
      out.h=S.items.filter(it=>it.man && it.fld && it.b.dataset.pos!=='捕').map(hpx);
      const bt=S.items.find(it=>it.man && it.man.userData.bill && it.man.userData.bill.role==='b'); if(bt) out.batBat=[bt.man.userData.bill.pose, hl3dBillTex(bt.man.userData.bill.U,'b','stand',false)===bt.man.userData.bill.pm.map];
      try{ hl3Declutter(st,true); out.decl=true; }catch(e){ out.decl=String(e); } }
    return out; } finally { Math.random=MR; window.__nr=nr; } }"""

res={}
with sync_playwright() as p:
    br=p.chromium.launch()
    for w in (390,1366):
        for name,u in (("new",URL),("base",BASE)):
            t0=time.time(); pg=open3d(br,u,w)
            pg.click("text=はじめる"); pg.wait_for_timeout(200); pg.evaluate("(t)=>loadFromText(t)",SAVE)
            pg.wait_for_function("()=>hl3dOk===true",timeout=15000); q=pg.evaluate(QUEUE); R=[]
            for i in range(min(q,3)):
                for stage in ("pre","play"):
                    o=pg.evaluate(STEP,[i,stage]);
                    if o is None: continue
                    o["nr"]=pg.evaluate("()=>window.__nr"); o["i"]=i; o["stage"]=stage; R.append(o)
            # 撮る(プレー前。台本どおりに動かす)
            pg.evaluate("()=>{ hlClearTimers(); highlightIdx=0; const ev=highlightQueue[0]; if(Array.isArray(ev.pn)) hlRenderPre(highlightGameResult,ev); else hlRenderPlay(highlightGameResult,ev); }"); pg.wait_for_timeout(1000)
            pg.locator("#hlStage").screenshot(path=f"{OUT}/kansen_{w}_{name}.png")
            res[(w,name)]=(R,pg.errs,time.time()-t0); pg.context.close()
        N,B=res[(w,"new")],res[(w,"base")]
        ok(f"③ {w}px 人が全部板・札なし・エラーなし", all(o["n"]==o["bills"]>0 and o["tags"]==0 for o in N[0]) and not N[1], [(o["n"],o["bills"],o["tags"],o["tex"]) for o in N[0]][:6]+N[1][:2])
        ok(f"③ {w}px 板の絵の使い回し(1 場面 12 種類まで)", max(o["tex"] for o in N[0])<=12, [o["tex"] for o in N[0]])
        same=[(a["i"],a["stage"]) for a,b in zip(N[0],B[0]) if a["pos"]!=b["pos"]]
        ok(f"④ {w}px 位置・腕の角度が元と同じ", len(N[0])==len(B[0]) and not same and sum(len(o["pos"]) for o in N[0])>0, [same, sum(len(o["pos"]) for o in N[0])])
        if w==390:
            P={}
            for o in N[0]:
                for k,v in o["poses"].items(): P.setdefault(k,set()).update(v)
            pre=[o for o in N[0] if o["stage"]=="pre"]
            ok("⑤ 姿勢(捕手しゃがむ・打者バット・走る 2 コマ・投げる/捕る・左右反転)",
               all("crouch" in o["poses"].get("fC",{}) for o in pre) and all(o["batBat"]==["stand",True] for o in pre if o["batBat"]) and
               {"run1","run2"} <= (P.get("r",set())|P.get("b",set())|P.get("f",set())) and "throw" in P.get("f",set()) and sum(o["flips"] for o in N[0])>0,
               [{k:sorted(v) for k,v in P.items()}, [o["batBat"] for o in pre], sum(o["flips"] for o in N[0])])
        hn=statistics.median([h for o in N[0] if o["stage"]=="pre" for h in o["h"]]); hb=statistics.median([h for o in B[0] if o["stage"]=="pre" for h in o["h"]])
        cn=[o["calls"] for o in N[0] if o["stage"]=="pre"]; cb=[o["calls"] for o in B[0] if o["stage"]=="pre"]
        ok(f"⑥ {w}px 選手の高さ {hb:.1f}px → {hn:.1f}px(×{hn/hb:.2f})・draw call {cb} → {cn}", hn>=hb*1.6 and all(a<=b for a,b in zip(cn,cb)), "")
        ok(f"⑦ {w}px 3D の間の Math.random の回数が元と同じ", [o["nr"] for o in N[0]]==[o["nr"] for o in B[0]], [[o["nr"] for o in N[0]],[o["nr"] for o in B[0]]])
        ok(f"   {w}px hl3Declutter がエラーなし", all(o.get("decl") is True for o in N[0] if o["stage"]=="pre"), "")
        print(f"   {w}px 時間(開く〜6 場面) 新 {N[2]:.1f}s・元 {B[2]:.1f}s", flush=True)
    # ⑧ 2.5D
    pg=open3d(br,URL,390,mode="on"); pg.click("text=はじめる"); pg.wait_for_timeout(200); pg.evaluate("(t)=>loadFromText(t)",SAVE); pg.wait_for_timeout(300); pg.evaluate(QUEUE)
    t=pg.evaluate("()=>{ hlClearTimers(); highlightIdx=0; const ev=highlightQueue[0]; hlRenderPre(highlightGameResult,ev); const st=document.querySelector('#hlSvg .hlStage.hl3'); return [!!st, st && st.classList.contains('hl3d'), st? st.querySelectorAll('.hl3tag').length : 0]; }")
    ok("⑧ 2.5D では札が出る", t[0] and not t[1] and t[2]>=9 and not pg.errs, [t,pg.errs[:2]]); pg.context.close()
    # ⑨ 試合画面の背景
    BG="""()=>{ const S=hl3dBgS, V=THREE.Vector3, c={men:S.men.length, menBill:S.men.filter(m=>m.userData.bill).length, bills:S.bills? S.bills.length : 0, pen:0, penBill:0, ondeck:[], bench:[], face:0, tex:new Set(), poses:{}};
      S.sc.traverse(o=>{ const B=o.userData && o.userData.bill; if(o.userData && o.userData.k==='pen'){ c.pen++; if(B) c.penBill++; }
        if(o.userData && o.userData.k==='ondeck') c.ondeck.push([B? B.role : null, B? B.pose : null, o.children.length]);
        if(o.userData && o.userData.k==='bench'){ o.updateMatrixWorld(true); const top=B.pv.localToWorld(new V(0,15.5-HL3D_BILL_TOP[B.pose]/16,0)); c.bench.push([B.pose, +o.scale.x.toFixed(2), +top.y.toFixed(2)]); } });
      const pens=(S.bills||[]).filter(m=>m.userData.bill.pen);
      for(let t=0;t<6;t+=.1){ hl3dNR(()=>hl3dBgDraw(t)); pens.forEach(m=>{ c.poses[m.userData.bill.pose]=1; }); }
      S.cam.updateMatrixWorld(); (S.bills||[]).forEach(m=>{ m.updateMatrixWorld(true); const d=m.userData.bill.pv.getWorldDirection(new V()), to=S.cam.position.clone().sub(m.position); if(d.dot(to)>0) c.face++; c.tex.add(m.userData.bill.pm.map); });
      c.tex=c.tex.size; c.catcher=S.men[S.men.length-1].userData.bill? S.men[S.men.length-1].userData.bill.pose : null; c.calls=hl3dBgR.info.render.calls; return c; }"""
    BGB="""()=>{ hl3dNR(()=>hl3dBgDraw(1)); return {men:hl3dBgS.men.length, calls:hl3dBgR.info.render.calls}; }"""
    bgr={}
    for name,u in (("new",URL),("base",BASE)):
        ctx=br.new_context(viewport={"width":390,"height":844}); pg=ctx.new_page(); pg.errs=[]; pg.on("pageerror",lambda e: pg.errs.append(str(e)))
        pg.route(CDN,lambda route: route.fulfill(status=200,content_type="application/javascript",body=body))
        pg.add_init_script(SEED_JS%(7,"localStorage.setItem('pennantHl3d','3d');")); pg.goto(u,wait_until="domcontentloaded"); pg.wait_for_timeout(400)
        pg.wait_for_function("()=>hl3dOk===true",timeout=15000); create(pg,{"numTeams":"6"})
        pg.evaluate("()=>{ for(let i=0;i<20;i++) simScheduledGame(); updateMatchup(); }"); pg.click("#mainNav [data-p=game]"); pg.wait_for_timeout(1500); pg.wait_for_function("()=>hl3dBgS && hl3dBgS.men",timeout=15000)
        if name=="base": bgr[name]=pg.evaluate(BGB); pg.screenshot(path=f"{OUT}/bg_390_{name}.png"); ctx.close(); continue
        a=pg.evaluate(BG); pg.screenshot(path=f"{OUT}/bg_390_{name}.png"); pens=[]; pg.evaluate("()=>{ window.hl3dParkLook0=hl3dParkLook; }")
        for pen in (1,0):
            pg.evaluate("(pen)=>{ hl3dParkLook=(h,pk)=>Object.assign(hl3dParkLook0(h,pk),{pen,of:0}); hl3dBgS.key=''; updateMatchup(); }",pen); pg.wait_for_timeout(900); pens.append(pg.evaluate(BG))
            if pen==1:   # ブルペンとベンチを写す(カメラを向ける)
                for nm,tt in (("bullpen",12.5),("bench",22.5)):
                    pg.evaluate("(t)=>{ hl3dBgStop(); hl3dBgS.t0=performance.now()-t*1000; hl3dNR(()=>hl3dBgDraw(t)); }",tt); pg.wait_for_timeout(250); pg.screenshot(path=f"{OUT}/bg_{nm}.png")
        bgr[name]=a; bgr["pens"]=pens; bgr["errs"]=pg.errs; ctx.close()
    a=bgr["new"]
    ok("⑨ 背景の人が全部板(野手 7・捕手しゃがむ・待つ打者 2 はバットでリングなし)", a["men"]==a["menBill"]==8 and a["catcher"]=="crouch" and a["ondeck"]==[["b","stand",2]]*2 and not bgr["errs"], {k:a[k] for k in ("men","menBill","catcher","ondeck","bills")})
    ok("⑨ ベンチ(しゃがむ・.6 倍・頭が屋根 4.6 より下)", len(a["bench"])>=8 and all(b[0]=="crouch" and b[1]==0.6 and b[2]<4.6 for b in a["bench"]), a["bench"])
    ok("⑨ ブルペン 8 が板(2 型)・投げる/立つを繰り返す", all(q["pen"]==8 and q["penBill"]==8 and q["poses"].get("throw") and q["poses"].get("stand") for q in bgr["pens"]), [(q["pen"],q["penBill"],q["poses"]) for q in bgr["pens"]])
    ok("⑨ 全部の板がカメラのほうを向く", a["face"]==a["bills"]>0 and all(q["face"]==q["bills"] for q in bgr["pens"]), [a["face"],a["bills"],[(q["face"],q["bills"]) for q in bgr["pens"]]])
    ok(f"⑨ 背景の draw call {bgr['base']['calls']} → {a['calls']}・板の絵 {a['tex']} 種類", a["calls"]<=bgr["base"]["calls"] and a["tex"]<=6, "")
    br.close()
# 並べた写し(左=元・右=新)
try:
    from PIL import Image
    for w in (390,1366):
        A=Image.open(f"{OUT}/kansen_{w}_base.png"); Bm=Image.open(f"{OUT}/kansen_{w}_new.png"); C=Image.new("RGB",(A.width+Bm.width+8,max(A.height,Bm.height)),"white"); C.paste(A,(0,0)); C.paste(Bm,(A.width+8,0)); C.save(f"{OUT}/cmp_kansen_{w}.png")
    A=Image.open(f"{OUT}/bg_390_base.png"); Bm=Image.open(f"{OUT}/bg_390_new.png"); C=Image.new("RGB",(A.width+Bm.width+8,max(A.height,Bm.height)),"white"); C.paste(A,(0,0)); C.paste(Bm,(A.width+8,0)); C.save(f"{OUT}/cmp_bg_390.png")
except Exception as e: print("並べた写しは作れなかった:",e)
print("NG",bad)
