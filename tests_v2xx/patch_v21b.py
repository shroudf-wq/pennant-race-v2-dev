# v2.1.a のソースに当てると v2.1.b(3D の絵。Three.js r128)。python3 patch_v21b.py src.html new.html
# 見た目だけ。試合の計算・記録・セーブには触らない。
#   ・設定「立体」に「3D」を足す(端末ごと)。選ぶと Three.js を読み、読めるまで・読めないときは「あり」(2.5D)で描く
#   ・3D の作り:2.5D と同じ舞台の HTML(hl3StageHtml。動きは台本 hl3PlayScript が data-* に書いたもの)を使い、
#       地面・フェンス・観客席・人(カプセル形)・ボールだけを WebGL で描く。地面の絵は 2.5D の SVG(球場の広さ・芝・屋根・スタイルの色)をそのまま貼る
#       札・文字・アウトの印・名前の帯・ボールカウントは HTML のまま、3D の点を画面に写した所へ毎コマ置く(札の重なりをほどく hl3Declutter もそのまま効く)
#     → 観戦(つなぎ・プレー前・プレー)も、じっくり采配(場面・結果)も、同じ道で 3D になる
#   ・カメラは B・E・G・C(と D・A)を本物の 3D のカメラにした(HL3D_CAMS)。切り替えは 2.5D と同じ(B↔E/G は 0.45 秒で回す、C へは暗転)
#   ・途中で失敗した・WebGL が切れたときは hl3dBroken にして、それからあとは 2.5D
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.a"; const BASE_V1="v1.2.v";','const APP_VERSION="v2.1.b"; const BASE_V1="v1.2.v";')

# ===== 設定 =====
rep("""          <option value="on">あり(場面でカメラを切り替える)</option>""",
    """          <option value="3d">3D(Three.js。読めないときは「あり」)</option>
          <option value="on">あり(場面でカメラを切り替える)</option>""")
rep("""          <option value="off">なし(2D)</option>
        </select>""","""          <option value="off">なし(2D)</option>
        </select>
        <span id="hl3dNote" class="small"></span>""")
rep("""let HL3D="on"; try{ const v=localStorage.getItem("pennantHl3d"); if(v==="on"||v==="weak"||v==="off") HL3D=v; }catch(e){}
function setHl3d(v){ if(!(v==="on"||v==="weak"||v==="off")) return; HL3D=v; try{ localStorage.setItem("pennantHl3d",v); }catch(e){} hl3Sync(); }""",
"""let HL3D="on"; try{ const v=localStorage.getItem("pennantHl3d"); if(v==="on"||v==="weak"||v==="off"||v==="3d") HL3D=v; }catch(e){}
function setHl3d(v){ if(!(v==="on"||v==="weak"||v==="off"||v==="3d")) return; HL3D=v; try{ localStorage.setItem("pennantHl3d",v); }catch(e){} hl3Sync(); if(v==="3d") hl3dPrep(); }
// v2.1.b:3D を選んだら Three.js を読む(読めるまでは「あり」で描く)
function hl3dPrep(){ const note=t=>{ const n=document.getElementById("hl3dNote"); if(n) n.textContent=t; };
  if(hl3dOk){ note(""); return; } note("3D を読み込み中…");
  hl3dLoad().then(ok=>{ hl3dOk=ok; note(ok? "" : "3D を読み込めなかったので、「あり」(2.5D)で表示します"); }); }""")
rep("""hlOptSync(); hl3Sync(); bxSettingsSync();""","""hlOptSync(); hl3Sync(); bxSettingsSync(); if(HL3D==="3d") hl3dPrep();""")

