# v2.1.s のソースに当てると v2.1.t。python3 patch_v21t.py src.html new.html
# 試合画面の背景の球場の「グラウンドを広く」。見た目だけ(試合の計算・v1 の SVG・観戦の 3D・セーブには触らない)。
#   ユーザーの「グラウンドもっと広めにとってもいいのでは?」:今は本塁からフェンスまでが塁間の 2.8 倍(実物は両翼 3.6・中堅 4.4)、ファウルゾーンも狭かった。
#   ① 広さの決め方 hl3dWide(FR):フェンスは円でなく「両翼 FRl=FR×1.21(182→220)・センター FRc=FR×1.48(182→270)」の形 Rf(f)。
#      伸ばし方 warp(f,r):本塁から 100(内野の土の弧)まではそのまま、その外を方向ごとに Rf(f) まで伸ばす
#   ② 背景の地面は平らな板でなく極座標の網(4°×約 25 輪)に SVG の絵を貼る。絵の中のウォーニングトラック・フェンスの線は一緒に伸びる。
#      外野の芝の輪(飾り)は背景の写しだけ 9 ごとに置き直す(伸ばすと 16 の間隔が倍近く開くので)
#   ③ 球場の部品を新しい形に置き直す:フェンス・帯(Rf の形の壁。f 30〜150 と線の外まで)・バックスクリーン(FRc)・外野席(Rf+5〜。f 30〜150・区画 12)・応援旗・照明塔・ドームの針金・地面の円
#   ④ ファウルゾーンを広く:ファウルゾーンの席 o 26→40(手前 s 28→43)・ベンチ o 14→20・エキサイトシート o 12→18・ウイング席 o 10→16・ラバーフェンス o 25→39
#   ⑤ バックネット裏を後ろへ:内野席 1 階 r 40→55・通路 80→95・2 階 86→101。バックネット 36→51。内野側の照明塔 128→143
#   ⑥ 守備位置に立つ野手は同じ伸ばし方で外野へ。マウンドのカメラは位置そのまま、見る距離 90→110(ad も)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.s"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.t"; const BASE_V1="v1.4.b";')

# ① 広さの決め方
rep("""function hl3dParkMeshes(sc,own,pk,home,opt){   // v2.1.m:opt.full=球場を一周つなげる(試合画面の背景の 360 度)
  const T=THREE, FR=pk? pk.R : HL_FR, add=(geo,mat)=>{ own.push(geo,mat); const m=new T.Mesh(geo,mat); sc.add(m); return m; }, heads=[];
  const th0=Math.PI*.75, thL=Math.PI*.5;
  const fence=add(new T.CylinderGeometry(FR,FR,7,48,1,true,th0,thL), new T.MeshLambertMaterial({color:0x1d4a30,side:T.DoubleSide})); fence.position.y=3.5;""",
"""// v2.1.t:背景の球場の広さ。フェンスは「両翼 FRl・センター FRc」の形 Rf(f)(f は地面の図の角度:45=ライト線・90=センター・135=レフト線)。
//   warp(f,r):本塁から 100 まではそのまま、その外を Rf(f) まで伸ばす(地面の絵・野手の位置に使う)。線の外(f<45・f>135)は FRl
function hl3dWide(FR){ const FRl=Math.round(FR*1.21), FRc=Math.round(FR*1.48);
  const Rf=f=>{ if(f<=45 || f>=135) return FRl; const t=Math.sin((f-45)/90*Math.PI); return FRl+(FRc-FRl)*Math.pow(t,.8); };
  const warp=(f,r)=> r<=100? r : 100+(r-100)*(Rf(f)-100)/(FR-100);
  return {FR, FRl, FRc, Rf, warp, fo:14, bo:15}; }   // fo=ファウルゾーンを広げる分、bo=バックネット裏を後ろへ下げる分
// Rf(f) の形の壁(f0〜f1・高さ y0〜y1)。UV は u=f の割合、v=高さ
function hl3dArcWall(T,Rf,f0,f1,y0,y1,N,U,V){ const p=[],u=[]; for(let j=0;j<N;j++){ const a=f0+(f1-f0)*j/N, b=f0+(f1-f0)*(j+1)/N, ta=(a+90)*Math.PI/180, tb=(b+90)*Math.PI/180, ra=Rf(a), rb=Rf(b);
    const A=[ra*Math.sin(ta),ra*Math.cos(ta)], B=[rb*Math.sin(tb),rb*Math.cos(tb)], ua=(U||1)*j/N, ub=(U||1)*(j+1)/N, vv=V||1;
    p.push(A[0],y0,A[1], B[0],y0,B[1], B[0],y1,B[1], A[0],y0,A[1], B[0],y1,B[1], A[0],y1,A[1]); u.push(ua,0, ub,0, ub,vv, ua,0, ub,vv, ua,vv); }
  const g=new T.BufferGeometry(); g.setAttribute("position",new T.BufferAttribute(new Float32Array(p),3)); g.setAttribute("uv",new T.BufferAttribute(new Float32Array(u),2)); g.computeVertexNormals(); return g; }
function hl3dParkMeshes(sc,own,pk,home,opt){   // v2.1.m:opt.full=球場を一周つなげる(試合画面の背景の 360 度)
  const T=THREE, FR=pk? pk.R : HL_FR, add=(geo,mat)=>{ own.push(geo,mat); const m=new T.Mesh(geo,mat); sc.add(m); return m; }, heads=[];
  const th0=Math.PI*.75, thL=Math.PI*.5, WD= (opt&&opt.full)? hl3dWide(FR) : null; if(WD) opt.wd=WD;   // v2.1.t:背景は広いグラウンド
  const fence= WD? add(hl3dArcWall(T,WD.Rf,30,150,0,7,56), new T.MeshLambertMaterial({color:0x1d4a30,side:T.DoubleSide}))
    : add(new T.CylinderGeometry(FR,FR,7,48,1,true,th0,thL), new T.MeshLambertMaterial({color:0x1d4a30,side:T.DoubleSide})); if(!WD) fence.position.y=3.5;""")
