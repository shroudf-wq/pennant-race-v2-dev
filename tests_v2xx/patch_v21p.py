# v2.1.o のソースに当てると v2.1.p。python3 patch_v21p.py src.html new.html
# 試合画面の背景の球場(opt.full)の観客席を作り直す。見た目だけ(乱数は使わない。決まった数列)。観戦の 3D は変えない。
#   ユーザーの「観客席のクオリティを更に上げることはできるか?」→「1(段のある席)と2(お客さんの見た目)まで進めて、3(動き)はいくつかサンプル」
#   ① 段のある席(hl3dStandsFull):外野席(13列)・ファウルゾーンの席(一塁側・三塁側 各12列)・内野席(1階 8列+通路と帯+2階 9列)。
#      1列ごとに 座面(座席の色)・段の立ち上がり(コンクリート)・お客さんの列(人の絵を立てた帯)。縦の通路(階段)をところどころに
#   ② お客さんの絵(hl3dPeopleTex):頭と肩の形の人。シャツ・帽子・タオルの色はばらばら。外野のライト側はホームチーム、レフト側はビジターの色に寄せる(応援席)。
#      応援席に応援旗(ライト=ホーム・レフト=ビジターの色)
#   ③ 動きの見本(HL3D_BG_MOTION。初めは "off"。設定には出さない):"towel"(応援席がタオルを振る:腕を上げた絵と交互に)・
#      "wave"(ウェーブ:席の区画が順に立ち上がって一周)・"flags"(旗がはためく)。いくつでも組み合わせられる(空白区切り)
#   ビジターの球団名を hl3dBgAway で読む(スコアボードの試合の g[1]。読むだけ)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.o"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.p"; const BASE_V1="v1.4.b";')

# ----- 古い観客席は背景では見せない -----
rep("""const stands=new T.Mesh(sgeo,smat); sc.add(stands); stands.position.y=20;""",
"""const stands=new T.Mesh(sgeo,smat); sc.add(stands); stands.position.y=20; if(opt && opt.full) stands.visible=false;   // v2.1.p:背景は段のある席(hl3dStandsFull)""")
rep("""    sc.add(new T.Mesh(g,smat)); });""","""    const qm=new T.Mesh(g,smat); if(opt && opt.full) qm.visible=false; sc.add(qm); });""")
rep("""const inf=new T.Mesh(ig,smat); inf.position.y=17; sc.add(inf);""","""const inf=new T.Mesh(ig,smat); inf.position.y=17; inf.visible=false; sc.add(inf);   // v2.1.p:段のある内野席に替えた""")
rep("""    // v2.1.o:ベンチ・エキサイトシート・ウイング席・フェンス(一塁側 sx=1・三塁側 sx=−1)""",
"""    hl3dStandsFull(sc,own,FR,hc,opt,dome);   // v2.1.p:段のある席・お客さん・応援旗
    // v2.1.o:ベンチ・エキサイトシート・ウイング席・フェンス(一塁側 sx=1・三塁側 sx=−1)""")
# バックスクリーン:背景では高く(後ろの席をふさぐ)
rep("""  { const bs=add(new T.PlaneGeometry(46,30), new T.MeshLambertMaterial({color:0x173626,side:T.DoubleSide})); bs.position.set(0,17,-(FR+9)); }""",
"""  { const full=!!(opt&&opt.full), bh= full? 50 : 30, bs=add(new T.PlaneGeometry(46,bh), new T.MeshLambertMaterial({color:0x173626,side:T.DoubleSide})); bs.position.set(0,2+bh/2,-(FR+9)); }   // v2.1.p:背景では高く""")