# ===== 舞台の印(3D で描く舞台は .hl3d) =====
rep("""  return `<div class="hlStage hl3${c.flip? " flip" : ""}${HL3D==="weak"? " hl3flat" : ""}${hl3Park&&hl3Park.dome? " pkDome" : ""}" id="${id}\"""",
    """  return `<div class="hlStage hl3${c.flip? " flip" : ""}${HL3D==="weak"? " hl3flat" : ""}${hl3Park&&hl3Park.dome? " pkDome" : ""}${hl3dReady()? " hl3d" : ""}" id="${id}\"""")

# ===== CSS =====
rep(""".hl3.hl3flat .hl3shade{display:none}""",""".hl3.hl3flat .hl3shade{display:none}
/* v2.1.b:3D。地面の SVG は絵の元として残して隠す。札・文字は .hl3dLab に移し、3D の点を画面に写した所へ置く(大きさは --ls) */
.hlStage.hl3d .hl3cam{visibility:hidden}
.hl3dCv{position:absolute;left:0;top:0;width:100%;height:100%;display:block;z-index:0}
.hl3dLab{position:absolute;inset:0;pointer-events:none;overflow:hidden;z-index:1}
.hl3dLab .hl3bb{transform-style:flat;will-change:transform}
.hl3d .hl3cap{display:none}
.hl3d .hl3dLab .hl3tag{bottom:2px;transform-origin:50% 100%;transform:translateX(-50%) scale(var(--ls,1.5)) translate(var(--ox,0px),var(--oy,0px))}
.hl3d .hl3dLab .hl3txt{transform-origin:50% 100%;transform:translateX(-50%) scale(var(--ls,1.5)) translate(var(--ox,0px),var(--oy,0px))}
.hl3d .hl3dLab .hl3txt.outMk{animation-name:hl3OutMk3}
@keyframes hl3OutMk3{0%{opacity:0;transform:translateX(-50%) scale(calc(var(--ls,1.5)*1.5))}12%{opacity:1;transform:translateX(-50%) scale(var(--ls,1.5))}75%{opacity:1;transform:translateX(-50%) scale(var(--ls,1.5))}100%{opacity:0;transform:translateX(-50%) scale(var(--ls,1.5))}}""")

