# v2.1.n のソースに当てると v2.1.o。python3 patch_v21o.py src.html new.html
# 試合画面の背景の球場(マウンドから 360 度)の側面を、実際の球場らしくする。見た目だけ(乱数は使わない)。背景だけ(opt.full)で、観戦の 3D は変えない。
#   ユーザーの「側面とかは実際の球場の感じにできないか?(選手のベンチとかエキサイトシートだったりウイング席だったり)」
#   一塁側・三塁側それぞれ、ファウルラインからの道のり s(本塁から)と、ラインの外への離れ o で置く(ファウルゾーンのスタンドは o 26〜66):
#   ① ベンチ(ダッグアウト):s 18〜48・o 14〜24。掘り下げた暗い箱+屋根(縁はホームチームの色)+前の手すり。中に座る選手が4人(上半身だけ見える)
#   ② エキサイトシート:s 54〜(フェンス−40)・o 12〜22。グラウンドと同じ高さの赤い3段の席+前の防球ネット
#   ③ ウイング席:s 6〜18・o 10〜30。本塁の横からベンチの手前へせり出す低い席(4段。バックネットの外)
#   ⑤ ファウルゾーンのスタンドの模様を背景では大きく貼る ⑥ ボードを隠しているときは前方 70 の芝を、ボードのあった場所の上から 8 割の所に合わせる
#   ⑦ 背景の地面の絵を .hl3world の中で描く(人工芝の土の切り抜きが黒くなっていた)。ベンチの選手は屋根の下に収まる大きさ
#   ④ フェンス(ラバー):ファウルゾーンとスタンドの間(o 25.5・s 50〜フェンス−8)に高さ 2.6 の濃い紺の壁
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.n"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.o"; const BASE_V1="v1.4.b";')
rep("""    if(!dome) [[205,128],[335,128]].forEach(([a,r])=>{   // 内野側の照明塔""",
"""    // v2.1.o:ベンチ・エキサイトシート・ウイング席・フェンス(一塁側 sx=1・三塁側 sx=−1)
    const box=(sx,s0,s1,o0,o1,y0,y1,mat)=>{ const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2], sm=(s0+s1)/2, om=(o0+o1)/2;
      const m=add(new T.BoxGeometry(s1-s0,y1-y0,o1-o0), mat); m.position.set(d[0]*sm+n[0]*om,(y0+y1)/2,d[1]*sm+n[1]*om); m.rotation.y=Math.atan2(-d[1],d[0]); return m; };
    const mDark=new T.MeshLambertMaterial({color:0x15181c}), mRoof=new T.MeshLambertMaterial({color:0xcfd4d8}), mRail=new T.MeshLambertMaterial({color:0x8b939b}),
      mPad=new T.MeshLambertMaterial({color:0x1b2a4a}), mHc=new T.MeshLambertMaterial({color:hc}),
      mRed=new T.MeshLambertMaterial({color:0xc4413a,map:crowd}), mWing=new T.MeshLambertMaterial({color:new T.Color(0xffffff).lerp(hc,.25).multiplyScalar(.85),map:crowd}),
      mNet=new T.MeshBasicMaterial({color:0x0c1014,transparent:true,opacity:.28,side:T.DoubleSide,depthWrite:false});
    own.push(mDark,mRoof,mRail,mPad,mHc,mRed,mWing,mNet);
    [1,-1].forEach(sx=>{
      // ① ベンチ:掘り下げた箱(床 −2.5)・奥の壁・屋根・屋根の縁(ホームチームの色)・前の手すり・座る選手
      box(sx,18,48,14,24,-2.5,.2,mDark); box(sx,18,48,22.6,24,-2.5,4.6,mDark);
      box(sx,17,49,15.5,24.5,4.6,5.4,mRoof); box(sx,17,49,15.2,15.8,4.2,5.6,mHc); box(sx,18,48,13.6,14.2,.2,1.8,mRail);
      [22,30,38,44].forEach((sp,i)=>{ const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2], o=19.5+(i%2)*1.2;
        const man=hl3dMan(0xece8dc,own,false); man.scale.setScalar(.9); man.position.set(d[0]*sp+n[0]*o,-4.8,d[1]*sp+n[1]*o); man.rotation.y=Math.atan2(-n[0],-n[1]); sc.add(man); });
      // ② エキサイトシート:3段の赤い席と前の防球ネット
      const e1=FR-40; [[12,15.3,0,1.2],[15.3,18.6,0,2.4],[18.6,22,0,3.6]].forEach(([o0,o1,y0,y1])=>box(sx,54,e1,o0,o1,y0,y1,mRed));
      { const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2], sm=(54+e1)/2, net=add(new T.PlaneGeometry(e1-54,9),mNet);
        net.position.set(d[0]*sm+n[0]*11.4,4.5,d[1]*sm+n[1]*11.4); net.rotation.y=Math.atan2(-d[1],d[0]); }
      // ③ ウイング席:本塁の横から、ベンチの手前へせり出す低い席
      for(let k=0;k<4;k++) box(sx,6,18,10+k*5,15+k*5,0,1.4+k*1.7,mWing);
      // ④ フェンス(ラバー):ファウルゾーンとスタンドの間
      box(sx,50,FR-8,25,26,0,2.6,mPad);
    });
    if(!dome) [[205,128],[335,128]].forEach(([a,r])=>{   // 内野側の照明塔""")
