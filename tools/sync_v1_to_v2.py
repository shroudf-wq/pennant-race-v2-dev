# v1 の patch(tests_v11?/patch_v11?.py)を v2 のソースに流す道具
#
# 使い方:
#   python3 sync_v1_to_v2.py <v2のソース> <v1のpatch> <出力先> [--v2 v2.0.b] [--base v1.1.y]
#
# やること:
#   1. v1 の patch の rep(old,new) をそのまま v2 のソースに当てる
#      (APP_VERSION を書き換える rep だけは飛ばす。v2 の版は --v2 で付ける)
#   2. v2 の BASE_V1(元にした v1 の版)を --base に書き換える
#   3. 当たらなかった rep があれば止まる(= v2 の計算部が v1 からずれている印。手で直す)
#
# 流す順番は v1 の版の順(v1.1.y → v1.1.z …)。飛ばすと途中の rep が当たらなくなる。
import sys, re

args = sys.argv[1:]
def opt(name, default=None):
    if name in args:
        i = args.index(name); v = args[i+1]; del args[i:i+2]; return v
    return default
v2ver = opt("--v2"); base = opt("--base")
src_path, patch_path, out_path = args

src = open(src_path, encoding="utf-8").read()
skipped = []; applied = []

def rep(old, new):
    global src
    if "APP_VERSION" in old:
        skipped.append(old); return          # 版は v2 側で付ける
    n = src.count(old)
    assert n == 1, ("v2 のソースに当たらない(計算部が v1 とずれている)", n, old[:80])
    src = src.replace(old, new); applied.append(old[:60])

# patch を読み、open/write の行を抜いて rep だけを実行する
code = open(patch_path, encoding="utf-8").read()
code = re.sub(r"^src=open\(.*$", "", code, flags=re.M)
code = re.sub(r"^def rep\(old,new\):\n(    .*\n)+", "", code, flags=re.M)
code = re.sub(r"^open\(sys\.argv\[2\].*$", "", code, flags=re.M)
code = re.sub(r'^print\("ok"\).*$', "", code, flags=re.M)
exec(compile(code, patch_path, "exec"), {"rep": rep, "sys": sys})

if v2ver:
    m = re.search(r'const APP_VERSION="(v2[^"]*)"', src)
    assert m, "v2 の APP_VERSION が見つからない"
    src = src.replace(m.group(0), f'const APP_VERSION="{v2ver}"')
if base:
    m = re.search(r'const BASE_V1="(v1[^"]*)"', src)
    assert m, 'v2 のソースに const BASE_V1="v1.x.x" がない(最初の v2 を作るときに APP_VERSION の隣に足す)'
    src = src.replace(m.group(0), f'const BASE_V1="{base}"')

open(out_path, "w", encoding="utf-8").write(src)
print(f"ok 当てた:{len(applied)} 飛ばした:{len(skipped)} → {out_path}")
