# v2.0.e のソースに当てると v2.0.f(球場の個性を 2.5D の絵に出す)。python3 patch_v20f.py src.html new.html
# 見た目だけ。試合の計算・記録・セーブ・2D の図(v1 の hlFieldSvg)には触らない。
#   ・広さ:狭い/標準/広い でフェンスの距離を変える(半径 164/182/200。打球の落ち方も同じ割合で伸び縮み)
#   ・人工芝:芝を刈り目のない一色にし、内野は塁・本塁・マウンドの周りだけ土を切り抜く
#   ・屋根つき(人工芝の約半分。v1.2.k の rainDome):フェンスの外にドームの縁を描き、観客席を暗く
# 球場のデータ(球団の park)は、リーグ作成で「球場の個性:あり」を選び、試合の計算が書き込んだものだけを読む。
# parkOf() は呼ぶと球団に park を書き込むので、絵からは呼ばない(セーブに項目を足さない:決め事3)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.0.e"; const BASE_V1="v1.2.k";','const APP_VERSION="v2.0.f"; const BASE_V1="v1.2.k";')

# ===== CSS:人工芝・屋根つき(手書きスコアボードが基本。ほかのスタイルは形だけ変わり、色はそのスタイルのまま) =====
rep(".hl3.hl3flat .hl3shade{display:none}", r""".hl3.hl3flat .hl3shade{display:none}
/* v2.0.f:球場の個性(2.5D の地面だけ)。.pkTurf=人工芝、.pkDome=屋根つき */
[data-base=board] .hl3world svg.pkTurf .f-grass,[data-base=board] .hl3world svg.pkTurf .f-ring,[data-base=board] .hl3world svg.pkTurf .f-ring2,[data-base=board] .hl3world svg.pkTurf .f-igrass{fill:#2e8b57}
[data-base=board] .hl3world svg.pkTurf .f-track{stroke:#2a7a4d}
.hl3world .f-cut{fill:#b98552}
[data-style=led] .hl3world .f-cut{fill:rgba(255,171,46,.07);stroke:var(--led);stroke-width:.8}
[data-style=scorebook] .hl3world .f-cut,[data-style=note] .hl3world .f-cut{fill:#f1e8d6;stroke:#34383e;stroke-width:.8}
.hl3world .f-roof{fill:none;stroke:#8a929c;stroke-width:7;opacity:.9}
.hl3world .f-roof2{fill:none;stroke:#c3c9d1;stroke-width:1.2;opacity:.8}
[data-base=board] .hl3world svg.pkDome .f-stands{fill:#151a20}
.hlStage.hl3.pkDome{--hl3bg:#11161b}
[data-style=led] .hl3world .f-roof{stroke:var(--led);stroke-width:2;opacity:.6}
[data-style=led] .hl3world .f-roof2{display:none}""")

