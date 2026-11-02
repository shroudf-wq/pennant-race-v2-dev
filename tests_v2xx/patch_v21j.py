# v2.1.i のソースに当てると v2.1.j。python3 patch_v21j.py src.html new.html
# 試合画面の背景を 3D の球場にする(決め事 10)。見た目だけ。試合の計算・記録・セーブには触らない(乱数は 3D 専用の hl3dRand)。
#   ・試合タブの上のカード(スコアボードとボタン)の後ろに、夜の球場をバックネット裏から見た絵を描く(専用の WebGL の描き手 hl3dBgR)
#   ・球場は次の試合のホームチームのもの(広さ・芝・屋根・帯の色。球場の個性なしのリーグは標準)。試合がないとき(オフなど)は自チーム。地面の色はスタイルに合わせる
#   ・9人の野手が守備位置に立つ。照明塔に光のにじみ。星。カメラはゆっくり左右に揺れる(24 秒で1往復)
#   ・描くのは、試合タブが開いていて、画面に見えていて、観戦などの窓が開いていないときだけ(1 秒に 30 コマまで)
#   ・v1 の HTML には触らない:起動のときにカードに .hl3bgCard を付けて背景の箱を差し込む。updateMatchup のあとに背景を合わせる(関数を包む)
#   ・立体が「3D」で描けるときだけ。設定の「立体」の下に「試合画面に 3D の球場を出す」(端末ごと・pennantHl3dBg。初めはあり)
#   ・観戦の球場を作る部分を hl3dParkMeshes に切り出した(観戦の絵は変えない)。hl3ParkFor は hl3ParkOf(読むだけ)を呼ぶ形に
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.i"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.j"; const BASE_V1="v1.4.b";')

# ===== CSS =====
rep(""".hl3dCv{position:absolute;left:0;top:0;width:100%;height:100%;display:block;z-index:0}""",
""".hl3dCv{position:absolute;left:0;top:0;width:100%;height:100%;display:block;z-index:0}
/* v2.1.j:試合画面の背景の球場 */
.hl3bgCard{position:relative;isolation:isolate;overflow:hidden}
.hl3dBg{position:absolute;left:0;top:0;width:100%;z-index:-1;pointer-events:none;overflow:hidden;border-radius:inherit}
.hl3dBg canvas{display:block;width:100%;height:100%}
.hl3dBg::after{content:"";position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,.18) 0%,rgba(0,0,0,0) 30%,rgba(0,0,0,.08) 62%,var(--hl3bgFade,transparent) 100%)}
.hl3bgOn{background:transparent!important}
.hl3bgOn .manageToggle,.hl3bgOn #nextStep{background:rgba(8,14,22,.62);color:#f3efe2;border-radius:999px;padding:6px 14px;width:fit-content;max-width:100%;margin-left:auto;margin-right:auto;box-sizing:border-box}
.hl3bgOn{padding-top:var(--hl3bgTop,64px)!important}
.hl3bgOn #nextStep:empty{display:none}
.hl3bgOn #actionBar button.sec{background-color:var(--hl3bgFade,#16241c)}
.hl3bgOn .matchup{box-shadow:0 10px 26px rgba(0,0,0,.45);margin-bottom:var(--hl3bgGap,72px)}""")

# ===== 設定:試合画面に 3D の球場を出す =====
rep("""        <span id="hl3dNote" class="small"></span>
      </div>""","""        <span id="hl3dNote" class="small"></span>
      </div>
      <label style="display:flex;align-items:center;gap:10px;min-height:44px;cursor:pointer">
        <input type="checkbox" id="hl3dBgChk" onchange="setHl3dBg(this.checked)" style="width:22px;height:22px;accent-color:var(--gold)">
        <span>試合画面に 3D の球場を出す(立体が「3D」のとき)</span>
      </label>""")
