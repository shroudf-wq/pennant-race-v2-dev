# v2.2.o のテスト:盗塁の場面の動き。python3 v22o_check.py <v2.2.o の URL> <v2.2.n の URL> <three.min.js の写し> <撮る先>
#   (リポジトリの一番上で回す。tests_v2xx/h.py と tests_v2xx/saves/save_A.json を使う)
#   ① パッチ後の <script> が node --check を通る
#   ② 観戦の盗塁死(CS。作った場面):動く野手は遊撃手だけ(中堅手は動かない)。遊撃手は送球が着く 0.9 秒より前に二塁に着く
#   ③ 観戦の盗塁死:一塁の走者が 0 秒に走り出し、二塁で 0.96 秒にアウト(data-mv="1,2"・data-out)。一塁に止まっている札はない。二塁に「アウト」の印
#   ④ 観戦の盗塁成功(SB):動く野手は遊撃手だけ。走者は 0 秒に走り出し 0.85 秒で二塁(アウトの印なし)
#   ⑤ 3D でも同じ:CS で遊撃手の板が二塁へ、走者の板が 0.9 秒に二塁のそば、中堅手は動かない。エラーなし
#   ⑥ じっくり采配の盗塁の結果(hl3MgResultStage):失敗は走者が二塁へ走ってアウト・送球あり・遊撃手が入る。成功は今までどおり(送球なし・走者が二塁へ)
#   ⑦ 盗塁以外の場面(シーズンの最初の 3 試合の観戦)は v2.2.n と台本が同じ(走者・送球・野手の動き)
import sys, os, re, subprocess, json
sys.path.insert(0, os.path.join(os.getcwd(), "tests_v2xx"))
from h import *
URL, BASE, LOCAL, OUT = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]; os.makedirs(OUT, exist_ok=True)
CDN="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"; body=open(LOCAL,"rb").read()
SAVE=open("tests_v2xx/saves/save_A.json",encoding="utf-8").read()
bad=0
def ok(n,c,x=""):
    global bad
    if not c: bad+=1
    print(("PASS " if c else "FAIL ")+n, str(x)[:500], flush=True)
