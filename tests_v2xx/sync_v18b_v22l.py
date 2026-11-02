# v1.4.q → v1.8.b の差分を v2.2.k に流して v2.2.l を作る(同期手順の B:3者マージ)。
#   python3 sync_v18b_v22l.py <元 v1.4.q 本編> <v2.2.k 本編> <新 v1.8.b 本編> <出力>
#   v1.4.r〜v1.8.b の 74 版ぶん(v1.4.r〜z・v1.5.a〜z・v1.6.a〜k・v1.7.a〜z・v1.8.a〜b)。計算が変わる版を含む
#   (v1.5.v 名前の一覧・v1.6.k 調子・v1.7.k 作戦・v1.7.n 二塁打・v1.7.r 衰え・v1.7.t FA の補償 など)。v2 は計算部に触っていないので、
#   同じ乱数で v1.8.b と一致する(par_v2.py 5通り・sav_v2.py 6本)。
#   衝突は6か所(想定と違えば止まる):
#     1 版の行 → v2.2.l / BASE_V1=v1.8.b
#     2 hlPreBanner の直前に v2 が 2.5D/3D の観戦を足した所。v1.6.f で hlPreBanner の「チャンス到来」が直った → v2 の足し分+v1 の新しい行
#     3 hlRenderPre の cutin の行。v1.7.w の esc → v1 の新しい行+v2 の 2.5D の分
#     4 SEL_TIPS。v2 が頭に hl3dSel・尾に英語を足し、v1 が中身を足した → v1 の新しい中身に v2 の2つの足し分を同じ所へ
#     5 v1 の mgBczDetail(v1.4.w)と v2 の hl3MgResultStage が同じ所に足された → 両方(v1 → v2 の順)
#     6 版の表示。v2 が「(2D: v1.x)」を足し、v1.7.s が tdLsGet にした → 1行目は v2・2行目は v1
import sys, subprocess, re, difflib
base, ours, theirs, out = sys.argv[1:5]
r = subprocess.run(["git", "merge-file", "-p", "--diff3", "-L", "v2", "-L", "v14q", "-L", "v18b", ours, base, theirs], capture_output=True)
s = r.stdout.decode("utf-8")
pat = re.compile(r'<<<<<<< v2\n(.*?)\|\|\|\|\|\|\| v14q\n(.*?)=======\n(.*?)>>>>>>> v18b\n', re.S)
blocks = list(pat.finditer(s))
if len(blocks) != 6: raise SystemExit(f"衝突の数が想定と違う: {len(blocks)}")
def merge_inserts(o, b, t):   # v2 が b に足しただけの所を、t の同じ場所へ足す
    sm = difflib.SequenceMatcher(None, b, o, autojunk=False)
    ops = sm.get_opcodes()
    if any(op not in ("equal", "insert") for op, *_ in ops): raise SystemExit("4:v2 が足す以外の直しをしている")
    res = t
    for op, i1, i2, j1, j2 in sorted([x for x in ops if x[0] == "insert"], key=lambda x: -x[1]):
        ctx = b[max(0, i1 - 80):i1]
        if res.count(ctx) != 1: raise SystemExit("4:足す場所が決まらない")
        p = res.index(ctx) + len(ctx); res = res[:p] + o[j1:j2] + res[p:]
    return res
parts = []; last = 0
for k, m in enumerate(blocks, 1):
    o, b, t = m.groups()
    if k == 1:
        if 'APP_VERSION="v2.2.k"' not in o: raise SystemExit("1:版の行の形が違う")
        rr = 'const APP_VERSION="v2.2.l"; const BASE_V1="v1.8.b";   /* v2(3D版):BASE_V1 は「元にした v1 の版」。同期するたびに上げる */\n'
    elif k == 2:
        if not o.endswith(b): raise SystemExit("2:形が違う")
        rr = o[:-len(b)] + t
    elif k == 3:
        if not o.startswith(b): raise SystemExit("3:形が違う")
        rr = t + o[len(b):]
    elif k == 4:
        rr = merge_inserts(o, b, t)
    elif k == 5:
        if b != "": raise SystemExit("5:形が違う")
        rr = t + o
    elif k == 6:
        ol, bl, tl = o.split("\n"), b.split("\n"), t.split("\n")
        if not (ol[1] == bl[1] and tl[0] == bl[0]): raise SystemExit("6:形が違う")
        rr = "\n".join([ol[0]] + tl[1:])
    parts.append(s[last:m.start()]); parts.append(rr); last = m.end()
parts.append(s[last:])
res = "".join(parts)
if "<<<<<<<" in res or "||||||| v14q" in res: raise SystemExit("衝突が残った")
open(out, "w", encoding="utf-8").write(res)
print("ok", len(res.encode()))
