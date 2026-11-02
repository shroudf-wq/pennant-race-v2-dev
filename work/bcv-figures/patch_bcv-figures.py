# 打席の画面(bcv。AI の絵がオフのときの SVG の図)の打者と投手を、部品で描いた人物に替える(試作)。
# 使い方: python3 patch_bcv-figures.py 元(v2.2.l).html 出力.html
#   変えるのは人物の絵と姿勢の切り替えだけ。球の軌道・速さ・ゾーン・印・1球の時間・セーブ・乱数は触らない。
#   打者:球団の色・ホーム/ビジター・胸の背番号・似顔(FACE)と同じ肌の色・構え3通り(能力から)。右打者は反転し、番号は反転しない。
#   投手:球団の色の帽子とユニフォーム・セット→脚上げ→リリースの3コマ(左投げは反転)。
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)

# 1) CSS:姿勢の切り替え(構え/スイング・投手の3コマ)
rep(".bcvBatter .bcvStick{stroke:#c99b5f;stroke-width:5;stroke-linecap:round;fill:none}\n",
    ".bcvBatter .bcvStick{stroke:#c99b5f;stroke-width:5;stroke-linecap:round;fill:none}\n"
    "/* bcv-figures:部品で描いた打者と投手。.bcfSw=スイング(#bcfBat に sw が付いたとき)・.bcfF0〜2=投手のコマ(#bcfPit の data-f) */\n"
    "#bcfBat .bcfSw{display:none} #bcfBat.sw .bcfSw{display:inline} #bcfBat.sw .bcfSt{display:none}\n"
    "#bcfPit .bcfF{display:none} #bcfPit[data-f=\"0\"] .bcfF0,#bcfPit[data-f=\"1\"] .bcfF1,#bcfPit[data-f=\"2\"] .bcfF2{display:inline}\n"
    ".bcfNum{font-family:\"Arial Narrow\",\"Roboto Condensed\",Arial,sans-serif;font-weight:800;text-anchor:middle}\n")

