# v1.8.v(現役ドラフトの画面の関数の名前の付け替え)を v2.2.q に流して v2.2.r を作る(同期手順の A:rep をそのまま当てる)。
#   python3 sync_v18v_v22r.py <v2.2.q 本編> <出力>
#   v1.8.t の現役ドラフトの gdRender が、案内役(v1.7.h)の gdRender を上書きして案内役のカードが出なかった。v1 の patch_v18v.py と同じ4か所+版の行。
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    if s.count(a) != n: raise SystemExit(f"当たらない({s.count(a)}/{n}): {a[:80]}")
    s = s.replace(a, b)
rep('const APP_VERSION="v2.2.q"; const BASE_V1="v1.8.u";', 'const APP_VERSION="v2.2.r"; const BASE_V1="v1.8.v";')
rep('function gdOpen(){ const e=gdElig(league[myTeam]); gdUi={give:e[0]||null, wish:[]}; gdRender(); }',
    'function gdOpen(){ const e=gdElig(league[myTeam]); gdUi={give:e[0]||null, wish:[]}; gdDrRender(); }')
rep('function gdRender(){\n  const me=league[myTeam], mine=gdElig(me).slice(0,GD_OFFER_N)',
    'function gdDrRender(){   /* v1.8.v:案内役の gdRender とぶつかっていたので名前を変えた */\n  const me=league[myTeam], mine=gdElig(me).slice(0,GD_OFFER_N)')
rep('gdUi.give=p; gdKeepScroll(gdRender); }', 'gdUi.give=p; gdKeepScroll(gdDrRender); }')
rep('  gdKeepScroll(gdRender); }\nfunction gdConfirm()', '  gdKeepScroll(gdDrRender); }\nfunction gdConfirm()')
if s.count("function gdRender(") != 1: raise SystemExit("gdRender が1つになっていない")
open(dst, "w", encoding="utf-8").write(s)
print("ok", len(s.encode()))