rep("""  const band=add(new T.CylinderGeometry(FR+.3,FR+.3,1.4,48,1,true,th0,thL), new T.MeshLambertMaterial({color:hc,side:T.DoubleSide})); band.position.y=7.4;""",
"""  const band= WD? add(hl3dArcWall(T,f=>WD.Rf(f)+.3,30,150,6.7,8.1,56), new T.MeshLambertMaterial({color:hc,side:T.DoubleSide}))
    : add(new T.CylinderGeometry(FR+.3,FR+.3,1.4,48,1,true,th0,thL), new T.MeshLambertMaterial({color:hc,side:T.DoubleSide})); if(!WD) band.position.y=7.4;""")
# 照明塔(外野)・ドームの針金・バックスクリーン
rep("""  if(!dome) [[20,FR+24],[66,FR+80],[114,FR+80],[160,FR+24]].forEach(([a,r])=>{   // 照明塔(屋根つきの球場には無い)
    const p=hl3dP(...hlPt(a,r),0),""",
"""  if(!dome) [[20,24],[66,80],[114,80],[160,24]].forEach(([a,o])=>{   // 照明塔(屋根つきの球場には無い)。v2.1.t:背景ではフェンスの形 Rf に合わせる
    const r= WD? WD.Rf(a)+o : FR+o, p=hl3dP(...hlPt(a,r),0),""")
rep("""  if(pk && pk.dome){ const dm=add(new T.SphereGeometry(FR+110,28,10,0,Math.PI*2,0,Math.PI*.42), new T.MeshBasicMaterial({color:0xaab3bd,wireframe:true,transparent:true,opacity:.14})); dm.position.set(0,-40,-70); }""",
"""  if(pk && pk.dome){ const dR= WD? (WD.FRc+86+145)/2+25 : FR+110, dz= WD? (145-(WD.FRc+86))/2 : -70;   // v2.1.t:背景は広い器に合わせる
    const dm=add(new T.SphereGeometry(dR,28,10,0,Math.PI*2,0,Math.PI*.42), new T.MeshBasicMaterial({color:0xaab3bd,wireframe:true,transparent:true,opacity:.14})); dm.position.set(0,-40,dz); }""")
