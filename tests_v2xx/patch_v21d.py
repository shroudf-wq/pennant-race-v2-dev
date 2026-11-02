# v2.1.c のソースに当てると v2.1.d(守備の野手が打球を追う)。python3 patch_v21d.py src.html new.html
# 見た目だけ。試合の計算・記録・セーブには触らない(どの野手が追うかは、打球の落点と、あれば記録の打球の野手から決める。乱数は使わない)。
#   台本(hl3PlayScript)に「追う野手」chase を足す。2.5D も 3D も同じ台本を読む:
#     ・野手は打ってから 0.12 秒で動き出し、着く時刻まで走り続ける
#     ・安打:外野手が落ちた所へ走る(頭を越えた・間を抜けた当たりは後ろ・横へ追う)。送球がある場面は、拾って投げる時刻までに着く
#     ・内野を抜ける低い単打:打球の線にいちばん近い内野手(34 以内)が飛びつき、届かずに倒れて起き上がる
#     ・フライ・ライナーの凡打:捕る野手が落点へ走る。遠い(22 より遠い)ときは飛びついて捕る
#     ・ゴロの凡打:内野手が捕る所へ寄る。エラーは飛びついてはじく
#     ・本塁打:外野手がフェンスまで下がって見送る
#   飛びつき:3D は人が前へ倒れる(打球のほうへ)。2.5D は動くだけ
#   3D の人を 1.4 倍に(動きが見えるように)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.c"; const BASE_V1="v1.2.v";','const APP_VERSION="v2.1.d"; const BASE_V1="v1.2.v";')

# 野手の札に守備位置を書く(どの札を動かすかを台本と合わせる)
rep("""const [x,y]=hlPt(ang,dist); out+=hl3Bb(x,y,0,c,`<div class="hl3cap f"></div>${hl3TagHtml("",nm)}`,"hl3f"); });""",
    """const [x,y]=hlPt(ang,dist); out+=hl3Bb(x,y,0,c,`<div class="hl3cap f"></div>${hl3TagHtml("",nm)}`,"hl3f").replace('class="hl3bb hl3f"',`class="hl3bb hl3f" data-pos="${pos}"`); });""")

# ===== 台本:追う野手 =====
rep("""  const fld= isPc? null : hl3Fielding(ev,tr3,o.af), F=fld||{arr:{},mvOut:[],legs:[],marks:[]};""",
    """  const fld= isPc? null : hl3Fielding(ev,tr3,o.af), F=fld||{arr:{},mvOut:[],legs:[],marks:[]};
  const chase= isPc? [] : hl3Chase(ev,tr3,{pick: F.legs.length? F.legs[0].t0 : null, pos:o.fpos||null});   // v2.1.d:打球を追う野手""")
