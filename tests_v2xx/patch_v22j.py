# v2.2.i のソースに当てると v2.2.j。python3 patch_v22j.py src.html new.html
# 試合画面の背景:上下にドラッグ/スワイプで見上げ・見下ろし。外野手をフェンスの 75% に。背景だけ(計算・2.5D・観戦・セーブには触らない)。
#   ユーザーの「視点がボードの出し隠しで変わってるのが気になる」→「ドラッグかスワイプで上下に動かせたらいいかなと」、「センターがいないのが」→ A案(75%)
#   ① hl3dBgTilt(ラジアン。端末の中で覚える=ページを開き直すと 0。セーブ・localStorage には書かない)。hl3dBgDraw で、ボードとボタンの間に合わせる setViewOffset のあとに cam.rotateX(tilt)
#      (合わせる処理と喧嘩しないように、合わせたあとに回す)。+ で見上げる。範囲 −0.35〜+0.45 rad
#   ② hl3dBgDrag(card):カードに pointerdown/move/up。ボタン・入力・リンク・ラベル・ボードを隠すボタンの上から始めたものは無視(今まで通り押せる)。
#      指/マウスの動き dy(px)→ tilt += dy×(縦の画角/高さ)=絵が指についてくる向き。3px 動くまでは何もしない。
#      スマホ:空いた所から始めた touchmove は preventDefault(passive:false)でページのスクロールを止める(ボード・ボタンの上から始めればいつも通りスクロール)。
#      マウス:pointerdown で preventDefault(文字の選択を始めない)。背景を作り直しても(球場が変わっても)tilt は残る
#   ③ 外野手(左・中・右)は WD.Rf(f)×.75 に(今までは warp で 2.5D の位置を伸ばしていたので、センターがフェンスまで 30・バックスクリーンの前に重なって見えなかった)。内野手は今まで通り
#   テスト:hl3d_bg.py ㉔(空いた所でドラッグすると hl3dBgTilt が変わり、ボタンの上からでは変わらない・押せる。外野手 3 人が Rf×.75、内野は warp のまま)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.2.i"; const BASE_V1="v1.4.q";','const APP_VERSION="v2.2.j"; const BASE_V1="v1.4.q";')
# ① tilt
rep("""  S.cam.setViewOffset(S.W,S.H,0,off,S.W,S.H);""",
"""  S.cam.setViewOffset(S.W,S.H,0,off,S.W,S.H);
  if(hl3dBgTilt) S.cam.rotateX(hl3dBgTilt);   // v2.2.j:ドラッグ/スワイプの見上げ・見下ろし(合わせたあとに回す)""")
rep("""let hl3dSbHidden=false;""",
"""let hl3dSbHidden=false;
// v2.2.j:上下のドラッグ/スワイプで見上げ・見下ろし(ラジアン。端末の中で覚えるだけ。+ で見上げる)
let hl3dBgTilt=0; const HL3D_BG_TILT=[-.35,.45];
function hl3dBgDrag(card){ if(!card || card.dataset.hl3drag) return; card.dataset.hl3drag="1";
  const SKIP="button,input,select,textarea,a,label,summary,[contenteditable],.hl3sbBtn"; let act=null;
  const fovH=()=>{ const S=hl3dBgS; return S? (S.cam.fov*Math.PI/180)/Math.max(1,S.H) : 0; };
  card.addEventListener("pointerdown",e=>{ if(!hl3dBgS || e.button!==0 || (e.target.closest && e.target.closest(SKIP))) return; act={id:e.pointerId, y:e.clientY, t0:hl3dBgTilt, moved:false}; if(e.pointerType==="mouse") e.preventDefault(); try{ card.setPointerCapture(e.pointerId); }catch(x){} });
  card.addEventListener("pointermove",e=>{ if(!act || e.pointerId!==act.id) return; const dy=e.clientY-act.y; if(!act.moved && Math.abs(dy)<3) return; act.moved=true;
    hl3dBgTilt=Math.max(HL3D_BG_TILT[0],Math.min(HL3D_BG_TILT[1],act.t0+dy*fovH())); hl3dBgKick(); });
  const end=e=>{ if(!act || e.pointerId!==act.id) return; act=null; try{ card.releasePointerCapture(e.pointerId); }catch(x){} };
  card.addEventListener("pointerup",end); card.addEventListener("pointercancel",end);
  card.addEventListener("touchmove",e=>{ if(act && e.cancelable) e.preventDefault(); },{passive:false});   // 空いた所から始めたスワイプはページを動かさない
}""")
rep("""  let box=card.querySelector(":scope > .hl3dBg"); if(!box){ box=document.createElement("div"); box.className="hl3dBg"; card.insertBefore(box,card.firstChild); }""",
"""  let box=card.querySelector(":scope > .hl3dBg"); if(!box){ box=document.createElement("div"); box.className="hl3dBg"; card.insertBefore(box,card.firstChild); } hl3dBgDrag(card);   // v2.2.j:上下のドラッグ""")
# ③ 外野手
rep("""  const men=[]; Object.keys(HL_POS).filter(k=>k!=="投").forEach(k=>{ const [a,d]=HL_POS[k], m=hl3dMan(0xece8dc,own,true,UNI), p=hl3dP(...hlPt(a,WD.warp(a,d)),0); /* v2.1.t:外野手は伸ばした所へ */""",
"""  const men=[]; Object.keys(HL_POS).filter(k=>k!=="投").forEach(k=>{ const [a,d]=HL_POS[k], m=hl3dMan(0xece8dc,own,true,UNI), p=hl3dP(...hlPt(a, "左中右".includes(k)? WD.Rf(a)*.75 : WD.warp(a,d)),0); /* v2.1.t:外野手は伸ばした所へ。v2.2.j:外野手はフェンスの 75%(センターがバックスクリーンの前に重ならない) */""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
