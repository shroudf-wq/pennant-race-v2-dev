# ペナントレース シミュレーター 3D版(v2。クラウド作業用)

日本の架空プロ野球リーグのペナントレースを、1つの HTML ファイルで遊ぶシミュレーションゲームの **3D版(v2.x.x)**。2D版(v1.x.x。別のリポジトリ `pennant-race-dev`)の計算部をそのまま使い、ハイライト観戦・じっくり采配の「絵」(2.5D と Three.js の 3D)と、試合画面の背景の 3D の球場を足したもの。
このリポジトリは **Claude Code のクラウドセッションで v2 の部品を作るための作業場**。公開・記録・保存は別の場所(claude.ai の Project「3Dゲーム化」と PC の `filesb\v2\`)で行うので、ここでは **「前の版に当てるパッチとテスト」を作って渡す** ところまでを受け持つ。

## 0. いちばん大事な決まり

1. **やり取りと文書は日本語**。専門用語を避け、分かりやすい言葉で書く。
2. **計算部は v1 が正**。試合・成長・ドラフト・FA・殿堂入りなど「結果を決める部分」は v2 で直さない(直したくなったら v1 で直して同期する。`docs/同期手順_v1→v2.md`)。v2 で触ってよいのは**記録を読んで絵にする部分**だけ(`hl3*`・`hl3d*`・観戦の設定の欄・試合画面の背景)。
3. **同じ乱数で v1(`BASE_V1` の版)と結果が1つも違わないこと**を `tests_v2xx/par_v2.py` で確かめる。演出の乱数は試合の乱数と別(3D は `hl3dRand`/`hl3dNR`、決まった数列、`forteHash`)。`Math.random` を使わない。Three.js は物を作るたびに `Math.random` を使うので、作る・描くところは必ず `hl3dNR(()=>…)` で包む。
4. **セーブの形式は変えない**(版4。v1 のセーブをそのまま読め、v2 の保存を v1 が読める)。3D のために覚える値は端末ごとの設定(localStorage)か、その場だけの変数に置く。球団ごとの見た目の型は球団名のハッシュ(`forteHash(名前+"…")>>>3`)で決め、セーブに足さない。
5. **`src/pennant_source.html` を直接書き換えてコミットしない**。作るのは次の3つ(4章):
   - `work/<タスク名>/patch_<タスク名>.py`(元のソースに当てるパッチ。`rep(old,new)` の並び。`old` が1回だけ見つかることを確かめながら当てる)
   - `work/<タスク名>/<略称>_check.py`(テスト。`tests_v2xx/hl3d_bg.py` の ㉑〜㉕ が見本)
   - `work/<タスク名>/README_<タスク名>.md`(使い方・変えたこと・測った数字・直さなかったこと)
6. **`APP_VERSION` は変えない**(版の番号は Project 側でまとめるときに付ける)。
7. 1行の途中に `//` のコメントを入れない(行の残りが消える。前に2回やった)。途中は `/* */`。パッチを当てたら `node --check` で構文を確かめる。
8. 迷ったら、作る前に案を3つ(A=王道・B=尖った案・C=実装が簡単な案)を README に書き、いちばん無難な案で作る。**面白さと工数のつり合い**を考える。

## 1. ファイルの置き場

| 場所 | 中身 |
|---|---|
| `src/pennant_source.html` | ソースの正本(**v2.2.p**。元にした v1 は **v1.8.e**。約3.5MB の1ファイル) |
| `docs/引き継ぎ書_v2.md` | v2 の引き継ぎ書(0章 決め事・1章 現在の状態・4章 作りの方針=2.5D のカメラ・3D の絵・守備の動き・試合画面の背景の球場(4.8)・5章 テスト・6章 版ごとの記録) |
| `docs/同期手順_v1→v2.md` | v1 の計算部を v2 に流す手順(3者マージ)と、当てたあとの確認 |
| `tools/sync_v1_to_v2.py` | v1 の `rep` 形式のパッチを v2 に流す道具(同期手順の A) |
| `tests_v2xx/` | テストの道具一式と、版ごとの差分(`patch_v2xx.py`。v2.0.b〜v2.2.k・v2.2.n・v2.2.p)・同期のスクリプト(`sync_*.py`。v2.2.l=`sync_v18b_v22l.py`・v2.2.m=`sync_v18c_v22m.py`)。v2.2.n から 3D の選手は絵の板(`hl3dBill`。引き継ぎ書 4.9。`hl3dMan` はない)。使い方は `tools/README.md` と `docs/引き継ぎ書_v2.md` の5章 |
| `tests_v2xx/saves/` | 互換テスト用のセーブ6本(v1.1.y で乱数を固定して作った版4。`sav_v2.py`・`hl3d_shots.py`・`hl3_overlap.py` などが読む) |
| `vendor/three-0.128.0.min.js` | テストで使う Three.js r128 の写し(npm の `three@0.128.0`。本編は cdnjs から読む。この作業場所からは cdnjs に出られないので、テストは `HL3D_LOCAL` でこれを差し替えて読ませる) |
| `work/` | **ここに作る**(タスクごとに1フォルダ) |

**作業を始める前に `docs/引き継ぎ書_v2.md` の 0章・4章(触る所の節)・5章を読む。** 3D の作りは 4.6〜4.8、球場の部品は 4.8 の版ごとの行(v2.1.j〜v2.2.k)に関数名つきで書いてある。

## 2. 環境のしたく

```bash
pip install playwright --break-system-packages
python3 -m playwright install --with-deps chromium
```

テストは Playwright(Python)でページを開いて動かす。共通の部品は `tests_v2xx/h.py`(v1 と同じ:乱数の固定 `SEED_JS`・1シーズン `SEASON`・`open_page`・`create`)と `tests_v2xx/h3.py`(3D 用:`open_page3`=cdnjs の URL を手元の Three.js に差し替え、設定「立体:3D」で開く)。
3D のテストは環境変数 `HL3D_LOCAL=vendor/three-0.128.0.min.js`(絶対パス)を付けて回す。この作業場所の WebGL はソフトウェア描画なので、コマ数は実機より少なく出る(`hl3_perf.py` の数は比較用)。

## 3. 作り方

1. `cp src/pennant_source.html work/<タスク名>/base.html`(比べ用の元。コミットしない)
2. 関数は `grep -n "function 名前" src/pennant_source.html` で探す。v2 の層は `hl3`(2.5D)・`hl3d`(3D)・`hl3dBg`(試合画面の背景)で始まる。
3. パッチは `rep(old,new)` の並び(`tests_v2xx/patch_v22k.py` が見本)。使い方の形:`python3 patch_<タスク名>.py 元.html 出力.html`
4. 当てたら `node --check`(`<script>` の中身を抜いて)→ 見本の写しを撮る(背景は `hl3d_bg.py` の書き方、観戦は `hl3d_shots.py`)→ テスト。
5. 球場の部品を足すときの約束:背景だけのもの(`opt.full`)と観戦にも出すもの(`OFF`=観戦の 3D)を分ける。観戦ではフェンスの位置と形(本塁から FR の円)を変えない(打球の落点・本塁打の絵と合わせるため)。2.5D の札(`.hl3bb`)と重なる所に物を置かない。内側から見る壁の絵は `repeat.x=−1`(鏡)。

## 4. 渡すもの

- `work/<タスク名>/` に 0章の3つ。
- README には:何を・どこを変えたか(関数名)/テストの項目と結果/同じ乱数で元と同じだったか(`par_v2.py`)/重さ(draw call・コマ数)/直さなかったこと・決めてほしいこと。
- **コミットは `work/<タスク名>/` の中だけ**。ブランチ名は `task/<タスク名>`。

## 5. テスト(使い方は `docs/引き継ぎ書_v2.md` の5章)

| 何を | 道具 |
|---|---|
| 同じ乱数で v1 と一致(5通り) | `python3 tests_v2xx/par_v2.py <v1のURL> <v2のURL>`(v1 は `BASE_V1` の本編。`pennant-race-dev` の `src/`) |
| セーブの互換 ①〜④ | `python3 tests_v2xx/sav_v2.py <v1のURL> <v2のURL> tests_v2xx/saves` |
| 試合画面の背景の球場 ①〜㉕ | `HL3D_LOCAL=… python3 tests_v2xx/hl3d_bg.py <v2のURL> <three.min.js> <撮る先>` |
| 3D の観戦の写し | `python3 tests_v2xx/hl3d_shots.py <v2のURL> <three.min.js> <幅> tests_v2xx/saves/save_A.json <撮る先>` |
| 采配の一致・結果の場面 | `python3 tests_v2xx/hl3_manage.py <v1のURL> <v2のURL> 390 <撮る先>` |
| 札の重なり(1つずつ回す) | `python3 tests_v2xx/hl3_overlap.py <v2のURL> 390 tests_v2xx/saves/save_A.json tests_v2xx/saves/save_B.json` |
| 守備の形・送球の順番・大会・読み込み | `hl3d_pose.py`・`hl3_throw.py`・`hl3_cup.py`・`hl3_load.py` |

URL は `file:///…/pennant_source.html`。いくつも同時に回すと時間がずれて「重なり」「撮影の時間切れ」が出ることがある(1つずつ回し直して確かめる)。