# ===== 3D の本体 =====
rep("""let hl3RO=null;""",r"""/* ===== v2.1.b:3D の絵(Three.js r128。読み込みは hl3dLoad) =====
   2.5D と同じ舞台の HTML を使い、地面・フェンス・観客席・人・ボールだけを WebGL で描く。札・文字・名前の帯・ボールカウントは HTML のまま、
   3D の点を画面に写した所へ毎コマ置く(hl3Declutter もそのまま効く)。動きは台本(hl3PlayScript)が data-* に書いたものを読む(2.5D の hl3After と同じ時刻)。
   座標:地面の図の (x,y) と高さ z → 3D の (x−150, z, y−212)。本塁が原点、外野が −Z、上が +Y */
let hl3dOk=false, hl3dBroken=false, hl3dR=null, hl3dCur=null; const hl3dTex=new Map(), hl3dGeoC={};
function hl3dReady(){ return HL3D==="3d" && hl3dOk && !hl3dBroken && !!(window.THREE && window.THREE.WebGLRenderer) && animEnabled(); }
// カメラ:p=位置、t=見る点(3D の座標)、fov=縦の画角。300:230 より細い枠では、横が切れないよう画角を広げる(hl3dFov)
const HL3D_CAMS={   // 本塁・捕手・打者と外野のフェンス(いちばん広い球場)が枠の 9 割に収まり、上下の真ん中に来る所を、見下ろす角度を決めて計算で選んだ(tests_v2xx/hl3d_camfit.js)
  B:{p:[0,200,80],      t:[0,0,-85],  fov:45},   // バックネット裏(打席・打球のない場面)。見下ろし 51°。上の 15% は名前の帯のためにあける(外野のフェンスが枠の上から 15% より下)
  E:{p:[-131.75,205,82.15],t:[-10,0,-100],fov:45}, // 三塁側(左への打球)。43°
  G:{p:[131.75,205,82.15], t:[10,0,-100], fov:45}, // 一塁側(右への打球)。43°
  C:{p:[0,150,-285],    t:[0,0,-130], fov:45},   // 外野席(本塁打)。44°
  D:{p:[0,230,60],      t:[0,0,-80],  fov:45},
  A:{p:[0,230,120],     t:[0,0,-60],  fov:45},
};
function hl3dFov(f,asp){ const A0=300/230; return asp>=A0? f : 2*Math.atan(Math.tan(f*Math.PI/360)*A0/asp)*180/Math.PI; }
function hl3dP(x,y,z){ return new THREE.Vector3(x-HL_HX, z||0, y-HL_HY); }
function hl3dEase(x1,y1,x2,y2){   // CSS の cubic-bezier と同じ
  const A=(a,b)=>1-3*b+3*a, B=(a,b)=>3*b-6*a, C=a=>3*a, bz=(t,a,b)=>((A(a,b)*t+B(a,b))*t+C(a))*t, sl=(t,a,b)=>3*A(a,b)*t*t+2*B(a,b)*t+C(a);
  return x=>{ if(x<=0) return 0; if(x>=1) return 1; let t=x; for(let i=0;i<8;i++){ const d=bz(t,x1,x2)-x, s=sl(t,x1,x2); if(Math.abs(d)<1e-5 || Math.abs(s)<1e-6) break; t-=d/s; } return bz(Math.min(1,Math.max(0,t)),y1,y2); };
}
const hl3dFlyE=hl3dEase(.2,.7,.35,1), hl3dCamE=hl3dEase(.4,0,.2,1);
function hl3dGeo(k){ const T=THREE; if(hl3dGeoC[k]) return hl3dGeoC[k];
  const g= k==="plane"? new T.PlaneGeometry(300,230) : k==="body"? new T.CylinderGeometry(2.1,2.5,6,12) : k==="head"? new T.SphereGeometry(2.2,12,8)
    : k==="shadow"? new T.CircleGeometry(3.2,16) : k==="ball"? new T.SphereGeometry(1.9,12,8) : k==="disc"? new T.CircleGeometry(2.4,12) : new T.RingGeometry(5,6.4,32);
  return hl3dGeoC[k]=g; }
function hl3dRenderer(){ if(hl3dR) return hl3dR; const r=new THREE.WebGLRenderer({antialias:true}); r.setPixelRatio(Math.min(2,window.devicePixelRatio||1)); r.domElement.className="hl3dCv";
  r.domElement.addEventListener("webglcontextlost",e=>{ e.preventDefault(); hl3dBroken=true; hl3dStop(); }); return hl3dR=r; }
// 地面の絵:2.5D の SVG の写しに、計算済みの色を書き込んで画像にする(打球の線・光・脈・打者の輪は 3D で別に描くので外す)。同じ絵は使い回す
function hl3dFieldTex(svg,done){
  const src=[...svg.querySelectorAll("*")], cl=svg.cloneNode(true), dst=[...cl.querySelectorAll("*")];
  const P=["fill","fill-opacity","stroke","stroke-width","stroke-opacity","opacity","stroke-dasharray","stroke-linecap"];
  src.forEach((e,i)=>{ const d=dst[i]; if(!d) return; const cs=getComputedStyle(e); P.forEach(p=>{ const v=cs.getPropertyValue(p); if(v) d.style.setProperty(p,v); }); });
  cl.querySelectorAll(".f-trail,.f-ball,.f-burst,.f-pulse,.batRing,.f-runner,text,animate,animateMotion,animateTransform").forEach(x=>x.remove());
  cl.setAttribute("xmlns","http://www.w3.org/2000/svg"); cl.setAttribute("width","1200"); cl.setAttribute("height","920"); cl.setAttribute("preserveAspectRatio","none"); cl.removeAttribute("class");
  const key=new XMLSerializer().serializeToString(cl), hit=hl3dTex.get(key); if(hit){ done(hit); return; }
  const img=new Image();
  img.onload=()=>{ try{ const cv=document.createElement("canvas"); cv.width=1200; cv.height=920; cv.getContext("2d").drawImage(img,0,0,1200,920);
      const tx=new THREE.CanvasTexture(cv); tx.anisotropy=4;
      if(hl3dTex.size>=6){ const k0=hl3dTex.keys().next().value; hl3dTex.get(k0).dispose(); hl3dTex.delete(k0); }
      hl3dTex.set(key,tx); done(tx); }catch(e){} };
  img.src="data:image/svg+xml;charset=utf-8,"+encodeURIComponent(key);
}
function hl3dMan(col,own){ const T=THREE, g=new T.Group(), m=new T.MeshLambertMaterial({color:col,transparent:true}), sm=new T.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.32,depthWrite:false});
  own.push(m,sm); const b=new T.Mesh(hl3dGeo("body"),m), h=new T.Mesh(hl3dGeo("head"),m), sh=new T.Mesh(hl3dGeo("shadow"),sm);
  b.position.y=3.2; h.position.y=8; sh.rotation.x=-Math.PI/2; sh.position.y=.15; g.add(sh,b,h); g.userData.mats=[m,sm]; g.userData.op=[1,.32]; return g; }
function hl3dStop(){ const S=hl3dCur; if(!S) return; hl3dCur=null; if(S.raf) cancelAnimationFrame(S.raf); S.own.forEach(o=>{ try{ o.dispose(); }catch(e){} }); }
function hl3dKick(){ const S=hl3dCur; if(S && !S.raf && S.st.isConnected) S.raf=requestAnimationFrame(S.frame); }
function hl3dSize(S){ const W=S.st.clientWidth||300, H=S.st.clientHeight||230; S.W=W; S.H=H; hl3dR.setSize(W,H,false); S.cam.aspect=W/H;
  S.st.style.setProperty("--ls",Math.max(1.05,Math.min(2.4,Math.min(W/300,H/230)*1.3)).toFixed(3)); }
function hl3dStart(st){
  const T=THREE, R=hl3dRenderer(); hl3dStop();
  const own=[], sc=new T.Scene();
  try{ const cs=getComputedStyle(st); sc.background=new T.Color((cs.getPropertyValue("--hl3bg")||"").trim()||cs.backgroundColor||"#0f2418"); }catch(e){ sc.background=new T.Color(0x0f2418); }
  sc.add(new T.AmbientLight(0xffffff,.78)); const dl=new T.DirectionalLight(0xffffff,.5); dl.position.set(-60,150,110); sc.add(dl);
  const pk=hl3Park, FR=pk? pk.R : HL_FR, add=(geo,mat)=>{ own.push(geo,mat); const m=new T.Mesh(geo,mat); sc.add(m); return m; };
  // 地面(2.5D の SVG を貼る。絵ができるまでは芝の色)
  const gm=new T.MeshBasicMaterial({color:0x2e6b40}); own.push(gm); const gp=new T.Mesh(hl3dGeo("plane"),gm); gp.rotation.x=-Math.PI/2; gp.position.set(0,0,115-HL_HY); sc.add(gp);
  const svg=st.querySelector(".hl3world svg"); if(svg) hl3dFieldTex(svg,tx=>{ gm.map=tx; gm.color.set(0xffffff); gm.needsUpdate=true; hl3dKick(); });
  // フェンス・観客席・屋根(扇の角度 45°〜135° は、three の円柱では 135°〜225°)
  const th0=Math.PI*.75, thL=Math.PI*.5;
  const fence=add(new T.CylinderGeometry(FR,FR,7,48,1,true,th0,thL), new T.MeshLambertMaterial({color:0x1d4a30,side:T.DoubleSide})); fence.position.y=3.5;
  const stands=add(new T.CylinderGeometry(FR+86,FR+5,40,48,1,true,th0,thL), new T.MeshLambertMaterial({color:(pk&&pk.dome)? 0x1a2027 : 0x2b3540,side:T.DoubleSide})); stands.position.y=20;
  if(pk && pk.dome){ const dm=add(new T.SphereGeometry(FR+110,28,10,0,Math.PI*2,0,Math.PI*.42), new T.MeshBasicMaterial({color:0xaab3bd,wireframe:true,transparent:true,opacity:.14})); dm.position.set(0,-40,-70); }
  // 人と札(.hl3bb。カプセルの印 .hl3cap があれば人を立てる)
  const items=[];
  st.querySelectorAll(".hl3world .hl3bb").forEach(b=>{
    const cap=b.querySelector(".hl3cap"), it={b, x:+b.dataset.x, y:+b.dataset.y, z:+(b.dataset.z||0), mv: b.dataset.mv? b.dataset.mv.split(",").map(Number) : null,
      st:+(b.dataset.st||0), per:+(b.dataset.per||HL_PER), out: b.dataset.out!=null? +b.dataset.out : null, man:null, op:1};
    if(cap){ it.man=hl3dMan(cap.classList.contains("f")? 0xece8dc : cap.classList.contains("b")? 0xc0392b : 0xf2c94c, own); sc.add(it.man); }
    items.push(it); });
  // ボール・打球の線
  let fly=null; const be=st.querySelector(".hl3ball");
  if(be && be.dataset.fly){ const [ex,ey,h]=be.dataset.fly.split(",").map(Number), legs=(be.dataset.legs||"").split(";").filter(Boolean).map(q=>q.split(",").map(Number));
    const bm=add(hl3dGeo("ball").clone(), new T.MeshBasicMaterial({color:0xffffff})), bs=add(hl3dGeo("disc").clone(), new T.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.35,depthWrite:false})); bs.rotation.x=-Math.PI/2;
    const N=32, pos=new Float32Array((N+1)*3);
    for(let i=0;i<=N;i++){ const u=i/N, v=hl3dP(HL_HX+(ex-HL_HX)*u, (HL_HY-6)+(ey-(HL_HY-6))*u, .4); pos[i*3]=v.x; pos[i*3+1]=v.y; pos[i*3+2]=v.z; }
    const lg=new T.BufferGeometry(); lg.setAttribute("position",new T.BufferAttribute(pos,3)); lg.setDrawRange(0,0);
    const lm=new T.LineBasicMaterial({color:0xffffff,transparent:true,opacity:.75}); own.push(lg,lm); const line=new T.Line(lg,lm); sc.add(line);
    fly={ex,ey,h,legs,bm,bs,lg,N}; }
  // 本塁打の光・投手交代の脈・打者の輪(2.5D では地面の SVG にあるもの)
  const ring=(x,y,col,op)=>{ const m=add(hl3dGeo("ring").clone(), new T.MeshBasicMaterial({color:col,transparent:true,opacity:op,side:T.DoubleSide,depthWrite:false})); m.rotation.x=-Math.PI/2; m.position.copy(hl3dP(x,y,.5)); return m; };
  const burst= (svg && svg.querySelector(".f-burst") && fly)? ring(fly.ex,Math.max(fly.ey,18),0xffd34d,0) : null;
  const pulse= (svg && svg.querySelector(".f-pulse"))? ring(HL_HX,HL_HY-45,0xffffff,0) : null;
  if(svg && svg.querySelector(".batRing")) ring(HL_HX-14,HL_HY-6,0xffffff,.55).scale.setScalar(.9);
  // カメラ(切り替え:暗転がなければ 0.45 秒で回す)
  const to=st.dataset.to, from=st.dataset.cam, cut=!!st.querySelector(".hl3cut"), C1=HL3D_CAMS[to]||HL3D_CAMS.B, C0=(from!==to && !cut)? (HL3D_CAMS[from]||C1) : C1;
  const cam=new T.PerspectiveCamera(C1.fov,1.3,1,3000);
  // 置く
  const S={st,sc,cam,items,fly,burst,pulse,own,C0,C1,t0:performance.now(),raf:0,W:300,H:230,frame:null};
  hl3dCur=S; hl3dSize(S);
  st.insertBefore(R.domElement, st.firstChild);
  const lab=document.createElement("div"); lab.className="hl3dLab"; items.forEach(it=>lab.appendChild(it.b)); st.insertBefore(lab, R.domElement.nextSibling);
  let mvEnd=0; items.forEach(it=>{ if(!it.mv) return; const n=it.mv[1]-it.mv[0]; mvEnd=Math.max(mvEnd,(it.st+n*it.per)*1000+(it.mv[1]===4? 260 : 0)); });
  S.endT=Math.max(2.2, mvEnd/1000+.4, ...items.filter(it=>it.out!=null).map(it=>it.out+.9), fly? (fly.legs.length? fly.legs[fly.legs.length-1][5]+.3 : 1.1) : 0, burst? 1.9 : 0, pulse? 2.6 : 0);
  S.frame=()=>{ if(hl3dCur!==S) return; S.raf=0; if(!st.isConnected){ hl3dStop(); return; }
    const t=(performance.now()-S.t0)/1000;
    try{ hl3dUpdate(S,t); R.render(sc,cam); }catch(e){ hl3dBroken=true; hl3dStop(); return; }
    if(t<S.endT) S.raf=requestAnimationFrame(S.frame); };
  hl3dUpdate(S,0); R.render(sc,cam); S.raf=requestAnimationFrame(S.frame);
  // 札の重なりをほどく(2.5D と同じ時刻:カメラが落ち着いてから・走り終えてから)
  setTimeout(()=>hl3Declutter(st,true), C0!==C1? 520 : 40);
  if(mvEnd>0) setTimeout(()=>hl3Declutter(st,true), Math.max(mvEnd+40,560));
}
function hl3dUpdate(S,t){
  const T=THREE, bp=HL_BP();
  // カメラ
  const k= S.C0===S.C1? 1 : hl3dCamE(Math.min(1,t/.45)), L=(a,b)=>a+(b-a)*k;
  S.cam.position.set(L(S.C0.p[0],S.C1.p[0]),L(S.C0.p[1],S.C1.p[1]),L(S.C0.p[2],S.C1.p[2]));
  S.cam.fov=hl3dFov(L(S.C0.fov,S.C1.fov),S.cam.aspect); S.cam.updateProjectionMatrix();
  S.cam.lookAt(L(S.C0.t[0],S.C1.t[0]),L(S.C0.t[1],S.C1.t[1]),L(S.C0.t[2],S.C1.t[2])); S.cam.updateMatrixWorld();
  // ボール:本塁 → 落点(0.9 秒・高さ h の放物線)、続けて送球(低い弧)
  const F=S.fly;
  if(F){ let x,y,z; const sx=HL_HX, sy=HL_HY-6;
    if(t<=.9){ const u=hl3dFlyE(t/.9); x=sx+(F.ex-sx)*u; y=sy+(F.ey-sy)*u; z=4*F.h*u*(1-u); F.lg.setDrawRange(0,Math.max(2,Math.round(u*F.N)+1)); }
    else { x=F.ex; y=F.ey; z=0; F.lg.setDrawRange(0,F.N+1);
      for(const q of F.legs){ const [x0,y0,x1,y1,a,b]=q; if(t<a) break; const u=Math.min(1,(t-a)/Math.max(.06,b-a)), hh=Math.min(9,Math.hypot(x1-x0,y1-y0)/16); x=x0+(x1-x0)*u; y=y0+(y1-y0)*u; z=3+4*hh*u*(1-u); } }
    F.bm.position.copy(hl3dP(x,y,z+1.9)); F.bs.position.copy(hl3dP(x,y,.25)); F.bs.material.opacity=Math.max(.12,.4-z/150); }
  if(S.burst){ const q=(t-.85)/.9; if(q>0 && q<1){ S.burst.scale.setScalar(.6+3.2*q); S.burst.material.opacity=Math.sin(q*Math.PI); } else S.burst.material.opacity=0; }
  if(S.pulse){ const q=(t*1.1)%1; S.pulse.scale.setScalar(1+q*1.4); S.pulse.material.opacity=(t<2.4)? (1-q)*.8 : 0; }
  // 走者(塁の線を滑る)と札の置き場所
  S.items.forEach(it=>{ let x=it.x, y=it.y, op=1;
    if(it.mv){ const [a,b]=it.mv, n=b-a;
      if(n>0 && t>it.st){ const qq=Math.min(n,(t-it.st)/it.per), i=Math.min(n-1,Math.floor(qq)), f=qq-i, P0=bp[a+i], P1=bp[a+i+1]; x=P0[0]+(P1[0]-P0[0])*f; y=P0[1]+(P1[1]-P0[1])*f-6; }
      const arr=it.st+n*it.per;
      if(it.out!=null){ if(t>it.out+.45) op=Math.max(0,1-(t-it.out-.45)/.3); } else if(b===4 && t>arr) op=Math.max(0,1-(t-arr)/.25); }
    if(it.man){ it.man.position.copy(hl3dP(x,y,0)); if(op!==it.op){ it.man.visible=op>.01; it.man.userData.mats.forEach((m,j)=>{ m.opacity=it.man.userData.op[j]*op; }); } }
    if(op!==it.op){ it.b.style.opacity= op>=1? "" : op.toFixed(3); it.op=op; }
    const v=hl3dP(x,y,it.man? 11 : it.z).project(S.cam);
    it.b.style.transform=`translate(${((v.x+1)/2*S.W).toFixed(1)}px,${((1-v.y)/2*S.H).toFixed(1)}px)`;
    it.b.style.visibility= (v.z>1)? "hidden" : "";
  });
}
let hl3RO=null;""")
# 枠が変わったら 3D も合わせる
rep("""function hl3Fit(st){ if(!st || !st.isConnected) return; const w=st.clientWidth, h=st.clientHeight; if(!w||!h) return;""",
    """function hl3Fit(st){ if(!st || !st.isConnected) return; const w=st.clientWidth, h=st.clientHeight; if(!w||!h) return;
  if(hl3dCur && hl3dCur.st===st){ try{ hl3dSize(hl3dCur); hl3dUpdate(hl3dCur,(performance.now()-hl3dCur.t0)/1000); hl3dR.render(hl3dCur.sc,hl3dCur.cam); }catch(e){} }   // v2.1.b
 """)
