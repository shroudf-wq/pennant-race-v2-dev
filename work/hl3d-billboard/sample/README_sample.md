# 見本(捨てる作り)

- `proto_hl3d_billboard.py`:v2.2.l の `src/pennant_source.html` に当てると、観戦の 3D・試合画面の背景の選手が 2D の絵の板になる(`python3 proto_hl3d_billboard.py src/pennant_source.html out.html`)。名前の札は出さない。ブルペン・ベンチ・待つ打者・捕手も板。左右反転・`hl3Declutter` の整理・テストはやっていない
- `sample_pc.png`(1366)・`sample_390.png`(390):観戦の見本。`cmp_pc.png`・`cmp_390.png`:上/左が今(v2.2.l)、下/右が見本(札あり・初期の見本)
- `sample_bg_bullpen.png`・`sample_bg_bench.png`:試合画面の背景(ブルペン・ベンチ)
- 測った数:幅390のプレー前で選手1人の高さ 11px → 22px、PC(1366)で 24px → 49px
- 本番は `../hl3d-billboard-instruction.md` の通りに作る(この見本はそのまま使わず、作り直してよい)
