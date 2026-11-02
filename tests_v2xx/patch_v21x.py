# v2.1.w のソースに当てると v2.1.x。python3 patch_v21x.py src.html new.html
# 試合画面の背景の球場:フェンスの高さと色・外野 2 階席・照明塔(A-4)。見た目だけ(背景 opt.full のときだけ。計算・観戦の 3D・セーブには触らない)。
#   hl3dParkLook に足す型(球団名のハッシュで固定):
#   ① fence:0 低い(高さ 7・今まで)/1 高い(高さ 11)。fcol:フェンスの色 0 濃い緑/1 濃い紺/2 黒に近い灰。帯はフェンスの上に合わせる(観戦の 3D は今のまま)
#   ② deck2:外野 2 階席(屋外だけ)。外野席の後ろ(Rf+72〜112)に前の壁(ホームの色・y 40〜46)と 7 列の席(y 46〜68)。バックスクリーンの後ろは除く
#   ③ lights:0 塔 6 本(今まで)/1 塔 4 本(両翼の角の 2 本なし)/2 低い塔 6 本(柱 50・横長のヘッド 24×5)。大屋根の上の塔は柱 40(型 2 は 30)。外野 2 階席の上の塔は天面 68 から柱 50(型 2 は 30)
#   ④ 型は hl3dParkMeshes の先頭で決める(フェンスが先に要るので)
#   テスト:hl3d_bg.py ⑮(型を強制して、フェンスの高さ・2 階席の有無・照明塔の本数が合う)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.w"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.x"; const BASE_V1="v1.4.b";')
rep("""  return {roof: dome? 0 : h("大屋根")%3, of: dome? (h("外野席")%2)*2 : h("外野席")%3}; }   // v2.1.w:of 0 ベンチ/1 芝生/2 テラス(ドームは芝生なし)""",
"""  return {roof: dome? 0 : h("大屋根")%3, of: dome? (h("外野席")%2)*2 : h("外野席")%3,   // v2.1.w:of 0 ベンチ/1 芝生/2 テラス(ドームは芝生なし)
    fence: h("フェンス")%2, fcol: h("フェンスの色")%3, deck2: dome? 0 : h("外野2階")%2, lights: h("照明")%3}; }   // v2.1.x:フェンス 0 低い/1 高い・色 3 つ・外野 2 階席・照明塔 0 6本/1 4本/2 低い塔""")
rep("""  const fence= WD? add(hl3dArcWall(T,WD.Rf,30,150,0,7,56), new T.MeshLambertMaterial({color:0x1d4a30,side:T.DoubleSide}))
    : add(new T.CylinderGeometry(FR,FR,7,48,1,true,th0,thL), new T.MeshLambertMaterial({color:0x1d4a30,side:T.DoubleSide})); if(!WD) fence.position.y=3.5;""",
"""  const LOOK= WD? hl3dParkLook(home,pk) : null, FH= (LOOK && LOOK.fence)? 11 : 7, FC= LOOK? [0x1d4a30,0x1b2a4a,0x2a2e33][LOOK.fcol] : 0x1d4a30;   // v2.1.x:フェンスの高さと色(背景だけ)
  const fence= WD? add(hl3dArcWall(T,WD.Rf,30,150,0,FH,56), new T.MeshLambertMaterial({color:FC,side:T.DoubleSide}))
    : add(new T.CylinderGeometry(FR,FR,7,48,1,true,th0,thL), new T.MeshLambertMaterial({color:0x1d4a30,side:T.DoubleSide})); if(!WD) fence.position.y=3.5; fence.userData.k="fence"; fence.userData.h=FH;""")
