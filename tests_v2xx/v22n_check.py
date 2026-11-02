# v2.2.n のテスト:顔の書き分け・観戦の捕手を本塁の真後ろ・hl3dMan を消した。python3 v22n_check.py <v2.2.n の URL> <v2.2.m の URL> <three.min.js の写し> <撮る先>
#   (リポジトリの一番上で回す。tests_v2xx/h.py と tests_v2xx/saves/save_A.json を使う)
#   ① パッチ後の <script> が node --check を通る。hl3dMan の定義も呼ぶ所も残っていない
#   ② 顔の番号 hl3dFace:名前から決まる(同じ名前は同じ・違う名前は散らばる・乱数を使わない)。0〜359 の絵が全部描けて、互いに違う(36 種類で 30 以上の違う絵)
#   ③ 観戦の 3D(幅 390・1366):人は全部板で、顔の番号 = 札の data-nm(名前の全体。it.nm に控える)の hl3dFace。1 試合の中で 5 種類以上の顔。板の絵の種類は HL3D_BILL_MAX 以下。札なし・エラーなし
#   ④ 観戦の捕手:プレー前は 3D の位置が 2.5D の位置から x を 22 戻した所(本塁の真後ろ)。捕手が動く場面(hl3_throw.py と同じ作り方で本塁でアウトなど 3 つ)では「元の位置から 20 離れるまでに戻し分が 0」の式どおり。捕手以外は 2.5D の位置のまま
#   ⑤ v2.2.m と比べて、捕手以外の人の位置・腕の角度は同じ時刻で1つも違わない(捕手は x が 22 以内ずれるだけ)
#   ⑥ 2.5D の札:data-nm が名前の全体、見える文字は名字のまま(v2.2.m と同じ)。立体「あり」(2.5D)では札が出る
#   ⑦ 試合画面の背景:野手 7 の顔が 4 種類以上・捕手/待つ打者/ベンチ/ブルペンの板に顔の番号がある。⑲ の帽子の色はチームカラー(hl3d_bg.py ⑲)
#   ⑧ 3D を作る・描く間に Math.random(試合の乱数)を呼ぶ回数が v2.2.m と同じ
import sys, os, re, subprocess, time, json
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

