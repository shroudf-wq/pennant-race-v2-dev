# v2.2.c のソースに当てると v2.2.d。python3 patch_v22d.py src.html new.html
# 観戦の 3D の外野席を、試合画面の背景と同じ作りにする。見た目だけ(計算・2.5D・セーブには触らない)。
#   ユーザーの「試合中の画面を外野だけでもいまのと同じに出来ないか?」
#   ① hl3dWide0(FR):背景の広い形の代わりに「フェンス=本塁から FR の円」(Rf=FR・warp なし・fo/bo 0)。観戦ではフェンスの位置と形を変えない(打球の落点・本塁打の絵と合わせる)
#   ② hl3dStandsFull に opt.only="of":内野席とファウルゾーンの器(hl3dBowlEdge の部分)を作らない。外野席の範囲は opt.ofF0(観戦 30〜150°。背景 22〜158°)
#   ③ hl3dParkMeshes の opt.ofFull(観戦):球団の型 LOOK を引き、今までの外野席の円柱(crowd の模様)を消して hl3dStandsFull(only=of) で建てる。
#      バックスクリーンは今までの 46×30 のまま(本塁打のカメラの前に立つので大きくしない)。照明塔の型も効く。フェンス・帯・内野席・ファウルゾーンの席・バックネットは今まで通り。
#      フェンス裏型のブルペンの箱は観戦では作らない(penLow は opt.full のときだけ)
#   ④ hl3dStart0 から opt={ofFull:true} で呼ぶ
#   テスト:hl3d_shots.py・hl3_overlap.py・hl3_perf.py・hl3_manage.py・hl3d_pose.py。hl3d_bg.py は背景(変わらない)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.2.c"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.2.d"; const BASE_V1="v1.4.b";')
# ① 円のフェンス
rep("""function hl3dWide(FR){ const FRl=Math.round(FR*1.21), FRc=Math.round(FR*1.48);""",
"""function hl3dWide0(FR){ return {FR, FRl:FR, FRc:FR, Rf:()=>FR, warp:(f,r)=>r, fo:0, bo:0}; }   // v2.2.d:観戦用(フェンス=円のまま)
function hl3dWide(FR){ const FRl=Math.round(FR*1.21), FRc=Math.round(FR*1.48);""")
# ② 外野席だけ・範囲
rep("""  const ofTint=u=>{ const f=22+u*136;""","""  const F0= (opt.ofF0!=null)? opt.ofF0 : 22, FW=180-2*F0;   // v2.2.d:外野席の範囲(背景 22〜158°、観戦 30〜150°)
  const ofTint=u=>{ const f=F0+u*FW;""")
s=s.replace("22+u*136","F0+u*FW").replace("(82.5-22)/136","(82.5-F0)/FW").replace("(97.5-22)/136","(97.5-F0)/FW").replace("22+136*j/48","F0+FW*j/48").replace("22+136*(j+1)/48","F0+FW*(j+1)/48")
rep("""    const penLow= (opt.look && opt.look.pen===0)?""","""    const penLow= (opt.full && opt.look && opt.look.pen===0)?""")
rep("""  // v2.1.z:内野席とファウルゾーンの席をひと続きの器に。内縁の折れ線 E(本塁の後ろは半径 55 の弧、ラインの外は「ラインから 40」の直線)から外へ
  const OI=26+FO, RB=40+BO, E1=hl3dBowlEdge(OI,RB,FRl-14), E2=hl3dBowlEdge(OI,RB,FRl-50);   // 1 階は s=FRl−14 まで、2 階は FRl−50 まで""",
"""  // v2.1.z:内野席とファウルゾーンの席をひと続きの器に。内縁の折れ線 E(本塁の後ろは半径 55 の弧、ラインの外は「ラインから 40」の直線)から外へ
  if(opt.only!=="of"){   // v2.2.d:観戦(only="of")では外野席だけ
  const OI=26+FO, RB=40+BO, E1=hl3dBowlEdge(OI,RB,FRl-14), E2=hl3dBowlEdge(OI,RB,FRl-50);   // 1 階は s=FRl−14 まで、2 階は FRl−50 まで""")
rep("""      const A=[a.p[0]+a.n[0]*40,a.p[1]+a.n[1]*40], B=[b.p[0]+b.n[0]*40,b.p[1]+b.n[1]*40]; quad(CON,[A[0],16,A[1]],[B[0],16,B[1]],[B[0],19,B[1]],[A[0],19,A[1]]); } }
  mesh(SEAT,seatM); mesh(CON,conM); mesh(BAND,bandM);""",
"""      const A=[a.p[0]+a.n[0]*40,a.p[1]+a.n[1]*40], B=[b.p[0]+b.n[0]*40,b.p[1]+b.n[1]*40]; quad(CON,[A[0],16,A[1]],[B[0],16,B[1]],[B[0],19,B[1]],[A[0],19,A[1]]); } } }
  mesh(SEAT,seatM); mesh(CON,conM); mesh(BAND,bandM);""")
# ③ 観戦の hl3dParkMeshes
rep("""  const LOOK= WD? hl3dParkLook(home,pk) : null, FH= (LOOK && LOOK.fence)? 11 : 7,""","""  const OFF=!!(opt && opt.ofFull && !(opt && opt.full)), LOOK= (WD || OFF)? hl3dParkLook(home,pk) : null, FH= (LOOK && LOOK.fence && WD)? 11 : 7,""")
rep("""sc.add(stands); stands.position.y=20; if(opt && opt.full) stands.visible=false;   // v2.1.p:背景は段のある席(hl3dStandsFull)""",
"""sc.add(stands); stands.position.y=20; if((opt && opt.full) || OFF) stands.visible=false;   // v2.1.p:背景は段のある席(hl3dStandsFull)。v2.2.d:観戦も
  if(OFF){ const o2={only:"of", ofF0:30, wd:hl3dWide0(FR), look:LOOK, away:opt.away||null, out:(opt.out=opt.out||{})}; hl3dStandsFull(sc,own,FR,hc,o2,dome); }   // v2.2.d:観戦の外野席を背景と同じ作りに(フェンスは円のまま)""")
# ④ 観戦から
rep("""  hl3dParkMeshes(sc,own,pk,hl3Home);   // v2.1.j:フェンス・観客席・帯・照明塔・屋根(試合画面の背景と同じもの)""",
"""  const awayNm= hl3Teams? (hl3Teams.home===hl3Teams.bat? hl3Teams.fld : hl3Teams.bat) : null;   // v2.2.d:ビジター(応援席の色)
  hl3dParkMeshes(sc,own,pk,hl3Home,{ofFull:true, away:(awayNm && typeof teamColorMap!=="undefined" && teamColorMap[awayNm])||null});   // v2.1.j:フェンス・観客席・帯・照明塔・屋根(試合画面の背景と同じもの)。v2.2.d:外野席は背景と同じ作り""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
