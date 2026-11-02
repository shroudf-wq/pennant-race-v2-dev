# v2.1.l のソースに当てると v2.1.m。python3 patch_v21m.py src.html new.html
# 見た目だけ(試合の計算・記録・セーブには触らない。乱数は使わない)。
#   ① バックスクリーン:センターの外野席の前に濃い緑の板(観戦の 3D と試合画面の背景の両方。hl3dParkMeshes)
#   ② 試合画面の背景を「マウンドから 360 度見渡す」に:カメラはマウンドの上(高さ 24)で 60 秒に1周(最初はセンター向き)。
#      見渡せるように球場を一周つなげる(背景だけ。opt.full):本塁の後ろの内野席・バックネット・ファウルゾーンまで続く地面・内野側の照明塔2本。投手は立てない(カメラの所)
#      カメラは前方 90 の芝を見下ろし、その点をスコアボードとボタンの間のあいた所(100px に広げた)の真ん中に合わせる(前の「マウンドを合わせる」に代えて)。
#      上の帯に照明・スタンド、あいた所に芝と野手、ボタンの後ろに手前の地面。地面の絵のフェンスの外の暗い塗り(.f-stands)は背景では外して透かす
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.l"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.m"; const BASE_V1="v1.4.b";')

rep("""function hl3dParkMeshes(sc,own,pk,home){""","""function hl3dParkMeshes(sc,own,pk,home,opt){   // v2.1.m:opt.full=球場を一周つなげる(試合画面の背景の 360 度)""")
rep("""  if(pk && pk.dome){ const dm=add(new T.SphereGeometry(FR+110,28,10,0,Math.PI*2,0,Math.PI*.42), new T.MeshBasicMaterial({color:0xaab3bd,wireframe:true,transparent:true,opacity:.14})); dm.position.set(0,-40,-70); }
  return heads;
}""","""  if(pk && pk.dome){ const dm=add(new T.SphereGeometry(FR+110,28,10,0,Math.PI*2,0,Math.PI*.42), new T.MeshBasicMaterial({color:0xaab3bd,wireframe:true,transparent:true,opacity:.14})); dm.position.set(0,-40,-70); }
  // v2.1.m:バックスクリーン(センターの外野席の前に立つ濃い緑の板。本塁のほうを向く)
  { const bs=add(new T.PlaneGeometry(46,30), new T.MeshLambertMaterial({color:0x173626,side:T.DoubleSide})); bs.position.set(0,17,-(FR+9)); }
  if(opt && opt.full){   // 三 の円柱の角度 t は、地面の図の角度 f(本塁から見て 90°=センター)の f+90°
    const rad=d=>d*Math.PI/180;
    const g0=add(new T.CircleGeometry(FR+150,64), new T.MeshLambertMaterial({color:0x2a5534})); g0.rotation.x=-Math.PI/2; g0.position.y=-.3;   // ファウルゾーンから外まで続く地面
    const ig=new T.CylinderGeometry(118,40,34,40,1,true,rad(275),rad(170)); own.push(ig); const inf=new T.Mesh(ig,smat); inf.position.y=17; sc.add(inf);   // 本塁の後ろの内野席(f=185°〜355°)
    const net=add(new T.CylinderGeometry(36,36,16,24,1,true,rad(310),rad(100)), new T.MeshBasicMaterial({color:0x0c1014,transparent:true,opacity:.32,side:T.DoubleSide,depthWrite:false})); net.position.y=8;   // バックネット
    if(!dome) [[205,128],[335,128]].forEach(([a,r])=>{   // 内野側の照明塔
      const p=hl3dP(...hlPt(a,r),0), pole=add(new T.CylinderGeometry(1.1,1.6,68,6), new T.MeshLambertMaterial({color:0x7d868f})); pole.position.set(p.x,34,p.z);
      const head=add(new T.BoxGeometry(15,8,1.6), new T.MeshBasicMaterial({color:0xfff2c2})); head.position.set(p.x,70,p.z); head.lookAt(0,40,-60); heads.push(head.position.clone()); });
  }
  return heads;
}""")
rep("""  const heads=hl3dParkMeshes(sc,own,pk,home);""","""  const heads=hl3dParkMeshes(sc,own,pk,home,{full:true});""")
# 投手は立てない(カメラの所)
rep("""  const men=[]; Object.keys(HL_POS).forEach(k=>{ const [a,d]=HL_POS[k],""","""  const men=[]; Object.keys(HL_POS).filter(k=>k!=="投").forEach(k=>{ const [a,d]=HL_POS[k],""")
# カメラ:マウンドから 360 度
rep("""const HL3D_BGCAM={p:[0,62,150], t:[0,36,-200], fov:56, fovN:64, yaw:.07};   // 本塁の後ろの高い所から外野の奥を見る(fovN=縦長の枠)
function hl3dBgDraw(t){ const S=hl3dBgS; if(!S) return; const C=HL3D_BGCAM;
  const yaw=Math.sin(t*Math.PI*2/24)*C.yaw, ca=Math.cos(yaw), sa=Math.sin(yaw), px=C.p[0], pz=C.p[2]-C.t[2];   // 見る点のまわりにゆっくり左右に揺れる
  S.cam.position.set(C.t[0]+px*ca+pz*sa, C.p[1], C.t[2]+pz*ca-px*sa); S.cam.lookAt(C.t[0],C.t[1],C.t[2]);
  S.cam.clearViewOffset(); S.cam.updateMatrixWorld(); const v=hl3dP(HL_HX,HL_HY-40,0).project(S.cam), py=(1-v.y)/2*S.H, off=Math.max(-S.H*.45,Math.min(S.H*.45,py-(S.aimY||S.H*.62)));""",
"""const HL3D_BGCAM={eye:[0,50,-45], look:90, ly:0, ad:90, hy:0, period:60, fov:60, fovN:68};   // v2.1.m:マウンドの上(高さ 50)から 60 秒で1周。前方 90 の芝(高さ 0)を見下ろし、その点をボードとボタンの間に合わせる(ad・hy)
function hl3dBgDraw(t){ const S=hl3dBgS; if(!S) return; const C=HL3D_BGCAM;
  const a=t*Math.PI*2/C.period, dx=Math.sin(a), dz=-Math.cos(a), E=C.eye;   // a=0 でセンター(−Z)を向き、一塁側へ回る
  S.cam.position.set(E[0],E[1],E[2]); S.cam.lookAt(E[0]+dx*C.look, C.ly, E[2]+dz*C.look);
  S.cam.clearViewOffset(); S.cam.updateMatrixWorld(); const v=new THREE.Vector3(E[0]+dx*(C.ad||400), C.hy, E[2]+dz*(C.ad||400)).project(S.cam), py=(1-v.y)/2*S.H, off=Math.max(-S.H*.45,Math.min(S.H*.45,py-(S.aimY||S.H*.62)));""")
