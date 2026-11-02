# v2.1.j のソースに当てると v2.1.k。python3 patch_v21k.py src.html new.html
# 見た目だけ(2.5D・3D の観戦と采配の舞台)。試合の計算・記録・セーブには触らない。
#   ユーザーの「ハイライト観戦時、選手の名前で右上の1が見えない。v1 はしっかり見える」:
#   2.5D・3D では名前のカードを上端いっぱいの帯にしている(決め事 7)ので、打席の前の場面で、右上の投球の一覧の1球目(①)が帯の下に隠れていた。
#   帯が出ている間だけ、ボールカウントの箱(投球の一覧と B・S・O)の上端を帯の下まで下げる(帯が引っ込むと戻る)。2D(v1 の道)は変えない
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.1.j"; const BASE_V1="v1.4.b";','const APP_VERSION="v2.1.k"; const BASE_V1="v1.4.b";')
rep(""".hlStage.hl3 .hlCutin .cutSub{min-width:0;overflow:hidden;text-overflow:ellipsis}""",
""".hlStage.hl3 .hlCutin .cutSub{min-width:0;overflow:hidden;text-overflow:ellipsis}
/* v2.1.k:名前の帯が出ている間は、ボールカウントの箱を帯の下へ(右上の投球の一覧の①が隠れないように) */
.hlStage.hl3 .bcPanel{transition:top .25s ease}
.hlStage.hl3:has(> .hlCutin:not(.out)) .bcPanel{top:calc(var(--hl3cutH,23px) + 5px)}""")
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
