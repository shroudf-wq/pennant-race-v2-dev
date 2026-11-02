# v2.0.a のソースに当てると v2.0.b(ハイライト観戦・じっくり采配の 2.5D。場面でカメラを切り替える)。python3 patch_v20b.py src.html new.html
# 触るのは「記録を読んで絵にする部分」だけ。試合の計算・乱数・セーブの形には触らない。
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.0.a"; const BASE_V1="v1.1.y";','const APP_VERSION="v2.0.b"; const BASE_V1="v1.1.y";')

# ===== ① CSS:2.5D の舞台(地面を1枚回し、札は立てる) =====
rep("</style>\n</head>", r"""/* ===== v2.0.b:2.5D の観戦(引き継ぎ書 4.1)=====
   .hl3cam に perspective、.hl3world(300×230 の地面)を rotateX/rotateZ で回す。札(.hl3bb)は地面の点に立て、カメラの逆回転で正面を向く。
   試合の記録は同じものを読む。変えているのはカメラの置き方だけ */
.hlStage.hl3{background:var(--hl3bg,#0f2418)}
.hl3cam{position:absolute;inset:0;perspective:var(--p,760px);perspective-origin:50% var(--po,50%)}
.hl3world{position:absolute;left:50%;top:50%;width:300px;height:230px;margin:-115px 0 0 -150px;transform-style:preserve-3d;transform-origin:50% 50%;
  transform:translate3d(var(--tx,0px),var(--ty,0px),0) scale(var(--s,1)) scale(var(--zoom,1)) rotateX(var(--rx,0deg)) rotateZ(var(--rz,0deg))}
.hl3world>svg{position:absolute;inset:0;width:300px;height:230px;display:block}
.hl3shade{position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,rgba(0,0,0,var(--far,.35)),rgba(0,0,0,0) 55%)}
.hl3.flip .hl3shade{background:linear-gradient(0deg,rgba(0,0,0,var(--far,.35)),rgba(0,0,0,0) 55%)}
.hl3.sw .hl3world,.hl3.sw .hl3bb{transition:transform .45s cubic-bezier(.4,0,.2,1)}
.hl3.sw .hl3cam{transition:perspective .45s}
.hl3cut{position:absolute;inset:0;background:#000;pointer-events:none;animation:hl3cut .5s linear both;z-index:4}
@keyframes hl3cut{0%{opacity:1}45%{opacity:1}100%{opacity:0}}
.hl3bb{position:absolute;left:0;top:0;transform-style:preserve-3d;transform-origin:50% 100%;will-change:transform}
.hl3cap{position:absolute;left:0;bottom:0;width:7px;height:12px;border-radius:4px;transform:translateX(-50%);background:var(--gold);border:1px solid #1d3a2b;box-shadow:0 1px 0 rgba(0,0,0,.4)}
.hl3cap.f{background:#e9e5da;width:6px;height:10px}
.hl3cap.b{background:#b3302b}
.hl3tag{position:absolute;left:0;bottom:12px;transform:translateX(-50%);white-space:nowrap;font-size:8.5px;font-weight:bold;font-family:"Zen Kaku Gothic New",sans-serif;padding:1px 4px;border-radius:2px;line-height:1.3;background:rgba(255,255,255,.92);color:#16231b;border:.6px solid rgba(20,30,24,.65)}
.hl3tag.bat{background:#b3302b;color:#fff;border-color:#7a1f18;bottom:14px}
.hl3tag.run{background:#f2c94c;color:#1c1606;border-color:#6b5310;bottom:14px}
.hl3ball{position:absolute;left:0;top:0;width:8px;height:8px;margin:-4px 0 0 -4px;border-radius:50%;background:#fff;border:.8px solid #333;box-shadow:0 0 6px 2px rgba(255,255,255,.55);opacity:0;will-change:transform}
.hl3sh{position:absolute;left:0;top:0;width:9px;height:5px;margin:-2.5px 0 0 -4.5px;border-radius:50%;background:rgba(0,0,0,.45);opacity:0;will-change:transform,opacity}
.hl3txt{position:absolute;left:0;bottom:0;transform:translateX(-50%);white-space:nowrap;font-family:var(--display);color:#fff;paint-order:stroke;-webkit-text-stroke:0;text-shadow:0 0 3px #1d3a2b,0 0 3px #1d3a2b,0 1px 0 #1d3a2b}
.hl3txt.runs{color:var(--gold)}
.hl3txt.late{opacity:0;animation:hlFade .35s ease-out .85s forwards}
[data-style=led] .hlStage.hl3{--hl3bg:#050605}
[data-style=led] .hl3cap{background:var(--ledGreen);border-color:#0a2;filter:drop-shadow(0 0 3px rgba(98,242,140,.9))}
[data-style=led] .hl3cap.f{background:#e9e5da;filter:none}
[data-style=led] .hl3txt{color:var(--led);text-shadow:0 0 4px rgba(255,160,40,.8)}
[data-style=scorebook] .hlStage.hl3,[data-style=note] .hlStage.hl3{--hl3bg:#eef3f4}
[data-style=yakyuban] .hlStage.hl3{--hl3bg:#2b2d31}
[data-style=yakyuban][data-palette=toyBoardBlue] .hlStage.hl3{--hl3bg:#1d3a66}
.hl3.hl3flat .hl3shade{display:none}
body.noAnim .hl3.sw .hl3world,body.noAnim .hl3.sw .hl3bb,body.noAnim .hl3.sw .hl3cam{transition:none}
body.noAnim .hl3cut{animation:none;opacity:0}
@media (prefers-reduced-motion:reduce){ .hl3.sw .hl3world,.hl3.sw .hl3bb,.hl3.sw .hl3cam{transition:none} .hl3cut{animation:none;opacity:0} }
</style>
</head>""")

