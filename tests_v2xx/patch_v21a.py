# v2.0.k のソースに当てると v2.1.a(3D の下ごしらえ)。python3 patch_v21a.py src.html new.html
# 見た目は変えない(2.5D の舞台の HTML は v2.0.k と同じ。hl3_same.py で確かめる)。試合の計算・記録・セーブには触らない。
#   ① 動きの台本 hl3PlayScript:記録の場面から、カメラ・ボールの道筋・送球・アウトの印・走者(出発・1つの塁にかかる時間・アウト)・時刻を決める。
#      2.5D の舞台(hl3GroundHtml・hl3RunnersHtml・hl3BallHtml)はこれを読む。3D(v2.1.b〜)も同じ台本を読む(二重に書かない。決め事 4・4章)
#   ② Three.js の読み込み hl3dLoad:要るときだけ cdnjs から(版を固定)。読めない・WebGL がないときは false を返し、絵は 2.5D のまま。
#      まだ設定には出さない(3D の絵は v2.1.b から)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.0.k"; const BASE_V1="v1.2.v";','const APP_VERSION="v2.1.a"; const BASE_V1="v1.2.v";')

# ===== ① 動きの台本と、それを読む 2.5D の部品 =====
rep("""function hl3Ball(ev,tr,c,fld){
  if(!tr) return "";
  const h= (typeof tr.h==="number")? tr.h : ev.kind==="HR"? 62 : ev.kind==="SF"? 52 : ev.kind==="2B"? 30 : ev.kind==="3B"? 22 : 14;
  const lg= (fld && fld.legs.length)? ` data-legs="${fld.legs.map(l=>[l.x0,l.y0,l.x,l.y,l.t0,l.t1].map(n=>n.toFixed(2)).join(",")).join(";")}"` : "";   // v2.0.j:送球
  return `<div class="hl3sh" data-fly="${tr.ex.toFixed(1)},${tr.ey.toFixed(1)},${h}"></div><div class="hl3ball" data-fly="${tr.ex.toFixed(1)},${tr.ey.toFixed(1)},${h}"${lg}></div>`;
}
// 走者の移動(hlMovingRunners と同じ時間・同じ塁の線)。名前は打つ前の走者 pn(0=打者)
function hl3Movers(ev,c,names,fld){
  const bp=HL_BP(), st= ev.kind==="HR"? 1.0 : .9, per= ev.kind==="HR"? .3 : HL_PER, sur=n=>surnameOf(n), F=fld||{arr:{},mvOut:[]};
  const one=(a,b,pr,outT)=>{ const nm= a===0? ev.batter : (names&&names[a-1]); const p=bp[a];
    const inner= a===0? `<div class="hl3cap b"></div>${nm? hl3TagHtml(" bat",nm) : ""}` : `<div class="hl3cap"></div>${nm? hl3TagHtml(" run",nm) : ""}`;
    return hl3Bb(p[0],p[1]-6,0,c,inner,"hl3mv").replace('class="hl3bb hl3mv"',`class="hl3bb hl3mv" data-mv="${a},${b}" data-st="${st}" data-per="${pr.toFixed(3)}"${outT!=null? ` data-out="${outT.toFixed(2)}"` : ""}`); };
  return (ev.mv||[]).map(([a,b])=>{ const t=F.arr[a+","+b]; return one(a,b, t? (t-st)/(b-a) : per, null); }).join("")
    + F.mvOut.map(([a,b,ra])=>one(a,b,(ra-st)/((b-a)||1),ra)).join("");   // v2.0.j:アウトになる走者(v2.0.k:a===b は飛び出し)
}""",
r"""/* ===== v2.1.a:動きの台本(2.5D と 3D が同じものを読む) =====
   記録の場面 ev と、その場面で描く打球 tr(hlTrajectory か hl3Grounder の返り値。打球のない場面は null)から、プレーの動きを全部決める。ev には書き込まない。
   o:{tr, isPc(投手交代), af(打った後の塁 [bool×3]), names(打つ前の塁の名前。0=打者は ev.batter), extend(true=観戦。最後のアウトまで re を延ばす)}
   座標は地面の図(300×230。本塁 HL_HX,HL_HY。z は高さ)、時刻は打ってからの秒。返り値:
     cam        カメラ(HL3_CAMS の記号)
     tr3        描く打球の落点(球場の広さ・本塁打の止め方を入れたもの)。ex,ey,ang(,h,near)
     ball       {x0,y0,x,y,h,t1,ease}:本塁 → 落点を、高さ h の放物線で t1 秒(ease は cubic-bezier の4つの数)。null=ボールなし
     legs       送球の区間 [{x0,y0,x,y,t0,t1}]
     marks      アウトの印 [{x,y,t}]
     runners    走者 [{a,b,name,st,per,out}]:塁 a → b(0=本塁・4=本塁)、st 秒に走り出し、1つの塁に per 秒。out=アウトになって消える時刻(null=セーフ)
     moved      動く走者の元の塁(Set)。塁に止まっている札から外す
     re         走り終わる時刻(観戦はアウトの数・点数をここで変える)
     burst      本塁打の光   pulse:投手交代の脈   fld:hl3Fielding の返り値(null=なし) */
function hl3PlayScript(ev,o){
  const tr=o.tr||null, isPc=!!o.isPc, cam=hl3CamFor(ev,tr);
  const trp=hl3ParkTr(tr), tr3= trp? Object.assign({},trp,{ey: ev.kind==="HR"? Math.max(trp.ey, 36-((hl3Park? hl3Park.R : HL_FR)-HL_FR)) : trp.ey}) : null;   // 本塁打はフェンスの少し向こうに落とす(外野席のカメラで枠の外に出ないように)
  const fld= isPc? null : hl3Fielding(ev,tr3,o.af), F=fld||{arr:{},mvOut:[],legs:[],marks:[]};
  const moved=new Set([...(ev.mv||[]),...F.mvOut].map(([a])=>a));
  let re=hlRunEnd(ev); if(o.extend && fld && fld.end>re) re=fld.end;   // アウトの数・点数を変えるのは、最後のアウトのあと
  const st= ev.kind==="HR"? 1.0 : .9, per= ev.kind==="HR"? .3 : HL_PER, names=o.names||[], nm=a=> a===0? ev.batter : names[a-1];
  const runners=(ev.mv||[]).map(([a,b])=>{ const t=F.arr[a+","+b]; return {a,b,name:nm(a),st,per: t? (t-st)/(b-a) : per, out:null}; })
    .concat(F.mvOut.map(([a,b,ra])=>({a,b,name:nm(a),st,per:(ra-st)/((b-a)||1),out:ra})));   // アウトになる走者(a===b は飛び出し)
  const h= !tr3? 0 : (typeof tr3.h==="number")? tr3.h : ev.kind==="HR"? 62 : ev.kind==="SF"? 52 : ev.kind==="2B"? 30 : ev.kind==="3B"? 22 : 14;
  return {cam, tr3, fld, moved, re, runners, legs:F.legs, marks:F.marks,
    ball: tr3? {x0:HL_HX, y0:HL_HY-6, x:tr3.ex, y:tr3.ey, h, t1:.9, ease:[.2,.7,.35,1]} : null,
    burst: ev.kind==="HR" && !!tr3, pulse:isPc};
}
// 2.5D:地面に描くもの(打球の線・本塁打の光・投手交代の脈)
function hl3GroundHtml(S){
  let g=""; if(S.tr3) g+=`<path class="f-trail" pathLength="1" d="M${HL_HX},${HL_HY-6} L${S.tr3.ex.toFixed(1)},${S.tr3.ey.toFixed(1)}"/>`;
  if(S.burst) g+=hlBurst(S.tr3.ex,S.tr3.ey);
  if(S.pulse) g+=`<circle class="f-pulse" cx="${HL_HX}" cy="${HL_HY-45}" r="10"/>`;
  return g;
}
// 2.5D:ボール(本塁 → 落点、続けて送球。動かすのは hl3After)
function hl3BallHtml(S){
  const B=S.ball; if(!B) return "";
  const lg= S.legs.length? ` data-legs="${S.legs.map(l=>[l.x0,l.y0,l.x,l.y,l.t0,l.t1].map(n=>n.toFixed(2)).join(",")).join(";")}"` : "";   // v2.0.j:送球
  return `<div class="hl3sh" data-fly="${B.x.toFixed(1)},${B.y.toFixed(1)},${B.h}"></div><div class="hl3ball" data-fly="${B.x.toFixed(1)},${B.y.toFixed(1)},${B.h}"${lg}></div>`;
}
// 2.5D:走者(塁の線を滑る。動かすのは hl3After。時間は hlMovingRunners と同じ)
function hl3RunnersHtml(S,c){
  const bp=HL_BP();
  return S.runners.map(R=>{ const p=bp[R.a];
    const inner= R.a===0? `<div class="hl3cap b"></div>${R.name? hl3TagHtml(" bat",R.name) : ""}` : `<div class="hl3cap"></div>${R.name? hl3TagHtml(" run",R.name) : ""}`;
    return hl3Bb(p[0],p[1]-6,0,c,inner,"hl3mv").replace('class="hl3bb hl3mv"',`class="hl3bb hl3mv" data-mv="${R.a},${R.b}" data-st="${R.st}" data-per="${R.per.toFixed(3)}"${R.out!=null? ` data-out="${R.out.toFixed(2)}"` : ""}`); }).join("");
}""")

