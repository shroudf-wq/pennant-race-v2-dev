# v2.2.f のソースに当てると v2.2.g。python3 patch_v22g.py src.html new.html
# 外の景色と雰囲気(D案)。背景(opt.full)だけ。見た目だけ(計算・2.5D・観戦の 3D・セーブには触らない)。ユーザーの「おすすめで一通りやって」の 2 つ目。
#   ① hl3dParkLook に scene:0 街/1 山/2 海(forteHash(名前+"景色")%3。ドームでは使わない=屋根と壁で外が見えない)
#   ② hl3dSceneryTex(kind,day,seed):球場の外の景色の絵(4096×256・透明地)。街=ビルの影(夜は窓の灯り・高いビルに赤い灯、昼は灰青のビル)、
#      山=3 層の尾根(夜は紺、昼は青緑。遠い峰に雪)、海=低い対岸と島(夜は灯り)。決まった数列(試合の乱数は使わない)
#      hl3dBgScenery(sc,own,WD,kind,day):半径 900・高さ 300 の円筒の内側に貼る(MeshBasic・透明・depthWrite なし)。外の地面(半径 1300 の円。街=暗い灰、山=暗い緑、海=海の色)
#      userData.k="scenery"・"farGround"
#   ③ 夜の雰囲気:星を 160→240・大きく(2→2.6)、照明のにじみを 70→90、月(輝きの絵の Sprite 2 枚。屋外の夜だけ)。userData.k="moon"
#   ④ 大屋根の影の焼き込み:hl3dStandsFull の stand() に shade(u,v)→真偽。真の区画・列は席と段と人を暗い材質(×.62)で別に作る(SEATd・CONd・pMat の色)。
#      2 階(E2)の stand に opt.roofShade を渡す(全面 roof=2 は f 186〜354 の全列、部分 roof=1 は f 210〜330 の上 6 割(r 118 から))。userData.k="shade" は付けない(数は ㉒ で人の材質の色で数える)
#   テスト:hl3d_bg.py ㉒(型を強制して scene 0/1/2 で scenery 1・farGround 1、ドームで 0、夜に moon 2・星 240、roof 2 で暗い区画の材質がある・roof 0 でない)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.2.f"; const BASE_V1="v1.4.q";','const APP_VERSION="v2.2.g"; const BASE_V1="v1.4.q";')
# ① 型
rep("""    pen: (!dome && h("外野席")%3===1)? 1 : h("ブルペン")%2}; }""",
"""    pen: (!dome && h("外野席")%3===1)? 1 : h("ブルペン")%2,
    scene: h("景色")%3}; }   // v2.2.g:外の景色 0 街/1 山/2 海(ドームでは使わない)""")