# ----- 段のある席・お客さん・旗 -----
rep("""function hl3dParkMeshes(sc,own,pk,home,opt){""","""/* ===== v2.1.p:背景の段のある観客席 =====
   席は「長さ u(0〜1)・奥行き v(0〜1)→ 地面の (x,z)」と「高さ h(v)」で表す。列 i の座面は v の [i/N,(i+1)/N] で高さ i×段、
   その前に段の立ち上がり、座面の前寄りにお客さんの帯(人の絵を立てる)。お客さんの帯は区画(K 分け)ごとに別の形にする(ウェーブで区画ごとに動かす) */
let HL3D_BG_MOTION="off";   // 動きの見本:"towel" "wave" "flags" を空白区切りで(設定には出さない)
function hl3dPeopleTex(base,mix,up){   // base=寄せる色(null なら寄せない)、mix=その割合、up=腕(タオル)を上げた絵
  const cv=document.createElement("canvas"); cv.width=256; cv.height=64; const g=cv.getContext("2d");
  let x=(base? parseInt(String(base).replace("#",""),16)|0 : 4242)+(up? 77 : 0)+Math.round(mix*100)*131; const rnd=()=>{ x=(Math.imul(x,1103515245)+12345)&0x7fffffff; return x/0x7fffffff; };
  const shirts=["#e8e4dc","#2b4f8c","#b8312f","#f2c230","#3d8b4f","#1d1d1f","#7a4fa0","#e07a2e","#5aa3d8","#d6d0c4","#8c8c8c","#f08fb0"], skin=["#f0c9a0","#e2b48a","#c99a72","#f5d5b5"];
  g.fillStyle="#2a2f37"; g.fillRect(0,0,256,64);   // 座席の背もたれ(人のすき間)
  for(let k=0;k<10;k++){ const cx=12.8+k*25.6+(rnd()-.5)*5, sh= (base && rnd()<mix)? base : shirts[Math.floor(rnd()*shirts.length)], hy=24+rnd()*6;
    g.fillStyle=sh; g.beginPath(); g.ellipse(cx,64,10.5,30-(hy-24),0,Math.PI,0); g.fill();   // 肩と胴
    if(up && rnd()<.85){ g.strokeStyle=sh; g.lineWidth=4.5; g.lineCap="round"; g.beginPath(); g.moveTo(cx-7,44); g.lineTo(cx-10,hy-16); g.moveTo(cx+7,44); g.lineTo(cx+10,hy-16); g.stroke();
      g.fillStyle= base && rnd()<.7? base : "#f4f1e8"; g.fillRect(cx-12,hy-22,24,6); }   // 腕とタオル
    g.fillStyle=skin[Math.floor(rnd()*skin.length)]; g.beginPath(); g.arc(cx,hy,7,0,Math.PI*2); g.fill();   // 顔
    const r=rnd(); if(r<.35){ g.fillStyle= (base && rnd()<.6)? base : shirts[Math.floor(rnd()*shirts.length)]; g.beginPath(); g.arc(cx,hy-1.5,7.4,Math.PI,0); g.fill(); g.fillRect(cx-1,hy-3,10,3); }   // 帽子
    else if(r<.8){ g.fillStyle=["#1c1712","#3b2a1e","#2a2522","#6b4a2e"][Math.floor(rnd()*4)]; g.beginPath(); g.arc(cx,hy-2,7.2,Math.PI*1.05,-Math.PI*.05); g.fill(); }   // 髪
    if(!up && rnd()<.18){ g.fillStyle= base || "#f4f1e8"; g.fillRect(cx-9,50,18,5); } }   // 首にかけたタオル
  const t=new THREE.CanvasTexture(cv); t.wrapS=THREE.RepeatWrapping; t.anisotropy=4; return t; }
function hl3dStandsFull(sc,own,FR,hc,opt,dome){
  const T=THREE, out=(opt.out=opt.out||{}); out.sectors=[]; out.flags=[];
  const hcs="#"+hc.getHexString(), acs= opt.away? (()=>{ try{ return "#"+new T.Color(String(opt.away)).getHexString(); }catch(e){ return null; } })() : null;
  const TX={}, tex=(k,base,mix)=>{ if(!TX[k]){ TX[k]=[hl3dPeopleTex(base,mix,false), hl3dPeopleTex(base,mix,true)]; own.push(TX[k][0],TX[k][1]); } return TX[k]; };
  const lit= dome? .78 : 1, mats=[];
  const pMat=(texs,kind)=>{ const m=new T.MeshLambertMaterial({color:new T.Color(lit,lit,lit),map:texs[0],side:T.DoubleSide}); m.userData.tx=texs; m.userData.kind=kind; own.push(m); mats.push(m); return m; };
  const seatC=new T.Color(0x34425a).multiplyScalar(lit), conC=new T.Color(0x666c73).multiplyScalar(lit);
  const seatM=new T.MeshLambertMaterial({color:seatC,side:T.DoubleSide}), conM=new T.MeshLambertMaterial({color:conC,side:T.DoubleSide}), bandM=new T.MeshLambertMaterial({color:hc,side:T.DoubleSide});
  own.push(seatM,conM,bandM);
  const geo=()=>({p:[],u:[]}), quad=(G,a,b,c,d,ua,ub)=>{ G.p.push(...a,...b,...c,...a,...c,...d); const U=ua||[0,0,1,0,1,1,0,1]; G.u.push(U[0],U[1],U[2],U[3],U[4],U[5],U[0],U[1],U[4],U[5],U[6],U[7]); };
  const mesh=(G,m)=>{ if(!G.p.length) return null; const g=new T.BufferGeometry(); g.setAttribute("position",new T.BufferAttribute(new Float32Array(G.p),3)); g.setAttribute("uv",new T.BufferAttribute(new Float32Array(G.u),2)); g.computeVertexNormals(); own.push(g); const me=new T.Mesh(g,m); sc.add(me); return me; };
  const SEAT=geo(), CON=geo(), BAND=geo();
  // stand(名前, P(u,v)→[x,z], 高さ h0+v×H, 列 N, 長さ L(人の絵の繰り返しの元), 区画 K, 色を寄せる関数 tint(u)→[キー,色,割合], 通路を入れる区画の切れ目, 除く u の範囲)
  const stand=(P,h0,H,N,L,K,tint,aisle,skip)=>{
    const segU=24;
    for(let k=0;k<K;k++){ const u0=k/K, u1=(k+1)/K, PG=geo(); const [tk,tb,tm]=tint((u0+u1)/2);
      for(let i=0;i<N;i++){ const v0=i/N, v1=(i+1)/N, y=h0+H*i/N, y1=h0+H*(i+1)/N, vm=v0+(v1-v0)*.42, ph=Math.min(4.2,(H/N)*1.25+1.2);
        const ns=Math.max(2,Math.ceil(segU/K)); for(let j=0;j<ns;j++){ const a=u0+(u1-u0)*j/ns, b=u0+(u1-u0)*(j+1)/ns;
          if(skip && b>skip[0] && a<skip[1]) continue;
          const A0=P(a,v0), B0=P(b,v0), A1=P(a,v1), B1=P(b,v1), Am=P(a,vm), Bm=P(b,vm);
          quad(SEAT,[A0[0],y,A0[1]],[B0[0],y,B0[1]],[B1[0],y,B1[1]],[A1[0],y,A1[1]]);   // 座面
          quad(CON,[A1[0],y,A1[1]],[B1[0],y,B1[1]],[B1[0],y1,B1[1]],[A1[0],y1,A1[1]]);   // 段の立ち上がり
          const len=Math.hypot(Bm[0]-Am[0],Bm[1]-Am[1]), ua=(a*L)/40, ub=ua+len/40;
          const gap= aisle && j===0 && k>0 && k%aisle===0;   // 通路(区画の境目)
          if(!gap) quad(PG,[Am[0],y,Am[1]],[Bm[0],y,Bm[1]],[Bm[0],y+ph,Bm[1]],[Am[0],y+ph,Am[1]],[ua,0,ub,0,ub,1,ua,1]);
          else quad(CON,[Am[0],y+.05,Am[1]],[Bm[0],y+.05,Bm[1]],[B1[0],y1+.05,B1[1]],[A1[0],y1+.05,A1[1]]); } }   // 階段
      const me=mesh(PG,pMat(tex(tk,tb,tm),tk)); if(me){ const c=P((u0+u1)/2,.5); me.userData.ang=Math.atan2(c[0],-(c[1]+45)); me.userData.y0=0; out.sectors.push(me); } } };
  const fx=(f,r)=>{ const t=(f+90)*Math.PI/180; return [r*Math.sin(t), r*Math.cos(t)]; };   // 地面の図の角度 f・本塁から r の点(three の円柱と同じ向き)
  const mixT=()=>["mix",hcs,.18];
  // 外野席(13列)。ライト(f<80)はホーム、レフト(f>100)はビジターの色に寄せる。バックスクリーンの後ろ(f 82.5〜97.5)は除く
  stand((u,v)=>fx(45+u*90, FR+5+v*81), 0, 40, 13, Math.PI/2*(FR+40), 9,
    u=>{ const f=45+u*90; return f<80? ["home",hcs,.62] : f>100? (acs? ["away",acs,.62] : mixT()) : mixT(); }, 3, [(82.5-45)/90,(97.5-45)/90]);
  // ファウルゾーンの席(各 12 列)
  [1,-1].forEach(sx=>{ const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2], s0=28, s1=FR-8;
    stand((u,v)=>{ const ss=s0+u*(s1-s0), o=26+v*40; return [d[0]*ss+n[0]*o, d[1]*ss+n[1]*o]; }, 1, 29, 12, s1-s0, 5, mixT, 2, null); });
  // 内野席:1階(本塁から 40〜80・高さ 0〜16)・通路と帯・2階(86〜130・24〜48)
  stand((u,v)=>fx(185+u*170, 40+v*40), 0, 16, 8, Math.PI*170/180*60, 8, mixT, 2, null);
  for(let j=0;j<24;j++){ const a=185+170*j/24, b=185+170*(j+1)/24, A=fx(a,80), B=fx(b,80), A2=fx(a,86), B2=fx(b,86);
    quad(CON,[A[0],16,A[1]],[B[0],16,B[1]],[B2[0],16,B2[1]],[A2[0],16,A2[1]]);   // 通路
    quad(BAND,[A2[0],16,A2[1]],[B2[0],16,B2[1]],[B2[0],24,B2[1]],[A2[0],24,A2[1]]); }   // 2階の前の壁(ホームチームの色)
  stand((u,v)=>fx(188+u*164, 86+v*44), 24, 24, 9, Math.PI*164/180*108, 8, mixT, 2, null);
  mesh(SEAT,seatM); mesh(CON,conM); mesh(BAND,bandM);
  // 応援旗(外野の応援席:ライト=ホーム、レフト=ビジターの色)
  const flag=(f,col)=>{ const r=FR+48, p=fx(f,r), y0=40*(43/81)+2, pole=new T.Mesh(new T.CylinderGeometry(.5,.5,30,5), conM); own.push(pole.geometry); pole.position.set(p[0],y0+15,p[1]); sc.add(pole);
    const fg=new T.PlaneGeometry(22,13,12,1); own.push(fg); const fm=new T.MeshLambertMaterial({color:new T.Color(col),side:T.DoubleSide}); own.push(fm); const fl=new T.Mesh(fg,fm);
    fl.position.set(p[0],y0+23.5,p[1]); fl.rotation.y=Math.atan2(p[0],p[1]); fg.translate(11,0,0); fl.userData.base=Float32Array.from(fg.attributes.position.array); sc.add(fl); out.flags.push(fl); };
  [56,66].forEach(f=>flag(f,hcs)); if(acs) [114,124].forEach(f=>flag(f,acs));
  out.mats=mats;
}
function hl3dParkMeshes(sc,own,pk,home,opt){""")