# 差し込んだあと:3D の舞台は 3D で動かす(失敗したら 2.5D に戻る)
rep("""  const to=st.dataset.to, from=st.dataset.cam, c=HL3_CAMS[to]||HL3_CAMS.B;
  const place=()=>{""","""  if(st.classList.contains("hl3d")){   // v2.1.b:3D
    if(!hl3dReady()) st.classList.remove("hl3d");
    else try{ hl3dStart(st); hl3Cam=st.dataset.to; return; }catch(e){ hl3dBroken=true; hl3dStop(); st.classList.remove("hl3d"); const cv=st.querySelector(".hl3dCv"); if(cv) cv.remove(); const lb=st.querySelector(".hl3dLab"); if(lb){ const w=st.querySelector(".hl3world"); [...lb.children].forEach(b=>w.appendChild(b)); lb.remove(); } }
  }
  if(hl3dCur && hl3dCur.st!==st) hl3dStop();
  const to=st.dataset.to, from=st.dataset.cam, c=HL3_CAMS[to]||HL3_CAMS.B;
  const place=()=>{""")
# ===== 試合の乱数を Three.js に使わせない(決め事:演出の乱数は試合の乱数と別) =====
#   Three.js は物・材質・形・絵を作るたびに Math.random を4回使う(内部の番号 uuid)。読み込んだときにも自分の物をいくつか作る。
#   作る・描くときは Math.random を 3D 専用の乱数(hl3dRand)に差し替えてすぐ戻し(hl3dNR)、読み込みのときは Three.js の script が動いている間だけ差し替える
rep("""    try{ const el=document.createElement("script"); el.src=window.HL3D_THREE_URL||HL3D_THREE_URL; el.async=true; el.crossOrigin="anonymous";
      el.onload=()=>fin(true); el.onerror=()=>fin(false); document.head.appendChild(el); }catch(e){ fin(false); }""",
"""    try{ const el=document.createElement("script"), nat=Math.random, px=function(){ return (document.currentScript===el)? hl3dRand() : nat.apply(this,arguments); };
      const back=()=>{ if(Math.random===px) Math.random=nat; };   // v2.1.b:Three.js が読み込みのときに使う乱数は 3D 専用に
      el.src=window.HL3D_THREE_URL||HL3D_THREE_URL; el.async=true; el.crossOrigin="anonymous";
      el.onload=()=>{ back(); fin(true); }; el.onerror=()=>{ back(); fin(false); }; Math.random=px; document.head.appendChild(el); setTimeout(back,8000); }catch(e){ fin(false); }""")
