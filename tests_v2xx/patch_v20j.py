# v2.0.i のソースに当てると v2.0.j(アウトにする塁へ送球する。2.5D だけ)。python3 patch_v20j.py src.html new.html
# 見た目だけ。試合の計算・記録・セーブ・2D の図には触らない。乱数は hlRand だけ。記録の ev には何も書き込まない(見返しの記録はセーブに入るため)
#   ・ゴロの凡打:捕った野手 → 一塁。打者は一塁へ走り、ボールの直後に着いてアウト(間一髪)
#   ・併殺:捕った野手 → 二塁(一塁走者アウト)→ 一塁(打者アウト)
#   ・送りバント:転がった所 → 一塁。バントの失敗(野選):→ 先の走者がいた次の塁(二塁走者がいれば三塁、いなければ二塁)
#   ・フライの凡打:捕った所に「アウト」(投げない)
#   ・安打で走者が刺される(記録でアウトが増えた安打):外野 → 本塁(単打の二塁走者・長打の一塁走者)/三塁(単打の一塁走者)
#   ・アウトと得点の順番(野球の決まり):
#       3つ目のアウトがタッチプレー(三塁・本塁で刺す)で点が入る場面は、得点の走者が本塁を踏んでからアウトの印を出す
#       3つ目のアウトがフォースアウトで点が入る組み合わせは、計算では出ない(出たときは、本塁を踏むのをアウトのあとにする)
#   ・じっくり采配の結果は、v1 の計算が直前に決めた打球(lastBIP:ゴロ/フライと、処理した野手)を読む(読むだけ。書き込まない)
#     観戦(見返し)には打球の記録がないので、これまでどおり hlRand で決める
#   ・ゴロゴー(ゴロの間に三塁走者が還る)は v1.2.k の計算にないので出ない。v1 に入ったら、上の順番の決まりがそのまま効く
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.0.i"; const BASE_V1="v1.2.k";','const APP_VERSION="v2.0.j"; const BASE_V1="v1.2.k";')

rep(""".hl3txt.runs{color:var(--gold)}""",""".hl3txt.runs{color:var(--gold)}
.hl3txt.outMk{color:#fff;background:rgba(190,40,30,.88);border-radius:4px;padding:0 4px;line-height:1.35;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:bold;animation:hl3OutMk 1.5s ease-out both}   /* v2.0.j:アウトの印(出て、1秒ほどで消える。札に重なったままにしない) */
@keyframes hl3OutMk{0%{opacity:0;transform:translateX(-50%) scale(1.5)}12%{opacity:1;transform:translateX(-50%) scale(1)}75%{opacity:1;transform:translateX(-50%) scale(1)}100%{opacity:0;transform:translateX(-50%) scale(1)}}""")

# ===== 打球:采配では v1 が決めた打球(ゴロ/フライ・野手)を使う。バントの失敗(野選)はバントと同じ転がり =====
rep("""function hl3Grounder(ev,seed){
  const k=ev.kind; if(!(k==="OUT"||k==="FC"||k==="E"||k==="SH")) return null;
  const r1=hlRand(seed+.37), r2=hlRand(seed+1.7);
  let ang,dist,h,near=false;
  if(k==="SH"){ ang=72+r1*36; dist=24+r2*10; h=3; near=true; }""","""function hl3Grounder(ev,seed,bip){
  const k=ev.kind; if(!(k==="OUT"||k==="FC"||k==="E"||k==="SH")) return null;
  const r1=hlRand(seed+.37), r2=hlRand(seed+1.7);
  let ang,dist,h,near=false;
  if(k==="SH"||k==="FC"){ ang=72+r1*36; dist=24+r2*10; h=3; near=true; }   // v1 の野選はバントの失敗だけ
  else if(bip && bip.pos && (k==="OUT"||k==="E")){   // v2.0.j:采配の結果は v1 が決めた打球(処理した野手・ゴロかフライか)
    const gbB= bip.type==="GB" || !!ev.dp, P= bip.pos==="捕"? [96,12] : (HL_POS[bip.pos]||HL_POS.遊), inf= ["投","捕","一","二","遊","三"].includes(bip.pos);
    ang=P[0]+(r1-.5)*8;
    if(gbB){ dist=P[1]-4+(k==="E"? 22 : 0); h=4; } else { dist=P[1]-(inf? 2 : 6); h= inf? 30 : 46; } }""")