def path_of(u): return u[7:] if u.startswith("file://") else u
src=open(path_of(URL),encoding="utf-8").read()
js="\n;\n".join(re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",src,re.S)); tmp=os.path.join(OUT,"_check.js"); open(tmp,"w",encoding="utf-8").write(js)
r=subprocess.run(["node","--check",tmp],capture_output=True,text=True); os.remove(tmp)
ok("① node --check", r.returncode==0, r.stderr[:300])

def openp(br,url,w,mode):
    ctx=br.new_context(viewport={"width":w,"height":844 if w<700 else 700}); pg=ctx.new_page(); pg.errs=[]
    pg.on("pageerror",lambda e: pg.errs.append(str(e))); pg.on("dialog",lambda d:(pg.errs.append("DIALOG:"+d.message),d.dismiss()))
    pg.route(CDN,lambda route: route.fulfill(status=200,content_type="application/javascript",body=body))
    pg.add_init_script(SEED_JS%(9,f"localStorage.setItem('pennantHl3d','{mode}');"))
    pg.goto(url,wait_until="domcontentloaded"); pg.wait_for_timeout(400)
    pg.click("text=はじめる"); pg.wait_for_timeout(200); pg.evaluate("(t)=>loadFromText(t)",SAVE); return pg
QUEUE="""()=>{ for(;;){ while(gameIdx<schedule.length){ const g=schedule[gameIdx]; if(g[0]===myTeam||g[1]===myTeam) break; simScheduledGame(); }
    setManageMode(false); playNextGameHighlight(); if(highlightQueue.length>=3 || gameIdx>=schedule.length) break; closeHighlights(); }
  hlClearTimers(); return highlightQueue.length; }"""
# 2.5D の台本を読む(作った場面)
SC="""(e)=>{ hlClearTimers(); const base=highlightQueue[0], r=highlightGameResult;
  const ev=Object.assign({},base,e,{before:base.before,after:base.after,fw:undefined,fwLast:undefined,bp:undefined,rp:undefined});
  hl3Cam="B"; hlRenderPlay(r,ev); const st=document.querySelector('#hlStage')||document.querySelector('.hl3stage');
  const kf=[...document.querySelectorAll('#hlSvg .hl3bb[data-kf]')].map(b=>{ const K=b.dataset.kf.split(';').map(q=>q.split(',').map(Number)); return {pos:b.dataset.pos, t1:K[K.length-1][0], x:K[K.length-1][1], y:K[K.length-1][2]}; });
  const mv=[...document.querySelectorAll('#hlSvg .hl3mv')].map(b=>({mv:b.dataset.mv, st:+b.dataset.st, per:+b.dataset.per, out: b.dataset.out!=null? +b.dataset.out : null, nm:(b.querySelector('.hl3tag')||{}).textContent||''}));
  const runs=[...document.querySelectorAll('#hlSvg .hl3run')].map(b=>(b.querySelector('.hl3tag')||{}).textContent||'');
  const marks=document.querySelectorAll('#hlSvg .outMk').length, ball=!!document.querySelector('#hlSvg .hl3ball');
  const bp=HL_BP(); const S=hl3PlayScript(ev,{tr:hlTrajectory(ev,1), af:[0,0,0], names:ev.pn, extend:true});
  return {kf, mv, runs, marks, ball, B2:bp[2], mk:(S.marks||[]).map(m=>[+m.x.toFixed(1),+m.y.toFixed(1),m.t])}; }"""
CS={"kind":"CS","pn":["一走",None,None],"bases":[False,False,False],"rn":[0,0,0],"po":0,"outs":1,"runs":0,"mv":[]}
SB={"kind":"SB","pn":["一走",None,None],"bases":[False,True,False],"rn":[0,1,0],"po":1,"outs":1,"runs":0,"mv":[[1,2]]}
# 3D:作った CS の場面で時刻を進め、遊撃手・中堅手・走者の位置
S3="""(e)=>{ hlClearTimers(); const base=highlightQueue[0], r=highlightGameResult;
  const ev=Object.assign({},base,e,{before:base.before,after:base.after,fw:undefined,fwLast:undefined,bp:undefined,rp:undefined});
  hl3Cam="B"; hlRenderPlay(r,ev); const S=hl3dCur; if(!S) return {no3d:true}; cancelAnimationFrame(S.raf); S.raf=0; S.frame=()=>{};
  const P=it=>[+it.man.position.x.toFixed(2),+it.man.position.z.toFixed(2)], pos=k=>S.items.find(it=>it.man && it.b.dataset.pos===k), run=S.items.find(it=>it.man && it.b.classList.contains('hl3mv'));
  const ss=pos('遊'), cf=pos('中'); const o={}; [0,.5,.9,1.2].forEach(t=>{ hl3dNR(()=>hl3dUpdate(S,t)); o[t]={ss:ss&&P(ss), cf:cf&&P(cf), run:run&&P(run), runOp: run? run.op : null}; });
  const b2=hl3dP(HL_BP()[2][0],HL_BP()[2][1],0); return {o, b2:[+b2.x.toFixed(2),+b2.z.toFixed(2)], hasRun:!!run}; }"""
# 采配の盗塁の結果
MG="""(okk)=>{ const box=document.createElement('div'); box.innerHTML='<div id="mgField"></div>'; document.body.appendChild(box);
  const d={from:"steal", ok:okk, rn: okk? [null,"一走",null] : [null,null,null], batter:"打者", pitcher:"投手", po: okk? 1 : 0, outs:1, inn:5, half:"表"};
  hl3MgResultStage(box,d,["一走",null,null],null,highlightGameResult);
  const f=box.querySelector('#mgField'); const kf=[...f.querySelectorAll('.hl3bb[data-kf]')].map(b=>b.dataset.pos);
  const mv=[...f.querySelectorAll('.hl3mv')].map(b=>({mv:b.dataset.mv, st:+b.dataset.st, out: b.dataset.out!=null? +b.dataset.out : null}));
  const r={kf, mv, ball:!!f.querySelector('.hl3ball'), marks:f.querySelectorAll('.outMk').length, runs:[...f.querySelectorAll('.hl3run')].length}; box.remove(); return r; }"""
# 盗塁以外:観戦の最初の場面たちの台本
SCRIPTS="""()=>{ const out=[]; highlightQueue.forEach((ev,i)=>{ if(ev.kind==="SB"||ev.kind==="CS") return; const seed=i*13+7; const tr=hlTrajectory(ev,seed)||hl3Grounder(ev,seed,hl3Bip(ev));
  const S=hl3PlayScript(ev,{tr, af:(ev.rn||(ev.bases||[]).map(b=>!!b)).map(Boolean), names:ev.pn||[null,null,null], extend:true, fpos:(hl3Bip(ev)||{}).pos});
  out.push(JSON.stringify({r:S.runners, l:S.legs, m:S.marks, c:S.chase, re:S.re, b:S.ball})); }); return out; }"""
with sync_playwright() as p:
    br=p.chromium.launch()
    pg=openp(br,URL,390,"on"); pg.evaluate(QUEUE)
    a=pg.evaluate(SC,CS); print("CS",json.dumps(a,ensure_ascii=False)[:600])
    moved=[k["pos"] for k in a["kf"]]; ss=[k for k in a["kf"] if k["pos"]=="遊"]
    ok("② CS:動く野手は遊撃手だけ・0.9 秒より前に二塁", moved==["遊"] and ss and ss[0]["t1"]<.9, moved)
    m=[x for x in a["mv"] if x["mv"]=="1,2"]
    ok("③ CS:走者 1→2 が 0 秒に出て 0.96 秒にアウト・一塁に札なし・二塁に印", len(m)==1 and m[0]["st"]==0 and abs(m[0]["out"]-.96)<.01 and m[0]["nm"] and not a["runs"] and a["marks"]==1 and a["ball"]
       and abs(a["mk"][0][0]-a["B2"][0])<.2, (m,a["runs"],a["marks"],a["mk"]))
    b=pg.evaluate(SC,SB); print("SB",json.dumps(b,ensure_ascii=False)[:400])
    m=[x for x in b["mv"] if x["mv"]=="1,2"]
    ok("④ SB:動く野手は遊撃手だけ・走者は 0 秒に出て 0.85 秒で二塁・印なし", [k["pos"] for k in b["kf"]]==["遊"] and len(m)==1 and m[0]["st"]==0 and abs(m[0]["per"]-.85)<.01 and m[0]["out"] is None and b["marks"]==0, (b["kf"],m))
    g=pg.evaluate(MG,False); h2=pg.evaluate(MG,True); print("MG",g,h2)
    ok("⑥ 采配の盗塁:失敗は二塁へ走ってアウト・送球・遊撃手/成功は送球なしで二塁へ", g["kf"]==["遊"] and g["ball"] and g["marks"]==1 and g["mv"]==[{"mv":"1,2","st":0,"out":.96}] and g["runs"]==0
       and not h2["ball"] and h2["kf"]==[] and h2["mv"]==[{"mv":"1,2","st":0,"out":None}], (g,h2))
    sc_new=pg.evaluate(SCRIPTS); ok("2.5D:エラーなし", not pg.errs, pg.errs)
    pg.screenshot(path=os.path.join(OUT,"o_mg_390.png"))
    pg2=openp(br,BASE,390,"on"); pg2.evaluate(QUEUE); sc_base=pg2.evaluate(SCRIPTS)
    ok("⑦ 盗塁以外の場面の台本は v2.2.n と同じ", sc_new==sc_base and len(sc_new)>0, (len(sc_new),len(sc_base),sum(1 for x,y in zip(sc_new,sc_base) if x!=y)))
    for w in (390,1366):
        pg3=openp(br,URL,w,"3d"); pg3.wait_for_function("()=>hl3dOk===true",timeout=15000); pg3.evaluate(QUEUE)
        c=pg3.evaluate(S3,CS); print("3D",w,json.dumps(c)[:500])
        if c.get("no3d"): ok(f"⑤ 3D {w}",False,"3D が出ない"); continue
        o=c["o"]; d=lambda u,v: ((u[0]-v[0])**2+(u[1]-v[1])**2)**.5
        ok(f"⑤ 3D {w}:遊撃手が二塁へ・走者が 0.9 秒に二塁のそば・中堅手は動かない・エラーなし",
           c["hasRun"] and d(o["0.9"]["ss"],c["b2"])<8 and d(o["0"]["ss"],c["b2"])>8 and d(o["0.9"]["run"],c["b2"])<10 and d(o["0"]["cf"],o["1.2"]["cf"])<.01 and not pg3.errs, (o,c["b2"],pg3.errs))
        pg3.evaluate("(e)=>{ hlClearTimers(); const base=highlightQueue[0]; const ev=Object.assign({},base,e,{before:base.before,after:base.after,fw:undefined,fwLast:undefined,bp:undefined,rp:undefined}); hl3Cam='B'; hlRenderPlay(highlightGameResult,ev); }",CS)
        pg3.wait_for_timeout(950); pg3.screenshot(path=os.path.join(OUT,f"o_cs3d_{w}.png"))
    br.close()
print("NG",bad)
