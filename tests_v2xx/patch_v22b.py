# v2.2.a のソースに当てると v2.2.b。python3 patch_v22b.py src.html new.html
# 選手のユニフォーム(B案の 1 段目=A案)。3D(観戦・試合画面の背景)だけ。2.5D・v1 の絵・計算・セーブには触らない。
#   ユーザーの「選手にユニフォームをつけることは可能か?(チームカラーを基本として)」→ B案で
#   ① hl3dUniform(team,isHome):チームカラー tc(teamColorMap)から {body, cap, trim, skin}。ホーム=白地(0xf4f2ec)・帽子 tc・袖とベルト tc。
#      ビジター=tc 地・帽子は tc を暗く(×.6)・袖とベルトは白。肌 0xe6c3a0。色が無いときは灰
#   ② hl3dMan(col,own,glv,uni,role):uni があれば 胴=body、頭=肌、帽子(頭の上半分の球)とつば(前=+z)=cap、腕(袖)=trim、ベルト(腰の帯)=trim。
#      role "b"(打者)=足元に赤いリング、"r"(走者)=黄のリング(今までの体の色の役割をリングに移す)。uni が無ければ今まで通り 1 色。
#      新しい材質は userData.mats/op に入れる(観戦の消える演出がそのまま効く)。新しい形は hl3dGeo の "cap"・"brim"・"belt"・"rolering"
#   ③ 観戦:hl3Tags で hl3Teams={fld, bat, home} を覚え(表=ビジターが攻撃)、hl3dStart0 で野手=守備側・打者と走者=攻撃側のユニフォーム。
#      ホームかどうかは名前が home と同じか
#   ④ 試合画面の背景:野手・捕手・待つ打者・ブルペン・ベンチの選手は本拠地のホームのユニフォーム
#   テスト:hl3d_bg.py ⑲(背景の野手の帽子がホームチームの色)。見た目は hl3d_shots.py で撮る
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.2.a"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.2.b"; const BASE_V1="v1.4.b";')
# ② 形
rep("""    : k==="shadow"? new T.CircleGeometry(3.2,16) :""","""    : k==="cap"? new T.SphereGeometry(2.35,12,6,0,Math.PI*2,0,Math.PI*.5) : k==="brim"? new T.BoxGeometry(2.6,.35,1.7).translate(0,.75,2.2) : k==="belt"? new T.CylinderGeometry(2.42,2.42,.6,12) : k==="rolering"? new T.RingGeometry(2.7,3.5,24)   /* v2.2.b:帽子・つば・ベルト・役割のリング */
    : k==="shadow"? new T.CircleGeometry(3.2,16) :""")
