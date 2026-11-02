# v2.0.f のソースに当てると v2.0.g(じっくり采配の「結果」の場面も 2.5D で動かす)。python3 patch_v20g.py src.html new.html
# 見た目だけ。試合の計算・記録・セーブには触らない(乱数は hlRand だけ。Math.random は使わない)。
#   ・采配の結果(打席の結果)で、打球が飛び、走者が塁を回り、打球の向きでカメラが切り替わる(本塁打=C、左=E、右=G。三振・四球・凡打は B のまま)
#   ・打つ前の走者は、直前の采配の場面(mg.hl3Pre。采配中の試合の中だけで持つ。セーブには入らない)から取る
#   ・走者の動きは名前で合わせる(打つ前の塁 → 打った後の塁)。見つからない走者は、得点の数だけ本塁へ、残りはアウト(消える)
#   ・盗塁の結果:成功なら走者が1つ進む。失敗はそのまま
#   ・2D(立体なし・アニメーションなし)は v1 と同じ止まった図のまま
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.0.f"; const BASE_V1="v1.2.k";','const APP_VERSION="v2.0.g"; const BASE_V1="v1.2.k";')

# ===== 采配の結果の動き(打つ前の走者 → 打った後の走者 から mv を作る) =====
rep("""function renderManaged(){""",r"""// v2.0.g:采配の結果の場面の動き。pre=打つ前の塁の名前、d=結果。返すのは観戦の場面と同じ形(kind・mv・runs)
function hl3MgPlay(d,pre){
  const before=(pre||[null,null,null]).slice(0,3), after=(d.rn||[null,null,null]).slice(0,3), mv=[], used=new Set();
  if(d.from==="steal"){   // 盗塁:成功なら、いなくなった塁の走者が1つ先へ
    if(d.ok) for(let i=2;i>=0;i--){ if(!before[i]) continue; const j=after.indexOf(before[i]); if(j>i && !used.has(j)){ mv.push([i+1,j+1]); used.add(j); } }
    return {kind:"steal", mv, runs:0, names:before};
  }
  const res=d.res, hr= res==="HR";
  let left=d.scored||0;
  const bj= hr? -1 : after.indexOf(d.batter);   // 打者の行き先(本塁打は本塁)
  if(bj>=0) used.add(bj);
  const moved=[];   // [打つ前の塁, 行き先(0〜2 の塁 / 3=本塁 / -1=アウト・不明)]
  // 1回目:名前がそのまま見つかる走者
  for(let i=2;i>=0;i--){ if(!before[i]) continue; const j=after.indexOf(before[i]); if(j>=0 && j>=i && !used.has(j)){ used.add(j); moved[i]=j; } }
  // 2回目:見つからない走者(代走・延長の走者など)。先の走者から、得点 → 空いている先の塁 の順に
  for(let i=2;i>=0;i--){ if(!before[i] || moved[i]!==undefined) continue;
    if(hr || left>0){ moved[i]=3; left--; continue; }
    let j=-1; for(let k=i;k<3;k++) if(after[k] && !used.has(k) && !before.includes(after[k]) && after[k]!==d.batter){ j=k; break; }
    if(j>=0){ used.add(j); moved[i]=j; } else moved[i]=-1; }
  for(let i=0;i<3;i++){ const j=moved[i]; if(j===undefined || j<0 || j===i) continue; mv.push([i+1,j+1]); }
  if(hr) mv.push([0,4]); else if(bj>=0) mv.push([0,bj+1]);
  return {kind:res, mv, runs:d.scored||0, names:before};
}
function renderManaged(){""")

# 采配の場面(結果でない)を描くたびに、その時の塁を覚えておく(次の結果の「打つ前」になる)
rep("""  const evLike={fd:0, pitcher:d.pitcher, batter:d.batter, rn:rnShow}, rLike={log:{defs:d.def?[{m:d.def}]:[]}};
  if(hl3Active()){""","""  const evLike={fd:0, pitcher:d.pitcher, batter:d.batter, rn:rnShow}, rLike={log:{defs:d.def?[{m:d.def}]:[]}};
  const mgPre= mg.hl3Pre||null; if(d.kind!=="result") mg.hl3Pre=rnShow.slice(0,3);   // v2.0.g(描画だけで使う。セーブには入らない)
  if(hl3Active() && d.kind==="result" && mgPre){ hl3Park=hl3ParkFor(d.home); hl3MgResultStage(box,d,mgPre,evLike,rLike); }
  else if(hl3Active()){""")

rep("""function hl3MgPlay(d,pre){""",r"""// v2.0.g:采配の結果を 2.5D で動かす(観戦の hlRenderPlay の 2.5D の部分と同じ作り。名前のカードは出さない)
function hl3MgResultStage(box,d,pre,evLike,rLike){
  const p=hl3MgPlay(d,pre), ev={fd:0, kind:p.kind, mv:p.mv, runs:p.runs, batter:d.batter, pitcher:d.pitcher, hp:d.hp};
  const seed=d.inn*7+(d.half==="裏"? 3 : 0)+((typeof d.po==="number")? d.po : 0)*11+[...String(d.batter||"")].length;   // 演出用(hlRand。試合の乱数は使わない)
  const tr= p.kind==="steal"? null : hlTrajectory(ev,seed);
  const cam=hl3CamFor(ev,tr), c=HL3_CAMS[cam], moved=new Set(p.mv.map(([a])=>a)), dest=new Set(p.mv.map(([,b])=>b));
  const trp=hl3ParkTr(tr), tr3= trp? Object.assign({},trp,{ey: ev.kind==="HR"? Math.max(trp.ey, 36-((hl3Park? hl3Park.R : HL_FR)-HL_FR)) : trp.ey}) : null;
  let g=""; if(tr3) g+=`<path class="f-trail" pathLength="1" d="M${HL_HX},${HL_HY-6} L${tr3.ex.toFixed(1)},${tr3.ey.toFixed(1)}"/>`;
  if(ev.kind==="HR" && tr3) g+=hlBurst(tr3.ex,tr3.ey);
  // 止まっている走者:打った後の塁のうち、動いて着いた塁以外。動く走者は hl3Movers が打つ前の名前で出す
  const stay=(d.rn||[null,null,null]).map((n,i)=> dest.has(i+1)? null : n);
  let bb=hl3Tags(ev,rLike,stay,c,{noBatter: moved.has(0) || p.kind==="steal" || ev.kind==="HR"})+hl3Movers(ev,c,p.names)+hl3Ball(ev,tr3,c);
  if(ev.kind==="BB") bb+=hl3Txt(HL_HX,HL_HY-40,24,"late",ev.hp? "死球" : "四球",c);
  const re=hlRunEnd(ev);
  if(ev.runs>0) bb+=hl3Txt(HL_HX+26,HL_HY-2,20,"runs late",`+${ev.runs}`,c,`animation-delay:${re}s`);
  const smooth= hl3Cam!==cam && cam!=="C" && hl3Cam!=="C";
  box.querySelector("#mgField").innerHTML=hl3StageHtml("mgStage",cam,g,bb,"",{from: smooth? hl3Cam : null, cut: (cam==="C") !== (hl3Cam==="C"), label:"采配の結果"});
  hl3After(box.querySelector("#mgField"));
}
function hl3MgPlay(d,pre){""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