# ===== 球場の図(2.5D 用。v1 の hlFieldSvg を写して、半径・芝・屋根を変えられるようにしたもの) =====
rep("""let hl3RO=null;""",r"""// v2.0.f:いまの観戦・采配の球場。null=いつもの図(個性なしのリーグ・データのない球団)
let hl3Park=null;
const HL3_PARK_R=[164,182,200];   // 狭い・標準・広い のフェンスの半径(標準は HL_FR と同じ。枠に収まる範囲で差が見えるように)
function hl3ParkFor(homeName){
  if(typeof parkEnabled==="undefined" || !parkEnabled || !homeName) return null;
  const t=(typeof allTeamsEverywhere==="function"? allTeamsEverywhere() : []).find(x=>x && x.name===homeName);
  if(!t || !t.park) return null;   // 試合の計算が書き込んだものだけを読む(parkOf は呼ばない)
  const s=(t.park.s===0||t.park.s===2)? t.park.s : 1, turf=!!t.park.turf;
  const dome= turf && ((forteHash(String(t.name)+"屋根")>>>3)%2)===0;   // v1.2.k の rainDome と同じ決め方(parkOf を通さない)
  return {s, R:HL3_PARK_R[s], turf, dome};
}
function hl3FieldSvg(inner,label,pk){
  if(!pk) return hlFieldSvg(inner,label);
  const FR=pk.R, cid="hlFieldClip"+(++hlClipSeq), f=n=>n.toFixed(1);
  const L=hlPt(135,FR), R=hlPt(45,FR);
  const sector=`M${HL_HX},${HL_HY} L${f(R[0])},${f(R[1])} A${FR},${FR} 0 0 0 ${f(L[0])},${f(L[1])} Z`;
  let rings=""; for(let r=FR,k=0;r>40;r-=16,k++) rings+=`<circle cx="${HL_HX}" cy="${HL_HY}" r="${r}" class="${k%2?'f-ring2':'f-ring'}"/>`;
  const tR=FR-5, tL=hlPt(135,tR), tRt=hlPt(45,tR);
  const dR=100, dL=hlPt(135,dR), dRt=hlPt(45,dR);
  const b1=hlPt(45,64), b2=hlPt(90,90.5), b3=hlPt(135,64);
  const g1=hlPt(45,50), g2=hlPt(90,71), g3=hlPt(135,50);
  const base=([x,y])=>`<rect class="f-base" x="${f(x-3.5)}" y="${f(y-3.5)}" width="7" height="7" transform="rotate(45 ${f(x)} ${f(y)})"/>`;
  // 人工芝:内野も芝にして、塁・本塁・マウンドの周りだけ土を切り抜く。天然芝:いつもの土の扇
  const dirt= pk.turf? [b1,b2,b3].map(([x,y])=>`<circle class="f-cut" cx="${f(x)}" cy="${f(y)}" r="8"/>`).join("")+`<circle class="f-cut" cx="${HL_HX}" cy="${HL_HY}" r="12"/><circle class="f-cut" cx="${HL_HX}" cy="${HL_HY-45}" r="9"/>`
    : `<path class="f-dirt" d="M${HL_HX},${HL_HY} L${f(dRt[0])},${f(dRt[1])} A${dR},${dR} 0 0 0 ${f(dL[0])},${f(dL[1])} Z"/><polygon class="f-igrass" points="${HL_HX},${HL_HY-14} ${f(g1[0])},${f(g1[1])} ${f(g2[0])},${f(g2[1])} ${f(g3[0])},${f(g3[1])}"/>`;
  // 屋根つき:フェンスの外にドームの縁(2本の弧)
  const roof= pk.dome? (()=>{ const r1=FR+14, r2=FR+19, a=hlPt(150,r1), b=hlPt(30,r1), c2=hlPt(150,r2), d2=hlPt(30,r2);
      return `<path class="f-roof" d="M${f(b[0])},${f(b[1])} A${r1},${r1} 0 0 0 ${f(a[0])},${f(a[1])}"/><path class="f-roof2" d="M${f(d2[0])},${f(d2[1])} A${r2},${r2} 0 0 0 ${f(c2[0])},${f(c2[1])}"/>`; })() : "";
  return `<svg viewBox="0 0 300 230" preserveAspectRatio="xMidYMid meet" role="img" aria-label="${label||"グラウンド"}" class="${pk.turf? "pkTurf" : ""}${pk.dome? " pkDome" : ""}">
    <defs><clipPath id="${cid}"><path d="${sector}"/></clipPath></defs>
    <rect class="f-stands" x="0" y="0" width="300" height="230"/>
    ${roof}
    <path class="f-grass" d="${sector}"/>
    <g clip-path="url(#${cid})">${rings}</g>
    <path class="f-track" d="M${f(tRt[0])},${f(tRt[1])} A${tR},${tR} 0 0 0 ${f(tL[0])},${f(tL[1])}"/>
    <path class="f-fence" d="M${f(R[0])},${f(R[1])} A${FR},${FR} 0 0 0 ${f(L[0])},${f(L[1])}"/>
    ${dirt}
    <line class="f-line" x1="${HL_HX}" y1="${HL_HY}" x2="${f(L[0])}" y2="${f(L[1])}"/>
    <line class="f-line" x1="${HL_HX}" y1="${HL_HY}" x2="${f(R[0])}" y2="${f(R[1])}"/>
    <circle class="f-mound" cx="${HL_HX}" cy="${HL_HY-45}" r="7"/>
    ${base(b1)}${base(b2)}${base(b3)}
    <polygon class="f-base" points="${HL_HX-4},${HL_HY-4} ${HL_HX+4},${HL_HY-4} ${HL_HX+4},${HL_HY} ${HL_HX},${HL_HY+4} ${HL_HX-4},${HL_HY}"/>
    ${inner||""}
  </svg>`;
}
// 打球の落点を球場の広さに合わせて伸び縮みさせる(本塁を中心に半径の比で)
function hl3ParkTr(tr){ if(!tr || !hl3Park) return tr; const k=hl3Park.R/HL_FR; return Object.assign({},tr,{ex:HL_HX+(tr.ex-HL_HX)*k, ey:HL_HY+(tr.ey-HL_HY)*k}); }
let hl3RO=null;""")
rep("""${hlFieldSvg(ground,o.label)}""","""${hl3FieldSvg(ground,o.label,hl3Park)}""")
rep("""  return `<div class="hlStage hl3${c.flip? " flip" : ""}${HL3D==="weak"? " hl3flat" : ""}" id="${id}\"""",
    """  return `<div class="hlStage hl3${c.flip? " flip" : ""}${HL3D==="weak"? " hl3flat" : ""}${hl3Park&&hl3Park.dome? " pkDome" : ""}" id="${id}\"""")
# 観戦を開いたときに球場を決める(その試合の本拠地)
rep("""  stopHlAuto(); hlClearTimers(); hlShown={a:0,h:0}; hlStageName=""; hl3Cam="B";""",
    """  stopHlAuto(); hlClearTimers(); hlShown={a:0,h:0}; hlStageName=""; hl3Cam="B"; hl3Park=hl3ParkFor(r && r.homeTeam && r.homeTeam.name);""")
# 打球の落点:本塁打はフェンスの少し向こう。外野席のカメラで枠の外に出ないよう、広い球場ほど少し内側で止める
rep("""    const tr3= tr? Object.assign({},tr,{ey: ev.kind==="HR"? Math.max(tr.ey,36) : tr.ey}) : null;""",
    """    const trp=hl3ParkTr(tr), tr3= trp? Object.assign({},trp,{ey: ev.kind==="HR"? Math.max(trp.ey, 36-((hl3Park? hl3Park.R : HL_FR)-HL_FR)) : trp.ey}) : null;""")
# 采配:その試合の本拠地
rep("""  if(hl3Active()){ const cam= HL3D==="weak"? "D" : "B"; box.querySelector("#mgField").innerHTML=hl3StageHtml("mgStage\"""",
    """  if(hl3Active()){ const cam= HL3D==="weak"? "D" : "B"; hl3Park=hl3ParkFor(d.home); box.querySelector("#mgField").innerHTML=hl3StageHtml("mgStage\"""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