# ② 景色の絵と置く関数(hl3dBgSkyTex の前に)
rep("""function hl3dBgSkyTex(dome,day){""",
"""// v2.2.g:球場の外の景色(背景だけ)。kind 0 街/1 山/2 海。決まった数列(試合の乱数は使わない)
function hl3dSceneryTex(kind,day,seed){ const W=4096, H=256, cv=document.createElement("canvas"); cv.width=W; cv.height=H; const g=cv.getContext("2d"); let x=(seed|0)||12345; const rnd=()=>{ x=(Math.imul(x,1103515245)+12345)&0x7fffffff; return x/0x7fffffff; };
  if(kind===0){   // 街:ビルの影。夜は窓の灯り、昼は灰青のビル
    for(let bx=0;bx<W;){ const w=24+rnd()*60, h=30+Math.pow(rnd(),1.6)*170, tall=h>150; g.fillStyle= day? (rnd()<.5? "#aab5c2" : "#8f9cab") : (rnd()<.5? "#121826" : "#0d121c"); g.fillRect(bx,H-h,w,h);
      if(day){ g.fillStyle="rgba(60,72,90,.45)"; for(let yy=H-h+6;yy<H-6;yy+=10) for(let xx=bx+4;xx<bx+w-6;xx+=9) g.fillRect(xx,yy,4,5); }
      else { for(let yy=H-h+6;yy<H-6;yy+=10) for(let xx=bx+4;xx<bx+w-6;xx+=9) if(rnd()<.55){ g.fillStyle= rnd()<.8? "rgba(255,233,160,.9)" : "rgba(190,220,255,.8)"; g.fillRect(xx,yy,4,5); }
        if(tall){ g.fillStyle="#ff4a3a"; g.fillRect(bx+w/2-2,H-h-5,4,4); } }
      bx+=w+(rnd()<.3? 2+rnd()*14 : 0); }
    g.fillStyle= day? "#7f8a97" : "#0a0e16"; g.fillRect(0,H-22,W,22); }
  else if(kind===1){   // 山:3 層の尾根。遠い峰に雪
    const cols= day? ["#7d9bb5","#5f8098","#4a6a82"] : ["#1b2340","#151c33","#0f1526"];
    [[150,.9],[120,1.4],[85,2.2]].forEach(([amp,fq],L)=>{ g.fillStyle=cols[L]; g.beginPath(); g.moveTo(0,H); let ph=rnd()*9; const pts=[];
      for(let xx=0;xx<=W;xx+=8){ const t=xx/W*Math.PI*2*fq; const y=H-amp*(.55+.25*Math.sin(t*3.1+ph)+.2*Math.sin(t*7.3+ph*2)+.12*Math.sin(t*17+ph*3))-(L===0? 40 : L===1? 18 : 0); pts.push([xx,y]); g.lineTo(xx,y); }
      g.lineTo(W,H); g.closePath(); g.fill();
      if(L===0 && day){ g.fillStyle="rgba(240,246,250,.85)"; pts.forEach(([xx,y])=>{ if(y<H-150) g.fillRect(xx,y,8,Math.min(14,(H-150-y)*.5)); }); } });
    g.fillStyle= day? "#48617a" : "#0b1120"; g.fillRect(0,H-16,W,16); }
  else {   // 海:低い対岸と島。夜は灯り
    g.fillStyle= day? "#9fb4c6" : "#0e1526"; for(let i=0;i<9;i++){ const cx=rnd()*W, w=120+rnd()*500, h=12+rnd()*26; g.beginPath(); g.ellipse(cx,H-6,w/2,h,0,Math.PI,0); g.fill(); if(cx+w/2>W){ g.beginPath(); g.ellipse(cx-W,H-6,w/2,h,0,Math.PI,0); g.fill(); } }
    if(!day){ for(let i=0;i<140;i++){ g.fillStyle= rnd()<.7? "rgba(255,230,170,.85)" : "rgba(170,210,255,.8)"; g.fillRect(rnd()*W,H-8-rnd()*10,2,2); } }
    g.fillStyle= day? "#6f8aa0" : "#0a0f1c"; g.fillRect(0,H-7,W,7); }
  return hl3dNR(()=>new THREE.CanvasTexture(cv)); }
function hl3dBgScenery(sc,own,WD,kind,day,seed){ const T=THREE, R=900, tx=hl3dSceneryTex(kind,day,seed); own.push(tx);
  const gm=new T.MeshBasicMaterial({map:tx,transparent:true,side:T.DoubleSide,depthWrite:false}); const geo=new T.CylinderGeometry(R,R,300,64,1,true); own.push(gm,geo);
  const ring=new T.Mesh(geo,gm); ring.position.set(0,150,-60); ring.userData.k="scenery"; sc.add(ring);
  const fc= kind===2? (day? 0x3d7fb5 : 0x14284f) : kind===1? (day? 0x4f6d3f : 0x101a14) : (day? 0x6b7078 : 0x0c0f14);
  const fg=new T.CircleGeometry(1300,48), fm=new T.MeshBasicMaterial({color:fc}); own.push(fg,fm); const far=new T.Mesh(fg,fm); far.rotation.x=-Math.PI/2; far.position.set(0,-.8,-60); far.userData.k="farGround"; sc.add(far);
  return ring; }
function hl3dBgSkyTex(dome,day){""")
# ②③ 置く・星・月・にじみ
rep("""  if(!dome && !day){ const gt=hl3dBgGlowTex(); own.push(gt); heads.forEach(p=>{ const m=new T.SpriteMaterial({map:gt,color:0xfff3d0,transparent:true,depthWrite:false,blending:T.AdditiveBlending}); own.push(m);
      const sp=new T.Sprite(m); sp.position.copy(p); sp.scale.set(70,70,1); sc.add(sp); });""",
"""  if(!dome && popt.look) hl3dBgScenery(sc,own,WD,popt.look.scene|0,!!day,forteHash(String(home||"")+"景色")>>>3);   // v2.2.g:外の景色(街・山・海)
  if(!dome && !day){ const gt=hl3dBgGlowTex(); own.push(gt); heads.forEach(p=>{ const m=new T.SpriteMaterial({map:gt,color:0xfff3d0,transparent:true,depthWrite:false,blending:T.AdditiveBlending}); own.push(m);
      const sp=new T.Sprite(m); sp.position.copy(p); sp.scale.set(90,90,1); sc.add(sp); });   // v2.2.g:にじみを大きく(70→90)
    [[0xfff8e6,1,34],[0xfff2c8,.55,110]].forEach(([c,o,sz])=>{ const m=new T.SpriteMaterial({map:gt,color:c,transparent:true,depthWrite:false,blending:T.AdditiveBlending,opacity:o}); own.push(m); const sp=new T.Sprite(m); sp.position.set(-520,430,-880); sp.scale.set(sz,sz,1); sp.userData.k="moon"; sc.add(sp); });   // v2.2.g:月(核と輝き)""")