# ===== 守備の動き(送球の区間・アウトの印・アウトになる走者・本塁を踏む時刻の直し) =====
rep("""// 打球:地面の線(本塁→落点)と高さ(結果の種類で決める)。乱数は hlTrajectory と同じ seed(演出用)
function hl3Ball(ev,tr,c){""",r"""// v2.0.j:守備。ev=場面(kind・mv・pn 打つ前の塁・po 打つ前のアウト・outs・runs・dp)、tr=描く打球(ex,ey。h<10 ならゴロ)。ev には書き込まない
//   返り値:legs=送球の区間 [{x0,y0,x,y,t0,t1}](秒。打ってから)、marks=アウトの印 [{x,y,t}]、mvOut=アウトになる走者 [[元の塁,アウトの塁,着く時刻]]、arr=本塁を踏む時刻の直し {"a,b":時刻}、end=終わる時刻
function hl3Fielding(ev,tr){
  const F={legs:[],marks:[],mvOut:[],arr:{},end:0};
  if(!tr || ev.kind==="HR") return F;
  const bp=HL_BP(), st=.9, per=HL_PER, k=ev.kind, mv=ev.mv||[], pn=ev.pn||[null,null,null];
  const dOuts=Math.max(0,(ev.outs||0)-((typeof ev.po==="number")? ev.po : 0));
  const gb= typeof tr.h==="number" && tr.h<10, tgt=[]; let force=false;
  if(k==="OUT"){
    if(!gb){ F.marks.push({x:tr.ex,y:tr.ey,t:.92}); F.end=1.3; return F; }   // フライ:捕った所でアウト
    if(ev.dp) tgt.push([1,2],[0,1]); else tgt.push([0,1]); force=true;
  } else if(k==="SH"){ tgt.push([0,1]); force=true; }
  else if(k==="FC"){ tgt.push(pn[1]? [2,3] : [1,2]); force=true; }   // バントの失敗:先の走者を封殺
  else if((k==="1B"||k==="2B"||k==="3B") && dOuts>0){   // 安打で走者が刺される(記録でアウトが増えた安打。刺されたのは塁の動きがない走者)
    const src=new Set(mv.map(([a])=>a)); let n=dOuts;
    for(let i=2;i>=0 && n>0;i--){ if(!pn[i] || src.has(i+1)) continue; tgt.push([i+1,(k==="1B" && i===0)? 3 : 4]); n--; }
  }
  if(!tgt.length) return F;
  const arrive=(a,b)=>st+(b-a)*per, dur=(x0,y0,x1,y1)=>.1+Math.hypot(x1-x0,y1-y0)/650;
  const sT=mv.filter(([,b])=>b===4).map(([a,b])=>arrive(a,b)), lastScore= sT.length? Math.max(...sT) : 0;
  const third=(ev.outs||0)>=3 && (ev.runs||0)>0;
  let px=tr.ex, py=tr.ey, t=.9+(gb? .08 : .3);   // 捕ってから投げるまで(ゴロ・バントは素早く、外野は拾ってから)
  tgt.forEach(([a,b],i)=>{
    const [bx,by0]=bp[b], by=by0-3, last= i===tgt.length-1;
    let t0=t; const d=dur(px,py,bx,by);
    // タッチプレーで3つ目のアウト:得点の走者が本塁を踏んでからアウトにする(踏む前のアウトなら、その点は入らないため)
    if(last && third && !force) t0=Math.max(t0, lastScore+.12-d);
    const ta=t0+d; F.legs.push({x0:px,y0:py,x:bx,y:by,t0,t1:ta}); px=bx; py=by;
    const ra=Math.max(arrive(a,b), ta+.05);   // 走者はボールの直後に着く(間一髪)
    F.mvOut.push([a,b,ra]); F.marks.push({x:bx,y:by0,t:ta});
    t=ta+.06;   // 併殺の中継
    F.end=Math.max(F.end, ra+.3);
  });
  // フォースアウトで3つ目のアウトなのに点が入る組み合わせ(計算では出ない):本塁を踏むのをアウトのあとにして、点が入らないように見せる
  if(third && force){ const tag=F.marks[F.marks.length-1].t; mv.forEach(([a,b])=>{ if(b===4 && arrive(a,b)<=tag) F.arr[a+","+b]=tag+.1; }); }
  return F;
}
// 打球:地面の線(本塁→落点)と高さ(結果の種類で決める)。乱数は hlTrajectory と同じ seed(演出用)
function hl3Ball(ev,tr,c,fld){""")
rep("""  return `<div class="hl3sh" data-fly="${tr.ex.toFixed(1)},${tr.ey.toFixed(1)},${h}"></div><div class="hl3ball" data-fly="${tr.ex.toFixed(1)},${tr.ey.toFixed(1)},${h}"></div>`;""",
    """  const lg= (fld && fld.legs.length)? ` data-legs="${fld.legs.map(l=>[l.x0,l.y0,l.x,l.y,l.t0,l.t1].map(n=>n.toFixed(2)).join(",")).join(";")}"` : "";   // v2.0.j:送球
  return `<div class="hl3sh" data-fly="${tr.ex.toFixed(1)},${tr.ey.toFixed(1)},${h}"></div><div class="hl3ball" data-fly="${tr.ex.toFixed(1)},${tr.ey.toFixed(1)},${h}"${lg}></div>`;""")