# 観戦のプレー(2.5D の道)
rep("""    const trg= tr || hl3Grounder(ev,seed,hl3Bip(ev)), cam=hl3CamFor(ev,trg), c=HL3_CAMS[cam];
    const trp=hl3ParkTr(trg), tr3= trp? Object.assign({},trp,{ey: ev.kind==="HR"? Math.max(trp.ey, 36-((hl3Park? hl3Park.R : HL_FR)-HL_FR)) : trp.ey}) : null;   // 本塁打はフェンスの少し向こうに落とす(外野席のカメラで枠の外に出ないように)
    const fld= isPc? null : hl3Fielding(ev,tr3,(ev.rn||(ev.bases||[]).map(b=>!!b)).map(Boolean)), moved=new Set([...(ev.mv||[]),...(fld? fld.mvOut : [])].map(([a])=>a));   // v2.0.j:送球・アウト
    if(fld && fld.end>re) re=fld.end;   // アウトの数・点数を変えるのは、最後のアウトのあと
    let g=""; if(tr3) g+=`<path class="f-trail" pathLength="1" d="M${HL_HX},${HL_HY-6} L${tr3.ex.toFixed(1)},${tr3.ey.toFixed(1)}"/>`;
    if(ev.kind==="HR" && tr3) g+=hlBurst(tr3.ex,tr3.ey);
    if(isPc) g+=`<circle class="f-pulse" cx="${HL_HX}" cy="${HL_HY-45}" r="10"/>`;
    let bb=hl3Tags(ev,r,pn,c,{noBatter: moved.has(0) || isPc, skip:moved})+hl3Movers(ev,c,pn,fld)+hl3Ball(ev,tr3,c,fld)+hl3OutMarks(fld,c);""",
"""    const S=hl3PlayScript(ev,{tr: tr || hl3Grounder(ev,seed,hl3Bip(ev)), isPc, af:(ev.rn||(ev.bases||[]).map(b=>!!b)).map(Boolean), names:pn, extend:true});   // v2.1.a:動きの台本
    const cam=S.cam, c=HL3_CAMS[cam], moved=S.moved;
    if(S.re>re) re=S.re;
    const g=hl3GroundHtml(S);
    let bb=hl3Tags(ev,r,pn,c,{noBatter: moved.has(0) || isPc, skip:moved})+hl3RunnersHtml(S,c)+hl3BallHtml(S)+hl3OutMarks(S.fld,c);""")