src=open(path_of(URL),encoding="utf-8").read()
js="\n;\n".join(re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",src,re.S)); tmp=os.path.join(OUT,"_check.js"); open(tmp,"w",encoding="utf-8").write(js)
r=subprocess.run(["node","--check",tmp],capture_output=True,text=True); os.remove(tmp)
ok("① node --check・hl3dMan が残っていない", r.returncode==0 and "function hl3dMan(" not in src and not [l for l in src.split("\n") if "hl3dMan(" in l and "/*" not in l], r.stderr[:300])

def open3d(br,url,w,mode="3d"):
    ctx=br.new_context(viewport={"width":w,"height":844 if w<700 else 700}); pg=ctx.new_page(); pg.errs=[]
    pg.on("pageerror",lambda e: pg.errs.append(str(e))); pg.on("dialog",lambda d:(pg.errs.append("DIALOG:"+d.message),d.dismiss()))
    pg.route(CDN,lambda route: route.fulfill(status=200,content_type="application/javascript",body=body))
    pg.add_init_script(SEED_JS%(9,f"localStorage.setItem('pennantHl3d','{mode}');"))
    pg.goto(url,wait_until="domcontentloaded"); pg.wait_for_timeout(400); return pg
QUEUE="""()=>{ for(;;){ while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); }
    setManageMode(false); playNextGameHighlight(); if(highlightQueue.length>=3 || gameIdx>=schedule.length) break; closeHighlights(); }
  hlClearTimers(); return highlightQueue.length; }"""
# 1 場面を描いて自分で時刻を進め、人の位置・腕・顔・捕手の戻し分を集める
STEP="""([i,stage])=>{ let nr=0; const MR=Math.random; Math.random=function(){ nr++; return MR.apply(this,arguments); };
  try{ hlClearTimers(); highlightIdx=i; const ev=highlightQueue[i], r=highlightGameResult;
    if(stage==='pre'){ if(!Array.isArray(ev.pn)) return null; hlRenderPre(r,ev); } else hlRenderPlay(r,ev);
    const S=hl3dCur; if(!S) return {no3d:true}; cancelAnimationFrame(S.raf); S.raf=0; S.frame=()=>{};
    const st=S.st, out={pos:[], cat:[], faces:[], n:0, bills:0, tags:st.querySelectorAll('.hl3tag').length, texN: typeof hl3dBillC!=='undefined'? hl3dBillC.size : -1, catOK:true, catMoved:0};
    const T=[]; if(stage==='pre') T.push(0,.3,1.0); else for(let t=0;t<=S.endT+.001;t+=.05) T.push(+t.toFixed(2));
    const at=(it,t)=>{ if(!it.kf) return [it.x,it.y]; const K=it.kf; let k=0; while(k<K.length-1 && t>=K[k+1][0]) k++; if(k>=K.length-1) return [K[k][1],K[k][2]]; const a=K[k], b=K[k+1], f=Math.max(0,Math.min(1,(t-a[0])/Math.max(1e-6,b[0]-a[0]))); return [a[1]+(b[1]-a[1])*f, a[2]+(b[2]-a[2])*f]; };
    T.forEach(t=>{ hl3dNR(()=>hl3dUpdate(S,t));
      S.items.forEach((it,j)=>{ if(!it.man) return; const B=it.man.userData.bill, isC= it.b.dataset.pos==='捕';
        out.pos.push([j,t,isC? 'C' : '',+it.man.position.x.toFixed(3),+it.man.position.z.toFixed(3),+it.man.userData.arm.rotation.x.toFixed(3),+it.man.userData.glv.rotation.x.toFixed(3)]);
        if(!B) return;
        if(isC && typeof it.cp!=='undefined' && it.cp){ const p=at(it,t), d=Math.hypot(p[0]-it.cp[0],p[1]-it.cp[1]), ex=hl3dP(p[0]-HL3D_CAT_DX*Math.max(0,1-d/20),p[1],0);
          if(d>1) out.catMoved++; if(Math.abs(ex.x-it.man.position.x)>.05 || Math.abs(ex.z-it.man.position.z)>.05) out.catOK=false; out.cat.push([t,+d.toFixed(1),+(ex.x-it.man.position.x).toFixed(2)]); } }); });
    S.items.forEach(it=>{ if(!it.man || !it.man.userData.bill) return; out.faces.push([it.nm||null, it.man.userData.bill.face, it.nm? hl3dFace(it.nm) : null]); });
    out.n=S.items.filter(it=>it.man).length; out.bills=S.items.filter(it=>it.man && it.man.userData.bill).length;
    if(stage==='pre'){ const c=S.items.find(it=>it.man && it.b.dataset.pos==='捕'); if(c){ const p0=hl3dP(c.x,c.y,0), p1=hl3dP(c.x-22,c.y,0); out.catPre=[+c.man.position.x.toFixed(2),+p0.x.toFixed(2),+p1.x.toFixed(2),+c.man.position.z.toFixed(2),+p1.z.toFixed(2)]; }
      const f=S.items.find(it=>it.man && it.fld && it.b.dataset.pos!=='捕'); if(f){ const p=hl3dP(f.x,f.y,0); out.fldPre=[+f.man.position.x.toFixed(2),+p.x.toFixed(2)]; } }
    return out; } finally { Math.random=MR; window.__nr=nr; } }"""

# 捕手が動く場面(hl3_throw.py と同じ作り方:本塁でアウト・二塁走者が本塁で刺される)を 3D で描き、捕手の位置が式どおりか
CASES=[{"kind":"OUT","bp":"G三","pn":[None,None,"三走"],"po":0,"outs":1,"runs":0,"mv":[[0,1]],"af":[1,0,0]},
       {"kind":"1B","pn":[None,"二走","三走"],"po":0,"outs":1,"runs":1,"mv":[[3,4],[0,1]]},
       {"kind":"2B","pn":["一走",None,None],"po":1,"outs":2,"runs":0,"mv":[[0,2]]}]
SYN="""(cases)=>{ const out=[]; cases.forEach(e=>{ hlClearTimers(); const base=highlightQueue[0], r=highlightGameResult;
    const ev=Object.assign({},base,e,{bases:[null,null,null],rn:(e.af||[0,0,0]).map(Boolean),before:base.before,after:base.after,fw:undefined,fwLast:undefined});
    hl3Cam="B"; hlRenderPlay(r,ev); const S=hl3dCur; if(!S){ out.push({no3d:true}); return; } cancelAnimationFrame(S.raf); S.raf=0; S.frame=()=>{};
    const c=S.items.find(it=>it.man && it.b.dataset.pos==='捕'); if(!c){ out.push({noC:true}); return; }
    const at=(it,t)=>{ if(!it.kf) return [it.x,it.y]; const K=it.kf; let k=0; while(k<K.length-1 && t>=K[k+1][0]) k++; if(k>=K.length-1) return [K[k][1],K[k][2]]; const a=K[k], b=K[k+1], f=Math.max(0,Math.min(1,(t-a[0])/Math.max(1e-6,b[0]-a[0]))); return [a[1]+(b[1]-a[1])*f, a[2]+(b[2]-a[2])*f]; };
    let okk=true, moved=0, far=0, dEnd=0, offEnd=0;
    for(let t=0;t<=S.endT+.001;t+=.05){ hl3dNR(()=>hl3dUpdate(S,t)); const p=at(c,t), d=Math.hypot(p[0]-c.cp[0],p[1]-c.cp[1]), off=HL3D_CAT_DX*Math.max(0,1-d/20), ex=hl3dP(p[0]-off,p[1],0);
      if(d>1) moved++; far=Math.max(far,d); dEnd=d; offEnd=off; if(Math.abs(ex.x-c.man.position.x)>.05 || Math.abs(ex.z-c.man.position.z)>.05) okk=false; }
    out.push({kind:e.kind, kf:!!c.kf, moved, far:+far.toFixed(1), dEnd:+dEnd.toFixed(1), offEnd:+offEnd.toFixed(2), ok:okk}); }); return out; }"""
FACES="""()=>{ const a=hl3dFace('山田 太郎'), b=hl3dFace('山田 太郎'), c=hl3dFace('山田 次郎'); const MR=Math.random; let nr=0; Math.random=function(){ nr++; return MR.apply(this,arguments); };
  const names=[]; allTeamsEverywhere().forEach(t=>(t.batters||[]).concat(t.bench||[],t.rotation||[],t.bullpen||[]).forEach(p=>names.push(p.name)));
  const ids=new Set(names.map(hl3dFace)); const U=hl3dUniform(allTeamsEverywhere()[0].name,true);
  const sig=new Set(); let drew=0; for(let f=0;f<360;f++){ const tx=hl3dBillTex(U,'f','stand',true,f); drew++; if(f<36){ const g=tx.image.getContext('2d'); const d=g.getImageData(40,30,60,60).data; let h=0; for(let i=0;i<d.length;i+=4){ h=(h*31+d[i]+d[i+1]*3+d[i+2]*7)>>>0; } sig.add(h); } }
  Math.random=MR; return {same:a===b, diff:a!==c, names:names.length, ids:ids.size, drew, sig:sig.size, cache:hl3dBillC.size, max:HL3D_BILL_MAX, nr, hairFaces:[hl3dFaceOf(0),hl3dFaceOf(359)]}; }"""

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
                    o=pg.evaluate(STEP,[i,stage])
                    if o is None: continue
                    o["nr"]=pg.evaluate("()=>window.__nr"); o["i"]=i; o["stage"]=stage; R.append(o)
            if name=="new" and w==1366: res["faces"]=pg.evaluate(FACES)
            if name=="new": res[("syn",w)]=pg.evaluate(SYN,CASES)
            pg.evaluate("()=>{ hlClearTimers(); highlightIdx=0; const ev=highlightQueue[0]; if(Array.isArray(ev.pn)) hlRenderPre(highlightGameResult,ev); else hlRenderPlay(highlightGameResult,ev); }"); pg.wait_for_timeout(1000)
            pg.locator("#hlStage").screenshot(path=f"{OUT}/kansen_{w}_{name}.png")
            res[(w,name)]=(R,pg.errs,time.time()-t0); pg.context.close()
        N,B=res[(w,"new")],res[(w,"base")]
        if w==1366:
            F=res["faces"]
            ok("② 顔の番号:同じ名前は同じ・違う名前は違う・選手の名前で散らばる・乱数を使わない", F["same"] and F["diff"] and F["ids"]>=min(40,F["names"]//3) and F["nr"]==0, {k:F[k] for k in ("names","ids","nr")})
            ok("② 0〜359 の顔が全部描けて互いに違う(36 種類で 30 以上)・使い回しの上限 256", F["drew"]==360 and F["sig"]>=30 and F["cache"]<=F["max"]==256, {k:F[k] for k in ("drew","sig","cache","max")})
        fc=[f for o in N[0] for f in o["faces"]]
        ok(f"③ {w}px 人が全部板・顔の番号 = 札の名前の hl3dFace・札なし・エラーなし", all(o["n"]==o["bills"]>0 and o["tags"]==0 and o["texN"]<=256 for o in N[0]) and all(f[0] and f[1]==f[2] for f in fc) and not N[1], [(o["n"],o["bills"],o["tags"],o["texN"]) for o in N[0]][:6]+N[1][:2])
        ok(f"③ {w}px 1 試合の中で 5 種類以上の顔", len(set(f[1] for f in fc))>=5, sorted(set(f[1] for f in fc))[:12])
        pre=[o for o in N[0] if o["stage"]=="pre" and o.get("catPre")]
        ok(f"④ {w}px プレー前の捕手が本塁の真後ろ(2.5D の x から 22 戻した所)・捕手以外はそのまま", pre and all(abs(o["catPre"][0]-o["catPre"][2])<.05 and abs(o["catPre"][3]-o["catPre"][4])<.05 and abs(o["catPre"][0]-o["catPre"][1])>5 for o in pre) and all(abs(o["fldPre"][0]-o["fldPre"][1])<.05 for o in pre if o.get("fldPre")), [o["catPre"] for o in pre][:2])
        ok(f"④ {w}px 捕手が動く場面でも式どおり(動いた時刻 {sum(o['catMoved'] for o in N[0])})", all(o["catOK"] for o in N[0]), [o["cat"][-1] for o in N[0] if o["cat"]][:4])
        sy=res[("syn",w)]
        ok(f"④ {w}px 作った場面(本塁でアウトなど)で捕手が動き、式どおり・20 離れたら戻し分 0", all(o.get("kf") and o["moved"]>0 and o["ok"] for o in sy) and any(o["far"]>=20 and o["offEnd"]==0 for o in sy), sy)
        same=[(a["i"],a["stage"]) for a,b in zip(N[0],B[0]) if [p for p in a["pos"] if p[2]!='C']!=[p for p in b["pos"] if p[2]!='C']]
        catd=[abs(p[3]-q[3]) for a,b in zip(N[0],B[0]) for p,q in zip([p for p in a["pos"] if p[2]=='C'],[p for p in b["pos"] if p[2]=='C'])]
        ok(f"⑤ {w}px 捕手以外の位置・腕の角度が v2.2.m と同じ(捕手の x のずれは 22 以内)", len(N[0])==len(B[0]) and not same and sum(len(o["pos"]) for o in N[0])>0 and (not catd or max(catd)<=22.01), [same, sum(len(o["pos"]) for o in N[0]), (min(catd),max(catd)) if catd else None])
        ok(f"⑧ {w}px 3D の間の Math.random の回数が v2.2.m と同じ", [o["nr"] for o in N[0]]==[o["nr"] for o in B[0]], [[o["nr"] for o in N[0]],[o["nr"] for o in B[0]]])
    # ⑥ 2.5D(立体あり)の札
    pg=open3d(br,URL,390,"on"); pg.click("text=はじめる"); pg.wait_for_timeout(200); pg.evaluate("(t)=>loadFromText(t)",SAVE); pg.evaluate(QUEUE)
    t=pg.evaluate("""()=>{ hlClearTimers(); highlightIdx=0; const ev=highlightQueue[0]; if(Array.isArray(ev.pn)) hlRenderPre(highlightGameResult,ev); else hlRenderPlay(highlightGameResult,ev);
      const st=document.getElementById('hlStage'), tags=[...st.querySelectorAll('.hl3tag')]; return [st.classList.contains('hl3d'), tags.length, tags.map(e=>[e.dataset.nm, e.textContent]).slice(0,6), tags.every(e=>e.dataset.nm && e.textContent===hl3Sur(e.dataset.nm))]; }""")
    ok("⑥ 2.5D では札が出る・data-nm は名前の全体・見える文字は名字", t[0]==False and t[1]>0 and t[3], t[:3]); pg.context.close()
    # ⑦ 試合画面の背景
    pg=open3d(br,URL,1366); create(pg,{"numTeams":"6"}); pg.evaluate("()=>{ for(let i=0;i<5;i++) simScheduledGame(); updateMatchup(); }"); pg.click("#mainNav [data-p=game]")
    pg.wait_for_function("()=>!!(hl3dBgS && hl3dBgS.sc)",timeout=20000); pg.wait_for_timeout(800)
    bg=pg.evaluate("""()=>{ const S=hl3dBgS, men=S.men.map(m=>m.userData.bill && m.userData.bill.face), ks={}; S.sc.traverse(o=>{ const B=o.userData && o.userData.bill; if(B){ const k=o.userData.k||'man'; (ks[k]=ks[k]||[]).push(B.face); } });
      return {men, kinds:Object.fromEntries(Object.entries(ks).map(([k,v])=>[k,[v.length,v.filter(x=>x!=null).length,new Set(v).size]]))}; }""")
    pg.screenshot(path=f"{OUT}/bg_1366.png")
    ok("⑦ 背景:野手 7 の顔が 4 種類以上・捕手/待つ打者/ベンチ/ブルペンに顔の番号", len(bg["men"])==8 and all(x is not None for x in bg["men"]) and len(set(bg["men"][:7]))>=4 and all(v[0]==v[1] for v in bg["kinds"].values()) and {"ondeck","bench","pen"}<=set(bg["kinds"]), bg)
    ok("⑦ 背景のエラーなし", not pg.errs, pg.errs[:2]); pg.context.close()
    br.close()
print("NG",bad)
