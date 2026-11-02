# v2.1.v のソースに当てると v2.1.w。python3 patch_v21w.py src.html new.html
# 試合画面の背景の球場:外野席の種類(A-3)。見た目だけ(背景 opt.full のときだけ。計算・観戦の 3D・セーブには触らない)。
#   ① hl3dParkLook に of:0 ベンチ席(今まで)/1 芝生席/2 テラス席。forteHash(名前+"外野席")>>>3 を 3 で割った余り。ドームは芝生なし(0 か 2)
#   ② 芝生席:外野席の下 6 割(高さ 0〜24)をなだらかな芝の斜面(段なし・緑)にして、まばらに人(決まった数列で 260 人。バックスクリーンの後ろは除く)。
#      上 4 割はベンチ席(5 列)。芝の斜面は userData.k="lawn"。斜面の人はウェーブに乗らない(タオルの入れ替えも "mix" なのでなし)
#   ③ テラス席:フェンスの内側(Rf−8)に低いフェンス(高さ 2.6・上にホームの色の帯)と床、その後ろに 2 列の席(y 1.4〜5)。f 45〜135(フェアの中だけ)。
#      外側の席は今までどおり。低いフェンスは userData.k="terrace"
#   ④ 型は hl3dParkMeshes で決めて opt.look で渡す(hl3dStandsFull・大屋根で共用)
#   テスト:hl3d_bg.py ⑭(型を 0/1/2 に強制して、芝生・テラスの部品の有無が合う)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.v"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.w"; const BASE_V1="v1.4.b";')
rep("""  return {roof: dome? 0 : h("大屋根")%3}; }""","""  return {roof: dome? 0 : h("大屋根")%3, of: dome? (h("外野席")%2)*2 : h("外野席")%3}; }   // v2.1.w:of 0 ベンチ/1 芝生/2 テラス(ドームは芝生なし)""")
rep("""    hl3dStandsFull(sc,own,FR,hc,opt,dome);   // v2.1.p:段のある席・お客さん・応援旗
    const LOOK=hl3dParkLook(home,pk), ROOF= LOOK.roof? hl3dBigRoof(sc,own,add,LOOK.roof) : null;   // v2.1.v:内野席の大屋根(球団ごとの型)""",
"""    const LOOK=hl3dParkLook(home,pk); opt.look=LOOK;   // v2.1.v:球団ごとの型(v2.1.w:外野席の種類にも使う)
    hl3dStandsFull(sc,own,FR,hc,opt,dome);   // v2.1.p:段のある席・お客さん・応援旗
    const ROOF= LOOK.roof? hl3dBigRoof(sc,own,add,LOOK.roof) : null;   // v2.1.v:内野席の大屋根(球団ごとの型)""")
