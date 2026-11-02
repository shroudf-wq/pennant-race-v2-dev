# v2.1.y のソースに当てると v2.1.z。python3 patch_v21z.py src.html new.html
# 試合画面の背景の球場。見た目だけ(背景 opt.full のときだけ。計算・観戦の 3D・セーブには触らない)。
#   ユーザーの「フィールド上の人はもう少し小さくてもいい」「応援席のつながりはもっと自然に。特に内野席とファウルゾーンの境目」
#   ① 背景の人を小さく:守備位置の野手・捕手 1.4 → .8、ネクストバッターズサークルの打者 1.2 → .8(ベンチの中は .9 のまま)。最初 1.05 にしたが「もう少し小さく」で .8
#   ② 内野席とファウルゾーンの席をひと続きの器にする(hl3dBowlEdge):今までは「本塁を中心の弧(内野席)」と「ラインに沿った直線(ファウルゾーンの席)」が
#      別の形で、境目で列が交差し、高さも違っていた(内野 1 階 0〜16+2 階 24〜48/ファウルゾーン 1〜30)。
#      内縁を 1 本の折れ線にする:本塁の後ろは半径 55 の弧、ラインの外は「ラインから 40」の直線(r=40/sin(45−f))、大きいほうを取るので
#      f≈−2°(=358°)と 182° で弧から直線へ移る。両端はライン沿い s=FRl−8 まで。1° ごとに点を取り、長さで等分し直して区画にする。
#      1 階(奥行き 40・8 列・0〜16)・通路(40〜46・y 16)・2 階の前の壁(46・16〜24)・2 階(46〜90・9 列・24〜48)を同じ内縁から外へ(法線の向き)作る。
#      2 階はラインの先(s>FRl−50)には作らない(外野席と重なるので)。区画の数は長さ ÷ 30 くらい(1 階 18・2 階 15)、通路は 2 区画ごと
#   ④ 角の切れ目:外野席・フェンス・帯を f 22〜158 まで回す(今まで 30〜150)。ラインの先の角で 1 階(s=FRl−14 まで)と外野席がつながる
#   ③ テスト:hl3d_bg.py ⑰(1 階・2 階の区画の数が増え、人のメッシュのどれも高さ 48 を超えない=境目で列が交差していない)…簡単に「席の区画が 40 以上」
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.y"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.z"; const BASE_V1="v1.4.b";')
# ① 人を小さく
rep("""/* v2.1.t:外野手は伸ばした所へ */ m.position.copy(p);""","""/* v2.1.t:外野手は伸ばした所へ */ m.scale.setScalar(.8); /* v2.1.z:背景の人は小さく */ m.position.copy(p);""")
rep("""  { const c=hl3dMan(0xece8dc,own,true); c.position.copy(hl3dP(HL_HX,HL_HY+8,0)); c.rotation.y=Math.PI; sc.add(c); men.push(c); }""",
"""  { const c=hl3dMan(0xece8dc,own,true); c.scale.setScalar(.8); c.position.copy(hl3dP(HL_HX,HL_HY+8,0)); c.rotation.y=Math.PI; sc.add(c); men.push(c); }""")
rep("""const m=hl3dMan(0xece8dc,own,false); m.scale.setScalar(1.2); m.position.set(x,0,z); m.rotation.y=Math.PI; m.userData.k="ondeck";""",
"""const m=hl3dMan(0xece8dc,own,false); m.scale.setScalar(.8); m.position.set(x,0,z); m.rotation.y=Math.PI; m.userData.k="ondeck";""")
# ② ひと続きの器
rep("""  // ファウルゾーンの席(各 12 列)
  [1,-1].forEach(sx=>{ const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2], s0=28+BO, s1=FRl-8;
    stand((u,v)=>{ const ss=s0+u*(s1-s0), o=26+FO+v*40; return [d[0]*ss+n[0]*o, d[1]*ss+n[1]*o]; }, 1, 29, 12, s1-s0, 5, mixT, 2, null); });
  // 内野席:1階(本塁から 40〜80・高さ 0〜16)・通路と帯・2階(86〜130・24〜48)
  stand((u,v)=>fx(185+u*170, 40+BO+v*40), 0, 16, 8, Math.PI*170/180*60, 8, mixT, 2, null);
  for(let j=0;j<24;j++){ const a=185+170*j/24, b=185+170*(j+1)/24, A=fx(a,80+BO), B=fx(b,80+BO), A2=fx(a,86+BO), B2=fx(b,86+BO);
    quad(CON,[A[0],16,A[1]],[B[0],16,B[1]],[B2[0],16,B2[1]],[A2[0],16,A2[1]]);   // 通路
    quad(BAND,[A2[0],16,A2[1]],[B2[0],16,B2[1]],[B2[0],24,B2[1]],[A2[0],24,A2[1]]); }   // 2階の前の壁(ホームチームの色)
  stand((u,v)=>fx(188+u*164, 86+BO+v*44), 24, 24, 9, Math.PI*164/180*108, 8, mixT, 2, null);""",
"""  // v2.1.z:内野席とファウルゾーンの席をひと続きの器に。内縁の折れ線 E(本塁の後ろは半径 55 の弧、ラインの外は「ラインから 40」の直線)から外へ
  const OI=26+FO, RB=40+BO, E1=hl3dBowlEdge(OI,RB,FRl-14), E2=hl3dBowlEdge(OI,RB,FRl-50);   // 1 階は s=FRl−14 まで、2 階は FRl−50 まで
  const PE=(E,off)=>(u,v)=>{ const q=E.at(u); return [q.p[0]+q.n[0]*off(v), q.p[1]+q.n[1]*off(v)]; };
  stand(PE(E1,v=>v*40), 0, 16, 8, E1.L, Math.round(E1.L/30), mixT, 2, null);   // 1 階(奥行き 40・8 列・0〜16)
  { const K=Math.round(E2.L/8); for(let j=0;j<K;j++){ const a=E2.at(j/K), b=E2.at((j+1)/K), A=[a.p[0]+a.n[0]*40,a.p[1]+a.n[1]*40], B=[b.p[0]+b.n[0]*40,b.p[1]+b.n[1]*40], A2=[a.p[0]+a.n[0]*46,a.p[1]+a.n[1]*46], B2=[b.p[0]+b.n[0]*46,b.p[1]+b.n[1]*46];
      quad(CON,[A[0],16,A[1]],[B[0],16,B[1]],[B2[0],16,B2[1]],[A2[0],16,A2[1]]);   // 通路
      quad(BAND,[A2[0],16,A2[1]],[B2[0],16,B2[1]],[B2[0],24,B2[1]],[A2[0],24,A2[1]]); } }   // 2階の前の壁(ホームチームの色)
  stand(PE(E2,v=>46+v*44), 24, 24, 9, E2.L, Math.round(E2.L/30), mixT, 2, null);   // 2 階(46〜90・9 列・24〜48)
  { const K=Math.round(E1.L/8); for(let j=0;j<K;j++){ const a=E1.at(j/K), b=E1.at((j+1)/K); if(a.s<FRl-50 && b.s<FRl-50) continue;   // 2 階のない所(ラインの先)は 1 階の後ろに低い壁
      const A=[a.p[0]+a.n[0]*40,a.p[1]+a.n[1]*40], B=[b.p[0]+b.n[0]*40,b.p[1]+b.n[1]*40]; quad(CON,[A[0],16,A[1]],[B[0],16,B[1]],[B[0],19,B[1]],[A[0],19,A[1]]); } }""")