# ===== ② 設定の欄:立体(なし/弱/あり) =====
rep("""        <select id="hlSpeedSel" onchange="setHlOpt('speed',this.value)">""","""        <select id="hl3dSel" onchange="setHl3d(this.value)">
          <option value="on">あり(場面でカメラを切り替える)</option>
          <option value="weak">弱(軽い傾きだけ)</option>
          <option value="off">なし(2D)</option>
        </select>
      </div>
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;min-height:44px">
        <span>自動の速さ:</span>
        <select id="hlSpeedSel" onchange="setHlOpt('speed',this.value)">""")
rep("""      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;min-height:44px">
        <span>自動の速さ:</span>
        <select id="hl3dSel\"""","""      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;min-height:44px">
        <span>立体:</span>
        <select id="hl3dSel\"""")
rep("""      <p class="small">「次へ」を押せば、つなぎや前置きの途中でもすぐ打つ場面に進みます。アニメーションをオフにすると、つなぎや前置きは出さず、結果だけを見せます。</p>""",
    """      <p class="small">「次へ」を押せば、つなぎや前置きの途中でもすぐ打つ場面に進みます。アニメーションをオフにすると、つなぎや前置きは出さず、結果だけを見せます(立体もオフになり、今までの平面の図になります)。</p>
      <p class="small">立体「あり」は、打席はバックネット裏、打球が飛んだら打球の方向(左=三塁側・右=一塁側)のスタンドから、本塁打は外野席からの画角に切り替えます。試合の結果は変わりません。</p>""")