rep("""  { const full=!!(opt&&opt.full), bh= full? 50 : 30, bs=add(new T.PlaneGeometry(46,bh),""","""  { const full=!!(opt&&opt.full), bh= full? 50 : 30, bs=add(new T.PlaneGeometry(full? 60 : 46,bh),""")
rep("""bs.position.set(0,2+bh/2,-(FR+9)); }   // v2.1.p:背景では高く""","""bs.position.set(0,2+bh/2,-((WD? WD.FRc : FR)+9)); }   // v2.1.p:背景では高く。v2.1.t:センターのフェンス FRc の後ろ""")
# 地面の円・バックネット
rep("""    const g0=add(new T.CircleGeometry(FR+150,64), new T.MeshLambertMaterial({color:0x2a5534}));""","""    const g0=add(new T.CircleGeometry(WD.FRc+150,64), new T.MeshLambertMaterial({color:0x2a5534}));""")
rep("""    const net=add(new T.CylinderGeometry(36,36,16,24,1,true,rad(310),rad(100)),""","""    const net=add(new T.CylinderGeometry(36+WD.bo,36+WD.bo,16,24,1,true,rad(310),rad(100)),""")
# ④ ファウルゾーン(ベンチ・エキサイトシート・ウイング席・ラバーフェンス)
rep("""    [1,-1].forEach(sx=>{
      // ① ベンチ:掘り下げた箱(床 −2.5)・奥の壁・屋根・屋根の縁(ホームチームの色)・前の手すり・座る選手
      box(sx,18,48,14,24,-2.5,.2,mDark); box(sx,18,48,22.6,24,-2.5,4.6,mDark);
      box(sx,17,49,15.5,24.5,4.6,5.4,mRoof); box(sx,17,49,15.2,15.8,4.2,5.6,mHc); box(sx,18,48,13.6,14.2,.2,1.8,mRail);
      [22,30,38,44].forEach((sp,i)=>{ const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2], o=19.5+(i%2)*1.2;""",
"""    const FO=6, FRl=WD.FRl;   // v2.1.t:ファウルゾーンを広げる(ベンチ・エキサイトシート・ウイング席は o+6、席とラバーフェンスは o+14)
    [1,-1].forEach(sx=>{
      // ① ベンチ:掘り下げた箱(床 −2.5)・奥の壁・屋根・屋根の縁(ホームチームの色)・前の手すり・座る選手
      box(sx,18,48,14+FO,24+FO,-2.5,.2,mDark); box(sx,18,48,22.6+FO,24+FO,-2.5,4.6,mDark);
      box(sx,17,49,15.5+FO,24.5+FO,4.6,5.4,mRoof); box(sx,17,49,15.2+FO,15.8+FO,4.2,5.6,mHc); box(sx,18,48,13.6+FO,14.2+FO,.2,1.8,mRail);
      [22,30,38,44].forEach((sp,i)=>{ const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2], o=19.5+FO+(i%2)*1.2;""")
rep("""      const e1=FR-40; [[12,15.3,0,1.2],[15.3,18.6,0,2.4],[18.6,22,0,3.6]].forEach(([o0,o1,y0,y1])=>box(sx,54,e1,o0,o1,y0,y1,mRed));
      { const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2], sm=(54+e1)/2, net=add(new T.PlaneGeometry(e1-54,9),mNet);
        net.position.set(d[0]*sm+n[0]*11.4,4.5,d[1]*sm+n[1]*11.4); net.rotation.y=Math.atan2(-d[1],d[0]); }
      // ③ ウイング席:本塁の横から、ベンチの手前へせり出す低い席
      for(let k=0;k<4;k++) box(sx,6,18,10+k*5,15+k*5,0,1.4+k*1.7,mWing);
      // ④ フェンス(ラバー):ファウルゾーンとスタンドの間
      box(sx,50,FR-8,25,26,0,2.6,mPad);""",
"""      const e1=FRl-40; [[12,15.3,0,1.2],[15.3,18.6,0,2.4],[18.6,22,0,3.6]].forEach(([o0,o1,y0,y1])=>box(sx,54,e1,o0+FO,o1+FO,y0,y1,mRed));
      { const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2], sm=(54+e1)/2, net=add(new T.PlaneGeometry(e1-54,9),mNet);
        net.position.set(d[0]*sm+n[0]*(11.4+FO),4.5,d[1]*sm+n[1]*(11.4+FO)); net.rotation.y=Math.atan2(-d[1],d[0]); }
      // ③ ウイング席:本塁の横から、ベンチの手前へせり出す低い席
      for(let k=0;k<4;k++) box(sx,6,18,10+FO+k*5,15+FO+k*5,0,1.4+k*1.7,mWing);
      // ④ フェンス(ラバー):ファウルゾーンとスタンドの間
      box(sx,50,FRl-8,25+WD.fo,26+WD.fo,0,2.6,mPad);""")