rep("""function hl3dStandsFull(sc,own,FR,hc,opt,dome){""",
"""// v2.1.z:内野席とファウルゾーンの席の内縁(1 本の折れ線)。o=ラインからの離れ、rb=本塁の後ろの半径、sEnd=ライン沿いの終わり(本塁からの道のり)。
//   f を 1° ごとに取り(一塁線の先 → 本塁の後ろ → 三塁線の先)、長さ 2 ごとに取り直す。法線は前後 ±24 の平均(弧→直線の移り目で外の列がねじれないように)。at(u) → {p:[x,z], n:外向きの法線, s:ラインに沿った道のり(ラインの外だけ。それ以外は 0)}
function hl3dBowlEdge(o,rb,sEnd){ const fA=45-Math.atan2(o,sEnd)*180/Math.PI, pts=[];
  const rin=f=>{ if(f>-45 && f<45) return Math.max(rb, o/Math.sin((45-f)*Math.PI/180)); if(f>135 && f<225) return Math.max(rb, o/Math.sin((f-135)*Math.PI/180)); return rb; };
  for(let f=fA; f>=-180-fA-1e-9; f-=1){ const ff= f< -45? f+360 : f, r=rin(ff), t=(ff+90)*Math.PI/180; pts.push({f:ff, p:[r*Math.sin(t), r*Math.cos(t)]}); }
  let L=0; pts[0].l=0; for(let i=1;i<pts.length;i++){ L+=Math.hypot(pts[i].p[0]-pts[i-1].p[0], pts[i].p[1]-pts[i-1].p[1]); pts[i].l=L; }
  // 2 ごとに取り直し、法線は前後 ±24 の平均にする(弧から直線へ移る所で法線が急に 43° 変わると、外の列がねじれるので)
  const Q=[], ST=2, M=Math.floor(L/ST); const lerp=l=>{ let i=1; while(i<pts.length-1 && pts[i].l<l) i++; const a=pts[i-1], b=pts[i], k= (b.l>a.l)? (l-a.l)/(b.l-a.l) : 0; return {p:[a.p[0]+(b.p[0]-a.p[0])*k, a.p[1]+(b.p[1]-a.p[1])*k], f:a.f+(b.f-a.f)*k}; };
  for(let i=0;i<=M;i++) Q.push(lerp(Math.min(L,i*ST)));
  for(let i=0;i<=M;i++){ const a=Q[Math.max(0,i-1)], b=Q[Math.min(M,i+1)], tx=b.p[0]-a.p[0], tz=b.p[1]-a.p[1], tl=Math.hypot(tx,tz)||1; let n=[tz/tl,-tx/tl]; if(n[0]*Q[i].p[0]+n[1]*Q[i].p[1]<0) n=[-n[0],-n[1]]; Q[i].n0=n; }
  const W=12; for(let i=0;i<=M;i++){ let x=0,z=0; for(let j=Math.max(0,i-W);j<=Math.min(M,i+W);j++){ x+=Q[j].n0[0]; z+=Q[j].n0[1]; } const l=Math.hypot(x,z)||1; Q[i].n=[x/l,z/l]; }
  const at=u=>{ const t=Math.max(0,Math.min(1,u))*M, i=Math.min(M-1,Math.floor(t)), k=t-i, a=Q[i], b=Q[i+1];
    const p=[a.p[0]+(b.p[0]-a.p[0])*k, a.p[1]+(b.p[1]-a.p[1])*k], nx=a.n[0]+(b.n[0]-a.n[0])*k, nz=a.n[1]+(b.n[1]-a.n[1])*k, nl=Math.hypot(nx,nz)||1, n=[nx/nl,nz/nl];
    const f=a.f+(b.f-a.f)*k, s= (f>-45 && f<45)? p[0]*Math.SQRT1_2-p[1]*Math.SQRT1_2 : (f>135 && f<225)? -p[0]*Math.SQRT1_2-p[1]*Math.SQRT1_2 : 0;   // ラインに沿った道のり
    return {p,n,s}; };
  return {L, at}; }
function hl3dStandsFull(sc,own,FR,hc,opt,dome){""")

# ④ 角の切れ目:外野席・フェンス・帯を f 22〜158 まで回し(今まで 30〜150)、1 階はライン沿い s=FRl−14 までにして、ラインの先の角で外野席とつながるように
for a,b in (("30+u*120","22+u*136"),("(82.5-30)/120","(82.5-22)/136"),("(97.5-30)/120","(97.5-22)/136"),("30+120*j/48","22+136*j/48"),("30+120*(j+1)/48","22+136*(j+1)/48"),
            ("hl3dArcWall(T,WD.Rf,30,150","hl3dArcWall(T,WD.Rf,22,158"),("hl3dArcWall(T,f=>WD.Rf(f)+.3,30,150","hl3dArcWall(T,f=>WD.Rf(f)+.3,22,158")):
    if s.count(a)<1: raise SystemExit("none: "+a)
    s=s.replace(a,b)
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
