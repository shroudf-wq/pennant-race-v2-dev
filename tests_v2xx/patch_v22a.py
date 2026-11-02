# v2.1.z のソースに当てると v2.2.a。python3 patch_v22a.py src.html new.html
# 試合画面の背景の球場:ブルペン(B-5)。見た目だけ(背景 opt.full のときだけ。計算・観戦の 3D・セーブには触らない)。
#   ユーザーの「あとはブルペンも入れて」。グラウンドを広げた(v2.1.t)ので、ファウルゾーン型が置けるようになった。
#   ① hl3dParkLook に pen:1 ファウルゾーン型/0 フェンス裏型(forteHash(名前+"ブルペン")%2)。芝生席(of=1)の球場はファウルゾーン型に固定
#   ② ファウルゾーン型:両ラインの外(o 8 と 14)に 2 本の投球レーン(s 78→121。長さ 43=実物の 18.44m を塁間の比で。一塁・三塁の先)。
#      マウンド(土の円・半径 3)・プレートの土(半径 2.6)と白いプレート・投手(.8)・捕手(.8・しゃがみ y .62)。レーンの間に薄い芝の帯。エキサイトシートの前(o 17)に低い柵
#   ③ フェンス裏型:ライト(f 52〜64)とレフト(f 116〜128)の外野席の下 4 列を抜いて箱(床 FH−4・奥の壁 Rf+30・高さ 12.5)にし、
#      フェンスに沿った 2 本のレーン(Rf+13・Rf+23)にマウンド・プレート・投手・捕手。フェンスの上に頭が覗く。stand() に lowSkip(下 4 列だけ抜く範囲)を足した
#   ④ 印:投手・捕手は userData.k="pen"、フェンス裏の箱の床は "penBox"
#   テスト:hl3d_bg.py ⑱(型を強制して、pen の人 8・箱 0/2)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.z"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.2.a"; const BASE_V1="v1.4.b";')
rep("""    fence: h("フェンス")%2, fcol: h("フェンスの色")%3, deck2: dome? 0 : h("外野2階")%2, lights: h("照明")%3}; }""",
"""    fence: h("フェンス")%2, fcol: h("フェンスの色")%3, deck2: dome? 0 : h("外野2階")%2, lights: h("照明")%3,
    pen: (!dome && h("外野席")%3===1)? 1 : h("ブルペン")%2}; }   // v2.2.a:ブルペン 1 ファウルゾーン型/0 フェンス裏型(芝生席の球場はファウルゾーン型)""")
# ③ stand() に lowSkip
rep("""  const stand=(P,h0,H,N,L,K,tint,aisle,skip)=>{""","""  const stand=(P,h0,H,N,L,K,tint,aisle,skip,lowSkip)=>{""")
rep("""          if(skip && b>skip[0] && a<skip[1]){ pcs.push(null); continue; }""",
"""          if(skip && b>skip[0] && a<skip[1]){ pcs.push(null); continue; }
          if(lowSkip && i<4 && lowSkip.some(([p0,p1])=>b>p0 && a<p1)){ pcs.push(null); continue; }   // v2.2.a:フェンス裏のブルペン(下 4 列だけ抜く)""")
rep("""    stand((u,v)=>fx(22+u*136, Rf(22+u*136)+5+v*81), 0, 40, 13, Math.PI/2*(FR+40), 12, ofTint, 3, bsSkip);   // v2.1.t:f 30〜150(両翼の線の外まで回して角の切れ目を埋める)・フェンスの形 Rf に沿う""",
"""    const penLow= (opt.look && opt.look.pen===0)? [[(52-22)/136,(64-22)/136],[(116-22)/136,(128-22)/136]] : null;   // v2.2.a:フェンス裏のブルペンの範囲
    stand((u,v)=>fx(22+u*136, Rf(22+u*136)+5+v*81), 0, 40, 13, Math.PI/2*(FR+40), 12, ofTint, 3, bsSkip, penLow);   // v2.1.t:f 30〜150(両翼の線の外まで回して角の切れ目を埋める)・フェンスの形 Rf に沿う""")
# ② ④ ブルペン本体(ラバーフェンスの後に)
rep("""      box(sx,50,FRl-8,25+WD.fo,26+WD.fo,0,2.6,mPad);""",
"""      box(sx,50,FRl-8,25+WD.fo,26+WD.fo,0,2.6,mPad);
      if(LOOK.pen===1){   // v2.2.a:ブルペン(ファウルゾーン型):ラインの外 o 8・14 に 2 本の投球レーン(s 78→121)
        const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2], P=(s_,o)=>[d[0]*s_+n[0]*o, d[1]*s_+n[1]*o];
        box(sx,76,123,5,17,-.05,.1,mLane);   // 少し薄い芝の帯
        [8,14].forEach(o=>{ const m0=P(78,o), m1=P(121,o), mo=add(new T.CylinderGeometry(3,3.6,.7,16),mDirt); mo.position.set(m0[0],.35,m0[1]);
          const pl=add(new T.CylinderGeometry(2.6,2.6,.3,16),mDirt); pl.position.set(m1[0],.15,m1[1]); const hp=add(new T.BoxGeometry(1.4,.2,1.4),mPlate); hp.position.set(m1[0],.35,m1[1]);
          const ang=Math.atan2(d[0],d[1]), pm=hl3dMan(0xece8dc,own,false); pm.scale.setScalar(.8); pm.position.set(m0[0],.7,m0[1]); pm.rotation.y=ang; pm.userData.k="pen"; sc.add(pm);
          const cm=hl3dMan(0xece8dc,own,false); cm.scale.set(.8,.5,.8); cm.position.set(m1[0],.3,m1[1]); cm.rotation.y=ang+Math.PI; cm.userData.k="pen"; sc.add(cm); });
        box(sx,76,123,17,17.6,0,1.2,mRail); }""")