rep("""S.cam.fov= W/H<.8? HL3D_BGCAM.fovN : HL3D_BGCAM.fov;""","""S.cam.fov= W/H<.8? HL3D_BGCAM.fovN : HL3D_BGCAM.fov;""")
# 地面の絵:背景ではフェンスの外の暗い塗り(.f-stands)を外して透かす(下の地面が見える)
rep("""  // 地面:2.5D の地面の SVG(スタイルの色)を画面の外で描いて写す
  const gm=new T.MeshBasicMaterial({color:0x2e6b40}); own.push(gm);""","""  // 地面:2.5D の地面の SVG(スタイルの色)を画面の外で描いて写す。v2.1.m:フェンスの外の塗りは外して透かす
  const gm=new T.MeshBasicMaterial({color:0x2e6b40,transparent:true,alphaTest:.5}); own.push(gm);""")
rep("""document.body.appendChild(tmp); const svg=tmp.querySelector("svg"); if(svg) hl3dFieldTex(svg,""","""document.body.appendChild(tmp); const svg=tmp.querySelector("svg"); if(svg) svg.querySelectorAll(".f-stands").forEach(e=>e.remove()); if(svg) hl3dFieldTex(svg,""")
rep(""".hl3bgOn .matchup{box-shadow:0 10px 26px rgba(0,0,0,.45);margin-bottom:var(--hl3bgGap,72px)}""",""".hl3bgOn .matchup{box-shadow:0 10px 26px rgba(0,0,0,.45);margin-bottom:var(--hl3bgGap,100px)}""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
