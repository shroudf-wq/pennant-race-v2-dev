# v1.2.v → v1.3.d を v2.1.f に流して v2.1.g を作る(同期手順の B・差分のファイルなし)。
#   python3 sync_v13d_v21g.py <元 v1.2.v の本編> <v2.1.f の正本> <新 v1.3.d の本編> <出力>
#   3者マージ(git merge-file --diff3)。衝突は版の行の1か所だけのはず(違えば止まる)。
#   v1.2.w〜v1.3.d で v1 が観戦・采配の描画の関数(hlRenderPlay など)に手を入れた所はない。
#   入口の playNextGameHighlight・startManagedGame に銀河杯・世界大会の分かれ道が入っただけで、v2 の 2.5D/3D の層はそのまま使える
#   (世界大会の代表チームは teamColorMap にないので、3D の外野席の帯は灰色になる。v2 の層の決めたとおり)
#   記録に足された項目で v2 の層が読むべきものはない(大会の場面も ev.bp・ev.tac・ev.gg は同じ形)
import sys, subprocess, hashlib
BASE, OURS, THEIRS, OUT = sys.argv[1:5]
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()[:16]
print("元", sha(BASE), "あちら", sha(THEIRS))
r=subprocess.run(["git","merge-file","-p","--diff3","-L","v2","-L","v12v","-L","v13d",OURS,BASE,THEIRS],capture_output=True)
s=r.stdout.decode("utf-8")
if r.returncode!=1: raise SystemExit(f"衝突の数が想定と違う: {r.returncode}")
a=s.index("<<<<<<< v2\n"); e=s.index(">>>>>>> v13d\n")+len(">>>>>>> v13d\n")
blk=s[a:e]
if 'const APP_VERSION="v2.1.f"' not in blk or 'const APP_VERSION="v1.3.d"' not in blk: raise SystemExit("衝突が版の行ではない")
s=s[:a]+'const APP_VERSION="v2.1.g"; const BASE_V1="v1.3.d";   /* v2(3D版):BASE_V1 は「元にした v1 の版」。同期するたびに上げる */\n'+s[e:]
if "<<<<<<<" in s: raise SystemExit("衝突が残っている")
open(OUT,"w",encoding="utf-8").write(s); print("ok", len(s.encode("utf-8")))