# ① ② 人
rep("""function hl3dMan(col,own,glv){ const T=THREE, g=new T.Group(), m=new T.MeshLambertMaterial({color:col,transparent:true}), sm=new T.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.32,depthWrite:false});
  own.push(m,sm); const b=new T.Mesh(hl3dGeo("body"),m), h=new T.Mesh(hl3dGeo("head"),m), sh=new T.Mesh(hl3dGeo("shadow"),sm);
  b.position.y=3.2; h.position.y=8; sh.rotation.x=-Math.PI/2; sh.position.y=.15; g.add(sh,b,h); g.scale.setScalar(1.4); /* v2.1.d:1.4 倍 */
  const mk=sx=>{ const a=new T.Group(); a.position.set(2.7*sx,6.2,0); a.rotation.x=.15; a.rotation.z=.2*sx; a.add(new T.Mesh(hl3dGeo("arm"),m)); g.add(a); return a; };   // v2.1.f:腕を2本(右=投げる・左=グラブ)
  const sp=mk(1), gl=mk(-1); g.userData.arm=sp; g.userData.glv=gl; g.userData.mats=[m,sm]; g.userData.op=[1,.32];""",
"""// v2.2.b:ユニフォームの色。ホーム=白地に帽子・袖・ベルトがチームカラー、ビジター=チームカラー地に暗い帽子・白い袖
let hl3Teams=null;   // 観戦の場面の {fld:守備側, bat:攻撃側, home:本拠地}(hl3Tags で覚える)
function hl3dUniform(team,isHome){ const T=THREE; let tc; try{ tc=new T.Color(String((typeof teamColorMap!=="undefined" && team && teamColorMap[team])||"#888888")); }catch(e){ tc=new T.Color(0x888888); }
  return isHome? {body:0xf4f2ec, cap:tc.getHex(), trim:tc.getHex(), skin:0xe6c3a0} : {body:tc.getHex(), cap:tc.clone().multiplyScalar(.6).getHex(), trim:0xf4f2ec, skin:0xe6c3a0}; }
function hl3dMan(col,own,glv,uni,role){ const T=THREE, g=new T.Group(), U=uni||null, m=new T.MeshLambertMaterial({color: U? U.body : col,transparent:true}), sm=new T.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.32,depthWrite:false});
  own.push(m,sm); const mats=[m,sm], ops=[1,.32], mat=c=>{ const x=new T.MeshLambertMaterial({color:c,transparent:true}); own.push(x); mats.push(x); ops.push(1); return x; };
  const skinM= U? mat(U.skin) : m, capM= U? mat(U.cap) : null, trimM= U? mat(U.trim) : m;
  const b=new T.Mesh(hl3dGeo("body"),m), h=new T.Mesh(hl3dGeo("head"),skinM), sh=new T.Mesh(hl3dGeo("shadow"),sm);
  b.position.y=3.2; h.position.y=8; sh.rotation.x=-Math.PI/2; sh.position.y=.15; g.add(sh,b,h); g.scale.setScalar(1.4); /* v2.1.d:1.4 倍 */
  if(U){ const cap=new T.Mesh(hl3dGeo("cap"),capM), brim=new T.Mesh(hl3dGeo("brim"),capM), belt=new T.Mesh(hl3dGeo("belt"),trimM); cap.position.y=8; brim.position.y=8; belt.position.y=3.4; g.add(cap,brim,belt); }   // v2.2.b:帽子・つば・ベルト
  if(U && (role==="b" || role==="r")){ const rm=new T.MeshBasicMaterial({color: role==="b"? 0xc0392b : 0xf2c94c,transparent:true,opacity:.9,side:T.DoubleSide,depthWrite:false}); own.push(rm); mats.push(rm); ops.push(.9);
    const rg=new T.Mesh(hl3dGeo("rolering"),rm); rg.rotation.x=-Math.PI/2; rg.position.y=.22; g.add(rg); }   // v2.2.b:役割のリング(打者=赤・走者=黄)
  const mk=sx=>{ const a=new T.Group(); a.position.set(2.7*sx,6.2,0); a.rotation.x=.15; a.rotation.z=.2*sx; a.add(new T.Mesh(hl3dGeo("arm"),trimM)); g.add(a); return a; };   // v2.1.f:腕を2本(右=投げる・左=グラブ)。v2.2.b:袖の色
  const sp=mk(1), gl=mk(-1); g.userData.arm=sp; g.userData.glv=gl; g.userData.mats=mats; g.userData.op=ops;""")
# ③ 観戦
rep("""  const defs=(r.log&&r.log.defs)||[], d=(ev.fd!==undefined && ev.fd!==null)? defs[ev.fd] : null, m=d&&(d.m||d), sur=n=>surnameOf(n), o=opt||{};""",
"""  const defs=(r.log&&r.log.defs)||[], d=(ev.fd!==undefined && ev.fd!==null)? defs[ev.fd] : null, m=d&&(d.m||d), sur=n=>surnameOf(n), o=opt||{};
  try{ const hn=r.homeTeam&&r.homeTeam.name, an=r.awayTeam&&r.awayTeam.name; hl3Teams={home:hn, bat: ev.half==="表"? an : hn, fld: ev.half==="表"? hn : an}; }catch(e){ hl3Teams=null; }   // v2.2.b:ユニフォームの色のため""")
