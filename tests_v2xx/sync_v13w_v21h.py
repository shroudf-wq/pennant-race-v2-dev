# v1.3.d → v1.3.w を v2.1.g に流して v2.1.h を作る(同期手順の B・差分のファイルなし。3者マージ)。
#   python3 sync_v13w_v21h.py <元 v1.3.d の本編> <v2.1.g の正本> <新 v1.3.w の本編> <出力>
#   衝突は3か所のはず(違えば止まる):
#   ① <style> の終わり:v2 の 2.5D/3D の CSS と、v1.3.w のシンプル表示の CSS が同じ場所に足された → 両方残す(v2 が先)
#   ② 観戦の設定の説明:v2 は文を直し「立体」の段落を足した/v1.3.i は段落に data-tipfor="hlSpeedSel"(説明の帯の「詳しく」)を付けた
#      → v2 の文のまま、1つめに data-tipfor="hlSpeedSel"、2つめ(立体)に data-tipfor="hl3dSel" を付ける
#   ③ 版の行 → APP_VERSION="v2.1.h"; BASE_V1="v1.3.w"
#   ほかに足すもの:v2 の「立体」の選択欄に説明の帯の一言(SEL_TIPS.hl3dSel)と、その英語。
#   v1.3.e〜w で v1 が観戦・采配の描画の関数(hl*・renderManaged・startManagedGame・playNextGameHighlight)に手を入れた所はない(関数ごとに比べた)。
#   記録に足された項目で v2 の層が読むべきものはない(v1.3.p の achSkyTrack は実績用の記録だけ)。
import sys, subprocess, hashlib, json
BASE, OURS, THEIRS, OUT = sys.argv[1:5]
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()[:16]
print("元", sha(BASE), "こちら", sha(OURS), "あちら", sha(THEIRS))
r=subprocess.run(["git","merge-file","-p","--diff3","-L","v2","-L","v13d","-L","v13w",OURS,BASE,THEIRS],capture_output=True)
s=r.stdout.decode("utf-8")
if r.returncode!=3: raise SystemExit(f"衝突の数が想定と違う: {r.returncode}")
def blocks(s):
    out=[]; i=0
    while True:
        a=s.find("<<<<<<< v2\n",i)
        if a<0: return out
        b=s.index("||||||| v13d\n",a); c=s.index("=======\n",b); d=s.index(">>>>>>> v13w\n",c)
        out.append((a,s[a+11:b],s[b+13:c],s[c+8:d],d+13)); i=d+13
bl=blocks(s); assert len(bl)==3
def resolve(k):
    a,ours,base,theirs,e=bl[k]
    if k==0:
        assert base=="" and ".hl3cam{" in ours and "html[data-simple]" in theirs
        return ours+theirs
    if k==1:
        assert 'data-tipfor="hlSpeedSel"' in theirs and "立体「あり」" in ours and ours.count('<p class="small">')==2
        return ours.replace('<p class="small">','<p class="small" data-tipfor="hlSpeedSel">',1).replace('<p class="small">立体','<p class="small" data-tipfor="hl3dSel">立体',1)
    if k==2:
        assert 'APP_VERSION="v2.1.g"' in ours and 'APP_VERSION="v1.3.w"' in theirs
        return 'const APP_VERSION="v2.1.h"; const BASE_V1="v1.3.w";   /* v2(3D版):BASE_V1 は「元にした v1 の版」。同期するたびに上げる */\n'
for k in (2,1,0):
    a,_,_,_,e=bl[k]; s=s[:a]+resolve(k)+s[e:]
if "<<<<<<<" in s or ">>>>>>>" in s: raise SystemExit("衝突が残っている")
def rep(a,b):
    global s
    c=s.count(a); assert c==1,(c,a[:60]); s=s.replace(a,b)
TIP={"3d":"Three.js で立体に描きます。読めないときは「あり」になります","on":"場面ごとにカメラを切り替えて、斜めから見せます","weak":"軽く傾けるだけ","off":"今までの平面の図"}
rep('const SEL_TIPS={', 'const SEL_TIPS={"hl3dSel":'+json.dumps(TIP,ensure_ascii=False)+',')
EN={"Three.js で立体に描きます。読めないときは「あり」になります":"Draws in 3D with Three.js; falls back to 2.5D if it can't load",
    "場面ごとにカメラを切り替えて、斜めから見せます":"Switches the camera by scene and shows the field at an angle",
    "軽く傾けるだけ":"Just a slight tilt","今までの平面の図":"The flat 2D diagram"}
rep('"説明": "Info", ', '"説明": "Info", '+json.dumps(EN,ensure_ascii=False)[1:-1]+', ')
open(OUT,"w",encoding="utf-8").write(s); print("ok", len(s.encode("utf-8")), sha(OUT))
