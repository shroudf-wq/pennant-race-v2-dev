# v1.3.w → v1.4.b を v2.1.h に流して v2.1.i を作る(同期手順の B・差分のファイルなし。3者マージ)。
#   python3 sync_v14b_v21i.py <元 v1.3.w の本編> <v2.1.h の正本> <新 v1.4.b の本編> <出力>
#   衝突は1か所のはず(違えば止まる):版の行 → APP_VERSION="v2.1.i"; BASE_V1="v1.4.b"
#   v1.3.x〜v1.4.b で v1 と v2 の両方が触った関数はない(関数ごとに比べた。renderManaged の差は、関数のうしろの EASY_BOOST の行)。
#   v1 が観戦・采配の描画の関数(hl*・startManagedGame・playNextGameHighlight)に手を入れた所はない。記録に足された項目で v2 の層が読むべきものはない。
import sys, subprocess, hashlib
BASE, OURS, THEIRS, OUT = sys.argv[1:5]
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()[:16]
print("元", sha(BASE), "こちら", sha(OURS), "あちら", sha(THEIRS))
r=subprocess.run(["git","merge-file","-p","--diff3","-L","v2","-L","v13w","-L","v14b",OURS,BASE,THEIRS],capture_output=True)
s=r.stdout.decode("utf-8")
if r.returncode!=1: raise SystemExit(f"衝突の数が想定と違う: {r.returncode}")
a=s.index("<<<<<<< v2\n"); b=s.index("||||||| v13w\n",a); c=s.index("=======\n",b); d=s.index(">>>>>>> v14b\n",c)
ours=s[a+11:b]; theirs=s[c+8:d]
assert 'APP_VERSION="v2.1.h"' in ours and 'APP_VERSION="v1.4.b"' in theirs
s=s[:a]+'const APP_VERSION="v2.1.i"; const BASE_V1="v1.4.b";   /* v2(3D版):BASE_V1 は「元にした v1 の版」。同期するたびに上げる */\n'+s[d+13:]
if "<<<<<<<" in s or ">>>>>>>" in s: raise SystemExit("衝突が残っている")
open(OUT,"w",encoding="utf-8").write(s); print("ok", len(s.encode("utf-8")), sha(OUT))
