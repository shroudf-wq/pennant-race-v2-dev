# v1.8.c → v1.8.e の差分を v2.2.n に流して v2.2.o を作る(同期手順の B:3者マージ)。
#   python3 sync_v18e_v22o.py <元 v1.8.c 本編> <v2.2.n 本編> <新 v1.8.e 本編> <出力>
#   v1.8.d=ハイライトのスコアの遅れ・サヨナラの場面(hl-score)・v1.8.e=作戦を見えるようにする(sq-show)。
#   衝突は1か所(版の行)だけのはず(想定と違えば止まる) → v2.2.o / BASE_V1=v1.8.e
import sys, subprocess, re
base, ours, theirs, out = sys.argv[1:5]
r = subprocess.run(["git", "merge-file", "-p", "--diff3", "-L", "v2", "-L", "v18c", "-L", "v18e", ours, base, theirs], capture_output=True)
s = r.stdout.decode("utf-8")
pat = re.compile(r'<<<<<<< v2\n(.*?)\|\|\|\|\|\|\| v18c\n(.*?)=======\n(.*?)>>>>>>> v18e\n', re.S)
blocks = list(pat.finditer(s))
if len(blocks) != 1: raise SystemExit(f"衝突の数が想定と違う: {len(blocks)}")
o, b, t = blocks[0].groups()
if 'APP_VERSION="v2.2.n"' not in o or 'APP_VERSION="v1.8.e"' not in t: raise SystemExit("版の行の形が違う")
rr = 'const APP_VERSION="v2.2.o"; const BASE_V1="v1.8.e";   /* v2(3D版):BASE_V1 は「元にした v1 の版」。同期するたびに上げる */\n'
res = s[:blocks[0].start()] + rr + s[blocks[0].end():]
if "<<<<<<<" in res or "||||||| v18c" in res: raise SystemExit("衝突が残った")
open(out, "w", encoding="utf-8").write(res)
print("ok", len(res.encode()))
