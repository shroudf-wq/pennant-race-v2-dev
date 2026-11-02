# v2.2.g のソースに当てると v2.2.h。python3 patch_v22h.py src.html new.html
# 観戦の 3D の内野側(内野席・ファウルゾーンの席・ベンチ・エキサイトシート・バックネット・大屋根・照明塔)を試合画面の背景と同じ作りに。
# ユーザーの「おすすめで一通りやって」の 3 つ目(v2.2.d で外野席だけ同じにしていた)。見た目だけ(計算・2.5D・セーブ・カメラ・フェンスの位置には触らない)。
#   ① hl3dParkMeshes:背景だけだった「if(opt && opt.full)」の中を観戦(OFF)でも通す(FULL=opt.full)。観戦では:
#      ・hl3dStandsFull を only なしで(内野席とファウルゾーンの器 hl3dBowlEdge・外野席 f 30〜150・大屋根の影 roofShade)。wd=hl3dWide0(FR)(フェンスは円のまま・fo/bo 0)
#      ・ファウルゾーンの古い席の板(qm)は消す。地面の円(FR+150)・バックネット(半径 36)と格子と支柱・ベンチ(o 14〜24。背景は +6)・エキサイトシート・ウイング席・ラバーフェンス(o 25)・大屋根・内野側の照明塔
#      ・置かないもの:ネクストバッターズサークルと待つ打者(2.5D の札と重なる)・ブルペン(どちらの型も。ファウルゾーン型はラインの近くで札と重なる)・リボンビジョン(流せない)
#   ② カメラ(HL3D_CAMS)はそのまま。B(0,200,80)は 2 階席(r 86〜130・y 24〜48)と大屋根(r 99〜150・y 56〜63)の上。E/G(r 155・y 205)は屋根の外側の上
#   テスト:hl3d_shots.py(390・1366)・hl3_overlap.py・hl3_manage.py・hl3_perf.py・hl3d_pose.py・hl3_cup.py・hl3_throw.py。hl3d_bg.py は背景(変わらない)。
#          hl3d_bg.py ㉑の観戦の作り(ofFull)の数に bowl(内野席)を足す
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.2.g"; const BASE_V1="v1.4.q";','const APP_VERSION="v2.2.h"; const BASE_V1="v1.4.q";')
rep("""  if(OFF){ const o2={only:"of", ofF0:30, wd:hl3dWide0(FR), look:LOOK, away:opt.away||null, out:(opt.out=opt.out||{})}; hl3dStandsFull(sc,own,FR,hc,o2,dome); }   // v2.2.d:観戦の外野席を背景と同じ作りに(フェンスは円のまま)
""","")
rep("""    const qm=new T.Mesh(g,smat); if(opt && opt.full) qm.visible=false; sc.add(qm); });""",
"""    const qm=new T.Mesh(g,smat); if((opt && opt.full) || OFF) qm.visible=false; sc.add(qm); });   // v2.2.h:観戦も器の席に""")
rep("""  if(opt && opt.full){   // 三 の円柱の角度 t は、地面の図の角度 f(本塁から見て 90°=センター)の f+90°
    const rad=d=>d*Math.PI/180;
    const g0=add(new T.CircleGeometry(WD.FRc+150,64), new T.MeshLambertMaterial({color:0x2a5534})); g0.rotation.x=-Math.PI/2; g0.position.y=-.3;   // ファウルゾーンから外まで続く地面""",
"""  if(opt && (opt.full || OFF)){   // 三 の円柱の角度 t は、地面の図の角度 f(本塁から見て 90°=センター)の f+90°。v2.2.h:観戦(OFF)も同じ作り(FULL=背景だけのもの)
    const rad=d=>d*Math.PI/180, FULL=!!opt.full, BO= WD? WD.bo : 0;
    const g0=add(new T.CircleGeometry((WD? WD.FRc : FR)+150,64), new T.MeshLambertMaterial({color:0x2a5534})); g0.rotation.x=-Math.PI/2; g0.position.y=-.3;   // ファウルゾーンから外まで続く地面""")
rep("""    const NR=36+WD.bo, net=add(""","""    const NR=36+BO, net=add(""")
rep("""      const od=new T.MeshLambertMaterial({color:0x9a7250}); own.push(od);   // ネクストバッターズサークルと待つ打者
      [1,-1].forEach(sx=>{""","""      const od=new T.MeshLambertMaterial({color:0x9a7250}); own.push(od);   // ネクストバッターズサークルと待つ打者(v2.2.h:背景だけ。観戦は 2.5D の札と重なる)
      if(FULL) [1,-1].forEach(sx=>{""")