# アウトの印
rep("""function hl3Txt(x,y,size,cls,txt,c,style){""","""function hl3OutMarks(fld,c){ return fld? fld.marks.map(m=>hl3Txt(m.x,m.y-9,12,"outMk","アウト",c,`animation-delay:${m.t.toFixed(2)}s`)).join("") : ""; }   // v2.0.j
function hl3Txt(x,y,size,cls,txt,c,style){""")

# 走者:アウトになる走者(着く時刻に合わせた速さ・着いたら消える)と、本塁を踏む時刻の直し
rep("""function hl3Movers(ev,c,names){
  const bp=HL_BP(), st= ev.kind==="HR"? 1.0 : .9, per= ev.kind==="HR"? .3 : HL_PER, sur=n=>surnameOf(n);
  return (ev.mv||[]).map(([a,b])=>{ const nm= a===0? ev.batter : (names&&names[a-1]); const p=bp[a];
    const inner= a===0? `<div class="hl3cap b"></div>${nm? hl3TagHtml(" bat",nm) : ""}` : `<div class="hl3cap"></div>${nm? hl3TagHtml(" run",nm) : ""}`;
    return hl3Bb(p[0],p[1]-6,0,c,inner,"hl3mv").replace('class="hl3bb hl3mv"',`class="hl3bb hl3mv" data-mv="${a},${b}" data-st="${st}" data-per="${per}"`); }).join("");
}""","""function hl3Movers(ev,c,names,fld){
  const bp=HL_BP(), st= ev.kind==="HR"? 1.0 : .9, per= ev.kind==="HR"? .3 : HL_PER, sur=n=>surnameOf(n), F=fld||{arr:{},mvOut:[]};
  const one=(a,b,pr,outT)=>{ const nm= a===0? ev.batter : (names&&names[a-1]); const p=bp[a];
    const inner= a===0? `<div class="hl3cap b"></div>${nm? hl3TagHtml(" bat",nm) : ""}` : `<div class="hl3cap"></div>${nm? hl3TagHtml(" run",nm) : ""}`;
    return hl3Bb(p[0],p[1]-6,0,c,inner,"hl3mv").replace('class="hl3bb hl3mv"',`class="hl3bb hl3mv" data-mv="${a},${b}" data-st="${st}" data-per="${pr.toFixed(3)}"${outT!=null? ` data-out="${outT.toFixed(2)}"` : ""}`); };
  return (ev.mv||[]).map(([a,b])=>{ const t=F.arr[a+","+b]; return one(a,b, t? (t-st)/(b-a) : per, null); }).join("")
    + F.mvOut.map(([a,b,ra])=>one(a,b,(ra-st)/(b-a),ra)).join("");   // v2.0.j:アウトになる走者
}""")
# 動かす:送球の区間を、打球のあとに続けて飛ばす。アウトになった走者は着いたら薄くして消す
rep("""    try{ fly.animate(kb,{duration:dur,easing:ease,fill:"forwards"}); const sh=st.querySelector(".hl3sh"); if(sh) sh.animate(ks,{duration:dur,easing:ease,fill:"forwards"}); }catch(e){ fly.style.opacity=1; fly.style.transform=kb[n].transform; }
  }""","""    try{ fly.animate(kb,{duration:dur,easing:ease,fill:"forwards"}); const sh=st.querySelector(".hl3sh"); if(sh) sh.animate(ks,{duration:dur,easing:ease,fill:"forwards"}); }catch(e){ fly.style.opacity=1; fly.style.transform=kb[n].transform; }
    if(fly.dataset.legs){ const sh=st.querySelector(".hl3sh");   // v2.0.j:送球(低い弧)
      fly.dataset.legs.split(";").forEach(sg=>{ const [x0,y0,x1,y1,t0,t1]=sg.split(",").map(Number), m=12, hh=Math.min(9,Math.hypot(x1-x0,y1-y0)/16), k1=[], k2=[];
        for(let i=0;i<=m;i++){ const u=i/m, x=x0+(x1-x0)*u, y=y0+(y1-y0)*u, z=3+4*hh*u*(1-u);
          k1.push({transform:`translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,${z.toFixed(1)}px) ${hl3Rot(c)}`, opacity:1});
          k2.push({transform:`translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0.2px)`, opacity:.45}); }
        try{ fly.animate(k1,{duration:Math.max(60,(t1-t0)*1000),delay:t0*1000,fill:"forwards"}); if(sh) sh.animate(k2,{duration:Math.max(60,(t1-t0)*1000),delay:t0*1000,fill:"forwards"}); }catch(e){} }); }
  }""")