rep("""    if(cap){ it.man=hl3dMan(cap.classList.contains("f")? 0xece8dc : cap.classList.contains("b")? 0xc0392b : 0xf2c94c, own, cap.classList.contains("f")); sc.add(it.man); }""",
"""    if(cap){ const isF=cap.classList.contains("f"), role= isF? "f" : cap.classList.contains("b")? "b" : "r", tm= hl3Teams? (isF? hl3Teams.fld : hl3Teams.bat) : null;   // v2.2.b:守備側・攻撃側のユニフォーム
      it.man=hl3dMan(isF? 0xece8dc : role==="b"? 0xc0392b : 0xf2c94c, own, isF, tm? hl3dUniform(tm, tm===hl3Teams.home) : null, role); sc.add(it.man); }""")
# ④ 背景
rep("""  const men=[]; Object.keys(HL_POS).filter(k=>k!=="投").forEach(k=>{ const [a,d]=HL_POS[k], m=hl3dMan(0xece8dc,own,true), p=hl3dP(...hlPt(a,WD.warp(a,d)),0);""",
"""  const UNI=hl3dUniform(home,true);   // v2.2.b:本拠地のホームのユニフォーム
  const men=[]; Object.keys(HL_POS).filter(k=>k!=="投").forEach(k=>{ const [a,d]=HL_POS[k], m=hl3dMan(0xece8dc,own,true,UNI), p=hl3dP(...hlPt(a,WD.warp(a,d)),0);""")
rep("""  { const c=hl3dMan(0xece8dc,own,true); c.scale.setScalar(.8);""","""  { const c=hl3dMan(0xece8dc,own,true,UNI); c.scale.setScalar(.8);""")
rep("""        const m=hl3dMan(0xece8dc,own,false); m.scale.setScalar(.8); m.position.set(x,0,z); m.rotation.y=Math.PI; m.userData.k="ondeck";""",
"""        const m=hl3dMan(0xece8dc,own,false,hl3dUniform(home,true)); m.scale.setScalar(.8); m.position.set(x,0,z); m.rotation.y=Math.PI; m.userData.k="ondeck";""")
rep("""          const ang=Math.atan2(m1[0]-m0[0],m1[1]-m0[1]), pm=hl3dMan(0xece8dc,own,false); pm.scale.setScalar(.8); pm.position.set(m0[0],fy+.7,m0[1]); pm.rotation.y=ang; pm.userData.k="pen"; sc.add(pm);
          const cm=hl3dMan(0xece8dc,own,false); cm.scale.set(.8,.5,.8);""",
"""          const ang=Math.atan2(m1[0]-m0[0],m1[1]-m0[1]), pm=hl3dMan(0xece8dc,own,false,hl3dUniform(home,true)); pm.scale.setScalar(.8); pm.position.set(m0[0],fy+.7,m0[1]); pm.rotation.y=ang; pm.userData.k="pen"; sc.add(pm);
          const cm=hl3dMan(0xece8dc,own,false,hl3dUniform(home,true)); cm.scale.set(.8,.5,.8);""")
rep("""          const ang=Math.atan2(d[0],d[1]), pm=hl3dMan(0xece8dc,own,false); pm.scale.setScalar(.8); pm.position.set(m0[0],.7,m0[1]); pm.rotation.y=ang; pm.userData.k="pen"; sc.add(pm);
          const cm=hl3dMan(0xece8dc,own,false); cm.scale.set(.8,.5,.8);""",
"""          const ang=Math.atan2(d[0],d[1]), pm=hl3dMan(0xece8dc,own,false,hl3dUniform(home,true)); pm.scale.setScalar(.8); pm.position.set(m0[0],.7,m0[1]); pm.rotation.y=ang; pm.userData.k="pen"; sc.add(pm);
          const cm=hl3dMan(0xece8dc,own,false,hl3dUniform(home,true)); cm.scale.set(.8,.5,.8);""")
rep("""        const man=hl3dMan(0xece8dc,own,false); man.scale.setScalar(.9); man.position.set(d[0]*sp+n[0]*o,-4.8,d[1]*sp+n[1]*o);""",
"""        const man=hl3dMan(0xece8dc,own,false,hl3dUniform(home,true)); man.scale.setScalar(.9); man.position.set(d[0]*sp+n[0]*o,-4.8,d[1]*sp+n[1]*o);""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