rep("""function hl3Sync(){ const e=document.getElementById("hl3dSel"); if(e) e.value=HL3D; }""",
"""function hl3Sync(){ const e=document.getElementById("hl3dSel"); if(e) e.value=HL3D; const b=document.getElementById("hl3dBgChk"); if(b) b.checked=HL3DBG; }
let HL3DBG=true; try{ if(localStorage.getItem("pennantHl3dBg")==="off") HL3DBG=false; }catch(e){}   // v2.1.j:試合画面の背景の球場(端末ごと)
function setHl3dBg(on){ HL3DBG=!!on; try{ localStorage.setItem("pennantHl3dBg",on? "on" : "off"); }catch(e){} hl3Sync(); hl3dBgSync(); }""")
rep("""function setHl3d(v){ if(!(v==="on"||v==="weak"||v==="off"||v==="3d")) return; HL3D=v; try{ localStorage.setItem("pennantHl3d",v); }catch(e){} hl3Sync(); if(v==="3d") hl3dPrep(); }""",
"""function setHl3d(v){ if(!(v==="on"||v==="weak"||v==="off"||v==="3d")) return; HL3D=v; try{ localStorage.setItem("pennantHl3d",v); }catch(e){} hl3Sync(); if(v==="3d") hl3dPrep(); try{ hl3dBgSync(); }catch(e){} }""")

# ===== 球場を読む(hl3Home を書かない形) =====
rep("""function hl3ParkFor(homeName){
  hl3Home=homeName||null;
  if(typeof parkEnabled==="undefined" || !parkEnabled || !homeName) return null;""",
"""function hl3ParkFor(homeName){ hl3Home=homeName||null; return hl3ParkOf(homeName); }
function hl3ParkOf(homeName){   // v2.1.j:読むだけ(hl3Home を書かない。試合画面の背景からも呼ぶ)
  if(typeof parkEnabled==="undefined" || !parkEnabled || !homeName) return null;""")

# ===== 観戦の球場を作る部分を切り出す =====
OLD_PARK="""  // フェンス・観客席・屋根(扇の角度 45°〜135° は、three の円柱では 135°〜225°)
  const th0=Math.PI*.75, thL=Math.PI*.5;"""
i=s.index(OLD_PARK); j=s.index("""  // 人と札(.hl3bb。カプセルの印 .hl3cap があれば人を立てる)""",i)
body=s[i:j]
assert "hl3Home" in body and "pk && pk.dome" in body
s=s[:i]+"""  hl3dParkMeshes(sc,own,pk,hl3Home);   // v2.1.j:フェンス・観客席・帯・照明塔・屋根(試合画面の背景と同じもの)
"""+s[j:]
fn=body.replace("""  // フェンス・観客席・屋根(扇の角度 45°〜135° は、three の円柱では 135°〜225°)
""","")
fn=fn.replace("(typeof teamColorMap!==\"undefined\" && hl3Home && teamColorMap[hl3Home])","(typeof teamColorMap!==\"undefined\" && home && teamColorMap[home])")
assert "hl3Home" not in fn
rep("""function hl3dStart(st){ return hl3dNR(()=>hl3dStart0(st)); }""",
"""function hl3dStart(st){ return hl3dNR(()=>hl3dStart0(st)); }
/* v2.1.j:球場(フェンス・観客席・本拠地の色の帯・ファウルゾーンの席・照明塔・屋根)。観戦の hl3dStart0 と試合画面の背景 hl3dBgBuild が使う。
   pk=hl3ParkOf の結果(null なら標準)、home=本拠地の球団名(帯と観客席の色)。返り値は照明の頭の位置(光のにじみを置く) */
function hl3dParkMeshes(sc,own,pk,home){
  const T=THREE, FR=pk? pk.R : HL_FR, add=(geo,mat)=>{ own.push(geo,mat); const m=new T.Mesh(geo,mat); sc.add(m); return m; }, heads=[];
"""+fn.replace("head.lookAt(0,40,-60); });","head.lookAt(0,40,-60); heads.push(head.position.clone()); });")+"""  return heads;
}""")