rep("""const hl3dFlyE=hl3dEase(.2,.7,.35,1), hl3dCamE=hl3dEase(.4,0,.2,1);""","""const hl3dFlyE=hl3dEase(.2,.7,.35,1), hl3dCamE=hl3dEase(.4,0,.2,1);
// 3D 専用の乱数(Three.js の内部の番号だけに使う。試合の乱数とは別)
let hl3dSeed=0x2545F491; function hl3dRand(){ hl3dSeed=(hl3dSeed+0x6D2B79F5)|0; let t=Math.imul(hl3dSeed^hl3dSeed>>>15,1|hl3dSeed); t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; }
function hl3dNR(fn){ const r=Math.random; Math.random=hl3dRand; try{ return fn(); } finally{ Math.random=r; } }""")
rep("""function hl3dStart(st){
  const T=THREE, R=hl3dRenderer(); hl3dStop();""","""function hl3dStart(st){ return hl3dNR(()=>hl3dStart0(st)); }
function hl3dStart0(st){
  const T=THREE, R=hl3dRenderer(); hl3dStop();""")
rep("""    try{ hl3dUpdate(S,t); R.render(sc,cam); }catch(e){ hl3dBroken=true; hl3dStop(); return; }""",
    """    try{ hl3dNR(()=>{ hl3dUpdate(S,t); R.render(sc,cam); }); }catch(e){ hl3dBroken=true; hl3dStop(); return; }""")
rep("""  img.onload=()=>{ try{ const cv=document.createElement("canvas"); cv.width=1200; cv.height=920; cv.getContext("2d").drawImage(img,0,0,1200,920);
      const tx=new THREE.CanvasTexture(cv); tx.anisotropy=4;""","""  img.onload=()=>{ try{ const cv=document.createElement("canvas"); cv.width=1200; cv.height=920; cv.getContext("2d").drawImage(img,0,0,1200,920);
      const tx=hl3dNR(()=>new THREE.CanvasTexture(cv)); tx.anisotropy=4;""")
rep("""hl3dSize(hl3dCur); hl3dUpdate(hl3dCur,(performance.now()-hl3dCur.t0)/1000); hl3dR.render(hl3dCur.sc,hl3dCur.cam); }catch(e){} }""",
    """hl3dNR(()=>{ hl3dSize(hl3dCur); hl3dUpdate(hl3dCur,(performance.now()-hl3dCur.t0)/1000); hl3dR.render(hl3dCur.sc,hl3dCur.cam); }); }catch(e){} }""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