rep("""    const N=160, pos=new Float32Array(N*3); for(let i=0;i<N;i++){ const a=Math.PI*(.15+.7*rnd()), e=.18+.5*rnd(), r=1400; pos[i*3]=Math.cos(a)*r*Math.cos(e); pos[i*3+1]=r*Math.sin(e); pos[i*3+2]=-Math.sin(a)*r*Math.cos(e); }
    const sg=new T.BufferGeometry(); sg.setAttribute("position",new T.BufferAttribute(pos,3)); const sm=new T.PointsMaterial({color:0xdfe6ff,size:2,sizeAttenuation:false,transparent:true,opacity:.75}); own.push(sg,sm); sc.add(new T.Points(sg,sm)); }""",
"""    const N=240, pos=new Float32Array(N*3); for(let i=0;i<N;i++){ const a=Math.PI*(.15+.7*rnd()), e=.18+.5*rnd(), r=1400; pos[i*3]=Math.cos(a)*r*Math.cos(e); pos[i*3+1]=r*Math.sin(e); pos[i*3+2]=-Math.sin(a)*r*Math.cos(e); }   // v2.2.g:星を 160→240
    const sg=new T.BufferGeometry(); sg.setAttribute("position",new T.BufferAttribute(pos,3)); const sm=new T.PointsMaterial({color:0xdfe6ff,size:2.6,sizeAttenuation:false,transparent:true,opacity:.85}); own.push(sg,sm); const st=new T.Points(sg,sm); st.userData.k="stars"; sc.add(st); }""")
# ④ 屋根の影(stand の shade)
rep("""  const SEAT=geo(), CON=geo(), BAND=geo();""",
"""  const SEAT=geo(), CON=geo(), BAND=geo(), SEATd=geo(), CONd=geo(), SH=.62;   // v2.2.g:大屋根の影の下(暗い材質)
  const seatMd=new T.MeshLambertMaterial({color:seatC.clone().multiplyScalar(SH),side:T.DoubleSide}), conMd=new T.MeshLambertMaterial({color:conC.clone().multiplyScalar(SH),side:T.DoubleSide}); own.push(seatMd,conMd);""")
