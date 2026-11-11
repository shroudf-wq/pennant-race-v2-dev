# v1.8.e → v1.8.u の差分を v2.2.p に流して v2.2.q を作る(同期手順の B:3者マージ)。
#   python3 sync_v18u_v22q.py <元 v1.8.e 本編> <v2.2.p 本編> <新 v1.8.u 本編> <出力>
#   v1.8.f〜u(打順の右端・順位表の予想・SNS の画像・盗塁の演出・リーグの決まり2つ・本物のプレー①〜⑤・記録の線・背番号の守り・
#   打席の打者の描き直し・選手の節目・野手のコーチ・現役ドラフト)。衝突は1か所(版の行)だけのはず(想定と違えば止まる) → v2.2.q / BASE_V1=v1.8.u
#   v1.8.i の盗塁の演出(sbx)は hlRenderPlay・renderManaged のいちばん外を包むので、そのままだと 2.5D・3D のときも 2D の絵になる。
#   2.5D・3D(hl3Active())のときは使わないように、sbxHlOn・sbxMgOn に条件を1つ足す(v2 の 3D の盗塁=v2.2.p をそのまま見せる)。
import sys, subprocess, re
base, ours, theirs, out = sys.argv[1:5]
r = subprocess.run(["git", "merge-file", "-p", "--diff3", "-L", "v2", "-L", "v18e", "-L", "v18u", ours, base, theirs], capture_output=True)
s = r.stdout.decode("utf-8")
pat = re.compile(r'<<<<<<< v2\n(.*?)\|\|\|\|\|\|\| v18e\n(.*?)=======\n(.*?)>>>>>>> v18u\n', re.S)
blocks = list(pat.finditer(s))
if len(blocks) != 1: raise SystemExit(f"衝突の数が想定と違う: {len(blocks)}")
o, b, t = blocks[0].groups()
if 'APP_VERSION="v2.2.p"' not in o or 'APP_VERSION="v1.8.u"' not in t: raise SystemExit("版の行の形が違う")
rr = 'const APP_VERSION="v2.2.q"; const BASE_V1="v1.8.u";   /* v2(3D版):BASE_V1 は「元にした v1 の版」。同期するたびに上げる */\n'
s = s[:blocks[0].start()] + rr + s[blocks[0].end():]
if "<<<<<<<" in s or "||||||| v18e" in s: raise SystemExit("衝突が残った")
def rep(a, b, n=1):
    global s
    if s.count(a) != n: raise SystemExit(f"当たらない({s.count(a)}/{n}): {a[:80]}")
    s = s.replace(a, b)
rep('function sbxHlOn(ev){ return !!ev && ',
    'function sbxHlOn(ev){ return !(typeof hl3Active==="function" && hl3Active()) && !!ev && ')   # v2:2.5D・3D は v2 の盗塁の絵
rep('function sbxMgOn(d){ return !!d && ',
    'function sbxMgOn(d){ return !(typeof hl3Active==="function" && hl3Active()) && !!d && ')
open(out, "w", encoding="utf-8").write(s)
print("ok", len(s.encode()))