rep("""  stand((u,v)=>fx(30+u*120, Rf(30+u*120)+5+v*81), 0, 40, 13, Math.PI/2*(FR+40), 12,   // v2.1.t:f 30〜150(両翼の線の外まで回して角の切れ目を埋める)・フェンスの形 Rf に沿う
    u=>{ const f=30+u*120; return f<80? ["home",hcs,.62] : f>100? (acs? ["away",acs,.62] : mixT()) : mixT(); }, 3, [(82.5-30)/120,(97.5-30)/120]);""",
"""  const ofTint=u=>{ const f=30+u*120; return f<80? ["home",hcs,.62] : f>100? (acs? ["away",acs,.62] : mixT()) : mixT(); }, bsSkip=[(82.5-30)/120,(97.5-30)/120], OF=(opt.look&&opt.look.of)||0;
  if(OF===1){   // v2.1.w:芝生席。下 6 割は芝の斜面(段なし)にまばらな人、上 4 割はベンチ席
    const LG=geo(), lawnM=new T.MeshLambertMaterial({color:new T.Color(0x4f8a44).multiplyScalar(lit),side:T.DoubleSide}); own.push(lawnM);
    const PL=(u,v)=>fx(30+u*120, Rf(30+u*120)+5+v*81), hL=v=>24*Math.pow(v/.6,1.15);
    for(let j=0;j<48;j++){ const a=j/48, b=(j+1)/48; if(b>bsSkip[0] && a<bsSkip[1]) continue;
      for(let i=0;i<6;i++){ const v0=i/10, v1=(i+1)/10, A0=PL(a,v0), B0=PL(b,v0), A1=PL(a,v1), B1=PL(b,v1);
        quad(LG,[A0[0],hL(v0),A0[1]],[B0[0],hL(v0),B0[1]],[B1[0],hL(v1),B1[1]],[A1[0],hL(v1),A1[1]]); } }
    const lawn=mesh(LG,lawnM); if(lawn) lawn.userData.k="lawn";
    let x=777; const rnd=()=>{ x=(Math.imul(x,1103515245)+12345)&0x7fffffff; return x/0x7fffffff; };   // 決まった数列(試合の乱数は使わない)
    const PP=geo(); for(let i=0;i<260;i++){ const u=rnd(), v=rnd()*.56; if(u>bsSkip[0]-.02 && u<bsSkip[1]+.02) continue; const k=Math.floor(rnd()*10);
      const c=PL(u,v), t=PL(u+.004,v), dx=t[0]-c[0], dz=t[1]-c[1], L=Math.hypot(dx,dz), ex=dx/L*2, ez=dz/L*2, y=hL(v)+.1, ph=3.2;
      quad(PP,[c[0]-ex,y,c[1]-ez],[c[0]+ex,y,c[1]+ez],[c[0]+ex,y+ph,c[1]+ez],[c[0]-ex,y+ph,c[1]-ez],[k/10,0,(k+1)/10,0,(k+1)/10,1,k/10,1]); }
    mesh(PP,pMat(tex("mix",hcs,.18),"mix"));
    stand((u,v)=>fx(30+u*120, Rf(30+u*120)+5+(.6+v*.4)*81), 24, 16, 5, Math.PI/2*(FR+40), 12, ofTint, 3, bsSkip);
  } else {
    stand((u,v)=>fx(30+u*120, Rf(30+u*120)+5+v*81), 0, 40, 13, Math.PI/2*(FR+40), 12, ofTint, 3, bsSkip);   // v2.1.t:f 30〜150(両翼の線の外まで回して角の切れ目を埋める)・フェンスの形 Rf に沿う
    if(OF===2){   // v2.1.w:テラス席。フェンスの内側(Rf−8)に低いフェンスと床、その後ろに 2 列の席(f 45〜135)
      const tfM=new T.MeshLambertMaterial({color:0x1d4a30,side:T.DoubleSide}); own.push(tfM);
      const tf=new T.Mesh(hl3dArcWall(T,f=>Rf(f)-8,45,135,0,2.6,48),tfM); tf.userData.k="terrace"; own.push(tf.geometry); sc.add(tf);
      const tb=new T.Mesh(hl3dArcWall(T,f=>Rf(f)-7.7,45,135,2.5,3.3,48),bandM); own.push(tb.geometry); sc.add(tb);
      const TG=geo(); for(let j=0;j<48;j++){ const a=45+90*j/48, b=45+90*(j+1)/48, A=fx(a,Rf(a)-8), B=fx(b,Rf(b)-8), A2=fx(a,Rf(a)+.5), B2=fx(b,Rf(b)+.5);
        quad(TG,[A[0],1.4,A[1]],[B[0],1.4,B[1]],[B2[0],1.4,B2[1]],[A2[0],1.4,A2[1]]); quad(TG,[A[0],0,A[1]],[B[0],0,B[1]],[B[0],1.4,B[1]],[A[0],1.4,A[1]]); } mesh(TG,conM);
      stand((u,v)=>fx(45+u*90, Rf(45+u*90)-6.5+v*6), 1.4, 3.6, 2, Math.PI/2*FR, 9, u=>ofTint((45+u*90-30)/120), 3, [(82.5-45)/90,(97.5-45)/90]); } }""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
