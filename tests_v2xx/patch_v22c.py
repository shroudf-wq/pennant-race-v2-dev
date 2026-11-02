# v2.2.b のソースに当てると v2.2.c。python3 patch_v22c.py src.html new.html
# 選手のユニフォーム(B案の 2 段目):球団ごとのユニフォームの型。3D だけ(観戦・背景)。2.5D・計算・セーブには触らない。
#   ① hl3dUniform(team,isHome,style,brimAlt):型は球団名のハッシュで固定(forteHash(名前+"ユニ")%4・(名前+"つば")%2)。引数で上書きもできる(テスト用)
#      style 0 無地(v2.2.b のまま)/1 縦縞(胴に絵:ホーム=白地にチームカラーの細い縦縞、ビジター=チームカラー地に暗い縦縞)/
#            2 ラグラン(袖と帽子をチームカラーの暗い色に。ビジターは袖を暗い色)/3 胸の帯(胴に絵:胸の高さにチームカラー(ビジターは白)の横帯)
#      brimAlt 1 のときは帽子のつばを別の色に(ホーム=暗いチームカラー(ラグランは白)、ビジター=白)
#   ② hl3dUniTex(kind,base,acc):64×64 の canvas("stripe" 16px ごとに幅 3 の縦線/"band" y 7〜21 の横帯(胸。ベルトより上))。使い回す(hl3dUniTexC)
#   ③ hl3dMan:uni.tex があれば胴の側面の材質は map(色は白)、上下の面(肩)は無地(材質の配列)。袖=uni.sleeve、つば=uni.brim(無ければ帽子の色)
#   テスト:hl3d_bg.py ⑳(型を 0〜3 に上書きして人を作り、縦縞・帯で胴に絵、ラグランで袖が暗い、つばの色が変わる)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.2.b"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.2.c"; const BASE_V1="v1.4.b";')
rep("""function hl3dUniform(team,isHome){ const T=THREE; let tc; try{ tc=new T.Color(String((typeof teamColorMap!=="undefined" && team && teamColorMap[team])||"#888888")); }catch(e){ tc=new T.Color(0x888888); }
  return isHome? {body:0xf4f2ec, cap:tc.getHex(), trim:tc.getHex(), skin:0xe6c3a0} : {body:tc.getHex(), cap:tc.clone().multiplyScalar(.6).getHex(), trim:0xf4f2ec, skin:0xe6c3a0}; }""",
"""// v2.2.c:ユニフォームの絵(縦縞・胸の帯)。使い回す
const hl3dUniTexC=new Map();
function hl3dUniTex(kind,base,acc){ const k=kind+"|"+base+"|"+acc; if(hl3dUniTexC.has(k)) return hl3dUniTexC.get(k);
  const cv=document.createElement("canvas"); cv.width=64; cv.height=64; const g=cv.getContext("2d"); g.fillStyle="#"+base.toString(16).padStart(6,"0"); g.fillRect(0,0,64,64); g.fillStyle="#"+acc.toString(16).padStart(6,"0");
  if(kind==="stripe"){ for(let x=6;x<64;x+=16) g.fillRect(x,0,3,64); } else if(kind==="band"){ g.fillRect(0,7,64,14); }
  const tx=hl3dNR(()=>new THREE.CanvasTexture(cv)); tx.wrapS=THREE.RepeatWrapping; tx.repeat.set(2,1); hl3dUniTexC.set(k,tx); return tx; }
// v2.2.c:球団ごとのユニフォームの型(球団名のハッシュで固定。style・brimAlt を渡せば上書き)
function hl3dUniform(team,isHome,style,brimAlt){ const T=THREE; let tc; try{ tc=new T.Color(String((typeof teamColorMap!=="undefined" && team && teamColorMap[team])||"#888888")); }catch(e){ tc=new T.Color(0x888888); }
  const h=s=>(forteHash(String(team||"")+s)>>>3), st= (style==null)? h("ユニ")%4 : style, ba= (brimAlt==null)? h("つば")%2 : brimAlt;
  const W=0xf4f2ec, C=tc.getHex(), D=tc.clone().multiplyScalar(.6).getHex();
  const u= isHome? {body:W, cap:C, trim:C, sleeve:C, brim:C, skin:0xe6c3a0, style:st} : {body:C, cap:D, trim:W, sleeve:W, brim:D, skin:0xe6c3a0, style:st};
  if(st===1) u.tex=hl3dUniTex("stripe", u.body, isHome? C : D);
  else if(st===2){ u.sleeve=D; u.cap=D; u.brim=D; }
  else if(st===3) u.tex=hl3dUniTex("band", u.body, isHome? C : W);
  if(ba) u.brim= isHome? (st===2? W : D) : W;   // ラグラン(帽子が暗い)のホームは白いつば
  return u; }""")
