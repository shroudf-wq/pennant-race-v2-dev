# v2.2.e のソースに当てると v2.2.f。python3 patch_v22f.py src.html new.html
# 球場の看板とビジョン(C案)。見た目だけ(計算・2.5D・セーブには触らない)。ユーザーの「おすすめで一通りやって」の 1 つ目。
#   ① hl3dAdsTex(home):フェンスの広告看板。架空の社名 16 枚(実在の会社名・ロゴは使わない)を 8 色の板に。並びと色は本拠地名のハッシュで決めて固定(セーブには足さない)。
#      内側から見ると鏡になるので repeat.x=−1。本拠地ごとに使い回す(hl3dAdsTexC)
#   ② hl3dParkMeshes:フェンスの内側(Rf−.15)の y 1〜FH−1.2 に看板の壁(背景は弧の壁 U=2、観戦は円柱)。userData.k="ads"
#   ③ hl3dRibbonTex(text):リボンビジョン(暗い地に琥珀色の文字。2048 px に収まる回数だけ繰り返して継ぎ目なし)。
#      hl3dStandsFull(opt.ribbon・背景だけ):2 階の前の壁の中ほど(y 18.5〜21.5・内縁から 45.7)と、外野 2 階席の前の壁(y 41.6〜44.4・Rf+71.7)。
#      外野側は内側から見ると鏡なので別の texture(repeat.x=−1)。userData.k="ribbon"。hl3dBgDraw で offset.x を進めて流す(観客の動きの設定とは別。観戦では流さない)
#   ④ hl3dVisionInfo(home,away)・hl3dVisionDraw(cv,info)・hl3dVisionMake(info):バックスクリーンの大型ビジョン(512×256 の canvas)。
#      年目と日付、ビジター vs ホーム(チームカラーの下線)、勝敗と順位。hl3dParkMeshes(opt.vision):バックスクリーンの上のほうに枠つきで貼る(背景 48×24・観戦 32×16)。
#      userData.k="vision"。夜の背景は前にほのかな光。背景は試合が進んで勝敗が変わったら絵だけ描き直す(hl3dBgVisionSync。球場は作り直さない)
#   ⑤ hl3dBgBuild:names・ribbon・vision を渡す。hl3dStart0(観戦):vision を渡す(hl3Teams から)
#   テスト:hl3d_bg.py ㉑(ads 1・ribbon 2(2 階席あり)/1・vision 1・看板の鏡・勝敗が変わると絵が変わる・観戦にも ads と vision)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.2.e"; const BASE_V1="v1.4.q";','const APP_VERSION="v2.2.f"; const BASE_V1="v1.4.q";')
# ① ③ ④ 絵を作る関数(hl3dArcWall の前に)
rep("""// Rf(f) の形の壁(f0〜f1・高さ y0〜y1)。UV は u=f の割合、v=高さ
function hl3dArcWall(T,Rf,f0,f1,y0,y1,N,U,V){""",
"""// v2.2.f:フェンスの広告看板(架空の社名。実在の会社名・ロゴは使わない)。並びと色は本拠地名のハッシュで固定。内側から見ると鏡なので repeat.x=−1
const HL3D_ADS=["ホシノ電機","カゼ製菓","ツバサ航空","ヒノデ石油","モリヤ建設","アオバ住宅","ナミ食品","タチバナ薬局","ソラ通信","ユキ自動車","ハナ生命","コトブキ飲料","ミドリ鉄道","サカエ百貨店","トキワ保険","シオン化粧品"];
const HL3D_ADS_COL=[["#c8102e","#ffffff"],["#1a4fb4","#ffffff"],["#f2a900","#1a1a1a"],["#0d7a3e","#ffffff"],["#f4f4f4","#1a1a1a"],["#17191c","#ffffff"],["#e8601c","#ffffff"],["#5b2c8f","#ffffff"]];
const hl3dAdsTexC=new Map();
function hl3dAdsTex(home){ const k=String(home||""); if(hl3dAdsTexC.has(k)) return hl3dAdsTexC.get(k);
  const h=(forteHash(k+"看板")>>>3)%16, cv=document.createElement("canvas"); cv.width=2048; cv.height=96; const g=cv.getContext("2d"); g.fillStyle="#14181c"; g.fillRect(0,0,2048,96);
  g.textAlign="center"; g.textBaseline="middle"; g.font="bold 30px sans-serif";
  for(let i=0;i<16;i++){ const nm=HL3D_ADS[(i+h)%16], [bg,fg]=HL3D_ADS_COL[(i*3+h)%8], x=i*128; g.fillStyle=bg; g.fillRect(x+3,5,122,86); g.fillStyle=fg; g.fillText(nm,x+64,48,114); }
  const tx=hl3dNR(()=>new THREE.CanvasTexture(cv)); tx.wrapS=THREE.RepeatWrapping; tx.repeat.x=-1; hl3dAdsTexC.set(k,tx); return tx; }
// v2.2.f:リボンビジョンの絵(2048×48。text を収まる回数だけ等間隔に繰り返して継ぎ目なし)。mirror は内側から見て鏡になる壁用(repeat.x=−1)
function hl3dRibbonTex(text,mirror){ const cv=document.createElement("canvas"); cv.width=2048; cv.height=48; const g=cv.getContext("2d"); g.fillStyle="#0d1117"; g.fillRect(0,0,2048,48);
  g.fillStyle="#ffd36b"; g.font="bold 30px sans-serif"; g.textAlign="center"; g.textBaseline="middle"; const unit="◆  "+text+"  ", w=g.measureText(unit).width, n=Math.max(1,Math.floor(2048/(w+40))), slot=2048/n;
  for(let i=0;i<n;i++) g.fillText(unit,i*slot+slot/2,25,slot-24);
  const tx=hl3dNR(()=>new THREE.CanvasTexture(cv)); tx.wrapS=THREE.RepeatWrapping; if(mirror) tx.repeat.x=-1; return tx; }
// v2.2.f:バックスクリーンのビジョン。info={yd:"n年目 月/日", home:{n,w,l,t,r}, away:{...}, hc, ac}(読むだけ。試合の計算には触らない)
function hl3dVisionInfo(hn,an){ const q=n=>{ const o={n:n||"", w:0, l:0, t:0, r:0}; try{ const t=(typeof allTeamsEverywhere==="function"? allTeamsEverywhere() : []).find(x=>x && x.name===n); if(t){ o.w=t.w|0; o.l=t.l|0; o.t=t.t|0; o.r=teamRank(t)|0; } }catch(e){} return o; };
  let yd=""; try{ yd=`${year}年目 ${formatDate(gameDates[gameIdx])}`; }catch(e){} const col=n=>{ try{ return (typeof teamColorMap!=="undefined" && n && teamColorMap[n])||"#8a9199"; }catch(e){ return "#8a9199"; } };
  return {yd, home:q(hn), away:q(an), hc:col(hn), ac:col(an)}; }
function hl3dVisionDraw(cv,info){ const g=cv.getContext("2d"), W=cv.width, H=cv.height; g.fillStyle="#0a0e13"; g.fillRect(0,0,W,H); g.strokeStyle="#3a434d"; g.lineWidth=6; g.strokeRect(3,3,W-6,H-6);
  g.textAlign="center"; g.textBaseline="middle"; g.fillStyle="#dfe6ee"; g.font="bold 24px sans-serif"; g.fillText(info.yd||"",W/2,34);
  const side=(t,x,col)=>{ g.fillStyle="#ffffff"; g.font="bold 38px sans-serif"; g.fillText(t.n||"",x,104,196); g.fillStyle=col; g.fillRect(x-88,130,176,6);
    g.fillStyle="#dfe6ee"; g.font="bold 24px sans-serif"; g.fillText(t.n? `${t.w}勝${t.l}敗${t.t? t.t+"分" : ""}` : "",x,164,196); g.fillStyle="#ffd36b"; g.font="bold 22px sans-serif"; g.fillText((t.n && t.r)? `${t.r}位` : "",x,196); };
  side(info.away,128,info.ac); side(info.home,384,info.hc); g.fillStyle="#ffd36b"; g.font="bold 30px sans-serif"; g.fillText("vs",W/2,104);
  g.fillStyle="#9aa6b2"; g.font="bold 20px sans-serif"; g.fillText("HOME GAME",W/2,236); }
function hl3dVisionMake(info){ const cv=document.createElement("canvas"); cv.width=512; cv.height=256; hl3dVisionDraw(cv,info); const tx=hl3dNR(()=>new THREE.CanvasTexture(cv)); return {cv,tx,j:JSON.stringify(info)}; }
// Rf(f) の形の壁(f0〜f1・高さ y0〜y1)。UV は u=f の割合、v=高さ
function hl3dArcWall(T,Rf,f0,f1,y0,y1,N,U,V){""")
# ② フェンスの看板(帯の後)
rep("""    : add(new T.CylinderGeometry(FR+.3,FR+.3,1.4,48,1,true,th0,thL), new T.MeshLambertMaterial({color:hc,side:T.DoubleSide})); if(!WD) band.position.y=7.4;""",
"""    : add(new T.CylinderGeometry(FR+.3,FR+.3,1.4,48,1,true,th0,thL), new T.MeshLambertMaterial({color:hc,side:T.DoubleSide})); if(!WD) band.position.y=7.4;
  { const at=hl3dAdsTex(home), am=new T.MeshLambertMaterial({map:at,side:T.DoubleSide}); own.push(am);   // v2.2.f:フェンスの広告看板(内側 Rf−.15・y 1〜FH−1.2)。背景は弧の壁(看板 32 枚)、観戦は円柱(16 枚)
    const ads= WD? add(hl3dArcWall(T,f=>WD.Rf(f)-.15,22,158,1,FH-1.2,56,2),am) : add(new T.CylinderGeometry(FR-.15,FR-.15,4.8,48,1,true,th0,thL),am); if(!WD) ads.position.y=3.4; ads.userData.k="ads"; }""")