# 采配の結果
rep("""  const cam=hl3CamFor(ev,tr), c=HL3_CAMS[cam], dest=new Set(p.mv.map(([,b])=>b));
  const trp=hl3ParkTr(tr), tr3= trp? Object.assign({},trp,{ey: ev.kind==="HR"? Math.max(trp.ey, 36-((hl3Park? hl3Park.R : HL_FR)-HL_FR)) : trp.ey}) : null;
  const fld=hl3Fielding(ev,tr3,(d.rn||[null,null,null]).map(Boolean)), moved=new Set([...p.mv,...fld.mvOut].map(([a])=>a));   // v2.0.j:送球・アウト
  let g=""; if(tr3) g+=`<path class="f-trail" pathLength="1" d="M${HL_HX},${HL_HY-6} L${tr3.ex.toFixed(1)},${tr3.ey.toFixed(1)}"/>`;
  if(ev.kind==="HR" && tr3) g+=hlBurst(tr3.ex,tr3.ey);""",
"""  const S=hl3PlayScript(ev,{tr, af:(d.rn||[null,null,null]).map(Boolean), names:p.names});   // v2.1.a:動きの台本
  const cam=S.cam, c=HL3_CAMS[cam], dest=new Set(p.mv.map(([,b])=>b)), moved=S.moved;
  const g=hl3GroundHtml(S);""")
