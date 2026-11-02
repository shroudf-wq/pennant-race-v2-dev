# v1.8.b → v1.8.c の差分を v2.2.l に流して v2.2.m を作る(同期手順の B:3者マージ)。
#   python3 sync_v18c_v22m.py <元 v1.8.b 本編> <v2.2.l 本編> <新 v1.8.c 本編> <出力>
#   v1.8.c は打席の画面(bcv)の人物を部品で描く版(v2 の作業場の work/bcv-figures で試作し、ユーザーの「A=v1 に入れて v2 へ同期」で v1 に入れたもの)。
#   衝突は1か所(版の行)だけのはず(想定と違えば止まる) → v2.2.m / BASE_V1=v1.8.c
import sys, subprocess, re
base, ours, theirs, out = sys.argv[1:5]
r = subprocess.run(["git", "merge-file", "-p", "--diff3", "-L", "v2", "-L", "v18b", "-L", "v18c", ours, base, theirs], capture_output=True)
s = r.stdout.decode("utf-8")
pat = re.compile(r'<<<<<<< v2\n(.*?)\|\|\|\|\|\|\| v18b\n(.*?)=======\n(.*?)>>>>>>> v18c\n', re.S)
blocks = list(pat.finditer(s))
if len(blocks) != 1: raise SystemExit(f"衝突の数が想定と違う: {len(blocks)}")
o, b, t = blocks[0].groups()
if 'APP_VERSION="v2.2.l"' not in o or 'APP_VERSION="v1.8.c"' not in t: raise SystemExit("版の行の形が違う")
rr = 'const APP_VERSION="v2.2.m"; const BASE_V1="v1.8.c";   /* v2(3D版):BASE_V1 は「元にした v1 の版」。同期するたびに上げる */\n'
res = s[:blocks[0].start()] + rr + s[blocks[0].end():]
if "<<<<<<<" in res or "||||||| v18b" in res: raise SystemExit("衝突が残った")
open(out, "w", encoding="utf-8").write(res)
print("ok", len(res.encode()))
