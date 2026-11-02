# v1 の v1.1.y → v1.2.k を v2.0.d に流して v2.0.e を作る(同期手順。2026-10-20)
#   python3 sync_v12k_v20e.py <v1.1.yの本編> <v1.2.kの本編> <v2.0.dの正本> <出力>
# v1 側の差分は rep() 形式ではなく unified diff(filesb\v1.2.k\v1.1.y_to_v1.2.k.patch。v1.1.z〜v1.2.k の12版をまとめたもの)なので、
# sync_v1_to_v2.py ではなく 3者マージ(git merge-file。元=v1.1.y・こちら=v2.0.d・あちら=v1.2.k)で合わせる。
# 両方が同じ行を変えた所だけが衝突になる(4か所)。解き方は下の resolve() に固定して書いてあるので、同じ入力なら同じ結果になる。
import sys, re, subprocess, tempfile, os, shutil
BASE, THEIRS, OURS, OUT = sys.argv[1:5]
tmp=tempfile.mkdtemp()
for n,src in (("o",OURS),("b",BASE),("t",THEIRS)): shutil.copy(src,os.path.join(tmp,n))
r=subprocess.run(["git","merge-file","-p","--diff3","-L","v2.0.d","-L","v1.1.y","-L","v1.2.k",os.path.join(tmp,"o"),os.path.join(tmp,"b"),os.path.join(tmp,"t")],capture_output=True)
s=r.stdout.decode("utf-8")
blocks=list(re.finditer(r"<<<<<<< v2\.0\.d\n(.*?)\|\|\|\|\|\|\| v1\.1\.y\n(.*?)=======\n(.*?)>>>>>>> v1\.2\.k\n",s,re.S))
assert len(blocks)==4, ("衝突の数が想定(4)と違う。中身を見て直すこと",len(blocks))
def resolve(i,ours,base,theirs):
    if i==0:   # 設定の説明文:v2 の2行(立体の説明)+ v1.2.k のボールカウントの欄
        assert "立体「あり」" in ours and "hlBcSel" in theirs
        return ours+theirs.split("\n",1)[1]
    if i==1:   # 版の行
        return 'const APP_VERSION="v2.0.e"; const BASE_V1="v1.2.k";   /* v2(3D版):BASE_V1 は「元にした v1 の版」。同期するたびに上げる */\n'
    if i==2:   # v2 の 2.5D の層はそのまま、hlPreBanner は v1.2.k(引退試合の「ラストイヤーの打席へ」)
        assert ours.endswith(base); return ours[:-len(base)]+theirs
    if i==3:   # プレーの描画:2D は v1.2.k(ボールカウントの重ね bcHlOver)、2.5D にも同じ重ねを渡す
        assert "bb,over,{from: smooth" in ours
        return ours.replace("bb,over,{from: smooth","bb,over+bcHlOver(ev),{from: smooth").replace(base,theirs)
out=[];last=0
for i,m in enumerate(blocks):
    out.append(s[last:m.start()]); out.append(resolve(i,*m.groups())); last=m.end()
out.append(s[last:]); s="".join(out)
assert "<<<<<<<" not in s and ">>>>>>>" not in s
shutil.rmtree(tmp)

def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)
# 衝突しなかったが、v1.2.k が 2D の描画にだけ足したもの → 2.5D にも
rep('if(ev.kind==="BB") bb+=hl3Txt(HL_HX,HL_HY-40,24,"late","四球",c);',
    'if(ev.kind==="BB") bb+=hl3Txt(HL_HX,HL_HY-40,24,"late",ev.hp? "死球" : "四球",c);')   # v1.2.a の死球
# 札の重なりをほどく処理(v2.0.c)の2回目で、名前のカードに加えて v1.2.k のボールカウントの表示(右端の投球の一覧と B・S・O)もよける
rep("""  const cut=st.querySelector(".hlCutin:not(.out)");
  if(cut){ const cr={x:box.left+cut.offsetLeft, y:box.top+cut.offsetTop, w:cut.offsetWidth, h:cut.offsetHeight};
    items.forEach(o=>{ if(hit(o.a,cr)<=.5) return; const {w,h}=o.r;
      for(const [dx,dy] of candsOf(o)){ const a={x:o.r.x+dx, y:o.r.y+dy, w, h};
        if(hit(a,cr)>.5 || out(a)>0 || items.some(q=>q!==o && hit(a,q.a)>.5)) continue;""",
"""  const obs=[], cut=st.querySelector(".hlCutin:not(.out)"), bcp=st.querySelector(".bcPanel");
  if(cut) obs.push({x:box.left+cut.offsetLeft, y:box.top+cut.offsetTop, w:cut.offsetWidth, h:cut.offsetHeight});
  if(bcp) bcp.querySelectorAll(".bcList li,.bcBSO").forEach(e=>obs.push({x:box.left+bcp.offsetLeft+e.offsetLeft, y:box.top+bcp.offsetTop+e.offsetTop, w:e.offsetWidth, h:e.offsetHeight}));   // v2.0.e:ボールカウント
  if(obs.length){ const hitObs=a=>obs.reduce((t,c)=>t+hit(a,c),0);
    items.forEach(o=>{ if(hitObs(o.a)<=.5) return; const {w,h}=o.r;
      for(const [dx,dy] of candsOf(o)){ const a={x:o.r.x+dx, y:o.r.y+dy, w, h};
        if(hitObs(a)>.5 || out(a)>0 || items.some(q=>q!==o && hit(a,q.a)>.5)) continue;""")
open(OUT,"w",encoding="utf-8").write(s)
print("ok")