rep("""      mNet=new T.MeshBasicMaterial({color:0x0c1014,transparent:true,opacity:.28,side:T.DoubleSide,depthWrite:false});
    own.push(mDark,mRoof,mRail,mPad,mHc,mRed,mWing,mNet);""",
"""      mNet=new T.MeshBasicMaterial({color:0x0c1014,transparent:true,opacity:.28,side:T.DoubleSide,depthWrite:false}),
      mDirt=new T.MeshLambertMaterial({color:0x9a7250}), mPlate=new T.MeshLambertMaterial({color:0xf0ede4}), mLane=new T.MeshLambertMaterial({color:0x2f6e40});   // v2.2.a:ブルペン
    own.push(mDark,mRoof,mRail,mPad,mHc,mRed,mWing,mNet,mDirt,mPlate,mLane);
    if(LOOK.pen===0){   // v2.2.a:ブルペン(フェンス裏型):ライトとレフトの外野席の下 4 列を抜いた箱(床 FH−4)。フェンスに沿った 2 本のレーン
      const Rf=WD.Rf, fy=FH-4, fx2=(f,r)=>{ const t=(f+90)*Math.PI/180; return [r*Math.sin(t), r*Math.cos(t)]; }, mWall=new T.MeshLambertMaterial({color:0x666c73,side:T.DoubleSide}), mFl=new T.MeshLambertMaterial({color:0x3f6e3c}); own.push(mWall,mFl);
      [[52,64],[116,128]].forEach(([f0,f1])=>{ const p=[], w=[]; const q=(A,B,C,D,o)=>o.push(...A,...B,...C,...A,...C,...D);
        for(let j=0;j<8;j++){ const a=f0+(f1-f0)*j/8, b=f0+(f1-f0)*(j+1)/8, A=fx2(a,Rf(a)+5), B=fx2(b,Rf(b)+5), A2=fx2(a,Rf(a)+30), B2=fx2(b,Rf(b)+30);
          q([A[0],fy,A[1]],[B[0],fy,B[1]],[B2[0],fy,B2[1]],[A2[0],fy,A2[1]],p); q([A2[0],fy,A2[1]],[B2[0],fy,B2[1]],[B2[0],12.5,B2[1]],[A2[0],12.5,A2[1]],w); }
        [f0,f1].forEach(f=>{ const A=fx2(f,Rf(f)+5), B=fx2(f,Rf(f)+30); q([A[0],fy,A[1]],[B[0],fy,B[1]],[B[0],12.5,B[1]],[A[0],12.5,A[1]],w); });
        const g=new T.BufferGeometry(); g.setAttribute("position",new T.BufferAttribute(new Float32Array(p),3)); g.computeVertexNormals(); own.push(g); const fl=new T.Mesh(g,mFl); fl.userData.k="penBox"; sc.add(fl);
        const gw=new T.BufferGeometry(); gw.setAttribute("position",new T.BufferAttribute(new Float32Array(w),3)); gw.computeVertexNormals(); own.push(gw); sc.add(new T.Mesh(gw,mWall));
        [13,23].forEach(ro=>{ const m0=fx2(f0+1.6,Rf(f0+1.6)+ro), m1=fx2(f1-1.6,Rf(f1-1.6)+ro), mo=add(new T.CylinderGeometry(2.6,3.2,.7,16),mDirt); mo.position.set(m0[0],fy+.35,m0[1]);
          const pl=add(new T.CylinderGeometry(2.3,2.3,.3,16),mDirt); pl.position.set(m1[0],fy+.15,m1[1]); const hp=add(new T.BoxGeometry(1.2,.2,1.2),mPlate); hp.position.set(m1[0],fy+.35,m1[1]);
          const ang=Math.atan2(m1[0]-m0[0],m1[1]-m0[1]), pm=hl3dMan(0xece8dc,own,false); pm.scale.setScalar(.8); pm.position.set(m0[0],fy+.7,m0[1]); pm.rotation.y=ang; pm.userData.k="pen"; sc.add(pm);
          const cm=hl3dMan(0xece8dc,own,false); cm.scale.set(.8,.5,.8); cm.position.set(m1[0],fy+.3,m1[1]); cm.rotation.y=ang+Math.PI; cm.userData.k="pen"; sc.add(cm); }); }); }""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