# 2) 部品(bcvMarksHtml の前)
PART = r'''/* ===== bcv-figures:打席の画面の人物を部品で描く(試作。AI の絵がオフ・未読込のときの SVG の図だけ) =====
   打者:左打者の向き(図の右に立ち、左=本塁・投手を向く)で描き、右打者は translate(300,0) scale(-1,1) で反転。番号は反転の外に置く(鏡文字にしない)。
     胸がこちら(本塁)を向く形(ユーザーが出した横からの絵)。構えは3通り:std ふつう/kan 神主ふう/nek 寝かせ(bcfStance。能力から。乱数なし)。
     色:ヘルメット=球団の色。ホームは白、ビジターは球団の色(球団名のハッシュで4つに1つ・明るい色の球団は灰色)。肌は似顔(FACE)の seed と同じ決め方。
   投手:捕手から見て正面。右投げは図の左の手で投げる(左投げは反転)。セット(0)→脚上げ(1)→リリース(2)。リリースの手は bcvStart と同じ (150∓7,110)。
   ゲームの乱数・Math.random は使わない。セーブにも何も足さない。 */
const BCF_OUT="#16231c";
const BCF_POSE={
  std:{S1:[211,129],S2:[237,131],N:[220,120],hd:[219,110],H:[225,129],K:[223,137],T:[253,82],E1:[208,140],E2:[240,144],BL:[219,157],BR:[241,158],F:[[221,160],[205,185],[214,214]],B:[[238,162],[228,189],[236,221]]},
  kan:{S1:[212,129],S2:[237,131],N:[221,120],hd:[220,109],H:[213,139],K:[214,147],T:[203,84],E1:[206,147],E2:[232,148],BL:[220,157],BR:[241,158],F:[[222,160],[215,186],[216,215]],B:[[238,162],[236,189],[236,221]]},
  nek:{S1:[211,133],S2:[237,135],N:[220,124],hd:[220,114],H:[232,127],K:[228,133],T:[273,111],E1:[214,141],E2:[248,128],BL:[219,160],BR:[241,161],F:[[221,163],[202,187],[209,215]],B:[[239,165],[241,190],[243,221]]},
  swing:{S1:[213,128],S2:[235,130],N:[222,118],hd:[219,110],H:[204,146],K:[204,146],T:[152,150],E1:[207,137],E2:[227,148],BL:[217,157],BR:[238,158],F:[[219,159],[212,185],[209,213]],B:[[236,161],[229,190],[236,220]]}
};
/* 構え(案A):長打が得意=寝かせ・ミートが得意=神主ふう・ほか=ふつう */
function bcfStance(p){ try{ if(!p) return "std"; const m=+p.meet||0, w=+p.power||0;
  if(w>=75 && w>=m+5) return "nek"; if(m>=75 && m>=w+5) return "kan"; return "std"; }catch(e){ return "std"; } }
/* 肌:FACE の draw(seed) の最初の値(sk)と同じ数列(FACE.hash → mulberry32)。SKIN の明るいほうの色 */
const BCF_SKIN=["#f7dcc0","#f0c9a3","#e8b991","#d9a073","#b77c52"];
function bcfSkin(p){ try{ const seed=(p && (p.faceSeed||p.name))||""; if(!seed || typeof FACE==="undefined" || !FACE.hash) return "#e8bb93";
  let a=FACE.hash(seed)|0; a=a+0x6D2B79F5|0; let t=Math.imul(a^a>>>15,1|a); t=t+Math.imul(t^t>>>7,61|t)^t; const sk=((t^t>>>14)>>>0)/4294967296;
  return BCF_SKIN[sk<.3?0:sk<.6?1:sk<.82?2:sk<.95?3:4]; }catch(e){ return "#e8bb93"; } }
function bcfHex(c){ c=String(c||"").trim(); if(/^#[0-9a-f]{3}$/i.test(c)) c="#"+c.slice(1).split("").map(x=>x+x).join(""); return /^#[0-9a-f]{6}$/i.test(c)? c.toLowerCase() : "#5a6670"; }
function bcfLum(c){ const n=parseInt(bcfHex(c).slice(1),16), f=v=>{ v/=255; return v<=.03928? v/12.92 : Math.pow((v+.055)/1.055,2.4); }; return .2126*f(n>>16&255)+.7152*f(n>>8&255)+.0722*f(n&255); }
/* ユニフォームの色。t=球団・home=ホームか */
function bcfUni(t,home){
  let c="#5a6670"; try{ c=bcfHex((typeof teamColorMap!=="undefined" && t && teamColorMap[t.name]) || (t && t.color)); }catch(e){}
  if(home) return {team:c, jer:"#f4f2ec", under:c, pants:"#ecebe4", num:c, glove:c};
  let gray=bcfLum(c)>.45; try{ if(t && t.name && typeof forteHash==="function" && ((forteHash(String(t.name)+"ビジター")>>>3)%4)===0) gray=true; }catch(e){}
  if(gray) return {team:c, jer:"#a9aeb3", under:c, pants:"#b4b8bc", num:c, glove:c};
  return {team:c, jer:c, under:"#2b2f33", pants:"#d9dcde", num:bcfLum(c)>.3? "#1d2228" : "#f4f2ec", glove:"#f4f2ec"};
}
function bcfLimb(pts,w,col){ const d="M"+pts.map(p=>p.join(",")).join(" L");
  return `<path d="${d}" fill="none" stroke="${BCF_OUT}" stroke-width="${w+1.6}" stroke-linecap="round" stroke-linejoin="round"/><path d="${d}" fill="none" stroke="${col}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`; }
function bcfBatStick(x1,y1,x2,y2){ const dx=x2-x1, dy=y2-y1, l=Math.hypot(dx,dy)||1, nx=-dy/l, ny=dx/l;
  const p=(t,w)=>[x1+dx*t+nx*w, y1+dy*t+ny*w], q=(t,w)=>[x1+dx*t-nx*w, y1+dy*t-ny*w];
  const a=[p(0,1.1),p(.45,1.3),p(.8,2.6),p(1,2.7),q(1,2.7),q(.8,2.6),q(.45,1.3),q(0,1.1)];
  return `<polygon points="${a.map(v=>v[0].toFixed(1)+","+v[1].toFixed(1)).join(" ")}" fill="#d2a46a" stroke="#6b4a24" stroke-width=".7" stroke-linejoin="round"/><circle cx="${x1}" cy="${y1}" r="1.6" fill="#6b4a24"/>`; }
/* 打者1つの姿勢(左打者の向き)。返す num は胸の番号の位置 */
function bcfBatterFig(u,skin,pose){
  const P=BCF_POSE[pose]||BCF_POSE.std, sw=pose==="swing", shade="rgba(20,30,25,.16)", O=BCF_OUT;
  const {S1,S2,N,H,K,T,E1,E2,BL,BR,F,B}=P, hx=P.hd[0], hy=P.hd[1];
  let g=`<ellipse cx="225" cy="225" rx="26" ry="3.4" fill="rgba(0,0,0,.25)"/>`;
  const shin=(L,w)=>bcfLimb([L[1].map((v,i)=>v+(L[2][i]-v)*.45),L[2]],w,u.under);
  const shoe=A=>`<path d="M${A[0]+4},${A[1]+1.5} l-12,.6 q-2.4,-4.4 2,-5.2 l10,0 z" fill="#15181b" stroke="${O}" stroke-width=".6"/>`;
  const toe=A=>`<path d="M${A[0]+2},${A[1]+1} l-9,-1.5 q-1,-4 3,-4.4 l7,2 z" fill="#15181b" stroke="${O}" stroke-width=".6"/>`;
  g+=bcfLimb(F,9,u.pants)+shin(F,7.4)+shoe(F[2]);
  g+=bcfLimb(B,10,u.pants)+shin(B,8)+(sw? toe(B[2]) : shoe(B[2]));
  g+=`<path d="M${B[0][0]+4},${B[0][1]+2} L${B[1][0]+4},${B[1][1]} L${B[2][0]+3},${B[2][1]-6}" fill="none" stroke="${shade}" stroke-width="3"/>`;
  const arm=(S,E,Hh)=>bcfLimb([S,E],6.4,u.jer)+bcfLimb([E,Hh],4.6,u.under);
  const mt=[(S1[0]+S2[0])/2,Math.min(S1[1],S2[1])-4];
  g+=`<path d="M${S1} Q${mt} ${S2} L${S2[0]+2},${S2[1]+12} Q${BR[0]+2},${BR[1]-8} ${BR} L${BL} Q${BL[0]-6},${BL[1]-14} ${S1[0]-1},${S1[1]+10} Z" fill="${u.jer}" stroke="${O}" stroke-width="1"/>`;
  g+=`<path d="M${S1[0]-1},${S1[1]+10} Q${BL[0]-6},${BL[1]-14} ${BL} L${BL[0]+4},${BL[1]} Q${BL[0]-1},${BL[1]-14} ${S1[0]+3},${S1[1]+6} Z" fill="${shade}"/>`;
  g+=`<path d="M${N[0]-4},${S1[1]-1} L${N[0]+1},${S1[1]+6} L${N[0]+5},${S2[1]-2} Z" fill="${u.under}" stroke="${O}" stroke-width=".6"/>`;
  g+=`<path d="M${N[0]+1},${S1[1]+6} L${BL[0]+(BR[0]-BL[0])*.4},${BL[1]}" stroke="rgba(20,30,25,.3)" stroke-width=".7"/>`;
  g+=`<path d="M${BL[0]},${BL[1]-2} L${BR[0]},${BR[1]-2} L${BR[0]},${BR[1]+2.2} L${BL[0]},${BL[1]+2.2} Z" fill="#24262a"/>`;
  g+=`<rect x="${hx-2}" y="${hy+7}" width="7" height="${N[1]-hy-4}" fill="${skin}" stroke="${O}" stroke-width=".7"/>`;
  g+=`<path d="M${hx-7},${hy} Q${hx-8},${hy+9} ${hx-3},${hy+11} Q${hx+4},${hy+12.5} ${hx+7},${hy+5}" fill="${skin}" stroke="${O}" stroke-width=".8"/>`;
  g+=`<path d="M${hx-7},${hy+2} l-2.2,2 l2.1,.8" fill="${skin}" stroke="${O}" stroke-width=".7" stroke-linejoin="round"/>`;
  g+= sw? `<path d="M${hx-6.2},${hy+1.6} l2.2,.5" stroke="#1a1a1a" stroke-width="1.1" stroke-linecap="round"/>` : `<path d="M${hx-6.4},${hy+0.6} l2.2,-.4" stroke="#1a1a1a" stroke-width="1.1" stroke-linecap="round"/>`;
  g+=`<path d="M${hx-5.5},${hy+7.5} q1.6,.8 3,0" fill="none" stroke="${O}" stroke-width=".6"/>`;
  g+=`<path d="M${hx-8},${hy+1} Q${hx-9},${hy-12} ${hx+2},${hy-13} Q${hx+13},${hy-12} ${hx+12},${hy+2} L${hx+11},${hy+9} Q${hx+5},${hy+12} ${hx+2},${hy+7} L${hx},${hy+1} Z" fill="${u.team}" stroke="${O}" stroke-width=".9"/>`;
  g+=`<path d="M${hx+2},${hy+7} Q${hx+1},${hy+2} ${hx+4},${hy} Q${hx+9},${hy} ${hx+11},${hy+3}" fill="none" stroke="rgba(0,0,0,.35)" stroke-width=".9"/>`;
  g+=`<path d="M${hx-7.5},${hy-1.5} L${hx-15},${hy+0.2} Q${hx-14},${hy+1.6} ${hx-7},${hy+1} Z" fill="${u.team}" stroke="${O}" stroke-width=".8" stroke-linejoin="round"/>`;
  g+=`<path d="M${hx-3},${hy-9} Q${hx+3},${hy-12} ${hx+8},${hy-8}" fill="none" stroke="rgba(255,255,255,.4)" stroke-width="1.4" stroke-linecap="round"/>`;
  g+=arm(S2,E2,[H[0]+2,H[1]+3])+bcfBatStick(K[0],K[1],T[0],T[1])+arm(S1,E1,H);
  g+=`<ellipse cx="${E1[0]}" cy="${E1[1]}" rx="3.3" ry="3" fill="#2b2f33" stroke="${O}" stroke-width=".6"/>`;
  g+=`<circle cx="${H[0]}" cy="${H[1]}" r="3.3" fill="${u.glove}" stroke="${O}" stroke-width=".7"/><circle cx="${H[0]+2}" cy="${H[1]+3}" r="3" fill="${u.glove}" stroke="${O}" stroke-width=".7"/>`;
  return {g, num:[BL[0]+(BR[0]-BL[0])*.72, BL[1]-6]};
}
/* いまの打席の打者・投手・球団(baCtx。hlRenderCount から)。分からないときは null */
function bcfCtx(){ try{ if(typeof baCtx==="undefined" || !baCtx || !baCtx.r || !baCtx.ev) return null; const {r,ev}=baCtx, top=ev.half==="表";
  return {B:bczPl(r,ev.batter), P:bczPl(r,ev.pitcher), bt: top? r.awayTeam : r.homeTeam, pt: top? r.homeTeam : r.awayTeam, bHome:!top}; }catch(e){ return null; } }
function bcfBatterSvg(det,c){
  const lefty= det && det.side===1, B=c && c.B, u=bcfUni(c && c.bt, c? c.bHome : true), skin=bcfSkin(B), st=bcfStance(B);
  const no=(B && B.no!=null && B.no!=="" && isFinite(+B.no))? String(Math.floor(+B.no)) : "";
  const one=(pose,cls)=>{ const f=bcfBatterFig(u,skin,pose), mx= lefty? f.num[0] : 300-f.num[0];
    const txt= no? `<text class="bcfNum" x="${mx.toFixed(1)}" y="${f.num[1]}" font-size="8" fill="${u.num}" stroke="${BCF_OUT}" stroke-width=".35">${no}</text>` : "";
    return `<g class="${cls}">`+(lefty? `<g>${f.g}</g>` : `<g transform="translate(300,0) scale(-1,1)">${f.g}</g>`)+txt+`</g>`; };
  return `<g id="bcfBat" class="bcfBatter" data-st="${st}">`+one(st,"bcfSt")+one("swing","bcfSw")+`</g>`;
}
/* 投手(3コマを重ねて持ち、data-f で1つだけ見せる)。線の太さは打者の 0.42 倍 */
function bcfPitcherSvg(det,c){
  const P=c && c.P, u=bcfUni(c && c.pt, c? !c.bHome : false), skin=bcfSkin(P), O=BCF_OUT, lp=!!(P && P.throws==="左");
  const L=(p,w,col)=>bcfLimb(p,w,col).replace(/stroke-width="([\d.]+)"/g,(m,v)=>`stroke-width="${(+v*.42).toFixed(2)}"`);
  const frame=f=>{ let g=""; const hy= f===2? 101.5 : 99.5, by= f===2? 105 : 103;
    if(f===0) g+=L([[148,113],[147,119],[147,125.5]],5,u.pants)+L([[152,113],[153,119],[153,125.5]],5,u.pants);
    if(f===1) g+=L([[148,113],[148,119],[148,125.5]],5,u.pants)+L([[152,113],[156,109.5],[155,116]],5,u.pants);
    if(f===2) g+=L([[147.5,114],[144,120],[143,125.5]],5,u.pants)+L([[152.5,114],[158,119],[159,125.5]],5,u.pants);
    g+=`<ellipse cx="150" cy="126.2" rx="7" ry="1" fill="rgba(0,0,0,.25)"/>`;
    g+=`<path d="M145.5,${by} Q150,${by-1.6} 154.5,${by} L154,${by+10} Q150,${by+11.5} 146,${by+10} Z" fill="${u.jer}" stroke="${O}" stroke-width=".5"/>`;
    g+=`<rect x="146" y="${by+8.6}" width="8" height="1.3" fill="#2a2a2a"/>`;
    if(f===0) g+=L([[146,by+1.5],[146,by+5],[149,by+5.5]],2.6,u.jer)+L([[154,by+1.5],[154,by+5],[151,by+5.5]],2.6,u.jer)+`<circle cx="150.3" cy="${by+5.6}" r="1.9" fill="#4a3220"/>`;
    if(f===1) g+=L([[146,by+1.5],[146.5,by+3.5],[149,by+1]],2.6,u.jer)+L([[154,by+1.5],[154,by+3.5],[151,by+1]],2.6,u.jer)+`<circle cx="150.3" cy="${by+0.6}" r="1.9" fill="#4a3220"/>`;
    if(f===2) g+=L([[146,by+1.5],[143.5,by+3],[143,by+5]],2.6,u.jer)+`<circle cx="143" cy="${by+5}" r="1.1" fill="${skin}"/>`+L([[154,by+1.5],[156.5,by+4],[155,by+7]],2.6,u.jer)+`<circle cx="155" cy="${by+7}" r="1.9" fill="#4a3220"/>`;
    g+=`<circle cx="150" cy="${hy}" r="3.1" fill="${skin}" stroke="${O}" stroke-width=".45"/>`;
    g+=`<path d="M146.8,${hy-0.6} Q147,${hy-4.4} 150,${hy-4.4} Q153,${hy-4.4} 153.2,${hy-0.6} Z" fill="${u.team}" stroke="${O}" stroke-width=".4"/><path d="M146.5,${hy-0.5} L153.5,${hy-0.5} L152.5,${hy+0.7} L147.5,${hy+0.7} Z" fill="${u.team}" stroke="${O}" stroke-width=".35"/>`;
    return `<g class="bcfF bcfF${f}">${g}</g>`; };
  return `<g id="bcfPit" class="bcfPitcher" data-f="0"${lp? ` transform="translate(300,0) scale(-1,1)"` : ""}>`+frame(0)+frame(1)+frame(2)+`</g>`;
}
function bcfPf(f){ try{ const g=document.getElementById("bcfPit"); if(g) g.setAttribute("data-f",String(f)); }catch(e){} }
'''
rep("function bcvMarksHtml(det,upto){", PART + "function bcvMarksHtml(det,upto){")