# ⑤ ファウルゾーンのスタンドの模様:背景(opt.full)では大きく貼る(細かすぎて暗い板に見えた)。観戦はそのまま
rep("""    g.setAttribute("uv",new T.BufferAttribute(new Float32Array([0,0, 6,0, 6,1.4, 0,0, 6,1.4, 0,1.4]),2)); g.computeVertexNormals(); own.push(g);""",
"""    const U= (opt&&opt.full)? 1.3 : 6, V= (opt&&opt.full)? .45 : 1.4;   // v2.1.o:背景では模様を大きく
    g.setAttribute("uv",new T.BufferAttribute(new Float32Array([0,0, U,0, U,V, 0,0, U,V, 0,V]),2)); g.computeVertexNormals(); own.push(g);""")
# ⑥ ボードを隠しているときは、前方 70 の芝をボードのあった場所の上から 8 割の所に合わせる(ベンチ・エキサイトシートと、上に照明・空が見える)
rep("""  S.aimY= (mb>b0.top && bt>mb)? ((mb+bt)/2-b0.top) : S.H*.62; }""",
"""  S.aimY= (mb>b0.top && bt>mb)? ((mb+bt)/2-b0.top) : S.H*.62;
  S.hid= !!(S.box.parentElement && S.box.parentElement.classList.contains("hl3sbHide"));   // v2.1.o:ボードを隠しているとき
  if(S.hid){ const r=m.getBoundingClientRect(); S.aimY=r.top+r.height*.8-b0.top; } }""")
rep("""const v=new THREE.Vector3(E[0]+dx*(C.ad||400), C.hy, E[2]+dz*(C.ad||400)).project(S.cam)""",
"""const AD= S.hid? (C.adH||70) : (C.ad||400), v=new THREE.Vector3(E[0]+dx*AD, C.hy, E[2]+dz*AD).project(S.cam)""")
rep("""b.onclick=()=>{ hl3dSbHidden=!hl3dSbHidden; hl3dSbBtnSync(); hl3dBgKick(); };""","""b.onclick=()=>{ hl3dSbHidden=!hl3dSbHidden; hl3dSbBtnSync(); hl3dBgAim(); hl3dBgKick(); };""")
# ⑦ 背景の地面の絵を .hl3world の中で描く(人工芝の土の切り抜き .f-cut などの色は .hl3world の中だけに効くので、外では黒くなっていた)
rep("""tmp.innerHTML=hl3FieldSvg("","グラウンド",pk).replace(""","""tmp.innerHTML='<div class="hl3world">'+hl3FieldSvg("","グラウンド",pk).replace(""")
rep(""".replace(/hlFieldClip[0-9]+/g,"hl3dBgClip");""",""".replace(/hlFieldClip[0-9]+/g,"hl3dBgClip")+'</div>';""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
