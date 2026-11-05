# v2.2.o:盗塁の場面の動き(2.5D と 3D が同じ台本 hl3PlayScript を読む)
#   ① 盗塁(成功・失敗とも)で、捕手の送球を捕るのは二塁は遊撃手・三塁は三塁手(これまでは「打球にいちばん近い外野手」で中堅手が走ってきていた)
#   ② 盗塁で刺されても、走者は次の塁まで走り、送球が着いた直後にアウト(これまでは元の塁に立ったまま消えていた)。じっくり采配の盗塁の結果も同じ
#   ③ 盗塁の走者は投球と同時(0 秒)に走り出す(これまでは 0.9 秒=送球が着いてから)。成功は 0.85 秒で着く(送球 0.9 秒より先=セーフ)、失敗は 0.96 秒
#   使い方:python3 patch_v22o.py <v2.2.n の本編> <出力>
#   変えるのは絵の部分だけ(hl3Fielding・hl3PlayScript・hl3Chase0・hl3MgPlay・hl3MgResultStage)。記録の場面(ev)・試合の計算・乱数・セーブには触らない
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"見つかった数 {k}(1 のはず): {a[:90]!r}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.2.n"; const BASE_V1="v1.8.c";','const APP_VERSION="v2.2.o"; const BASE_V1="v1.8.c";')
# ② 刺される走者(観戦の CS は一塁→二塁。采配は ev.cso=[[元の塁,行き先],…])
rep('''  } else if(k==="SH"){ tgt.push([0,1]); force=true; }''',
'''  } else if(k==="CS"||k==="steal"){   /* v2.2.o:盗塁で刺される。走者は次の塁まで走り、捕手の送球(ボール 0.9 秒)が着いた直後にアウト */
    (k==="CS"? [[1,2]] : (ev.cso||[])).forEach(([a,b])=>{ if(!bp[b] || b>3) return; const ra=.96; F.mvOut.push([a,b,ra]); F.marks.push({x:bp[b][0],y:bp[b][1],t:.9}); F.end=Math.max(F.end,ra+.3); });
    return F;
  } else if(k==="SH"){ tgt.push([0,1]); force=true; }''')
# ③ 盗塁の走者は投球と同時に走り出す
rep('''  const st= ev.kind==="HR"? 1.0 : .9, per= ev.kind==="HR"? .3 : HL_PER, names=o.names||[], nm=a=> a===0? ev.batter : names[a-1];''',
'''  const stl= /^(SB|CS|steal)$/.test(ev.kind), st= ev.kind==="HR"? 1.0 : stl? 0 : .9, per= ev.kind==="HR"? .3 : stl? .85 : HL_PER, names=o.names||[], nm=a=> a===0? ev.batter : names[a-1];   /* v2.2.o:盗塁は投球と同時に走る */''')
# ① 送球を捕るのは塁に入る内野手
rep('''  if(k==="SH"||k==="FC"){   // v2.1.e:バント。''',
'''  if(k==="SB"||k==="CS"||k==="steal"){   /* v2.2.o:盗塁。二塁へは遊撃手、三塁へは三塁手が入って捕手の送球を捕る(外野手は動かない) */
    const b= k==="steal"? (((ev.cso||[])[0]||[0,2])[1]) : 2, f= b===3? "三" : b===2? "遊" : null; if(f) run(f,L,.86); return out; }
  if(k==="SH"||k==="FC"){   // v2.1.e:バント。''')
# ② じっくり采配の盗塁:刺された走者(打つ前にいて、後にいない)を cso に。送球の線を作る
rep('''    if(d.ok) for(let i=2;i>=0;i--){ if(!before[i]) continue; const j=after.indexOf(before[i]); if(j>i && !used.has(j)){ mv.push([i+1,j+1]); used.add(j); } }
    return {kind:"steal", mv, runs:0, names:before};''',
'''    if(d.ok) for(let i=2;i>=0;i--){ if(!before[i]) continue; const j=after.indexOf(before[i]); if(j>i && !used.has(j)){ mv.push([i+1,j+1]); used.add(j); } }
    const cso= d.ok? [] : [2,1,0].filter(i=> before[i] && i<2 && after.indexOf(before[i])<0).map(i=>[i+1,i+2]);   /* v2.2.o:刺された走者(本塁への盗塁は除く) */
    return {kind:"steal", mv, runs:0, names:before, cso};''')
rep('''const p=hl3MgPlay(d,pre), ev={fd:0, kind:p.kind, mv:p.mv,''',
'''const p=hl3MgPlay(d,pre), ev={fd:0, cso:p.cso, kind:p.kind, mv:p.mv,''')
rep('''  const tr= p.kind==="steal"? null : (hlTrajectory(ev,seed) || hl3Grounder(ev,seed,bip));''',
'''  const cs0=(p.cso||[])[0], csP= cs0? (cs0[1]===2? hlPt(90,86) : hlPt(135,60)) : null;   /* v2.2.o:刺される盗塁は捕手の送球(低い線。カメラは動かさない) */
  const tr= p.kind==="steal"? (csP? {ex:csP[0], ey:csP[1], ang: cs0[1]===2? 90 : 135, h:8, near:true} : null) : (hlTrajectory(ev,seed) || hl3Grounder(ev,seed,bip));''')
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
