# v2.1.x のソースに当てると v2.1.y。python3 patch_v21y.py src.html new.html
# 試合画面の背景の球場:グラウンドの細部(B-6・B-7)。見た目だけ(背景 opt.full のときだけ。計算・観戦の 3D・v1 の SVG・セーブには触らない)。
#   ① 芝の刈り込みの縞 hl3dBgStripes:背景の地面の絵(canvas)に、外野の芝(本塁から 100〜フェンス−5)へ弧の縞(幅 18。白 .09 と黒 .08 を交互)を重ねる。
#      絵は使い回すので一度だけ(tx.__stripes)。フェアの扇の中だけ(clip)
#   ② バックネット:半透明の板に格子の絵(128×64 の canvas・8px ごとの線。繰り返し 8×2)を重ね、支柱 4 本(半径 51・高さ 16)。格子は userData.k="net"
#   ③ ネクストバッターズサークル:両ベンチの手前(ラインから s 13・o 8)に土の円(半径 3)と待つ打者(userData.k="ondeck")
#   テスト:hl3d_bg.py ⑯(地面の絵に縞の印・格子 1・待つ打者 2)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.x"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.y"; const BASE_V1="v1.4.b";')
# ① 縞
rep("""if(svg) hl3dFieldTex(svg,tx=>{ gm.map=tx; gm.color.set(0xffffff); gm.needsUpdate=true; hl3dBgKick(); }); tmp.remove();""",
"""if(svg) hl3dFieldTex(svg,tx=>{ hl3dBgStripes(tx,WD.FR); gm.map=tx; gm.color.set(0xffffff); gm.needsUpdate=true; hl3dBgKick(); }); tmp.remove();""")
rep("""function hl3dBgSkyTex(dome,day){""",
"""// v2.1.y:外野の芝の刈り込みの縞(背景の地面の絵だけ。一度だけ重ねる)
function hl3dBgStripes(tx,FR){ try{ if(!tx.image || tx.__stripes || !tx.image.getContext) return; tx.__stripes=true; const cv=tx.image, g=cv.getContext("2d"), cx=HL_HX*4, cy=HL_HY*4;
    const pR=hlPt(45,10), pL=hlPt(135,10), a0=Math.atan2(pR[1]-HL_HY,pR[0]-HL_HX), a1=Math.atan2(pL[1]-HL_HY,pL[0]-HL_HX);
    g.save(); g.beginPath(); g.moveTo(cx,cy); g.arc(cx,cy,(FR-5)*4,a0,a1,true); g.closePath(); g.clip();
    const W=18; for(let r=100,k=0;r<FR-5;r+=W,k++){ g.beginPath(); g.arc(cx,cy,Math.min(FR-5,r+W)*4,a0,a1,true); g.arc(cx,cy,r*4,a1,a0,false); g.closePath(); g.fillStyle= k%2? "rgba(255,255,255,.09)" : "rgba(0,0,0,.08)"; g.fill(); }
    g.restore(); tx.needsUpdate=true; }catch(e){} }
function hl3dBgSkyTex(dome,day){""")
# ② バックネット ③ ネクストバッターズサークル
rep("""    const net=add(new T.CylinderGeometry(36+WD.bo,36+WD.bo,16,24,1,true,rad(310),rad(100)), new T.MeshBasicMaterial({color:0x0c1014,transparent:true,opacity:.32,side:T.DoubleSide,depthWrite:false})); net.position.y=8;   // バックネット""",
"""    const NR=36+WD.bo, net=add(new T.CylinderGeometry(NR,NR,16,24,1,true,rad(310),rad(100)), new T.MeshBasicMaterial({color:0x0c1014,transparent:true,opacity:.26,side:T.DoubleSide,depthWrite:false})); net.position.y=8;   // バックネット
    { const cv=document.createElement("canvas"); cv.width=128; cv.height=64; const g=cv.getContext("2d"); g.strokeStyle="rgba(230,235,240,.38)"; g.lineWidth=1;   // v2.1.y:格子と支柱
      for(let i=0;i<=128;i+=8){ g.beginPath(); g.moveTo(i+.5,0); g.lineTo(i+.5,64); g.stroke(); } for(let j=0;j<=64;j+=8){ g.beginPath(); g.moveTo(0,j+.5); g.lineTo(128,j+.5); g.stroke(); }
      const nt=hl3dNR(()=>new T.CanvasTexture(cv)); nt.wrapS=nt.wrapT=T.RepeatWrapping; nt.repeat.set(8,2); own.push(nt);
      const grid=add(new T.CylinderGeometry(NR+.2,NR+.2,16,24,1,true,rad(310),rad(100)), new T.MeshBasicMaterial({map:nt,transparent:true,side:T.DoubleSide,depthWrite:false})); grid.position.y=8; grid.userData.k="net";
      const pm=new T.MeshLambertMaterial({color:0x6b737b}); own.push(pm); for(let i=0;i<=3;i++){ const t=rad(310)+rad(100)*i/3, c=add(new T.CylinderGeometry(.5,.5,17,6),pm); c.position.set(NR*Math.sin(t),8.5,NR*Math.cos(t)); }
      const od=new T.MeshLambertMaterial({color:0x9a7250}); own.push(od);   // ネクストバッターズサークルと待つ打者
      [1,-1].forEach(sx=>{ const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2], x=d[0]*13+n[0]*8, z=d[1]*13+n[1]*8, c=add(new T.CircleGeometry(3,20),od); c.rotation.x=-Math.PI/2; c.position.set(x,.08,z);
        const m=hl3dMan(0xece8dc,own,false); m.scale.setScalar(1.2); m.position.set(x,0,z); m.rotation.y=Math.PI; m.userData.k="ondeck"; sc.add(m); }); }""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