# ----- 背景:ビジター・動き -----
rep("""function hl3dBgWant(){""","""function hl3dBgAway(){ try{ const busy= (typeof cupBusy==="function" && cupBusy()) || (post && post.done), g= !busy && schedule && schedule[gameIdx];
    if(g){ const a=schedTeam(g[1]); if(a && a.name) return a.name; } }catch(e){} return null; }   // v2.1.p:ビジター(応援席の色。読むだけ)
function hl3dBgWant(){""")
rep("""  const day=hl3dBgIsDay(), key=[home, pk? pk.s+"/"+pk.turf+"/"+pk.dome : "-", document.documentElement.dataset.style||"", (typeof teamColorMap!=="undefined" && teamColorMap[home])||"", day? "day" : "night"].join("|");""",
"""  const day=hl3dBgIsDay(), away=hl3dBgAway(), ac=(away && typeof teamColorMap!=="undefined" && teamColorMap[away])||"",
    key=[home, pk? pk.s+"/"+pk.turf+"/"+pk.dome : "-", document.documentElement.dataset.style||"", (typeof teamColorMap!=="undefined" && teamColorMap[home])||"", day? "day" : "night", ac].join("|");""")
rep("""    try{ hl3dNR(()=>hl3dBgBuild(box,home,pk,key,day)); }catch(e){ hl3dBgOff=true; hl3dBgOffNow(card); } }, hl3dBgS? 120 : 0);""",
"""    try{ hl3dNR(()=>hl3dBgBuild(box,home,pk,key,day,ac)); }catch(e){ hl3dBgOff=true; hl3dBgOffNow(card); } }, hl3dBgS? 120 : 0);""")
rep("""function hl3dBgBuild(box,home,pk,key,day){""","""function hl3dBgBuild(box,home,pk,key,day,ac){""")
rep("""  const heads=hl3dParkMeshes(sc,own,pk,home,{full:true});""","""  const popt={full:true, away:ac||null}, heads=hl3dParkMeshes(sc,own,pk,home,popt);""")
rep("""  hl3dBgS={key,box,sc,cam,own,men,raf:0,t0:performance.now(),last:0,W:0,H:0,io:true,day:!!day};""",
"""  hl3dBgS={key,box,sc,cam,own,men,raf:0,t0:performance.now(),last:0,W:0,H:0,io:true,day:!!day,fx:popt.out||{}};""")
rep("""  S.men.forEach((m,i)=>{ m.position.y=Math.max(0,Math.sin(t*2.1+i*1.7))*.25; });""","""  S.men.forEach((m,i)=>{ m.position.y=Math.max(0,Math.sin(t*2.1+i*1.7))*.25; });
  if(HL3D_BG_MOTION!=="off") hl3dBgMotion(S,t);""")