# ===== ③ 描画:2.5D の層 =====
rep("""function hlStageHtml(inner,over){ return `<div class="hlStage" id="hlStage">${inner}${over||""}</div>`; }""",
r"""function hlStageHtml(inner,over){ return `<div class="hlStage" id="hlStage">${inner}${over||""}</div>`; }
/* ===== v2.0.b:2.5D の観戦(引き継ぎ書 4.1)=====
   設定 HL3D(端末ごと・localStorage pennantHl3d):on=場面でカメラを切り替える / weak=軽い傾き(D)だけ / off=今までの平面の図。
   アニメーションがオフのとき(animEnabled() が false)は off と同じ。試合の計算・記録・セーブには触らない(hl3Active() が false なら v1 と同じ道を通る) */
let HL3D="on"; try{ const v=localStorage.getItem("pennantHl3d"); if(v==="on"||v==="weak"||v==="off") HL3D=v; }catch(e){}
function setHl3d(v){ if(!(v==="on"||v==="weak"||v==="off")) return; HL3D=v; try{ localStorage.setItem("pennantHl3d",v); }catch(e){} hl3Sync(); }
function hl3Sync(){ const e=document.getElementById("hl3dSel"); if(e) e.value=HL3D; }
function hl3Active(){ return HL3D!=="off" && animEnabled(); }
// カメラ(試作 hl25d_layouts.html の値)。rx/rz は度、p は perspective、zoom は拡大、tx/ty は枠の中の位置、far は奥の暗さ
const HL3_CAMS={
  B:{name:"バックネット裏",p:560,po:55,rx:62,rz:0,zoom:1.5,tx:0,ty:-2,far:.45},
  E:{name:"三塁側",p:2000,po:50,rx:55,rz:-35,zoom:1.3,tx:0,ty:6,far:.25},
  G:{name:"一塁側",p:760,po:50,rx:56,rz:34,zoom:1.2,tx:14,ty:6,far:.35},
  C:{name:"外野席",p:760,po:50,rx:52,rz:180,zoom:1.3,tx:0,ty:-12,far:.4,flip:true},
  A:{name:"スタンド上段",p:760,po:50,rx:50,rz:0,zoom:1.42,tx:0,ty:-2,far:.35},
  D:{name:"軽い傾き",p:900,po:50,rx:32,rz:0,zoom:1.18,tx:0,ty:4,far:.2},
};
let hl3Cam="B";   // いまのカメラ(観戦の中で持ち越す。プレー前で B に戻る)
function hl3Rot(c){ return `rotateZ(${-c.rz}deg) rotateX(${-c.rx}deg)`; }
function hl3Vars(c){ return `--p:${c.p}px;--po:${c.po}%;--rx:${c.rx}deg;--rz:${c.rz}deg;--zoom:${c.zoom};--tx:${c.tx}px;--ty:${c.ty}px;--far:${c.far}`; }
// 打球の方向でカメラを選ぶ(引き継ぎ書 4.1):本塁打=C、左(角度 100° 以上)=E、右(80° 以下)=G、中=直前が E/G ならそのまま。打球がない場面は動かさない(C にいたら B へ)
function hl3CamFor(ev,tr){
  if(HL3D==="weak") return "D";
  if(ev.kind==="HR" && tr) return "C";
  if(!tr) return hl3Cam==="C"? "B" : hl3Cam;
  const ang=tr.ang;
  if(ang>=100) return "E"; if(ang<=80) return "G";
  return (hl3Cam==="E"||hl3Cam==="G")? hl3Cam : "G";
}
function hl3Bb(x,y,z,c,inner,cls){ return `<div class="hl3bb${cls? " "+cls : ""}" data-x="${x.toFixed(1)}" data-y="${y.toFixed(1)}" data-z="${(z||0).toFixed(1)}" style="transform:translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,${(z||0).toFixed(1)}px) ${hl3Rot(c)}">${inner}</div>`; }
// 野手・捕手・打者・走者の札(hlNames と同じ場所・同じ名前の出し方)。runners=塁にいる走者の名前(null=いない)。打者は mover に入っていれば出さない
function hl3Tags(ev,r,runners,c,opt){
  const defs=(r.log&&r.log.defs)||[], d=(ev.fd!==undefined && ev.fd!==null)? defs[ev.fd] : null, m=d&&(d.m||d), sur=n=>surnameOf(n), o=opt||{};
  let out="";
  if(m){
    Object.entries(HL_POS).forEach(([pos,[ang,dist]])=>{ const nm= pos==="投"? ev.pitcher : m[pos]; if(!nm) return; const [x,y]=hlPt(ang,dist); out+=hl3Bb(x,y,0,c,`<div class="hl3cap f"></div><div class="hl3tag">${sur(nm)}</div>`); });
    if(m["捕"]) out+=hl3Bb(HL_HX+22,HL_HY+8,0,c,`<div class="hl3cap f"></div><div class="hl3tag">${sur(m["捕"])}</div>`);
  }
  if(ev.batter && !o.noBatter) out+=hl3Bb(HL_HX-14,HL_HY-4,0,c,`<div class="hl3cap b"></div><div class="hl3tag bat">${sur(ev.batter)}</div>`,"hl3bat");
  const bp=HL_BP();
  [0,1,2].forEach(i=>{ if(!runners || !runners[i] || (o.skip && o.skip.has(i+1))) return; const [x,y]=bp[i+1]; out+=hl3Bb(x,y-6,0,c,`<div class="hl3cap"></div><div class="hl3tag run">${sur(runners[i])}</div>`); });
  return out;
}
// 打球:地面の線(本塁→落点)と高さ(結果の種類で決める)。乱数は hlTrajectory と同じ seed(演出用)
function hl3Ball(ev,tr,c){
  if(!tr) return "";
  const h= ev.kind==="HR"? 62 : ev.kind==="SF"? 52 : ev.kind==="2B"? 30 : ev.kind==="3B"? 22 : 14;
  return `<div class="hl3sh" data-fly="${tr.ex.toFixed(1)},${tr.ey.toFixed(1)},${h}"></div><div class="hl3ball" data-fly="${tr.ex.toFixed(1)},${tr.ey.toFixed(1)},${h}"></div>`;
}
// 走者の移動(hlMovingRunners と同じ時間・同じ塁の線)。名前は打つ前の走者 pn(0=打者)
function hl3Movers(ev,c,names){
  const bp=HL_BP(), st= ev.kind==="HR"? 1.0 : .9, per= ev.kind==="HR"? .3 : HL_PER, sur=n=>surnameOf(n);
  return (ev.mv||[]).map(([a,b])=>{ const nm= a===0? ev.batter : (names&&names[a-1]); const p=bp[a];
    const inner= a===0? `<div class="hl3cap b"></div>${nm? `<div class="hl3tag bat">${sur(nm)}</div>` : ""}` : `<div class="hl3cap"></div>${nm? `<div class="hl3tag run">${sur(nm)}</div>` : ""}`;
    return hl3Bb(p[0],p[1]-6,0,c,inner,"hl3mv").replace('class="hl3bb hl3mv"',`class="hl3bb hl3mv" data-mv="${a},${b}" data-st="${st}" data-per="${per}"`); }).join("");
}
function hl3Txt(x,y,size,cls,txt,c,style){ return hl3Bb(x,y,0,c,`<div class="hl3txt ${cls||""}" style="font-size:${size}px;${style||""}">${txt}</div>`); }
// 舞台の HTML。from=切り替えの始まりのカメラ(なめらかに回すとき)。cut=暗転で切る
function hl3StageHtml(id,camId,ground,bbs,over,opt){
  const c=HL3_CAMS[camId]||HL3_CAMS.B, o=opt||{}, start= o.from? HL3_CAMS[o.from] : c;
  return `<div class="hlStage hl3${c.flip? " flip" : ""}${HL3D==="weak"? " hl3flat" : ""}" id="${id}" data-cam="${o.from||camId}" data-to="${camId}" style="${hl3Vars(start)}"><div class="hl3cam"><div class="hl3world">${hlFieldSvg(ground,o.label)}<div class="hl3shade"></div>${bbs||""}</div></div>${o.cut? '<div class="hl3cut"></div>' : ""}${over||""}</div>`;
}
let hl3RO=null;
function hl3Fit(st){ if(!st || !st.isConnected) return; const w=st.clientWidth, h=st.clientHeight; if(!w||!h) return; st.style.setProperty("--s",Math.min(w/300,h/230).toFixed(3)); }
// 差し込んだあとに呼ぶ:枠に合わせて拡大し、カメラの切り替え(なめらか)とボール・走者の動きを始める
function hl3After(host){
  const st=host.querySelector(".hlStage.hl3"); if(!st) return;
  hl3Fit(st);
  try{ if(!hl3RO) hl3RO=new ResizeObserver(es=>es.forEach(e=>hl3Fit(e.target))); hl3RO.disconnect(); hl3RO.observe(st); }catch(e){}
  const to=st.dataset.to, from=st.dataset.cam, c=HL3_CAMS[to]||HL3_CAMS.B;
  const place=()=>{ st.querySelectorAll(".hl3bb").forEach(b=>{ b.style.transform=`translate3d(${b.dataset.x}px,${b.dataset.y}px,${b.dataset.z}px) ${hl3Rot(c)}`; }); };
  if(to!==from){ requestAnimationFrame(()=>{ if(!st.isConnected) return; st.classList.add("sw"); st.style.cssText+=";"+hl3Vars(c); st.dataset.cam=to; place(); setTimeout(()=>st.classList.remove("sw"),500); }); }
  hl3Cam=to;
  // ボール(本塁→落点の線の上を、高さぶん持ち上げて飛ぶ)
  const fly=st.querySelector(".hl3ball"); if(fly){
    const [ex,ey,h]=fly.dataset.fly.split(",").map(Number), sx=HL_HX, sy=HL_HY-6, n=24, kb=[], ks=[];
    for(let i=0;i<=n;i++){ const u=i/n, x=sx+(ex-sx)*u, y=sy+(ey-sy)*u, z=4*h*u*(1-u);
      kb.push({transform:`translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,${z.toFixed(1)}px) ${hl3Rot(c)}`, opacity:1});
      ks.push({transform:`translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0.2px)`, opacity:Math.max(.15,.55-z/120)}); }
    const dur= 900, ease="cubic-bezier(.2,.7,.35,1)";
    try{ fly.animate(kb,{duration:dur,easing:ease,fill:"forwards"}); const sh=st.querySelector(".hl3sh"); if(sh) sh.animate(ks,{duration:dur,easing:ease,fill:"forwards"}); }catch(e){ fly.style.opacity=1; fly.style.transform=kb[n].transform; }
  }
  // 走者(塁の線を滑る。時間は hlMovingRunners と同じ)
  const bp=HL_BP();
  st.querySelectorAll(".hl3mv").forEach(el=>{
    const [a,b]=el.dataset.mv.split(",").map(Number), stt=Number(el.dataset.st)*1000, per=Number(el.dataset.per)*1000, kf=[], n=b-a;
    for(let i=a;i<=b;i++) kf.push({transform:`translate3d(${bp[i][0].toFixed(1)}px,${(bp[i][1]-6).toFixed(1)}px,0px) ${hl3Rot(c)}`, offset:(i-a)/n, easing:"linear"});
    try{ el.animate(kf,{duration:n*per,delay:stt,fill:"forwards"}); if(b===4) el.animate([{opacity:1},{opacity:0}],{duration:250,delay:stt+n*per,fill:"forwards"}); }catch(e){}
  });
}
""")

