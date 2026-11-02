# v2.0.c のソースに当てると v2.0.d(2.5D のとき、打者・投手の名前のカードを上端の細い1行の帯にする)。python3 patch_v20d.py src.html new.html
# 触るのは CSS(.hlStage.hl3 の中の .hlCutin)と、B の画角(HL3_CAMS.B の ty)だけ。2D のカード・試合の計算・記録・セーブには触らない。
# 理由:スマホの幅では、カードが B(バックネット裏)の画面の左上(左翼・三塁の辺り)を覆い、その下の野手の札が隠れていた(v2.0.c の 4.1「残っている粗さ」)
import sys
s=open(sys.argv[1],encoding="utf-8").read()
def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
rep('const APP_VERSION="v2.0.c"; const BASE_V1="v1.1.y";','const APP_VERSION="v2.0.d"; const BASE_V1="v1.1.y";')
rep(".hl3.hl3flat .hl3shade{display:none}", r""".hl3.hl3flat .hl3shade{display:none}
/* v2.0.d:2.5D のときの名前のカードは、上端に横いっぱいの細い1行の帯(番号|名前 チーム・今日の成績)。下の野手の札を隠さない */
.hlStage.hl3 .hlCutin{top:0;left:0;right:0;max-width:none;border-radius:0;padding:2px 8px;gap:6px;box-shadow:0 1px 0 rgba(0,0,0,.35);z-index:3}
.hlStage.hl3 .hlCutin.l,.hlStage.hl3 .hlCutin.r{border-radius:0}
.hlStage.hl3 .hlCutin br{display:none}
.hlStage.hl3 .hlCutin>span:last-child{display:flex;align-items:baseline;gap:8px;min-width:0;overflow:hidden}
.hlStage.hl3 .hlCutin .cutNo{font-size:1rem;min-width:1.3em;padding-right:5px;border-right-width:1.5px}
.hlStage.hl3 .hlCutin .cutName{font-size:.9rem;line-height:1.25;white-space:nowrap;flex:0 0 auto}
.hlStage.hl3 .hlCutin .cutSub{min-width:0;overflow:hidden;text-overflow:ellipsis}""")
# B(バックネット裏)の画角を 12px 下げる:上端の帯の下に中堅手の札が入るように(B の画面の下側は観客席で空いている)
rep('B:{name:"バックネット裏",p:560,po:55,rx:62,rz:0,zoom:1.5,tx:0,ty:-2,far:.45},','B:{name:"バックネット裏",p:560,po:55,rx:62,rz:0,zoom:1.5,tx:0,ty:10,far:.45},')
open(sys.argv[2],"w",encoding="utf-8").write(s)
print("ok")
