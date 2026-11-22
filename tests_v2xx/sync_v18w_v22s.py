# v1.8.w(選手の中身の設定を「あり」に統一・前のセーブはそのまま)を v2.2.r に流して v2.2.s を作る(同期手順の A:rep をそのまま当てる)。
#   python3 sync_v18w_v22s.py <v2.2.r 本編> <出力>
#   v1 の patch_v18w.py と同じ置き換え(版の行だけ v2 の形)。リーグ作成の画面・プリセット・キャンプのおまかせの印・説明の文。計算部は触らない。
import sys
src, dst = sys.argv[1:3]
s = open(src, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    if s.count(a) != n: raise SystemExit(f"当たらない({s.count(a)}/{n}): {a[:80]}")
    s = s.replace(a, b)
rep('const APP_VERSION="v2.2.r"; const BASE_V1="v1.8.v";', 'const APP_VERSION="v2.2.s"; const BASE_V1="v1.8.w";')
# 1. 7つの行を隠す
UNI = ["growthSel", "tensionSel", "skillSel", "forteSel", "traitSel", "archSel", "posFitSel"]
for k in UNI:
    rep(f'<div class="formRow"><label for="{k}">', f'<div class="formRow uniHide"><label for="{k}">')
rep('.liteHide{display:none !important}', '.liteHide{display:none !important}\n.uniHide{display:none !important}   /* v1.8.w:新しいリーグでは選べない項目(いつも「あり」) */')
# 変えた数の数え方・段の中身の判定でも、隠した行を数えない
rep('if(!sel || row.classList.contains("liteHide") || row.classList.contains("hidden")) return;',
    'if(!sel || row.classList.contains("liteHide") || row.classList.contains("uniHide") || row.classList.contains("hidden")) return;')

# 2. プリセット「シンプル」
rep('simple:{tensionSel:"off",skillSel:"off",uniqSel:"off",spUniques:"0",forteSel:"off",',
    'simple:{tensionSel:"on",skillSel:"on",uniqSel:"off",spUniques:"0",forteSel:"on",')
rep('tacSel:"off",cupSel:"off",worldSel:"off",traitSel:"off",retrySel:"off",frontSel:"off",growthSel:"old",importSel:"off",posFitSel:"off",',
    'tacSel:"off",cupSel:"off",worldSel:"off",traitSel:"on",retrySel:"off",frontSel:"off",growthSel:"new",importSel:"off",posFitSel:"on",')

# 3. シンプルで作ったリーグは秋季キャンプをおまかせ(リーグごとの印)
rep('growthNews=[]; campPending=null; }   // 成長(v1.0.t)。従来なら v1.0.s と同じ',
    'growthNews=[]; campPending=null; { const ps=document.getElementById("presetSel"); campAutoLg= !!ps && ps.value==="simple"; } }   // 成長(v1.0.t)。従来なら v1.0.s と同じ。v1.8.w:シンプルなら秋季キャンプはおまかせ')
rep('campPending=null;   // 成長(v1.0.t)。それより前のセーブは「従来」のまま',
    'campPending=null; campAutoLg= st.campAutoLg===true;   // 成長(v1.0.t)。それより前のセーブは「従来」のまま')
rep('traitEnabled, leagueRecords, growth2Enabled, growthNews, ',
    'traitEnabled, leagueRecords, growth2Enabled, growthNews, campAutoLg, ')
rep('function campAutoOn(){ return LITE || lsGet("pennantCampAuto")==="1"; }\nfunction setCampAuto(on){ try{ tdLsSet("pennantCampAuto",on?"1":"0"); }catch(e){} renderCampSetting(); }',
    'let campAutoLg=false;   /* v1.8.w:プリセット「シンプル」で作ったリーグ(セーブに入る) */\n'
    'function campAutoOn(){ return LITE || campAutoLg || lsGet("pennantCampAuto")==="1"; }\n'
    'function setCampAuto(on){ if(!on) campAutoLg=false; try{ tdLsSet("pennantCampAuto",on?"1":"0"); }catch(e){} renderCampSetting(); }')

# 4. 説明の文(日本語と英語)
OLD_JA = 'シンプル:テンション・スキル・目玉選手・得意・フロント交代なし、ケガあり、投打バランス標準。マシマシ:テンション・スキル・目玉選手・得意・フロント交代あり、ケガなし、投打バランス打高。選んだあとで、項目を1つずつ変えることもできます。'
NEW_JA = 'シンプル:目玉選手・作戦・大会・演出・フロント交代なし、秋季キャンプはおまかせ、ケガあり、投打バランス標準。マシマシ:目玉選手・作戦・大会・演出・フロント交代あり、ケガなし、投打バランス打高。選んだあとで、項目を1つずつ変えることもできます。テンション・スキル・得意・特性・特色の上乗せ・守備の慣れ・成長は、いつも「あり」です。'
rep('下の項目をまとめて切り替えます。' + OLD_JA, '下の項目をまとめて切り替えます。' + NEW_JA, 2)
OLD_JA2 = '「シンプル」はテンション・スキル・目玉選手・得意・フロント交代なし、ケガあり、投打バランス標準。「マシマシ」はテンション・スキル・目玉選手・得意・フロント交代あり、ケガなし、投打バランス打高。'
NEW_JA2 = '「シンプル」は目玉選手・作戦・大会・演出・フロント交代なし、秋季キャンプはおまかせ、ケガあり、投打バランス標準。「マシマシ」は目玉選手・作戦・大会・演出・フロント交代あり、ケガなし、投打バランス打高。テンション・スキル・得意・特性・特色の上乗せ・守備の慣れ・成長は、いつも「あり」です。'
rep(OLD_JA2, NEW_JA2, 2)
rep('"Switches the settings below all at once. Simple: no mood, skills, phenoms, fortes, or front-office changes; injuries on; standard scoring. Loaded: mood, skills, phenoms, fortes, and front-office changes on; injuries off; hitter-friendly scoring. You can still change any setting afterward."',
    '"Switches the settings below all at once. Simple: no phenoms, tactics, cups, effects, or front-office changes; fall camp is automatic; injuries on; standard scoring. Loaded: phenoms, tactics, cups, effects, and front-office changes on; injuries off; hitter-friendly scoring. You can still change any setting afterward. Mood, skills, fortes, traits, club styles, position fit, and growth are always on."')
rep('"{0}: When creating a league, a preset switches the rule settings all at once. \\"Simple\\" turns off mood, skills, phenoms, fortes, and front-office changes, with injuries on and standard scoring. \\"Loaded\\" turns them on, with injuries off and hitter-friendly scoring.',
    '"{0}: When creating a league, a preset switches the rule settings all at once. \\"Simple\\" turns off phenoms, tactics, cups, effects, and front-office changes, makes fall camp automatic, and keeps injuries on with standard scoring. \\"Loaded\\" turns them on, with injuries off and hitter-friendly scoring. Mood, skills, fortes, traits, club styles, position fit, and growth are always on.')

# 5. 「遊び方」の欄のいちばん上に、いつも「あり」の項目を1行で出す
rep('<summary><h3>遊び方(選手と試合)</h3><span class="foldSum"></span></summary><div class="foldBody">',
    '<summary><h3>遊び方(選手と試合)</h3><span class="foldSum"></span></summary><div class="foldBody">\n    <p class="formHint" id="uniNote">テンション・スキル・得意・特性・特色の上乗せ・守備の慣れ・成長は、いつも「あり」です。</p>')
rep('let csMode="champ";', 'try{ I18N.add("en",{"テンション・スキル・得意・特性・特色の上乗せ・守備の慣れ・成長は、いつも「あり」です。":"Mood, skills, fortes, traits, club styles, position fit, and growth are always on."}); }catch(e){}   /* v1.8.w */\nlet csMode="champ";')

open(dst, "w", encoding="utf-8").write(s)
print("ok", len(s.encode()))
