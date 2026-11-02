# v2.1.m のソースに当てると v2.1.n。python3 patch_v21n.py src.html new.html
# 試合画面の背景の球場の続き。見た目だけ(試合の計算・記録・セーブには触らない)。
#   ユーザーの「スコアボードの表示をオンオフできるようにすればいいのでは」:
#   背景が出ているとき、カードの右上に「ボードを隠す/ボードを出す」のボタン(.hl3sbBtn)。隠すとスコアボード(v1 の .matchup)と飾り(.hl3sb)が消えて球場が見える。
#   ボードの場所はあけたまま(visibility:hidden。下のボタンの位置は動かない)。ふつうの試合の表示(.mSide がある)のときだけボタンを出し、
#   それ以外(ドラフト・FA・ポストシーズンの終わりなど、ボードの中に操作がある画面)では必ず出す。隠した状態は覚えない(開き直すと出る)
import sys, json
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.m"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.n"; const BASE_V1="v1.4.b";')
rep(""".hl3sb{position:absolute;left:0;top:0;width:100%;height:100%;z-index:-1;pointer-events:none}""",
""".hl3sb{position:absolute;left:0;top:0;width:100%;height:100%;z-index:-1;pointer-events:none}
/* v2.1.n:スコアボードを隠すボタン */
.hl3sbBtn{position:absolute;top:14px;left:50%;transform:translateX(-50%);white-space:nowrap;z-index:2;display:none;align-items:center;gap:6px;min-height:34px;padding:4px 12px;border-radius:999px;border:1px solid rgba(255,255,255,.28);background:rgba(8,14,22,.66);color:#f3efe2;font-size:13px;font-weight:bold;cursor:pointer}
.hl3bgOn>.hl3sbBtn.can{display:inline-flex}
.hl3bgOn.hl3sbHide .matchup{visibility:hidden}
.hl3bgOn.hl3sbHide .hl3sb{display:none}""")
rep("""  if(card){ card.classList.remove("hl3bgCard","hl3bgOn"); const b=card.querySelector(":scope > .hl3dBg"); if(b) b.remove(); const d=card.querySelector(":scope > .hl3sb"); if(d) d.remove(); } }""",
"""  if(card){ card.classList.remove("hl3bgCard","hl3bgOn","hl3sbHide"); const b=card.querySelector(":scope > .hl3dBg"); if(b) b.remove(); const d=card.querySelector(":scope > .hl3sb"); if(d) d.remove(); const k=card.querySelector(":scope > .hl3sbBtn"); if(k) k.remove(); } }
// v2.1.n:スコアボードを隠す・出す(覚えない)
let hl3dSbHidden=false;
function hl3dSbBtnSync(card){ card=card||hl3dBgCard(); if(!card) return; const m=document.getElementById("matchup");
  let b=card.querySelector(":scope > .hl3sbBtn"); if(!b){ b=document.createElement("button"); b.type="button"; b.className="hl3sbBtn"; b.onclick=()=>{ hl3dSbHidden=!hl3dSbHidden; hl3dSbBtnSync(); hl3dBgKick(); }; card.appendChild(b); }
  const can= !!(m && m.querySelector(".mSide")), hide= can && hl3dSbHidden;
  b.classList.toggle("can",can); card.classList.toggle("hl3sbHide",hide);
  const t= hide? "ボードを出す" : "ボードを隠す"; if(b.dataset.t!==t){ b.dataset.t=t; b.textContent=(typeof tr==="function"? tr(t) : t); b.setAttribute("aria-pressed",hide? "true" : "false"); } }""")
rep("""  card.classList.add("hl3bgCard","hl3bgOn"); card.style.setProperty("--hl3bgFade",fade);""",
"""  card.classList.add("hl3bgCard","hl3bgOn"); card.style.setProperty("--hl3bgFade",fade); hl3dSbBtnSync(card);""")
EN={"ボードを隠す":"Hide board","ボードを出す":"Show board"}
rep('"説明": "Info", ','"説明": "Info", '+json.dumps(EN,ensure_ascii=False)[1:-1]+', ')
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
