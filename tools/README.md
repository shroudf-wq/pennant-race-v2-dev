# tools

| ファイル | 中身 |
|---|---|
| `sync_v1_to_v2.py` | v1 の `rep(old,new)` 形式のパッチを v2 のソースに流す(同期手順の A。`docs/同期手順_v1→v2.md`) |

テストの道具は `tests_v2xx/`(`h.py`=v1 と共通の部品、`h3.py`=3D 用、`par_v2.py`・`sav_v2.py`・`hl3*.py`・`hl3d*.py`)。使い方は `docs/引き継ぎ書_v2.md` の5章と `CLAUDE.md` の5章。

```bash
export HL3D_LOCAL=$(pwd)/vendor/three-0.128.0.min.js
V1=file:///path/to/pennant-race-dev/src/pennant_source.html   # BASE_V1 の版(v1.8.b)
V2=file://$(pwd)/src/pennant_source.html
python3 tests_v2xx/par_v2.py $V1 $V2
python3 tests_v2xx/sav_v2.py $V1 $V2 tests_v2xx/saves
python3 tests_v2xx/hl3d_bg.py $V2 $HL3D_LOCAL out/bg
python3 tests_v2xx/hl3d_shots.py $V2 $HL3D_LOCAL 390 tests_v2xx/saves/save_A.json out/s390
```