# ⑤ 内野側の照明塔
rep("""    if(!dome) [[205,128],[335,128]].forEach(([a,r])=>{   // 内野側の照明塔""","""    if(!dome) [[205,128+WD.bo],[335,128+WD.bo]].forEach(([a,r])=>{   // 内野側の照明塔(v2.1.t:席と一緒に後ろへ)""")

# ③④⑤ 観客席
rep("""function hl3dStandsFull(sc,own,FR,hc,opt,dome){
  const T=THREE, out=(opt.out=opt.out||{}); out.sectors=[]; out.flags=[];""",
"""function hl3dStandsFull(sc,own,FR,hc,opt,dome){
  const T=THREE, out=(opt.out=opt.out||{}); out.sectors=[]; out.flags=[];
  const WD=opt.wd||hl3dWide(FR), Rf=WD.Rf, FRl=WD.FRl, FO=WD.fo, BO=WD.bo;   // v2.1.t:広いグラウンド(フェンスの形 Rf・ファウルゾーン +FO・バックネット裏 +BO)""")
rep("""  stand((u,v)=>fx(45+u*90, FR+5+v*81), 0, 40, 13, Math.PI/2*(FR+40), 9,
    u=>{ const f=45+u*90; return f<80? ["home",hcs,.62] : f>100? (acs? ["away",acs,.62] : mixT()) : mixT(); }, 3, [(82.5-45)/90,(97.5-45)/90]);""",
"""  stand((u,v)=>fx(30+u*120, Rf(30+u*120)+5+v*81), 0, 40, 13, Math.PI/2*(FR+40), 12,   // v2.1.t:f 30〜150(両翼の線の外まで回して角の切れ目を埋める)・フェンスの形 Rf に沿う
    u=>{ const f=30+u*120; return f<80? ["home",hcs,.62] : f>100? (acs? ["away",acs,.62] : mixT()) : mixT(); }, 3, [(82.5-30)/120,(97.5-30)/120]);""")
rep("""  [1,-1].forEach(sx=>{ const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2], s0=28, s1=FR-8;
    stand((u,v)=>{ const ss=s0+u*(s1-s0), o=26+v*40; return [d[0]*ss+n[0]*o, d[1]*ss+n[1]*o]; }, 1, 29, 12, s1-s0, 5, mixT, 2, null); });""",
"""  [1,-1].forEach(sx=>{ const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2], s0=28+BO, s1=FRl-8;
    stand((u,v)=>{ const ss=s0+u*(s1-s0), o=26+FO+v*40; return [d[0]*ss+n[0]*o, d[1]*ss+n[1]*o]; }, 1, 29, 12, s1-s0, 5, mixT, 2, null); });""")
rep("""  stand((u,v)=>fx(185+u*170, 40+v*40), 0, 16, 8, Math.PI*170/180*60, 8, mixT, 2, null);
  for(let j=0;j<24;j++){ const a=185+170*j/24, b=185+170*(j+1)/24, A=fx(a,80), B=fx(b,80), A2=fx(a,86), B2=fx(b,86);""",
"""  stand((u,v)=>fx(185+u*170, 40+BO+v*40), 0, 16, 8, Math.PI*170/180*60, 8, mixT, 2, null);
  for(let j=0;j<24;j++){ const a=185+170*j/24, b=185+170*(j+1)/24, A=fx(a,80+BO), B=fx(b,80+BO), A2=fx(a,86+BO), B2=fx(b,86+BO);""")
rep("""  stand((u,v)=>fx(188+u*164, 86+v*44), 24, 24, 9, Math.PI*164/180*108, 8, mixT, 2, null);""","""  stand((u,v)=>fx(188+u*164, 86+BO+v*44), 24, 24, 9, Math.PI*164/180*108, 8, mixT, 2, null);""")
rep("""  const flag=(f,col)=>{ const r=FR+48, p=fx(f,r),""","""  const flag=(f,col)=>{ const r=Rf(f)+48, p=fx(f,r),""")