# ===== 試合画面の背景 =====
rep("""function hl3dUpdate(S,t){""","""/* ===== v2.1.j:試合画面の背景の球場(決め事 10) =====
   試合タブの上のカード(#matchup と #actionBar の入ったカード)に .hl3bgCard を付け、後ろに .hl3dBg(専用の WebGL の描き手)を差し込む。
   v1 の HTML・ボタン・文字には触らない。updateMatchup のあとに hl3dBgSync で球場(次の試合のホームチーム)とスタイルの色を合わせる。
   描くのは、試合タブが開いていて・カードが画面に見えていて・観戦などの窓が開いていないときだけ。作る・描くときは 3D 専用の乱数(hl3dNR) */
let hl3dBgR=null, hl3dBgS=null, hl3dBgOff=false, hl3dBgWatch=0;
function hl3dBgCard(){ const m=document.getElementById("matchup"); return m? m.closest(".card") : null; }
function hl3dBgHome(){
  try{ if(typeof league==="undefined" || !league || !league.length) return null;
    const busy= (typeof cupBusy==="function" && cupBusy()) || (post && post.done), g= !busy && schedule && schedule[gameIdx];
    if(g){ const h=schedTeam(g[0]); if(h && h.name) return h.name; }
    return league[myTeam]? league[myTeam].name : null; }catch(e){ return null; } }
function hl3dBgWant(){ return HL3DBG && !hl3dBgOff && hl3dReady() && !!hl3dBgHome(); }
function hl3dBgOffNow(card){ if(hl3dBgS){ hl3dBgStop(); hl3dBgS.own.forEach(o=>{ try{ o.dispose(); }catch(e){} }); hl3dBgS=null; }
  if(card){ card.classList.remove("hl3bgCard","hl3bgOn"); const b=card.querySelector(":scope > .hl3dBg"); if(b) b.remove(); } }
function hl3dBgSync(){
  const card=hl3dBgCard(); if(!card) return;
  if(HL3DBG && HL3D==="3d" && !hl3dOk && !hl3dBroken && typeof hl3dLoad==="function"){ try{ hl3dLoad().then(ok=>{ if(ok) hl3dBgSync(); }); }catch(e){} }
  if(!hl3dBgWant()){ hl3dBgOffNow(card); return; }
  const home=hl3dBgHome(), pk=hl3ParkOf(home), cs=getComputedStyle(card);
  const fade= (cs.getPropertyValue("--card")||"").trim() || "#16241c";
  const key=[home, pk? pk.s+"/"+pk.turf+"/"+pk.dome : "-", document.documentElement.dataset.style||"", (typeof teamColorMap!=="undefined" && teamColorMap[home])||""].join("|");
  card.classList.add("hl3bgCard","hl3bgOn"); card.style.setProperty("--hl3bgFade",fade);
  let box=card.querySelector(":scope > .hl3dBg"); if(!box){ box=document.createElement("div"); box.className="hl3dBg"; card.insertBefore(box,card.firstChild); }
  if(hl3dBgS && hl3dBgS.key===key && hl3dBgS.box===box){ hl3dBgSize(); hl3dBgKick(); return; }
  // 続けて呼ばれたとき(「まとめて進める」など)は、最後の1回だけ作る
  clearTimeout(hl3dBgT); hl3dBgT=setTimeout(()=>{ hl3dBgT=0; if(!hl3dBgWant() || !box.isConnected) return;
    try{ hl3dNR(()=>hl3dBgBuild(box,home,pk,key)); }catch(e){ hl3dBgOff=true; hl3dBgOffNow(card); } }, hl3dBgS? 120 : 0);
}
let hl3dBgT=0;
function hl3dBgRenderer(){ if(hl3dBgR) return hl3dBgR; const r=new THREE.WebGLRenderer({antialias:true}); r.setPixelRatio(Math.min(1.5,window.devicePixelRatio||1));
  r.domElement.className="hl3dBgCv"; r.domElement.addEventListener("webglcontextlost",e=>{ e.preventDefault(); hl3dBgOff=true; hl3dBgOffNow(hl3dBgCard()); }); return hl3dBgR=r; }
function hl3dBgGlowTex(){ const cv=document.createElement("canvas"); cv.width=cv.height=64; const g=cv.getContext("2d"), gr=g.createRadialGradient(32,32,0,32,32,32);
  gr.addColorStop(0,"rgba(255,246,214,1)"); gr.addColorStop(.25,"rgba(255,236,180,.55)"); gr.addColorStop(1,"rgba(255,230,160,0)"); g.fillStyle=gr; g.fillRect(0,0,64,64); return new THREE.CanvasTexture(cv); }
function hl3dBgSkyTex(dome){ const cv=document.createElement("canvas"); cv.width=4; cv.height=128; const g=cv.getContext("2d"), gr=g.createLinearGradient(0,0,0,128);
  if(dome){ gr.addColorStop(0,"#1c2026"); gr.addColorStop(1,"#3a424c"); } else { gr.addColorStop(0,"#070c18"); gr.addColorStop(.6,"#121c33"); gr.addColorStop(1,"#26365a"); }
  g.fillStyle=gr; g.fillRect(0,0,4,128); return new THREE.CanvasTexture(cv); }
function hl3dBgBuild(box,home,pk,key){
  const T=THREE, R=hl3dBgRenderer(); if(hl3dBgS){ hl3dBgStop(); hl3dBgS.own.forEach(o=>{ try{ o.dispose(); }catch(e){} }); }
  const own=[], sc=new T.Scene(), dome=!!(pk&&pk.dome), sky=hl3dBgSkyTex(dome); own.push(sky); sc.background=sky;
  sc.add(new T.AmbientLight(0xffffff,.72)); const dl=new T.DirectionalLight(0xfff4dc,.55); dl.position.set(40,160,120); sc.add(dl);
  // 地面:2.5D の地面の SVG(スタイルの色)を画面の外で描いて写す
  const gm=new T.MeshBasicMaterial({color:0x2e6b40}); own.push(gm); const gp=new T.Mesh(hl3dGeo("plane"),gm); gp.rotation.x=-Math.PI/2; gp.position.set(0,0,115-HL_HY); sc.add(gp);
  const tmp=document.createElement("div"); tmp.style.cssText="position:fixed;left:-10000px;top:0;width:300px;height:230px;visibility:hidden"; tmp.innerHTML=hl3FieldSvg("","グラウンド",pk).replace(/hlFieldClip[0-9]+/g,"hl3dBgClip");   // 番号を決まった名前にして、同じ球場・スタイルの絵を使い回す(hl3dFieldTex)
  document.body.appendChild(tmp); const svg=tmp.querySelector("svg"); if(svg) hl3dFieldTex(svg,tx=>{ gm.map=tx; gm.color.set(0xffffff); gm.needsUpdate=true; hl3dBgKick(); }); tmp.remove();
  const heads=hl3dParkMeshes(sc,own,pk,home);
  // 照明のにじみ・星
  if(!dome){ const gt=hl3dBgGlowTex(); own.push(gt); heads.forEach(p=>{ const m=new T.SpriteMaterial({map:gt,color:0xfff3d0,transparent:true,depthWrite:false,blending:T.AdditiveBlending}); own.push(m);
      const sp=new T.Sprite(m); sp.position.copy(p); sp.scale.set(70,70,1); sc.add(sp); });
    let x=2463534242; const rnd=()=>{ x^=x<<13; x^=x>>>17; x^=x<<5; return (x>>>0)/4294967296; };
    const N=160, pos=new Float32Array(N*3); for(let i=0;i<N;i++){ const a=Math.PI*(.15+.7*rnd()), e=.18+.5*rnd(), r=1400; pos[i*3]=Math.cos(a)*r*Math.cos(e); pos[i*3+1]=r*Math.sin(e); pos[i*3+2]=-Math.sin(a)*r*Math.cos(e); }
    const sg=new T.BufferGeometry(); sg.setAttribute("position",new T.BufferAttribute(pos,3)); const sm=new T.PointsMaterial({color:0xdfe6ff,size:2,sizeAttenuation:false,transparent:true,opacity:.75}); own.push(sg,sm); sc.add(new T.Points(sg,sm)); }
  // 守備位置に立つ野手
  const men=[]; Object.keys(HL_POS).forEach(k=>{ const [a,d]=HL_POS[k], m=hl3dMan(0xece8dc,own,true), p=hl3dP(...hlPt(a,d),0); m.position.copy(p); m.rotation.order="YXZ"; m.rotation.y=Math.atan2(-p.x,-p.z); sc.add(m); men.push(m); });
  { const c=hl3dMan(0xece8dc,own,true); c.position.copy(hl3dP(HL_HX,HL_HY+8,0)); c.rotation.y=Math.PI; sc.add(c); men.push(c); }
  const cam=new T.PerspectiveCamera(56,1,1,4000);
  box.textContent=""; box.appendChild(R.domElement);
  hl3dBgS={key,box,sc,cam,own,men,raf:0,t0:performance.now(),last:0,W:0,H:0,io:true};
  hl3dBgSize(); hl3dBgAim(); hl3dBgDraw(0); hl3dBgKick();
}
function hl3dBgSize(){ const S=hl3dBgS; if(!S) return; const card=S.box.parentElement; if(!card) return;
  const W=card.clientWidth||360, H=Math.round(Math.min(card.clientHeight||420, Math.max(380, W*1.25)));
  S.box.style.height=H+"px"; if(W===S.W && H===S.H) return; S.W=W; S.H=H; hl3dBgR.setSize(W,H,false); S.cam.aspect=W/H; S.cam.fov= W/H<.8? HL3D_BGCAM.fovN : HL3D_BGCAM.fov; S.cam.updateProjectionMatrix(); }
// マウンドの辺りが、スコアボードとボタンの間(あいた所)の真ん中に来るように、写す所を上下にずらす(枠の縦横の比によらない)
function hl3dBgAim(){ const S=hl3dBgS; if(!S) return; const m=document.getElementById("matchup"), bar=document.getElementById("actionBar");
  if(!m || !bar){ S.aimY=S.H*.62; return; } const b0=S.box.getBoundingClientRect(), mb=m.getBoundingClientRect().bottom, bt=bar.getBoundingClientRect().top;
  S.aimY= (mb>b0.top && bt>mb)? ((mb+bt)/2-b0.top) : S.H*.62; }
const HL3D_BGCAM={p:[0,62,150], t:[0,36,-200], fov:56, fovN:64, yaw:.07};   // 本塁の後ろの高い所から外野の奥を見る(fovN=縦長の枠)
function hl3dBgDraw(t){ const S=hl3dBgS; if(!S) return; const C=HL3D_BGCAM;
  const yaw=Math.sin(t*Math.PI*2/24)*C.yaw, ca=Math.cos(yaw), sa=Math.sin(yaw), px=C.p[0], pz=C.p[2]-C.t[2];   // 見る点のまわりにゆっくり左右に揺れる
  S.cam.position.set(C.t[0]+px*ca+pz*sa, C.p[1], C.t[2]+pz*ca-px*sa); S.cam.lookAt(C.t[0],C.t[1],C.t[2]);
  S.cam.clearViewOffset(); S.cam.updateMatrixWorld(); const v=hl3dP(HL_HX,HL_HY-40,0).project(S.cam), py=(1-v.y)/2*S.H, off=Math.max(-S.H*.45,Math.min(S.H*.45,py-(S.aimY||S.H*.62)));
  S.cam.setViewOffset(S.W,S.H,0,off,S.W,S.H);
  S.men.forEach((m,i)=>{ m.position.y=Math.max(0,Math.sin(t*2.1+i*1.7))*.25; });
  hl3dBgR.render(S.sc,S.cam); }
function hl3dBgVisible(){ const S=hl3dBgS; if(!S || !S.box.isConnected || document.hidden) return false;
  const pg=document.getElementById("p-game"); if(!pg || !pg.classList.contains("active")) return false;
  if(document.querySelector(".modalOverlay:not(.hidden)")) return false;
  const r=S.box.getBoundingClientRect(); return r.bottom>0 && r.top<(window.innerHeight||800) && r.width>0; }
function hl3dBgFrame(now){ const S=hl3dBgS; if(!S){ return; } S.raf=0;
  if(!hl3dBgVisible()) return;   // 見えないときは止める(見張りが 1 秒ごとにまた動かす)
  if(now-S.last>=33){ S.last=now; try{ hl3dNR(()=>{ hl3dBgSize(); if(!S.aimT || now-S.aimT>500){ S.aimT=now; hl3dBgAim(); } hl3dBgDraw((now-S.t0)/1000); }); }catch(e){ hl3dBgOff=true; hl3dBgOffNow(hl3dBgCard()); return; } }
  if(animEnabled()) S.raf=requestAnimationFrame(hl3dBgFrame); }
function hl3dBgKick(){ const S=hl3dBgS; if(S && !S.raf && hl3dBgVisible()) S.raf=requestAnimationFrame(hl3dBgFrame);
  if(!hl3dBgWatch) hl3dBgWatch=setInterval(()=>{ if(hl3dBgS) hl3dBgKick(); }, 1000); }
function hl3dBgStop(){ const S=hl3dBgS; if(S && S.raf){ cancelAnimationFrame(S.raf); S.raf=0; } }
// updateMatchup(v1)のあとに背景を合わせる(v1 の関数の中身には触らない)
{ const um=updateMatchup; updateMatchup=function(){ const r=um.apply(this,arguments); try{ hl3dBgSync(); }catch(e){} return r; }; }
window.addEventListener("resize",()=>{ try{ if(hl3dBgS){ hl3dBgSize(); hl3dBgKick(); } }catch(e){} });
function hl3dUpdate(S,t){""")

open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
