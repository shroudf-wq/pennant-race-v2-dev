# v2.0.h のソースに当てると v2.0.i(狭い画面で、札がボールカウントの表示の下に入るのを減らす。2.5D だけ)。python3 patch_v20i.py src.html new.html
# 見た目だけ。試合の計算・記録・セーブ・2D の図とボールカウント(v1)には触らない。
#   ・2.5D の舞台の幅が 400px 未満のとき(.hl3n。hl3Fit で付ける):右端の投球の一覧を、最後の1球以外は番号の丸だけにする(色で ボール/ストライク/ファールが分かる)
#     → 一覧の幅が 約 50px から 約 20px になり、右翼側の札が隠れにくくなる
#   ・札の重なりをほどく処理の2回目(カード・ボールカウントの下の札を移す):探す範囲を横・下にも広げる
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.0.h"; const BASE_V1="v1.2.k";','const APP_VERSION="v2.0.i"; const BASE_V1="v1.2.k";')
rep("""@media (max-width:420px){ .bcList li{font-size:11px} .bcBSO{padding:4px 6px} }""",
    """@media (max-width:420px){ .bcList li{font-size:11px} .bcBSO{padding:4px 6px} }
/* v2.0.i:2.5D の舞台が狭いとき、投球の一覧は最後の1球だけ字を出し、ほかは番号の丸だけ */
.hlStage.hl3.hl3n .bcList li:not(.bcLast):not(.bcMore) .bcAb{display:none}
.hlStage.hl3.hl3n .bcList li:not(.bcLast){padding:1px;background:rgba(10,20,15,.6)}
.hlStage.hl3.hl3n .bcList{gap:1px}""")
rep("""function hl3Fit(st){ if(!st || !st.isConnected) return; const w=st.clientWidth, h=st.clientHeight; if(!w||!h) return; st.style.setProperty("--s",Math.min(w/300,h/230).toFixed(3)); }""",
    """function hl3Fit(st){ if(!st || !st.isConnected) return; const w=st.clientWidth, h=st.clientHeight; if(!w||!h) return; st.style.setProperty("--s",Math.min(w/300,h/230).toFixed(3)); st.classList.toggle("hl3n", w<400); }   // v2.0.i:狭い舞台(.hl3n)""")
# 2回目の探す範囲:1回目の候補に、横に 2.2 幅・下に 3 段まで足す(近い順は変えない)
rep("""  if(obs.length){ const hitObs=a=>obs.reduce((t,c)=>t+hit(a,c),0);
    items.forEach(o=>{ if(hitObs(o.a)<=.5) return; const {w,h}=o.r;
      for(const [dx,dy] of candsOf(o)){""","""  const candsWide=o=>{ const {w,h}=o.r, cs=[];   // v2.0.i:2回目は広く探す
    for(const dy of [0,-(h+gap),(h+gap),-2*(h+gap),2*(h+gap),3*(h+gap)]) for(const dx of [0,-(w*.55+gap),(w*.55+gap),-(w+gap),(w+gap),-(w*1.6+gap),(w*1.6+gap),-(w*2.2+gap)]) cs.push([dx,dy,Math.abs(dx)*.7+Math.abs(dy)+(dy>0? h : 0)]);
    return cs.sort((a,b)=>a[2]-b[2]); };
  if(obs.length){ const hitObs=a=>obs.reduce((t,c)=>t+hit(a,c),0);
    items.forEach(o=>{ if(hitObs(o.a)<=.5) return; const {w,h}=o.r;
      for(const [dx,dy] of candsWide(o)){""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