rep("""    opt.look=LOOK; opt.roofShade=LOOK.roof;   // v2.1.v:球団ごとの型(v2.1.w:外野席の種類にも使う。v2.1.x:先頭で決める)。v2.2.g:大屋根の影
    hl3dStandsFull(sc,own,FR,hc,opt,dome);   // v2.1.p:段のある席・お客さん・応援旗""",
"""    opt.look=LOOK; opt.roofShade=LOOK.roof;   // v2.1.v:球団ごとの型(v2.1.w:外野席の種類にも使う。v2.1.x:先頭で決める)。v2.2.g:大屋根の影
    const so= FULL? opt : {wd:hl3dWide0(FR), ofF0:30, look:LOOK, roofShade:LOOK.roof, away:opt.away||null, out:(opt.out=opt.out||{})};   // v2.2.h:観戦はフェンス=円・外野席 f 30〜150・リボンなし
    hl3dStandsFull(sc,own,FR,hc,so,dome);   // v2.1.p:段のある席・お客さん・応援旗""")
rep("""    if(LOOK.pen===0){   // v2.2.a:ブルペン(フェンス裏型)""","""    if(FULL && LOOK.pen===0){   // v2.2.a:ブルペン(フェンス裏型。v2.2.h:背景だけ)""")
rep("""    const FO=6, FRl=WD.FRl;   // v2.1.t:ファウルゾーンを広げる(ベンチ・エキサイトシート・ウイング席は o+6、席とラバーフェンスは o+14)""",
"""    const FO= FULL? 6 : 0, FRl= WD? WD.FRl : FR, FOP= WD? WD.fo : 0;   // v2.1.t:ファウルゾーンを広げる(ベンチ・エキサイトシート・ウイング席は o+6、席とラバーフェンスは o+14)。v2.2.h:観戦は広げない""")
rep("""      box(sx,50,FRl-8,25+WD.fo,26+WD.fo,0,2.6,mPad);""","""      box(sx,50,FRl-8,25+FOP,26+FOP,0,2.6,mPad);""")
rep("""      if(LOOK.pen===1){   // v2.2.a:ブルペン(ファウルゾーン型)""","""      if(FULL && LOOK.pen===1){   // v2.2.a:ブルペン(ファウルゾーン型。v2.2.h:背景だけ)""")
rep("""    if(!dome) [[205,128+WD.bo],[335,128+WD.bo]].forEach(([a,r])=>{""","""    if(!dome) [[205,128+BO],[335,128+BO]].forEach(([a,r])=>{""")
# ③ 観戦は軽く:内野席の区画を 60 ごと(背景は 30)、ベンチに座る選手を 2 人(背景は 4 人)。draw call 252→約 195(v2.2.g は 134)
rep("""  stand(PE(E1,v=>v*40), 0, 16, 8, E1.L, Math.round(E1.L/30), mixT, 2, null);   // 1 階(奥行き 40・8 列・0〜16)""",
"""  const SL=opt.secL||30;   // v2.2.h:区画の長さ(観戦は 60 で軽く)
  stand(PE(E1,v=>v*40), 0, 16, 8, E1.L, Math.round(E1.L/SL), mixT, 2, null);   // 1 階(奥行き 40・8 列・0〜16)""")
rep("""  stand(PE(E2,v=>46+v*44), 24, 24, 9, E2.L, Math.round(E2.L/30), mixT, 2, null, null, shade2);   // 2 階(46〜90・9 列・24〜48)""",
"""  stand(PE(E2,v=>46+v*44), 24, 24, 9, E2.L, Math.round(E2.L/SL), mixT, 2, null, null, shade2);   // 2 階(46〜90・9 列・24〜48)""")
rep("""    const so= FULL? opt : {wd:hl3dWide0(FR), ofF0:30, look:LOOK, roofShade:LOOK.roof, away:opt.away||null, out:(opt.out=opt.out||{})};""",
"""    const so= FULL? opt : {wd:hl3dWide0(FR), ofF0:30, look:LOOK, roofShade:LOOK.roof, secL:60, away:opt.away||null, out:(opt.out=opt.out||{})};""")
rep("""      [22,30,38,44].forEach((sp,i)=>{""","""      (FULL? [22,30,38,44] : [26,40]).forEach((sp,i)=>{ /* v2.2.h:観戦は 2 人 */""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
