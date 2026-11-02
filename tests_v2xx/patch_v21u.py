# v2.1.t のソースに当てると v2.1.u。python3 patch_v21u.py src.html new.html
# 試合画面の背景の球場:ドームの屋根(A-1)。見た目だけ(試合の計算・観戦の 3D・セーブには触らない。背景 opt.full のときだけ)。
#   ユーザーの「球場のクオリティを実際の球場をもとに更に上げられるか?」→ A-1。見本 sample_stadium.png の作りを広い器(v2.1.t)に合わせた。
#   ① hl3dDomeRoof:針金の半球をやめ、外周の壁(円柱・半径 275・高さ 61。内側だけ描く)+内側が見えるシェル(球の帽子・半径 293・中心 y −40)。
#      中心 z は器の中心((145−(FRc+86))/2)。骨組みの筋は絵(1024×256 の canvas:縦 32 本・横 5 本の線)で貼る(使い回す hl3dDomeTexC)
#   ② 天井の照明:2 つの輪(緯度 .14π に 28・.26π に 40)。発光の板(5×1×3)と光のにじみ(hl3dBgGlowTex の sprite・26)。昼はにじみを弱く
#   ③ 壁の上の縁(濃い帯・高さ 2)と、壁の通路の口(黒い四角を 24 か所)で壁ののっぺりを減らす
#   ④ 照明塔に userData.k="tower"、屋根に userData.k="domeRoof"(テストで数える)
#   テスト:hl3d_bg.py ⑫(ドームの本拠地では屋根 1・照明塔 0、屋外では屋根 0・照明塔 6)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.t"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.u"; const BASE_V1="v1.4.b";')
rep("""  if(pk && pk.dome){ const dR= WD? (WD.FRc+86+145)/2+25 : FR+110, dz= WD? (145-(WD.FRc+86))/2 : -70;   // v2.1.t:背景は広い器に合わせる
    const dm=add(new T.SphereGeometry(dR,28,10,0,Math.PI*2,0,Math.PI*.42), new T.MeshBasicMaterial({color:0xaab3bd,wireframe:true,transparent:true,opacity:.14})); dm.position.set(0,-40,dz); }""",
"""  if(pk && pk.dome){ if(WD) hl3dDomeRoof(sc,own,add,WD,!!(opt&&opt.day));   // v2.1.u:背景は本物の屋根
    else { const dm=add(new T.SphereGeometry(FR+110,28,10,0,Math.PI*2,0,Math.PI*.42), new T.MeshBasicMaterial({color:0xaab3bd,wireframe:true,transparent:true,opacity:.14})); dm.position.set(0,-40,-70); } }""")