rep("""function hl3dMan(col,own,glv,uni,role){ const T=THREE, g=new T.Group(), U=uni||null, m=new T.MeshLambertMaterial({color: U? U.body : col,transparent:true}), sm=new T.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.32,depthWrite:false});
  own.push(m,sm); const mats=[m,sm], ops=[1,.32], mat=c=>{ const x=new T.MeshLambertMaterial({color:c,transparent:true}); own.push(x); mats.push(x); ops.push(1); return x; };
  const skinM= U? mat(U.skin) : m, capM= U? mat(U.cap) : null, trimM= U? mat(U.trim) : m;""",
"""function hl3dMan(col,own,glv,uni,role){ const T=THREE, g=new T.Group(), U=uni||null, m=new T.MeshLambertMaterial(U&&U.tex? {color:0xffffff,map:U.tex,transparent:true} : {color: U? U.body : col,transparent:true}), sm=new T.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.32,depthWrite:false});   // v2.2.c:縦縞・帯は絵
  own.push(m,sm); const mats=[m,sm], ops=[1,.32], mat=c=>{ const x=new T.MeshLambertMaterial({color:c,transparent:true}); own.push(x); mats.push(x); ops.push(1); return x; };
  const skinM= U? mat(U.skin) : m, capM= U? mat(U.cap) : null, trimM= U? mat(U.trim) : m, slvM= U? (U.sleeve===U.trim? trimM : mat(U.sleeve)) : m, brimM= U? ((U.brim==null||U.brim===U.cap)? capM : mat(U.brim)) : null;   // v2.2.c:袖・つば""")
rep("""  const b=new T.Mesh(hl3dGeo("body"),m), h=new T.Mesh(hl3dGeo("head"),skinM), sh=new T.Mesh(hl3dGeo("shadow"),sm);""",
"""  const b=new T.Mesh(hl3dGeo("body"), (U&&U.tex)? [m, mat(U.body), mats[mats.length-1]] : m), h=new T.Mesh(hl3dGeo("head"),skinM), sh=new T.Mesh(hl3dGeo("shadow"),sm);   // v2.2.c:絵のときは胴の上下の面(肩)は無地""")
rep("""  if(U){ const cap=new T.Mesh(hl3dGeo("cap"),capM), brim=new T.Mesh(hl3dGeo("brim"),capM), belt=new T.Mesh(hl3dGeo("belt"),trimM);""",
"""  if(U){ const cap=new T.Mesh(hl3dGeo("cap"),capM), brim=new T.Mesh(hl3dGeo("brim"),brimM), belt=new T.Mesh(hl3dGeo("belt"),trimM);""")
rep("""a.add(new T.Mesh(hl3dGeo("arm"),trimM)); g.add(a); return a; };   // v2.1.f:腕を2本(右=投げる・左=グラブ)。v2.2.b:袖の色""",
"""a.add(new T.Mesh(hl3dGeo("arm"),slvM)); g.add(a); return a; };   // v2.1.f:腕を2本(右=投げる・左=グラブ)。v2.2.b:袖の色""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
