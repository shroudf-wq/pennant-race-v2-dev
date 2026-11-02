# v2.2.j のソースに当てると v2.2.k。python3 patch_v22k.py src.html new.html
# エキサイトシートに観客(ユーザーの「エキサイトシートに観客を乗せられるか?」)。背景と観戦の 3D。見た目だけ(計算・2.5D・セーブには触らない)。
#   ① hl3dStandsFull の stand() に geos(席と段を入れる別の geo。省くと今まで通り)と ph0(人の帯の高さの上書き)を足す
#   ② opt.excite={fo, frl} があれば、両ラインの外(o 12〜22+fo・s 54〜frl−40)に 3 段(高さ 3.6)のエキサイトシートを stand() で作る:
#      席と段は赤(c4413a×lit。今までの箱と同じ色)、人はふつうの席と同じ絵(mix:本拠地の色 18%)。人の帯の高さ 3.2(段が低いので式のままだと 2.7)。区画は 30 ごと・通路なし
#   ③ hl3dParkMeshes:今までの赤い箱 3 段を外し、hl3dStandsFull に excite を渡す(背景は fo 6、観戦は 0)。防球ネット・ウイング席・ラバーフェンスは今まで通り
#   テスト:hl3d_bg.py ㉕(エキサイトシートの人の区画が 2 以上、赤い席の mesh が 2(席・段))
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.2.j"; const BASE_V1="v1.4.q";','const APP_VERSION="v2.2.k"; const BASE_V1="v1.4.q";')
# ①
rep("""  const stand=(P,h0,H,N,L,K,tint,aisle,skip,lowSkip,shade)=>{""","""  const stand=(P,h0,H,N,L,K,tint,aisle,skip,lowSkip,shade,geos,ph0)=>{   /* v2.2.k:geos={SEAT,CON} 席と段の入れ先・ph0 人の帯の高さ */""")
rep("""      for(let i=0;i<N;i++){ const v0=i/N, v1=(i+1)/N, y=h0+H*i/N, y1=h0+H*(i+1)/N, vm=v0+(v1-v0)*.42, ph=Math.min(4.2,(H/N)*1.25+1.2);""",
"""      for(let i=0;i<N;i++){ const v0=i/N, v1=(i+1)/N, y=h0+H*i/N, y1=h0+H*(i+1)/N, vm=v0+(v1-v0)*.42, ph=ph0||Math.min(4.2,(H/N)*1.25+1.2);""")
rep("""        const dk= !!(shade && shade((u0+u1)/2,(v0+v1)/2)), SEAT=dk? SEATd : SEAT0, CON=dk? CONd : CON0, PG=dk? PGd : PG0;   // v2.2.g:屋根の影の下は暗い材質へ""",
"""        const dk= !!(shade && shade((u0+u1)/2,(v0+v1)/2)), SEAT=geos? geos.SEAT : dk? SEATd : SEAT0, CON=geos? geos.CON : dk? CONd : CON0, PG=dk? PGd : PG0;   // v2.2.g:屋根の影の下は暗い材質へ。v2.2.k:geos""")
# ② エキサイトシート(席の mesh を作る前に)
rep("""  mesh(SEAT,seatM); mesh(CON,conM); mesh(BAND,bandM); mesh(SEATd,seatMd); mesh(CONd,conMd);""",
"""  if(opt.excite){   // v2.2.k:エキサイトシート(両ラインの外 o 12〜22・s 54〜frl−40・3 段)に観客。席と段は赤、人はふつうの席と同じ絵
    const EXS=geo(), EXC=geo(), exM=new T.MeshLambertMaterial({color:new T.Color(0xc4413a).multiplyScalar(lit),side:T.DoubleSide}); own.push(exM); const FO2=opt.excite.fo||0, s0=54, s1=opt.excite.frl-40;
    [1,-1].forEach(sx=>{ const d=[sx*Math.SQRT1_2,-Math.SQRT1_2], n=[sx*Math.SQRT1_2,Math.SQRT1_2];
      const P=(u,v)=>{ const s_=s0+u*(s1-s0), o=12+FO2+v*10; return [d[0]*s_+n[0]*o, d[1]*s_+n[1]*o]; };
      stand(P, 0, 3.6, 3, s1-s0, Math.max(1,Math.round((s1-s0)/30)), mixT, 0, null, null, null, {SEAT:EXS,CON:EXC}, 3.2); });
    const m1=mesh(EXS,exM), m2=mesh(EXC,exM); if(m1) m1.userData.k="excite"; if(m2) m2.userData.k="excite"; }
  mesh(SEAT,seatM); mesh(CON,conM); mesh(BAND,bandM); mesh(SEATd,seatMd); mesh(CONd,conMd);""")
# ③
rep("""    opt.look=LOOK; opt.roofShade=LOOK.roof;   // v2.1.v:球団ごとの型(v2.1.w:外野席の種類にも使う。v2.1.x:先頭で決める)。v2.2.g:大屋根の影
    const so= FULL? opt : {wd:hl3dWide0(FR), ofF0:30, look:LOOK, roofShade:LOOK.roof, secL:60, away:opt.away||null, out:(opt.out=opt.out||{})};""",
"""    opt.look=LOOK; opt.roofShade=LOOK.roof; opt.excite={fo: FULL? 6 : 0, frl: WD? WD.FRl : FR};   // v2.1.v:球団ごとの型(v2.1.w:外野席の種類にも使う。v2.1.x:先頭で決める)。v2.2.g:大屋根の影。v2.2.k:エキサイトシート
    const so= FULL? opt : {wd:hl3dWide0(FR), ofF0:30, look:LOOK, roofShade:LOOK.roof, secL:60, excite:opt.excite, away:opt.away||null, out:(opt.out=opt.out||{})};""")
rep("""      const e1=FRl-40; [[12,15.3,0,1.2],[15.3,18.6,0,2.4],[18.6,22,0,3.6]].forEach(([o0,o1,y0,y1])=>box(sx,54,e1,o0+FO,o1+FO,y0,y1,mRed));""",
"""      const e1=FRl-40;   /* v2.2.k:3 段の赤い箱は hl3dStandsFull(opt.excite)で人つきの段に */""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