# 照明塔に印
rep("""    const r= WD? WD.Rf(a)+o : FR+o, p=hl3dP(...hlPt(a,r),0), pole=add(new T.CylinderGeometry(1.1,1.6,68,6), new T.MeshLambertMaterial({color:0x7d868f})); pole.position.set(p.x,34,p.z);""",
"""    const r= WD? WD.Rf(a)+o : FR+o, p=hl3dP(...hlPt(a,r),0), pole=add(new T.CylinderGeometry(1.1,1.6,68,6), new T.MeshLambertMaterial({color:0x7d868f})); pole.position.set(p.x,34,p.z); pole.userData.k="tower";""")
rep("""      const p=hl3dP(...hlPt(a,r),0), pole=add(new T.CylinderGeometry(1.1,1.6,68,6), new T.MeshLambertMaterial({color:0x7d868f})); pole.position.set(p.x,34,p.z);""",
"""      const p=hl3dP(...hlPt(a,r),0), pole=add(new T.CylinderGeometry(1.1,1.6,68,6), new T.MeshLambertMaterial({color:0x7d868f})); pole.position.set(p.x,34,p.z); pole.userData.k="tower";""")
rep("""  const popt={full:true, away:ac||null}, heads=hl3dParkMeshes(sc,own,pk,home,popt);""","""  const popt={full:true, away:ac||null, day:!!day}, heads=hl3dParkMeshes(sc,own,pk,home,popt);""")
# ① ② ③ 屋根
rep("""function hl3dParkMeshes(sc,own,pk,home,opt){   // v2.1.m:opt.full=球場を一周つなげる(試合画面の背景の 360 度)""",
"""// v2.1.u:ドームの屋根(背景だけ)。壁(半径 WR・高さ WH)+球の帽子(半径 SR・中心 y −40)。骨組みの筋は絵。天井に照明の輪 2 つ
let hl3dDomeTexC=null;
function hl3dDomeTex(){ if(hl3dDomeTexC) return hl3dDomeTexC; const cv=document.createElement("canvas"); cv.width=1024; cv.height=256; const g=cv.getContext("2d");
  g.fillStyle="#c9ced4"; g.fillRect(0,0,1024,256); g.strokeStyle="#8b939b"; g.lineWidth=3;
  for(let i=0;i<32;i++){ g.beginPath(); g.moveTo(i*32,0); g.lineTo(i*32,256); g.stroke(); } for(let j=1;j<6;j++){ g.beginPath(); g.moveTo(0,j*42); g.lineTo(1024,j*42); g.stroke(); }
  g.strokeStyle="rgba(255,255,255,.4)"; g.lineWidth=1; for(let i=0;i<32;i++){ g.beginPath(); g.moveTo(i*32+16,0); g.lineTo(i*32+16,256); g.stroke(); }
  hl3dDomeTexC=hl3dNR(()=>new THREE.CanvasTexture(cv)); return hl3dDomeTexC; }
function hl3dDomeRoof(sc,own,add,WD,day){ const T=THREE, CZ=(145-(WD.FRc+86))/2, WR=Math.max(275, (WD.FRc+86)+CZ+6), SR=WR+18, WH=Math.sqrt(SR*SR-WR*WR)-40, lit=.78;
  const wall=add(new T.CylinderGeometry(WR,WR,WH,64,1,true), new T.MeshLambertMaterial({color:new T.Color(0x9aa2aa).multiplyScalar(lit),side:T.BackSide})); wall.position.set(0,WH/2,CZ); wall.userData.k="domeRoof";
  const rim=add(new T.CylinderGeometry(WR-.5,WR-.5,2,64,1,true), new T.MeshLambertMaterial({color:0x4a5058,side:T.BackSide})); rim.position.set(0,WH-1,CZ);
  const gm=new T.MeshBasicMaterial({color:0x0e1216}); own.push(gm); for(let i=0;i<24;i++){ const a=i/24*Math.PI*2+.13, b=add(new T.BoxGeometry(9,7,1),gm); b.position.set((WR-1.2)*Math.sin(a),52,CZ+(WR-1.2)*Math.cos(a)); b.rotation.y=a; }   // 通路の口
  const shell=add(new T.SphereGeometry(SR,64,20,0,Math.PI*2,0,Math.asin(WR/SR)), new T.MeshLambertMaterial({map:hl3dDomeTex(),color:new T.Color(lit,lit,lit),side:T.BackSide,emissive: day? 0x3a3e44 : 0x2a2e33})); shell.position.set(0,-40,CZ);
  const gt=hl3dBgGlowTex(); own.push(gt); const lm=new T.MeshBasicMaterial({color:0xfff6d8}); own.push(lm);
  [[.14,28],[.26,40]].forEach(([ph,N])=>{ const phi=Math.PI*ph, r=SR*Math.sin(phi), y=-40+SR*Math.cos(phi)-1.5;
    for(let i=0;i<N;i++){ const a=i/N*Math.PI*2, x=r*Math.sin(a), z=CZ+r*Math.cos(a), b=add(new T.BoxGeometry(5,1,3),lm); b.position.set(x,y,z); b.lookAt(0,-40,CZ); b.rotateX(Math.PI/2);
      const sm=new T.SpriteMaterial({map:gt,color:0xfff3d0,transparent:true,depthWrite:false,blending:T.AdditiveBlending,opacity: day? .35 : .6}); own.push(sm); const sp=new T.Sprite(sm); sp.position.set(x,y-2,z); sp.scale.set(26,26,1); sc.add(sp); } }); }
function hl3dParkMeshes(sc,own,pk,home,opt){   // v2.1.m:opt.full=球場を一周つなげる(試合画面の背景の 360 度)""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