# ④ バックスクリーンのビジョン
rep("""  { const full=!!(opt&&opt.full), bh= full? 50 : 30, bs=add(new T.PlaneGeometry(full? 60 : 46,bh), new T.MeshLambertMaterial({color:0x173626,side:T.DoubleSide})); bs.position.set(0,2+bh/2,-((WD? WD.FRc : FR)+9)); }   // v2.1.p:背景では高く。v2.1.t:センターのフェンス FRc の後ろ""",
"""  { const full=!!(opt&&opt.full), bh= full? 50 : 30, bs=add(new T.PlaneGeometry(full? 60 : 46,bh), new T.MeshLambertMaterial({color:0x173626,side:T.DoubleSide})); bs.position.set(0,2+bh/2,-((WD? WD.FRc : FR)+9));   // v2.1.p:背景では高く。v2.1.t:センターのフェンス FRc の後ろ
    const vi= opt && opt.vision; if(vi){   // v2.2.f:大型ビジョン(バックスクリーンの上のほう。枠つき。本塁のほうを向く)
      const vw= full? 48 : 32, vh=vw/2, vy= 2+bh-3-vh/2, vz=bs.position.z;
      const fr=add(new T.BoxGeometry(vw+3,vh+3,1.2), new T.MeshLambertMaterial({color:0x2b3238})); fr.position.set(0,vy,vz+.5);
      const vm=new T.MeshBasicMaterial({map:vi.tx}); own.push(vm); const sm=add(new T.PlaneGeometry(vw,vh),vm); sm.position.set(0,vy,vz+1.2); sm.userData.k="vision"; (opt.out=opt.out||{}).vision=vi;
      if(full && !opt.day){ const gt=hl3dBgGlowTex(); own.push(gt); const gm=new T.SpriteMaterial({map:gt,color:0xbfd8ff,transparent:true,depthWrite:false,blending:T.AdditiveBlending,opacity:.22}); own.push(gm); const sp=new T.Sprite(gm); sp.position.set(0,vy,vz+2); sp.scale.set(vw*1.7,vh*2.4,1); sc.add(sp); } } }""")
