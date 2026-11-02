# v2.0.g のソースに当てると v2.0.h(凡打・エラー・バントにも打球の線を出す。2.5D だけ)。python3 patch_v20h.py src.html new.html
# 見た目だけ。試合の計算・記録・セーブ・2D の図(v1 の hlTrajectory)には触らない。乱数は hlRand だけ。
#   ・凡打(OUT)・野選(FC):半分はゴロ(内野手へ低く)、半分はフライ(外野手へ高く)。併殺はいつもゴロ
#   ・エラー(E):内野手へのゴロが、少し後ろへ抜ける
#   ・送りバント(SH):本塁の前に転がるだけ。カメラは動かさない
#   ・カメラは打球の向きで(左=E、右=G)。観戦(見返し・引退の打席・エラーで得点)と、じっくり采配の結果の両方
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.0.g"; const BASE_V1="v1.2.k";','const APP_VERSION="v2.0.h"; const BASE_V1="v1.2.k";')

# ===== 打球の線(2.5D 用。hlTrajectory が線を返さない結果のとき) =====
rep("""// 打球:地面の線(本塁→落点)と高さ(結果の種類で決める)。乱数は hlTrajectory と同じ seed(演出用)
function hl3Ball(ev,tr,c){
  if(!tr) return "";
  const h= ev.kind==="HR"? 62 : ev.kind==="SF"? 52 : ev.kind==="2B"? 30 : ev.kind==="3B"? 22 : 14;""",
r"""// v2.0.h:凡打・野選・エラー・バントの打球(2.5D だけ。2D の hlTrajectory は v1 のまま)。返り値は hlTrajectory と同じ形+高さ h・near(カメラを動かさない)
function hl3Grounder(ev,seed){
  const k=ev.kind; if(!(k==="OUT"||k==="FC"||k==="E"||k==="SH")) return null;
  const r1=hlRand(seed+.37), r2=hlRand(seed+1.7);
  let ang,dist,h,near=false;
  if(k==="SH"){ ang=72+r1*36; dist=24+r2*10; h=3; near=true; }
  else if(k!=="E" && !ev.dp && r1<.5){ const of=[HL_POS.左,HL_POS.中,HL_POS.右][Math.floor(r2*3)%3]; ang=of[0]+(r2-.5)*14; dist=of[1]-6; h=46; }   // フライ
  else { const inf=[HL_POS.三,HL_POS.遊,HL_POS.二,HL_POS.一][Math.floor(r2*4)%4]; ang=inf[0]+(r1-.5)*10; dist=inf[1]-4+(k==="E"? 22 : 0); h=4; }   // ゴロ(エラーは野手の後ろへ抜ける)
  let [ex,ey]=hlPt(ang,dist); ey=Math.max(ey,5);
  return {d:`M${HL_HX},${HL_HY-6} L${ex.toFixed(1)},${ey.toFixed(1)}`, ex, ey, ang, h, near};
}
// 打球:地面の線(本塁→落点)と高さ(結果の種類で決める)。乱数は hlTrajectory と同じ seed(演出用)
function hl3Ball(ev,tr,c){
  if(!tr) return "";
  const h= (typeof tr.h==="number")? tr.h : ev.kind==="HR"? 62 : ev.kind==="SF"? 52 : ev.kind==="2B"? 30 : ev.kind==="3B"? 22 : 14;""")
# カメラ:バントは動かさない
rep("""  if(!tr) return hl3Cam==="C"? "B" : hl3Cam;
  const ang=tr.ang;""","""  if(!tr || tr.near) return hl3Cam==="C"? "B" : hl3Cam;
  const ang=tr.ang;""")
# 観戦の 2.5D の道:線のない結果はゴロ・フライの線を使う(2D の道の tr はそのまま)
rep("""    const cam=hl3CamFor(ev,tr), c=HL3_CAMS[cam], moved=new Set((ev.mv||[]).map(([a])=>a));
    const trp=hl3ParkTr(tr),""","""    const trg= tr || hl3Grounder(ev,seed), cam=hl3CamFor(ev,trg), c=HL3_CAMS[cam], moved=new Set((ev.mv||[]).map(([a])=>a));
    const trp=hl3ParkTr(trg),""")
# 采配の結果:同じ(併殺は d.dp)
rep("""  const p=hl3MgPlay(d,pre), ev={fd:0, kind:p.kind, mv:p.mv, runs:p.runs, batter:d.batter, pitcher:d.pitcher, hp:d.hp};""",
    """  const p=hl3MgPlay(d,pre), ev={fd:0, kind:p.kind, mv:p.mv, runs:p.runs, batter:d.batter, pitcher:d.pitcher, hp:d.hp, dp:!!d.dp};""")
rep("""  const tr= p.kind==="steal"? null : hlTrajectory(ev,seed);""","""  const tr= p.kind==="steal"? null : (hlTrajectory(ev,seed) || hl3Grounder(ev,seed));""")
# 球場の広さで落点を伸び縮みさせるのは安打・本塁打だけ(凡打は野手の札のところへ落とす。札は広さで動かないため)
rep("""function hl3ParkTr(tr){ if(!tr || !hl3Park) return tr;""","""function hl3ParkTr(tr){ if(!tr || !hl3Park || typeof tr.h==="number") return tr;""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