rep("""  const stand=(P,h0,H,N,L,K,tint,aisle,skip,lowSkip)=>{
    const segU=24;
    for(let k=0;k<K;k++){ const u0=k/K, u1=(k+1)/K, PG=geo(); const [tk,tb,tm]=tint((u0+u1)/2);
      for(let i=0;i<N;i++){ const v0=i/N, v1=(i+1)/N, y=h0+H*i/N, y1=h0+H*(i+1)/N, vm=v0+(v1-v0)*.42, ph=Math.min(4.2,(H/N)*1.25+1.2);
        const ns=Math.max(2,Math.ceil(segU/K)), pcs=[];""",
"""  const stand=(P,h0,H,N,L,K,tint,aisle,skip,lowSkip,shade)=>{
    const segU=24;
    for(let k=0;k<K;k++){ const u0=k/K, u1=(k+1)/K, PG0=geo(), PGd=geo(); const [tk,tb,tm]=tint((u0+u1)/2);
      for(let i=0;i<N;i++){ const v0=i/N, v1=(i+1)/N, y=h0+H*i/N, y1=h0+H*(i+1)/N, vm=v0+(v1-v0)*.42, ph=Math.min(4.2,(H/N)*1.25+1.2);
        const dk= !!(shade && shade((u0+u1)/2,(v0+v1)/2)), SEAT=dk? SEATd : SEAT0, CON=dk? CONd : CON0, PG=dk? PGd : PG0;   // v2.2.g:屋根の影の下は暗い材質へ
        const ns=Math.max(2,Math.ceil(segU/K)), pcs=[];""")
rep("""      const me=mesh(PG,pMat(tex(tk,tb,tm),tk)); if(me){ const c=P((u0+u1)/2,.5); me.userData.ang=Math.atan2(c[0],-(c[1]+45)); me.userData.y0=0; out.sectors.push(me); } } };""",
"""      [[PG0,1],[PGd,SH]].forEach(([PG,f])=>{ const pm=pMat(tex(tk,tb,tm),tk); if(f<1){ pm.color.multiplyScalar(f); pm.userData.shade=true; } const me=mesh(PG,pm); if(me){ const c=P((u0+u1)/2,.5); me.userData.ang=Math.atan2(c[0],-(c[1]+45)); me.userData.y0=0; out.sectors.push(me); } }); } };
  const SEAT0=SEAT, CON0=CON;""")
rep("""  stand(PE(E2,v=>46+v*44), 24, 24, 9, E2.L, Math.round(E2.L/30), mixT, 2, null);   // 2 階(46〜90・9 列・24〜48)""",
"""  const RS= opt.roofShade|0, shade2= RS? (u,v)=>{ const q=E2.at(u).p, f=Math.atan2(q[0],q[1])*180/Math.PI-90, fx_=((f%360)+360)%360; return (RS===2? (fx_>186 && fx_<354) : (fx_>210 && fx_<330 && v>.39)); } : null;   // v2.2.g:大屋根の影(全面は全列、部分は f 210〜330 の上 6 割)
  stand(PE(E2,v=>46+v*44), 24, 24, 9, E2.L, Math.round(E2.L/30), mixT, 2, null, null, shade2);   // 2 階(46〜90・9 列・24〜48)""")
rep("""  mesh(SEAT,seatM); mesh(CON,conM); mesh(BAND,bandM);
  // 応援旗""","""  mesh(SEAT,seatM); mesh(CON,conM); mesh(BAND,bandM); mesh(SEATd,seatMd); mesh(CONd,conMd);
  // 応援旗""")
rep("""    opt.look=LOOK;   // v2.1.v:球団ごとの型(v2.1.w:外野席の種類にも使う。v2.1.x:先頭で決める)""",
"""    opt.look=LOOK; opt.roofShade=LOOK.roof;   // v2.1.v:球団ごとの型(v2.1.w:外野席の種類にも使う。v2.1.x:先頭で決める)。v2.2.g:大屋根の影""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