# ③ リボンビジョン(hl3dStandsFull)
rep("""  const T=THREE, out=(opt.out=opt.out||{}); out.sectors=[]; out.flags=[];""",
"""  const T=THREE, out=(opt.out=opt.out||{}); out.sectors=[]; out.flags=[]; out.ribbons=[];   // v2.2.f:ribbons""")
rep("""    const d2=mesh(D2,bandM); if(d2) d2.userData.k="deck2";""",
"""    const d2=mesh(D2,bandM); if(d2) d2.userData.k="deck2";
    if(opt.ribbon){ const RB=geo(); let acc=0; for(let j=0;j<48;j++){ const a=F0+FW*j/48, b=F0+FW*(j+1)/48, ua=j/48, ub=(j+1)/48, A=fx(a,Rf(a)+71.7), B=fx(b,Rf(b)+71.7), l=Math.hypot(B[0]-A[0],B[1]-A[1]), u0=acc/90, u1=(acc+l)/90; acc+=l;   // v2.2.f:外野 2 階席の前のリボンビジョン(内側から見ると鏡なので mirror の絵)
        if(ub>bsSkip[0] && ua<bsSkip[1]) continue; quad(RB,[A[0],41.6,A[1]],[B[0],41.6,B[1]],[B[0],44.4,B[1]],[A[0],44.4,A[1]],[u0,0,u1,0,u1,1,u0,1]); }
      const rm=new T.MeshBasicMaterial({map:opt.ribbon[1],side:T.DoubleSide}); own.push(rm); const r2=mesh(RB,rm); if(r2){ r2.userData.k="ribbon"; out.ribbons.push(r2); } }""")