rep("""    burst: ev.kind==="HR" && !!tr3, pulse:isPc};""","""    burst: ev.kind==="HR" && !!tr3, pulse:isPc, chase};""")
rep("""// 2.5D:地面に描くもの(打球の線・本塁打の光・投手交代の脈)""",r"""/* v2.1.d:打球を追う野手。返り値 [{pos, kf:[[時刻,x,y,倒れ(0=立つ〜1=倒れる)],…]}](時刻は打ってからの秒、x,y は地面の図)。
   どの野手か:記録の打球の野手(o.pos。凡打・エラー)があればそれ、なければ落点にいちばん近い野手。打ってから 0.12 秒で動き出し、着く時刻まで走り続ける(速さは図の単位で 1 秒に 120 まで。遠いときは遅れて着く) */
const HL3_FSP=120, HL3_REACT=.12;
function hl3PassT(u){ let a=0,b=1; for(let i=0;i<22;i++){ const m=(a+b)/2; if(hl3dFlyE(m)<u) a=m; else b=m; } return .9*(a+b)/2; }   // 打球が線の u の所を通る時刻
function hl3Chase(ev,tr3,o){
  if(!tr3) return [];
  const k=ev.kind, L=[tr3.ex,tr3.ey], gb= typeof tr3.h==="number" && tr3.h<10, h= typeof tr3.h==="number"? tr3.h : (k==="2B"? 30 : k==="3B"? 22 : k==="SF"? 52 : 14), out=[];
  const P=pos=>hlPt(HL_POS[pos][0],HL_POS[pos][1]), D=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
  const OF=["左","中","右"], IF=["一","二","遊","三"];
  const near=list=>list.reduce((m,p)=> (!m || D(P(p),L)<D(P(m),L))? p : m, null);
  const mine= (o.pos && HL_POS[o.pos])? o.pos : null;
  // 走る:arrive に to へ着く(遠くて間に合わないときは速さのまま遅れて着く)。dive=最後に飛びつく
  const run=(pos,to,arrive,dive)=>{ const f=P(pos), d=D(f,to), t0=HL3_REACT, t1=Math.max(t0+.05, arrive, t0+d/HL3_FSP);   // 打った瞬間から動き出し、着くまで走り続ける
    if(!dive){ out.push({pos, kf:[[0,f[0],f[1],0],[t0,f[0],f[1],0],[t1,to[0],to[1],0]]}); return t1; }
    const m=[f[0]+(to[0]-f[0])*.8, f[1]+(to[1]-f[1])*.8];
    out.push({pos, kf:[[0,f[0],f[1],0],[t0,f[0],f[1],0],[Math.max(t0+.04,t1-.12),m[0],m[1],0],[t1,to[0],to[1],1],[t1+.5,to[0],to[1],1],[t1+.9,to[0],to[1],0]]}); return t1; };
  if(k==="SH"||k==="FC") return out;   // バント:今は動かさない
  if(k==="HR"){   // フェンスまで下がって見送る
    const of=near(OF), a=Math.atan2(HL_HY-L[1],L[0]-HL_HX), R=(hl3Park? hl3Park.R : HL_FR)-6;
    run(of,[HL_HX+R*Math.cos(a), HL_HY-R*Math.sin(a)],1.0); return out; }
  if(gb && (k==="OUT"||k==="E")){   // ゴロ:内野手が寄って捕る。エラーは飛びついてはじく
    const f= (mine && IF.concat(["投"]).includes(mine))? mine : near(IF.concat(["投"]));
    if(k==="E"){ const F=P(f), q=[F[0]+(L[0]-F[0])*.45, F[1]+(L[1]-F[1])*.45]; run(f,q,hl3PassT(Math.min(.98,D([HL_HX,HL_HY-6],q)/Math.max(1,D([HL_HX,HL_HY-6],L)))),true); }
    else run(f,L,.86);
    return out; }
  if(k==="OUT"||k==="SF"||k==="E"){   // フライ・ライナー:捕る野手が落点へ(遠いときは飛びつく)
    const f= mine || near(OF.concat(IF)); run(f,L,.9,D(P(f),L)>22); return out; }
  // 安打:低い単打は近い内野手が飛びつき、届かない
  if(k==="1B" && h<=16){ const H0=[HL_HX,HL_HY-6], vx=L[0]-H0[0], vy=L[1]-H0[1], vv=vx*vx+vy*vy||1; let best=null;
    IF.forEach(p=>{ const F=P(p), u=Math.max(.05,Math.min(.95,((F[0]-H0[0])*vx+(F[1]-H0[1])*vy)/vv)), Q=[H0[0]+vx*u,H0[1]+vy*u], d=D(F,Q); if(d<34 && (!best || d<best.d)) best={p,Q,d,u}; });
    if(best){ const F=P(best.p), tp=Math.max(HL3_REACT+.2, hl3PassT(best.u)), q=[best.Q[0]+(F[0]-best.Q[0])*.3, best.Q[1]+(F[1]-best.Q[1])*.3];   // 打球の線の少し手前で倒れる(届かない)
      out.push({pos:best.p, kf:[[0,F[0],F[1],0],[Math.max(HL3_REACT,tp-.2),F[0],F[1],0],[tp,q[0],q[1],1],[tp+.55,q[0],q[1],1],[tp+.95,q[0],q[1],0]]}); } }
  // 外野手は落ちた所へ(頭を越えた・間を抜けた当たりは後ろ・横へ追う)。送球がある場面は拾う時刻までに
  run(near(OF), L, Math.max(.95, o.pick? o.pick-.04 : 1.15));
  return out;
}
// 野手の札に、追う動き(data-kf)を書き足す
function hl3ChaseAttr(html,S){ (S.chase||[]).forEach(c=>{ html=html.replace(`data-pos="${c.pos}"`,`data-pos="${c.pos}" data-kf="${c.kf.map(q=>q.map(n=>(+n).toFixed(2)).join(",")).join(";")}"`); }); return html; }
// 2.5D:地面に描くもの(打球の線・本塁打の光・投手交代の脈)""")
# 観戦・采配で、札に動きを書き足す(記録の打球の野手も渡す)
rep("""    const S=hl3PlayScript(ev,{tr: tr || hl3Grounder(ev,seed,hl3Bip(ev)), isPc, af:(ev.rn||(ev.bases||[]).map(b=>!!b)).map(Boolean), names:pn, extend:true});   // v2.1.a:動きの台本""",
    """    const S=hl3PlayScript(ev,{tr: tr || hl3Grounder(ev,seed,hl3Bip(ev)), isPc, af:(ev.rn||(ev.bases||[]).map(b=>!!b)).map(Boolean), names:pn, extend:true, fpos:(hl3Bip(ev)||{}).pos});   // v2.1.a:動きの台本""")
rep("""    let bb=hl3Tags(ev,r,pn,c,{noBatter: moved.has(0) || isPc, skip:moved})+""","""    let bb=hl3ChaseAttr(hl3Tags(ev,r,pn,c,{noBatter: moved.has(0) || isPc, skip:moved}),S)+""")
rep("""  const S=hl3PlayScript(ev,{tr, af:(d.rn||[null,null,null]).map(Boolean), names:p.names});   // v2.1.a:動きの台本""",
    """  const S=hl3PlayScript(ev,{tr, af:(d.rn||[null,null,null]).map(Boolean), names:p.names, fpos:bip&&bip.pos});   // v2.1.a:動きの台本""")