rep("""  const band= WD? add(hl3dArcWall(T,f=>WD.Rf(f)+.3,30,150,6.7,8.1,56), new T.MeshLambertMaterial({color:hc,side:T.DoubleSide}))""",
"""  const band= WD? add(hl3dArcWall(T,f=>WD.Rf(f)+.3,30,150,FH-.3,FH+1.1,56), new T.MeshLambertMaterial({color:hc,side:T.DoubleSide}))""")
rep("""  if(!dome) [[20,24],[66,80],[114,80],[160,24]].forEach(([a,o])=>{   // 照明塔(屋根つきの球場には無い)。v2.1.t:背景ではフェンスの形 Rf に合わせる
    const r= WD? WD.Rf(a)+o : FR+o, p=hl3dP(...hlPt(a,r),0), pole=add(new T.CylinderGeometry(1.1,1.6,68,6), new T.MeshLambertMaterial({color:0x7d868f})); pole.position.set(p.x,34,p.z); pole.userData.k="tower";
    const head=add(new T.BoxGeometry(15,8,1.6), new T.MeshBasicMaterial({color:0xfff2c2})); head.position.set(p.x,70,p.z); head.lookAt(0,40,-60); heads.push(head.position.clone()); });""",
"""  const LT= LOOK? LOOK.lights : 0, HP= LT===2? 50 : 68, HW= LT===2? [24,5] : [15,8];   // v2.1.x:照明塔の型(0 6本/1 4本/2 低い塔・横長のヘッド)
  if(!dome) (LT===1? [[66,80],[114,80]] : [[20,24],[66,80],[114,80],[160,24]]).forEach(([a,o])=>{   // 照明塔(屋根つきの球場には無い)。v2.1.t:背景ではフェンスの形 Rf に合わせる
    const onD= !!(LOOK && LOOK.deck2 && o===80), y0= onD? 68 : 0, hp= onD? (LT===2? 30 : 50) : HP;   // 外野 2 階席の上に立つ塔は 2 階席の天面(68)から
    const r= WD? WD.Rf(a)+o : FR+o, p=hl3dP(...hlPt(a,r),0), pole=add(new T.CylinderGeometry(1.1,1.6,hp,6), new T.MeshLambertMaterial({color:0x7d868f})); pole.position.set(p.x,y0+hp/2,p.z); pole.userData.k="tower";
    const head=add(new T.BoxGeometry(HW[0],HW[1],1.6), new T.MeshBasicMaterial({color:0xfff2c2})); head.position.set(p.x,y0+hp+2,p.z); head.lookAt(0,40,-60); heads.push(head.position.clone()); });""")
rep("""    const LOOK=hl3dParkLook(home,pk); opt.look=LOOK;   // v2.1.v:球団ごとの型(v2.1.w:外野席の種類にも使う)""","""    opt.look=LOOK;   // v2.1.v:球団ごとの型(v2.1.w:外野席の種類にも使う。v2.1.x:先頭で決める)""")
rep("""      const on= !!(ROOF && a>=ROOF.f0 && a<=ROOF.f1 && r>=ROOF.r0 && r<=ROOF.r1), y0= on? ROOF.y1 : 0, hp= on? 40 : 68;""",
"""      const on= !!(ROOF && a>=ROOF.f0 && a<=ROOF.f1 && r>=ROOF.r0 && r<=ROOF.r1), y0= on? ROOF.y1 : 0, hp= on? (LT===2? 30 : 40) : HP;""")
rep("""      const head=add(new T.BoxGeometry(15,8,1.6), new T.MeshBasicMaterial({color:0xfff2c2})); head.position.set(p.x,y0+hp+2,p.z); head.lookAt(0,40,-60); heads.push(head.position.clone()); });""",
"""      const head=add(new T.BoxGeometry(HW[0],HW[1],1.6), new T.MeshBasicMaterial({color:0xfff2c2})); head.position.set(p.x,y0+hp+2,p.z); head.lookAt(0,40,-60); heads.push(head.position.clone()); });""")
# ② 外野 2 階席
rep("""      stand((u,v)=>fx(45+u*90, Rf(45+u*90)-6.5+v*6), 1.4, 3.6, 2, Math.PI/2*FR, 9, u=>ofTint((45+u*90-30)/120), 3, [(82.5-45)/90,(97.5-45)/90]); } }""",
"""      stand((u,v)=>fx(45+u*90, Rf(45+u*90)-6.5+v*6), 1.4, 3.6, 2, Math.PI/2*FR, 9, u=>ofTint((45+u*90-30)/120), 3, [(82.5-45)/90,(97.5-45)/90]); } }
  if(opt.look && opt.look.deck2){   // v2.1.x:外野 2 階席。外野席の後ろ(Rf+72〜112)に前の壁(ホームの色・y 40〜46)と 7 列の席(y 46〜68)。バックスクリーンの後ろは除く
    const D2=geo(); for(let j=0;j<48;j++){ const a=30+120*j/48, b=30+120*(j+1)/48, ua=j/48, ub=(j+1)/48; if(ub>bsSkip[0] && ua<bsSkip[1]) continue;
      const A=fx(a,Rf(a)+72), B=fx(b,Rf(b)+72); quad(D2,[A[0],40,A[1]],[B[0],40,B[1]],[B[0],46,B[1]],[A[0],46,A[1]]); }
    const d2=mesh(D2,bandM); if(d2) d2.userData.k="deck2";
    stand((u,v)=>fx(30+u*120, Rf(30+u*120)+72+v*40), 46, 22, 7, Math.PI/2*(FR+40), 12, ofTint, 3, bsSkip); }""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