rep("""function hl3dBgVisible(){""","""// v2.1.p:動きの見本(HL3D_BG_MOTION)
function hl3dBgMotion(S,t){ const F=S.fx||{}, M=" "+HL3D_BG_MOTION+" ";
  if(M.includes(" towel ")){ const ph=Math.floor(t/.42)%2; (F.mats||[]).forEach((m,i)=>{ const tx=m.userData.tx; if(!tx || m.userData.kind==="mix") return; /* 応援席(外野のライト・レフト)だけ */ const want= (m.map===tx[0]||m.map===tx[1])? tx[(ph+i)%2] : m.map; if(m.map!==want){ m.map=want; m.needsUpdate=true; } }); }
  if(M.includes(" wave ")){ const w=(t*1.1)%(Math.PI*2); (F.sectors||[]).forEach(me=>{ let d=Math.abs(((me.userData.ang-w+Math.PI*3)%(Math.PI*2))-Math.PI); const k=Math.max(0,1-d/.45); me.position.y=k*k*4.2;
      const tx=me.material.userData.tx; if(tx){ const want= k>.25? tx[1] : tx[0]; if(me.material.map!==want){ me.material.map=want; me.material.needsUpdate=true; } } }); }   // 立ち上がった区画は腕を上げた絵
  if(M.includes(" flags ")) (F.flags||[]).forEach((fl,i)=>{ const P=fl.geometry.attributes.position, B=fl.userData.base; for(let j=0;j<P.count;j++){ const x=B[j*3]; const w=Math.sin(x*.32-t*5.2+i)*(x/22); P.array[j*3+1]=B[j*3+1]+w*1.8; P.array[j*3+2]=B[j*3+2]+w*3.2; } P.needsUpdate=true; fl.geometry.computeVertexNormals(); });
}
function hl3dBgVisible(){""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