rep("""  let bb=hl3Tags(ev,rLike,stay,c,{noBatter: moved.has(0) || p.kind==="steal" || ev.kind==="HR"})+""","""  let bb=hl3ChaseAttr(hl3Tags(ev,rLike,stay,c,{noBatter: moved.has(0) || p.kind==="steal" || ev.kind==="HR"}),S)+""")

# ===== 2.5D:野手を動かす =====
rep("""  if(mvEnd>0) setTimeout(()=>hl3Declutter(st,true), Math.max(mvEnd+40,560));   // v2.0.c:走り終えた走者の札も入れて、もう一度""",
    """  st.querySelectorAll(".hl3bb[data-kf]").forEach(el=>{   // v2.1.d:打球を追う野手
    const kf=el.dataset.kf.split(";").map(q=>q.split(",").map(Number)), T=kf[kf.length-1][0]; if(!(T>0)) return;
    try{ el.animate(kf.map(([t,x,y])=>({transform:`translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0px) ${hl3Rot(c)}`, offset:Math.min(1,t/T)})),{duration:T*1000,fill:"forwards"}); }catch(e){}
    mvEnd=Math.max(mvEnd,T*1000); });
  if(mvEnd>0) setTimeout(()=>hl3Declutter(st,true), Math.max(mvEnd+40,560));   // v2.0.c:走り終えた走者の札も入れて、もう一度""")

# ===== 3D:野手を動かす(飛びつきは前へ倒れる) =====
rep("""      st:+(b.dataset.st||0), per:+(b.dataset.per||HL_PER), out: b.dataset.out!=null? +b.dataset.out : null, man:null, op:1};""",
    """      st:+(b.dataset.st||0), per:+(b.dataset.per||HL_PER), out: b.dataset.out!=null? +b.dataset.out : null, man:null, op:1,
      kf: b.dataset.kf? b.dataset.kf.split(";").map(q=>q.split(",").map(Number)) : null, hd:0};   // v2.1.d:追う野手""")
rep("""  let mvEnd=0; items.forEach(it=>{ if(!it.mv) return; const n=it.mv[1]-it.mv[0]; mvEnd=Math.max(mvEnd,(it.st+n*it.per)*1000+(it.mv[1]===4? 260 : 0)); });""",
    """  let mvEnd=0; items.forEach(it=>{ if(it.kf) mvEnd=Math.max(mvEnd,it.kf[it.kf.length-1][0]*1000); if(!it.mv) return; const n=it.mv[1]-it.mv[0]; mvEnd=Math.max(mvEnd,(it.st+n*it.per)*1000+(it.mv[1]===4? 260 : 0)); });""")
rep("""  S.items.forEach(it=>{ let x=it.x, y=it.y, op=1;""","""  S.items.forEach(it=>{ let x=it.x, y=it.y, op=1, dv=0;
    if(it.kf){ const K=it.kf; let i=0; while(i<K.length-1 && t>=K[i+1][0]) i++;   // v2.1.d:追う野手(区切りの間はまっすぐ)
      if(i>=K.length-1){ x=K[i][1]; y=K[i][2]; dv=K[i][3]; }
      else { const a=K[i], b=K[i+1], f=Math.max(0,Math.min(1,(t-a[0])/Math.max(.001,b[0]-a[0]))); x=a[1]+(b[1]-a[1])*f; y=a[2]+(b[2]-a[2])*f; dv=a[3]+(b[3]-a[3])*f;
        if(Math.hypot(b[1]-a[1],b[2]-a[2])>.5) it.hd=Math.atan2(b[1]-a[1],b[2]-a[2]); } }""")
rep("""    if(it.man){ it.man.position.copy(hl3dP(x,y,0)); if(op!==it.op){""","""    if(it.man && it.kf){ it.man.rotation.order="YXZ"; it.man.rotation.y=it.hd; it.man.rotation.x=dv*1.35; }
    if(it.man){ it.man.position.copy(hl3dP(x,y,0)); if(op!==it.op){""")
rep("""    const v=hl3dP(x,y,it.man? 11 : it.z).project(S.cam);""","""    const v=hl3dP(x,y,it.man? 11*(1-.65*dv) : it.z).project(S.cam);""")
# 人を 1.4 倍に(飛びつき・追う動きが見えるように)。札の高さは 11 のまま(15 にすると札の重なりが 390px で 1 → 7 に増えた。頭に少しかかる)
rep("""b.position.y=3.2; h.position.y=8; sh.rotation.x=-Math.PI/2; sh.position.y=.15; g.add(sh,b,h);""","""b.position.y=3.2; h.position.y=8; sh.rotation.x=-Math.PI/2; sh.position.y=.15; g.add(sh,b,h); g.scale.setScalar(1.4); /* v2.1.d:1.4 倍 */""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
