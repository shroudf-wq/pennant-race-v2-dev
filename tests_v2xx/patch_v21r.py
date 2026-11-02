# v2.1.q のソースに当てると v2.1.r。python3 patch_v21r.py src.html new.html
# 見た目だけ(背景の観客席。乱数は使わない)。
#   ① ユーザーの「バックネット裏の人が途切れてるのはちょっと気になる」:お客さんの帯の絵の位置を、ひと切れごとに (u×L)/40 で決めていたので、
#      曲がった列(内野席など)では実際の長さとずれて、切れ目ごとに人が縦に切れていた。列ごとに実際の長さを足し合わせて続ける
#   ② ユーザーの「動きは入れてok」:観客の動き(タオル・ウェーブ・旗)を入れる。設定「観客の動き(タオル・ウェーブ・旗)」(端末ごと・pennantHl3dCrowd。初めはあり)。
#      変えたら背景を作り直す(動いた途中の形が残らないように)
import sys, json
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.q"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.r"; const BASE_V1="v1.4.b";')
# ① 列ごとに長さを足し合わせる
rep("""    const segU=24;""","""    const segU=24, cum=new Array(N).fill(0);   // v2.1.r:列ごとの、絵の続きの位置(実際の長さを足し合わせる)""")
rep("""          const len=Math.hypot(Bm[0]-Am[0],Bm[1]-Am[1]), ua=(a*L)/40, ub=ua+len/40;""",
"""          const len=Math.hypot(Bm[0]-Am[0],Bm[1]-Am[1]), ua=cum[i]/40, ub=ua+len/40; cum[i]+=len;""")
# ② 設定
rep("""let HL3D_BG_MOTION="off";   // 動きの見本:"towel" "wave" "flags" を空白区切りで(設定には出さない)""",
"""let HL3D_BG_MOTION="towel wave flags";   // v2.1.r:観客の動き("towel" "wave" "flags" を空白区切り。"off" で止める)。設定「観客の動き」(pennantHl3dCrowd)
try{ if(localStorage.getItem("pennantHl3dCrowd")==="off") HL3D_BG_MOTION="off"; }catch(e){}
function setHl3dCrowd(on){ HL3D_BG_MOTION= on? "towel wave flags" : "off"; try{ localStorage.setItem("pennantHl3dCrowd",on? "on" : "off"); }catch(e){} hl3Sync(); if(hl3dBgS) hl3dBgS.key+="*"; try{ hl3dBgSync(); }catch(e){} }""")
rep("""const b=document.getElementById("hl3dBgChk"); if(b) b.checked=HL3DBG; }""",
"""const b=document.getElementById("hl3dBgChk"); if(b) b.checked=HL3DBG; const c=document.getElementById("hl3dCrowdChk"); if(c) c.checked=(typeof HL3D_BG_MOTION==="undefined" || HL3D_BG_MOTION!=="off"); }""")
rep("""        <span>試合画面に 3D の球場を出す(立体が「3D」のとき)</span>
      </label>""","""        <span>試合画面に 3D の球場を出す(立体が「3D」のとき)</span>
      </label>
      <label style="display:flex;align-items:center;gap:10px;min-height:44px;cursor:pointer">
        <input type="checkbox" id="hl3dCrowdChk" onchange="setHl3dCrowd(this.checked)" style="width:22px;height:22px;accent-color:var(--gold)">
        <span>観客の動き(タオル・ウェーブ・旗)</span>
      </label>""")
EN={"試合画面に 3D の球場を出す(立体が「3D」のとき)":"Show the 3D ballpark on the game screen (when 3D is on)","観客の動き(タオル・ウェーブ・旗)":"Crowd motion (towels, wave, flags)"}
rep('"説明": "Info", ','"説明": "Info", '+json.dumps(EN,ensure_ascii=False)[1:-1]+', ')
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