# ===== ④ プレー前(B)を 2.5D で =====
rep("""  const over= (HLO.fx==="on" && ev.batter && !isPc)? hlCutin("l",ev.bn,ev.batter,`${hlBatTeam(r,ev)}${hlTodayText(ev)}`) : "";
  hlId("hlSvg").innerHTML=hlSitBarS(r,ev,isPc? (ev.outs||0) : po, pn, ev.before)+hlStageHtml(hlFieldSvg(inner,hlPreBanner(ev)),over);
  hlSetLine(r,ev,"before",false);
  hlSetBanner(hlPreBanner(ev),"pre");""",
"""  const over= (HLO.fx==="on" && ev.batter && !isPc)? hlCutin("l",ev.bn,ev.batter,`${hlBatTeam(r,ev)}${hlTodayText(ev)}`) : "";
  if(hl3Active()){   // v2.0.b:プレー前はバックネット裏(B)。直前の場面から 0.45 秒で回す
    const cam= HL3D==="weak"? "D" : "B", c=HL3_CAMS[cam];
    let g=""; if(ev.batter && !isPc) g+=`<circle class="batRing" cx="${HL_HX-14}" cy="${HL_HY-6}" r="6"/>`; if(isPc) g+=`<circle class="f-pulse" cx="${HL_HX}" cy="${HL_HY-45}" r="10"/>`;
    hlId("hlSvg").innerHTML=hlSitBarS(r,ev,isPc? (ev.outs||0) : po, pn, ev.before)+hl3StageHtml("hlStage",cam,g,hl3Tags(ev,r,pn,c),over,{from:(hl3Cam!==cam && hl3Cam!=="C")? hl3Cam : null, cut: hl3Cam==="C" && cam!=="C", label:hlPreBanner(ev)});
    hl3After(hlId("hlSvg"));
  } else
  hlId("hlSvg").innerHTML=hlSitBarS(r,ev,isPc? (ev.outs||0) : po, pn, ev.before)+hlStageHtml(hlFieldSvg(inner,hlPreBanner(ev)),over);
  hlSetLine(r,ev,"before",false);
  hlSetBanner(hlPreBanner(ev),"pre");""")