# ② 地面の網・芝の輪・⑥ 野手
rep("""  const gm=new T.MeshBasicMaterial({color:0x2e6b40,transparent:true,alphaTest:.5}); own.push(gm); const gp=new T.Mesh(hl3dGeo("plane"),gm); gp.rotation.x=-Math.PI/2; gp.position.set(0,0,115-HL_HY); sc.add(gp);""",
"""  const gm=new T.MeshBasicMaterial({color:0x2e6b40,transparent:true,alphaTest:.5,side:T.DoubleSide}); own.push(gm);
  // v2.1.t:地面は極座標の網(4°×輪)。絵の座標は hlPt(f,r)、置く所は warp で伸ばした hlPt(f,r')。UV=絵の (x/300, 1−y/230)
  const WD=hl3dWide(pk? pk.R : HL_FR), rings=[]; for(let r=0;r<=100;r+=12.5) rings.push(r); for(let k=1;k<=12;k++) rings.push(100+(WD.FR+4-100)*k/12);
  { const P=[],U=[]; const pt=(f,r)=>{ const q=hlPt(f,r), w=hlPt(f,WD.warp(f,r)); return [[w[0]-HL_HX,w[1]-HL_HY],[q[0]/300,1-q[1]/230]]; };
    for(let i=0;i<90;i++){ const a=i*4, b=(i+1)*4; for(let k=0;k<rings.length-1;k++){ const r0=rings[k], r1=rings[k+1], A=pt(a,r0), B=pt(b,r0), C=pt(b,r1), D=pt(a,r1);
      [A,B,C,A,C,D].forEach(([p,u])=>{ P.push(p[0],0,p[1]); U.push(u[0],u[1]); }); } }
    const gg=new T.BufferGeometry(); gg.setAttribute("position",new T.BufferAttribute(new Float32Array(P),3)); gg.setAttribute("uv",new T.BufferAttribute(new Float32Array(U),2)); own.push(gg); sc.add(new T.Mesh(gg,gm)); }""")
rep("""  document.body.appendChild(tmp); const svg=tmp.querySelector("svg"); if(svg) svg.querySelectorAll(".f-stands").forEach(e=>e.remove());""",
"""  document.body.appendChild(tmp); const svg=tmp.querySelector("svg"); if(svg) svg.querySelectorAll(".f-stands").forEach(e=>e.remove());
  if(svg){ const rg=[...svg.querySelectorAll("circle.f-ring,circle.f-ring2")].filter(c=>+c.getAttribute("r")>100);   // v2.1.t:外野の芝の輪は 9 ごとに置き直す(伸ばすと間隔が倍近く開くので)
    if(rg.length){ const par=rg[0].parentNode; rg.forEach(c=>c.remove()); for(let r=109,k=0;r<WD.FR-6;r+=9,k++){ const c=document.createElementNS("http://www.w3.org/2000/svg","circle"); c.setAttribute("cx",HL_HX); c.setAttribute("cy",HL_HY); c.setAttribute("r",r); c.setAttribute("class",k%2? "f-ring2" : "f-ring"); par.appendChild(c); } } }""")
rep("""  const men=[]; Object.keys(HL_POS).filter(k=>k!=="投").forEach(k=>{ const [a,d]=HL_POS[k], m=hl3dMan(0xece8dc,own,true), p=hl3dP(...hlPt(a,d),0);""",
"""  const men=[]; Object.keys(HL_POS).filter(k=>k!=="投").forEach(k=>{ const [a,d]=HL_POS[k], m=hl3dMan(0xece8dc,own,true), p=hl3dP(...hlPt(a,WD.warp(a,d)),0); /* v2.1.t:外野手は伸ばした所へ */""")
# ⑥ カメラ
rep("""const HL3D_BGCAM={eye:[0,50,-45], look:90, ly:0, ad:90, hy:0, period:60, fov:60, fovN:68};""","""const HL3D_BGCAM={eye:[0,50,-45], look:110, ly:0, ad:110, hy:0, period:60, fov:60, fovN:68};   // v2.1.t:グラウンドが広いので、見る点を 110 に""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