rep("""    try{ el.animate(kf,{duration:n*per,delay:stt,fill:"forwards"}); if(b===4) el.animate([{opacity:1},{opacity:0}],{duration:250,delay:stt+n*per,fill:"forwards"}); }catch(e){}
    mvEnd=Math.max(mvEnd,stt+n*per+(b===4? 260 : 0));""","""    const oT= el.dataset.out? Number(el.dataset.out)*1000 : null;   // v2.0.j:アウトになった走者は、着いてしばらくして消える
    try{ el.animate(kf,{duration:n*per,delay:stt,fill:"forwards"}); if(b===4 && oT===null) el.animate([{opacity:1},{opacity:0}],{duration:250,delay:stt+n*per,fill:"forwards"});
      if(oT!==null) el.animate([{opacity:1},{opacity:0}],{duration:300,delay:oT+450,fill:"forwards"}); }catch(e){}
    mvEnd=Math.max(mvEnd,stt+n*per+(b===4? 260 : 0));""")

# ===== 観戦の 2.5D の道 =====
rep("""    const trg= tr || hl3Grounder(ev,seed), cam=hl3CamFor(ev,trg), c=HL3_CAMS[cam], moved=new Set((ev.mv||[]).map(([a])=>a));
    const trp=hl3ParkTr(trg), tr3= trp? Object.assign({},trp,{ey: ev.kind==="HR"? Math.max(trp.ey, 36-((hl3Park? hl3Park.R : HL_FR)-HL_FR)) : trp.ey}) : null;   // 本塁打はフェンスの少し向こうに落とす(外野席のカメラで枠の外に出ないように)""",
"""    const trg= tr || hl3Grounder(ev,seed), cam=hl3CamFor(ev,trg), c=HL3_CAMS[cam];
    const trp=hl3ParkTr(trg), tr3= trp? Object.assign({},trp,{ey: ev.kind==="HR"? Math.max(trp.ey, 36-((hl3Park? hl3Park.R : HL_FR)-HL_FR)) : trp.ey}) : null;   // 本塁打はフェンスの少し向こうに落とす(外野席のカメラで枠の外に出ないように)
    const fld= isPc? null : hl3Fielding(ev,tr3), moved=new Set([...(ev.mv||[]),...(fld? fld.mvOut : [])].map(([a])=>a));   // v2.0.j:送球・アウト
    if(fld && fld.end>re) re=fld.end;   // アウトの数・点数を変えるのは、最後のアウトのあと""")
