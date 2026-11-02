# v1.4.b → v1.4.q の差分を v2.2.d に流して v2.2.e を作る(同期手順の B:3者マージ)。
#   python3 sync_v14q_v22e.py <元 v1.4.b 本編> <v2.2.d 本編> <新 v1.4.q 本編> <出力>
#   v1.4.c〜v1.4.q の 15 版ぶん(練習モードの抜け道・スマホの見た目・PC の観戦 2 列・球団旗/リーグ旗/ディビジョン旗・試合タブの帯と対戦ボード・
#   結果のカード・順位表・成績の表/タイトル/比べる・球団名の飾り・ポストシーズンの成績を分ける)。計算が変わるのは v1.4.q だけ(2年目から)。
#   衝突は APP_VERSION の 1 行だけ(想定と違えば止まる)。h.py は v1.4.b から変わっていない。
import sys, subprocess
base, ours, theirs, out = sys.argv[1:5]
r=subprocess.run(["git","merge-file","-p","--diff3","-L","v2","-L","v14b","-L","v14q",ours,base,theirs],capture_output=True)
s=r.stdout.decode("utf-8")
n=s.count("<<<<<<< v2")
if n!=1: raise SystemExit(f"衝突の数が想定と違う: {n}")
a='''<<<<<<< v2
const APP_VERSION="v2.2.d"; const BASE_V1="v1.4.b";   /* v2(3D版):BASE_V1 は「元にした v1 の版」。同期するたびに上げる */
||||||| v14b
const APP_VERSION="v1.4.b";
=======
const APP_VERSION="v1.4.q";
>>>>>>> v14q
'''
if s.count(a)!=1: raise SystemExit("版の行の衝突の形が違う")
s=s.replace(a,'const APP_VERSION="v2.2.e"; const BASE_V1="v1.4.q";   /* v2(3D版):BASE_V1 は「元にした v1 の版」。同期するたびに上げる */\n')
open(out,"w",encoding="utf-8").write(s)
print("ok", len(s))