# ===== ⑤ プレー(打球の方向で E/G、本塁打は C)を 2.5D で =====
rep("""  inner+=hlNames(ev,r,{runners:null});
  hlId("hlSvg").innerHTML=hlSitBarS(r,ev,po,pn,ev.before)+hlStageHtml(hlFieldSvg(inner,hlBanner(ev)),over);
  { const bx=document.querySelector(".hlBox"); if(bx) bx.scrollTop=0; }""",
"""  inner+=hlNames(ev,r,{runners:null});
  if(hl3Active()){   // v2.0.b:2.5D。地面(軌跡・光・脈)は SVG のまま、ボール・走者・札・文字は立てる
    const cam=hl3CamFor(ev,tr), c=HL3_CAMS[cam], moved=new Set((ev.mv||[]).map(([a])=>a));
    const tr3= tr? Object.assign({},tr,{ey: ev.kind==="HR"? Math.max(tr.ey,36) : tr.ey}) : null;   // 本塁打はフェンスの少し向こうに落とす(外野席のカメラで枠の外に出ないように)
    let g=""; if(tr3) g+=`<path class="f-trail" pathLength="1" d="M${HL_HX},${HL_HY-6} L${tr3.ex.toFixed(1)},${tr3.ey.toFixed(1)}"/>`;
    if(ev.kind==="HR" && tr3) g+=hlBurst(tr3.ex,tr3.ey);
    if(isPc) g+=`<circle class="f-pulse" cx="${HL_HX}" cy="${HL_HY-45}" r="10"/>`;
    let bb=hl3Tags(ev,r,pn,c,{noBatter: moved.has(0) || isPc, skip:moved})+hl3Movers(ev,c,pn)+hl3Ball(ev,tr3,c);
    if(ev.kind==="pinch") bb+=hl3Txt(HL_HX,HL_HY-40,40,"late",ev.orig==="K"?"K":"OUT",c);
    if(isPc) bb+=hl3Txt(HL_HX,HL_HY-52,16,"",ev.to,c);
    if(ev.kind==="BB") bb+=hl3Txt(HL_HX,HL_HY-40,24,"late","四球",c);
    if(ev.runs>0) bb+=hl3Txt(HL_HX+26,HL_HY-2,20,"runs late",`+${ev.runs}`,c,`animation-delay:${re}s`);
    const smooth= hl3Cam!==cam && cam!=="C" && hl3Cam!=="C";
    hlId("hlSvg").innerHTML=hlSitBarS(r,ev,po,pn,ev.before)+hl3StageHtml("hlStage",cam,g,bb,over,{from: smooth? hl3Cam : null, cut: (cam==="C") !== (hl3Cam==="C"), label:hlBanner(ev)});
    hl3After(hlId("hlSvg"));
  } else
  hlId("hlSvg").innerHTML=hlSitBarS(r,ev,po,pn,ev.before)+hlStageHtml(hlFieldSvg(inner,hlBanner(ev)),over);
  { const bx=document.querySelector(".hlBox"); if(bx) bx.scrollTop=0; }""")