rep("""    let bb=hl3Tags(ev,r,pn,c,{noBatter: moved.has(0) || isPc, skip:moved})+hl3Movers(ev,c,pn)+hl3Ball(ev,tr3,c);
    if(ev.kind==="pinch")""","""    let bb=hl3Tags(ev,r,pn,c,{noBatter: moved.has(0) || isPc, skip:moved})+hl3Movers(ev,c,pn,fld)+hl3Ball(ev,tr3,c,fld)+hl3OutMarks(fld,c);
    if(ev.kind==="pinch")""")
# re を後から延ばせるように(観戦のプレー。采配の re は別の関数の中)
rep("""  if(ev.kind==="BB") inner+=`<text class="f-text f-late" x="${HL_HX}" y="${HL_HY-66}" font-size="24" text-anchor="middle">${ev.hp? "死球" : "四球"}</text>`;
  const re=hlRunEnd(ev);""","""  if(ev.kind==="BB") inner+=`<text class="f-text f-late" x="${HL_HX}" y="${HL_HY-66}" font-size="24" text-anchor="middle">${ev.hp? "死球" : "四球"}</text>`;
  let re=hlRunEnd(ev);""")

# ===== じっくり采配の結果 =====
rep("""  const p=hl3MgPlay(d,pre), ev={fd:0, kind:p.kind, mv:p.mv, runs:p.runs, batter:d.batter, pitcher:d.pitcher, hp:d.hp, dp:!!d.dp};""",
    """  const p=hl3MgPlay(d,pre), ev={fd:0, kind:p.kind, mv:p.mv, runs:p.runs, batter:d.batter, pitcher:d.pitcher, hp:d.hp, dp:!!d.dp, pn:p.names, po:d.po, outs:d.outs};
  const bip= (p.kind==="OUT"||p.kind==="E") && typeof lastBIP!=="undefined" && lastBIP && lastBIP.pos? {type:lastBIP.type, pos:lastBIP.pos} : null;   // v2.0.j:v1 が直前に決めた打球(読むだけ)""")
rep("""  const tr= p.kind==="steal"? null : (hlTrajectory(ev,seed) || hl3Grounder(ev,seed));
  const cam=hl3CamFor(ev,tr), c=HL3_CAMS[cam], moved=new Set(p.mv.map(([a])=>a)), dest=new Set(p.mv.map(([,b])=>b));
  const trp=hl3ParkTr(tr), tr3= trp? Object.assign({},trp,{ey: ev.kind==="HR"? Math.max(trp.ey, 36-((hl3Park? hl3Park.R : HL_FR)-HL_FR)) : trp.ey}) : null;""",
"""  const tr= p.kind==="steal"? null : (hlTrajectory(ev,seed) || hl3Grounder(ev,seed,bip));
  const cam=hl3CamFor(ev,tr), c=HL3_CAMS[cam], dest=new Set(p.mv.map(([,b])=>b));
  const trp=hl3ParkTr(tr), tr3= trp? Object.assign({},trp,{ey: ev.kind==="HR"? Math.max(trp.ey, 36-((hl3Park? hl3Park.R : HL_FR)-HL_FR)) : trp.ey}) : null;
  const fld=hl3Fielding(ev,tr3), moved=new Set([...p.mv,...fld.mvOut].map(([a])=>a));   // v2.0.j:送球・アウト""")
rep("""  let bb=hl3Tags(ev,rLike,stay,c,{noBatter: moved.has(0) || p.kind==="steal" || ev.kind==="HR"})+hl3Movers(ev,c,p.names)+hl3Ball(ev,tr3,c);""",
    """  let bb=hl3Tags(ev,rLike,stay,c,{noBatter: moved.has(0) || p.kind==="steal" || ev.kind==="HR"})+hl3Movers(ev,c,p.names,fld)+hl3Ball(ev,tr3,c,fld)+hl3OutMarks(fld,c);""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
