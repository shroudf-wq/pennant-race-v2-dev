# v2.2.h のソースに当てると v2.2.i。python3 patch_v22i.py src.html new.html
# 細かい直し(「おすすめで一通りやって」の残り)。見た目だけ。
#   ① フェンス裏型のブルペン(背景):箱の壁の高さ 12.5 → フェンス+.5。マウンドの上から投手・捕手の頭と上半身がフェンスの上に覗く(今まで灰色の箱にしか見えなかった)
#   ② 外の地面の色:地面の絵(2.5D の SVG を写した canvas)の外野の芝 hlPt(60,70) の色を 1 点読んで ×.86 にし、外の地面の円(g0)をその色の MeshBasic にする。
#      絵のファウルゾーンは透明(alphaTest で抜ける)なので、ファウルゾーンの地面は g0 が見えている。今までは固定の 0x2a5534 の Lambert で、配色によってはフェアの芝との継ぎ目(色の段差)が目立った。背景と観戦の両方。hl3dParkMeshes が opt.out.ground に材質を渡す
#   ③ 背景の外野席の draw call まとめは見送り(ウェーブは区画ごとに動かすので、まとめると動かせない。背景は 1 コマ 0.5〜0.7ms で軽い)
#   テスト:hl3d_bg.py ㉓(フェンス裏型の箱の壁の高さ FH+.5、地面の円が絵の色(2a5534 でない・MeshBasic))。観戦は hl3d_shots.py
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.2.h"; const BASE_V1="v1.4.q";','const APP_VERSION="v2.2.i"; const BASE_V1="v1.4.q";')
# ① 箱の壁
rep("""          q([A[0],fy,A[1]],[B[0],fy,B[1]],[B2[0],fy,B2[1]],[A2[0],fy,A2[1]],p); q([A2[0],fy,A2[1]],[B2[0],fy,B2[1]],[B2[0],12.5,B2[1]],[A2[0],12.5,A2[1]],w); }
        [f0,f1].forEach(f=>{ const A=fx2(f,Rf(f)+5), B=fx2(f,Rf(f)+30); q([A[0],fy,A[1]],[B[0],fy,B[1]],[B[0],12.5,B[1]],[A[0],12.5,A[1]],w); });""",
"""          q([A[0],fy,A[1]],[B[0],fy,B[1]],[B2[0],fy,B2[1]],[A2[0],fy,A2[1]],p); q([A2[0],fy,A2[1]],[B2[0],fy,B2[1]],[B2[0],WH,B2[1]],[A2[0],WH,A2[1]],w); }
        [f0,f1].forEach(f=>{ const A=fx2(f,Rf(f)+5), B=fx2(f,Rf(f)+30); q([A[0],fy,A[1]],[B[0],fy,B[1]],[B[0],WH,B[1]],[A[0],WH,A[1]],w); });""")
rep("""      const Rf=WD.Rf, fy=FH-4, fx2=(f,r)=>{""","""      const Rf=WD.Rf, fy=FH-4, WH=FH+.5, fx2=(f,r)=>{   /* v2.2.i:壁はフェンス+.5(頭が覗く) */""")
# ② 外の地面の色
rep("""    const g0=add(new T.CircleGeometry((WD? WD.FRc : FR)+150,64), new T.MeshLambertMaterial({color:0x2a5534})); g0.rotation.x=-Math.PI/2; g0.position.y=-.3;   // ファウルゾーンから外まで続く地面""",
"""    const g0=add(new T.CircleGeometry((WD? WD.FRc : FR)+150,64), new T.MeshBasicMaterial({color:0x2a5534})); g0.rotation.x=-Math.PI/2; g0.position.y=-.3; (opt.out=opt.out||{}).ground=g0.material;   // ファウルゾーンから外まで続く地面。v2.2.i:絵ができたら絵のファウルゾーンの芝の色に(hl3dGroundTint)""")
rep("""function hl3dBgSkyTex(dome,day){""",
"""// v2.2.i:外の地面の円(=ファウルゾーンの地面)を、地面の絵の外野の芝 hlPt(60,70) の色 ×.86 に合わせる(絵は 4 倍の canvas。ファウルゾーンは絵では透明)
function hl3dGroundTint(mat,tx){ try{ if(!mat || !tx || !tx.image || !tx.image.getContext) return; const g=tx.image.getContext("2d"), q=hlPt(60,70), d=g.getImageData(Math.round(q[0]*4),Math.round(q[1]*4),1,1).data; if(d[3]>200){ mat.color.setRGB(d[0]/255*.86,d[1]/255*.86,d[2]/255*.86); mat.needsUpdate=true; } }catch(e){} }
function hl3dBgSkyTex(dome,day){""")
rep("""if(svg) hl3dFieldTex(svg,tx=>{ hl3dBgStripes(tx,WD.FR); gm.map=tx; gm.color.set(0xffffff); gm.needsUpdate=true; hl3dBgKick(); }); tmp.remove();""",
"""if(svg) hl3dFieldTex(svg,tx=>{ hl3dBgStripes(tx,WD.FR); gm.map=tx; gm.color.set(0xffffff); gm.needsUpdate=true; hl3dGroundTint(bgG0,tx); hl3dBgKick(); }); tmp.remove();""")
rep("""  const tmp=document.createElement("div"); tmp.style.cssText="position:fixed;left:-10000px;top:0;width:300px;height:230px;visibility:hidden";""",
"""  let bgG0=null;   // v2.2.i:外の地面の材質(hl3dParkMeshes のあとに入る。絵が先にできたら下でもう一度)
  const tmp=document.createElement("div"); tmp.style.cssText="position:fixed;left:-10000px;top:0;width:300px;height:230px;visibility:hidden";""")
rep("""  const svg=st.querySelector(".hl3world svg"); if(svg) hl3dFieldTex(svg,tx=>{ gm.map=tx; gm.color.set(0xffffff); gm.needsUpdate=true; hl3dKick(); });""",
"""  const po={};   // v2.2.i:hl3dParkMeshes に渡すもの(out.ground=外の地面の材質)
  const svg=st.querySelector(".hl3world svg"); if(svg) hl3dFieldTex(svg,tx=>{ gm.map=tx; gm.color.set(0xffffff); gm.needsUpdate=true; hl3dGroundTint(po.out && po.out.ground,tx); hl3dKick(); });""")
rep("""  hl3dParkMeshes(sc,own,pk,hl3Home,{ofFull:true, away:(awayNm && typeof teamColorMap!=="undefined" && teamColorMap[awayNm])||null, vision:vis});""",
"""  Object.assign(po,{ofFull:true, away:(awayNm && typeof teamColorMap!=="undefined" && teamColorMap[awayNm])||null, vision:vis}); hl3dParkMeshes(sc,own,pk,hl3Home,po); if(gm.map) hl3dGroundTint(po.out && po.out.ground,gm.map);   /* 絵が使い回しで先にできていたとき */""")
rep("""  const popt={full:true, away:ac||null, day:!!day, ribbon, vision:hl3dVisionMake(vinfo)}, heads=hl3dParkMeshes(sc,own,pk,home,popt); own.push(popt.vision.tx);""",
"""  const popt={full:true, away:ac||null, day:!!day, ribbon, vision:hl3dVisionMake(vinfo)}, heads=hl3dParkMeshes(sc,own,pk,home,popt); own.push(popt.vision.tx); bgG0=popt.out && popt.out.ground; if(gm.map) hl3dGroundTint(bgG0,gm.map);   /* v2.2.i:絵が使い回しで先にできていたとき */""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