rep("""  let bb=hl3Tags(ev,rLike,stay,c,{noBatter: moved.has(0) || p.kind==="steal" || ev.kind==="HR"})+hl3Movers(ev,c,p.names,fld)+hl3Ball(ev,tr3,c,fld)+hl3OutMarks(fld,c);
  if(ev.kind==="BB") bb+=hl3Txt(HL_HX,HL_HY-40,24,"late",ev.hp? "死球" : "四球",c);
  const re=hlRunEnd(ev);""","""  let bb=hl3Tags(ev,rLike,stay,c,{noBatter: moved.has(0) || p.kind==="steal" || ev.kind==="HR"})+hl3RunnersHtml(S,c)+hl3BallHtml(S)+hl3OutMarks(S.fld,c);
  if(ev.kind==="BB") bb+=hl3Txt(HL_HX,HL_HY-40,24,"late",ev.hp? "死球" : "四球",c);
  const re=S.re;""")

# ===== ② Three.js の読み込み(v2.1.b から使う) =====
rep("""function hl3PlayScript(ev,o){""",r"""/* v2.1.a:Three.js(3D の絵。v2.1.b から)。要るときに1回だけ cdnjs から読む(版を固定。決め事 4)。
   hl3dLoad() は Promise<boolean>:読めて WebGL が使えれば true(window.THREE)。読めない・WebGL がない・8 秒で返事がないときは false で、絵は 2.5D のまま。
   ほかの所から読み替えるとき(テスト・オフライン用の写し)は、先に window.HL3D_THREE_URL に URL を入れておく */
const HL3D_THREE_URL="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js";
let hl3dState=null;   // null=まだ / Promise=読み込み中・済み
function hl3dWebGL(){ try{ const c=document.createElement("canvas"); return !!(window.WebGLRenderingContext && (c.getContext("webgl")||c.getContext("experimental-webgl"))); }catch(e){ return false; } }
function hl3dLoad(){
  if(hl3dState) return hl3dState;
  hl3dState=new Promise(res=>{
    if(!hl3dWebGL()){ res(false); return; }
    if(window.THREE && window.THREE.WebGLRenderer){ res(true); return; }
    let done=false; const fin=ok=>{ if(done) return; done=true; res(ok && !!(window.THREE && window.THREE.WebGLRenderer)); };
    try{ const el=document.createElement("script"); el.src=window.HL3D_THREE_URL||HL3D_THREE_URL; el.async=true; el.crossOrigin="anonymous";
      el.onload=()=>fin(true); el.onerror=()=>fin(false); document.head.appendChild(el); }catch(e){ fin(false); }
    setTimeout(()=>fin(false),8000);
  });
  return hl3dState;
}
function hl3PlayScript(ev,o){""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