# hlTrajectory に角度を持たせる(カメラの向きを決めるため。描画だけ)
rep("""  return {d:`M${sx},${sy} Q${mx.toFixed(1)},${my.toFixed(1)} ${ex.toFixed(1)},${ey.toFixed(1)}`, ex, ey};
}""","""  return {d:`M${sx},${sy} Q${mx.toFixed(1)},${my.toFixed(1)} ${ex.toFixed(1)},${ey.toFixed(1)}`, ex, ey, ang};
}""")
# 観戦を開いたときはカメラを B に戻す
rep("""  stopHlAuto(); hlClearTimers(); hlShown={a:0,h:0}; hlStageName="";
  clearTimeout(hlHideTimer); document.getElementById("highlightOverlay").classList.remove("closing");""",
"""  stopHlAuto(); hlClearTimers(); hlShown={a:0,h:0}; hlStageName=""; hl3Cam="B";
  clearTimeout(hlHideTimer); document.getElementById("highlightOverlay").classList.remove("closing");""")

# ===== ⑥ じっくり采配:場面の図をバックネット裏(B)で(静止。演出の重ねは今までどおり #mgStage に足す) =====
rep("""  box.querySelector("#mgField").innerHTML=mgStageHtml(hlFieldSvg(hlNames(evLike,rLike), "采配の場面"));""",
"""  if(hl3Active()){ const cam= HL3D==="weak"? "D" : "B"; box.querySelector("#mgField").innerHTML=hl3StageHtml("mgStage",cam,"",hl3Tags(evLike,rLike,rnShow,HL3_CAMS[cam]),"",{label:"采配の場面"}); hl3Cam=cam; hl3After(box.querySelector("#mgField")); }
  else box.querySelector("#mgField").innerHTML=mgStageHtml(hlFieldSvg(hlNames(evLike,rLike), "采配の場面"));""")

# ===== ⑦ 設定の同期 =====
rep("hlOptSync(); bxSettingsSync();","hlOptSync(); hl3Sync(); bxSettingsSync();")

open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