# 3) bcvSceneHtml:人形の打者と丸と四角の投手を、部品の人物に
rep('''  const batter=`<g class="bcvBatter"${lefty? "" : ` transform="translate(300,0) scale(-1,1)"`}><path d="M206,118 q14,-8 22,4 l4,28 q2,22 -4,44 l5,40 h-14 l-5,-36 l-6,36 h-14 l4,-44 q-6,-22 -2,-40 z"/>`+
    `<circle cx="216" cy="108" r="11"/><path class="bcvCap" d="M205,102 q11,-12 24,0 v4 h-24z"/><path id="bcvBat" class="bcvStick" d="M222,130 L250,84"/></g>`;''',
    '''  const bcfC=bcfCtx(), batter=bcfBatterSvg(det,bcfC);   /* bcv-figures:部品で描いた打者(前は1本の path の人形) */''')
rep('''    `<g class="bcvPitcher"><ellipse cx="150" cy="104" rx="4" ry="5"/><rect x="146" y="108" width="8" height="12" rx="2"/></g>`+''',
    '''    bcfPitcherSvg(det,bcfC)+''')

# 4) 姿勢の切り替え:投げる瞬間にリリース・少しあとでセット。振る球(空振り・ファウル・打った)は u≧0.85 でスイングに(前の「バットの線を替える」と同じとき)
#    脚上げは、1球を投げる 0.24 秒前(hlRenderCount の投げる時刻と同じ計算)。絵の打席(baArt)では何もしない
rep("let baOrigScene=null;\n",
    '''{ const o=bcvThrow; bcvThrow=function(det,k,dir,dur,then){
    try{ if(document.getElementById("bcfPit")){ bcfPf(2); hlLater(()=>bcfPf(0), Math.min(.4,dur*.8));
        const q=det && det.p[k-1];
        if(q && (q.t==="w" || q.t==="f" || q.t==="x")){ hlLater(()=>{ const b=document.getElementById("bcfBat"); if(b) b.classList.add("sw"); }, dur*.85);
          if(q.t!=="x") hlLater(()=>{ const b=document.getElementById("bcfBat"); if(b) b.classList.remove("sw"); }, dur+.04); } } }catch(e){}
    return o.apply(this,arguments); }; }
{ const o=hlRenderCount; hlRenderCount=function(r,ev,done){
    const res=o.apply(this,arguments);
    try{ if(document.getElementById("bcfPit")){ const bc=bcOfEv(ev); if(bc){ const s=HL_SPD[HLO.speed]||HL_SPD.normal, iv=BCV_IV[HLO.speed]||1.2, first=Math.max(.5,s.pre*.5), n=bc.seq.length-1;
        for(let k=1;k<=n+1;k++) hlLater(()=>bcfPf(1), Math.max(0,first+(k-1)*iv-.24)); } } }catch(e){}
    return res; }; }
let baOrigScene=null;
''')
open(dst, "w", encoding="utf-8").write(s)
print("ok", len(s.encode()))