rep("""      quad(BAND,[A2[0],16,A2[1]],[B2[0],16,B2[1]],[B2[0],24,B2[1]],[A2[0],24,A2[1]]); } }   // 2階の前の壁(ホームチームの色)""",
"""      quad(BAND,[A2[0],16,A2[1]],[B2[0],16,B2[1]],[B2[0],24,B2[1]],[A2[0],24,A2[1]]); }
    if(opt.ribbon){ const RB=geo(); for(let j=0;j<K;j++){ const a=E2.at(j/K), b=E2.at((j+1)/K), A=[a.p[0]+a.n[0]*45.7,a.p[1]+a.n[1]*45.7], B=[b.p[0]+b.n[0]*45.7,b.p[1]+b.n[1]*45.7], u0=j/K*E2.L/90, u1=(j+1)/K*E2.L/90;   // v2.2.f:2 階の前の壁の中ほどのリボンビジョン(一塁側→本塁の後ろ→三塁側。内側から見て鏡にならない)
        quad(RB,[A[0],18.5,A[1]],[B[0],18.5,B[1]],[B[0],21.5,B[1]],[A[0],21.5,A[1]],[u0,0,u1,0,u1,1,u0,1]); }
      const rm=new T.MeshBasicMaterial({map:opt.ribbon[0],side:T.DoubleSide}); own.push(rm); const r1=mesh(RB,rm); if(r1){ r1.userData.k="ribbon"; out.ribbons.push(r1); } } }   // 2階の前の壁(ホームチームの色)""")
# ⑤ 背景から渡す・流す・描き直す
rep("""  const popt={full:true, away:ac||null, day:!!day}, heads=hl3dParkMeshes(sc,own,pk,home,popt);""",
"""  const away=hl3dBgAway(), vinfo=hl3dVisionInfo(home,away), rtext=`${home}${away? "  vs  "+away : ""}  ◆  ${vinfo.yd}  ◆  ペナントレース`, ribbon=[hl3dRibbonTex(rtext,false),hl3dRibbonTex(rtext,true)]; own.push(ribbon[0],ribbon[1]);   // v2.2.f:リボンビジョンとビジョン
  const popt={full:true, away:ac||null, day:!!day, ribbon, vision:hl3dVisionMake(vinfo)}, heads=hl3dParkMeshes(sc,own,pk,home,popt); own.push(popt.vision.tx);""")
rep("""  S.men.forEach((m,i)=>{ m.position.y=Math.max(0,Math.sin(t*2.1+i*1.7))*.25; });
  if(HL3D_BG_MOTION!=="off") hl3dBgMotion(S,t);""",
"""  S.men.forEach((m,i)=>{ m.position.y=Math.max(0,Math.sin(t*2.1+i*1.7))*.25; });
  (S.fx.ribbons||[]).forEach(r=>{ r.material.map.offset.x=(t*.05)%1; });   // v2.2.f:リボンビジョンを流す(観客の動きの設定とは別)
  if(HL3D_BG_MOTION!=="off") hl3dBgMotion(S,t);""")
rep("""  if(hl3dBgS && hl3dBgS.key===key && hl3dBgS.box===box){ hl3dBgSize(); hl3dBgKick(); return; }""",
"""  if(hl3dBgS && hl3dBgS.key===key && hl3dBgS.box===box){ hl3dBgSize(); try{ hl3dBgVisionSync(); }catch(e){} hl3dBgKick(); return; }""")
rep("""let hl3dBgT=0;
function hl3dBgRenderer(){""",
"""let hl3dBgT=0;
// v2.2.f:試合が進んで勝敗・日付が変わったら、ビジョンの絵だけ描き直す(球場は作り直さない)
function hl3dBgVisionSync(){ const S=hl3dBgS, v=S && S.fx && S.fx.vision; if(!v) return; const info=hl3dVisionInfo(hl3dBgHome(),hl3dBgAway()), j=JSON.stringify(info); if(j===v.j) return; v.j=j; hl3dVisionDraw(v.cv,info); v.tx.needsUpdate=true; }
function hl3dBgRenderer(){""")
# ⑤ 観戦から(ビジョンだけ。リボンは流せないので置かない)
rep("""  hl3dParkMeshes(sc,own,pk,hl3Home,{ofFull:true, away:(awayNm && typeof teamColorMap!=="undefined" && teamColorMap[awayNm])||null});   // v2.1.j:フェンス・観客席・帯・照明塔・屋根(試合画面の背景と同じもの)。v2.2.d:外野席は背景と同じ作り""",
"""  const vis=hl3dVisionMake(hl3dVisionInfo(hl3Home,awayNm)); own.push(vis.tx);   // v2.2.f:バックスクリーンのビジョン(観戦)
  hl3dParkMeshes(sc,own,pk,hl3Home,{ofFull:true, away:(awayNm && typeof teamColorMap!=="undefined" && teamColorMap[awayNm])||null, vision:vis});   // v2.1.j:フェンス・観客席・帯・照明塔・屋根(試合画面の背景と同じもの)。v2.2.d:外野席は背景と同じ作り""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
