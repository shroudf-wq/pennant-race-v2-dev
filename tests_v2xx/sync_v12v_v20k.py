# v1 の v1.2.k → v1.2.v を v2.0.j に流して v2.0.k を作る(同期手順の「B」3者マージ。2026-10-22)
#   python3 sync_v12v_v20k.py <v1.2.kの本編> <v1.2.vの本編> <v2.0.jの正本> <出力>
# v1 の差分は版ごとの patch_v12x.py(tests_v12x.zip の中)だが、v1.2.k と v1.2.v の本編が PC にあるので、それを元に3者マージする(元=v1.2.k・こちら=v2.0.j・あちら=v1.2.v)。
# 衝突は版の行の1か所だけ。そのあと、v1.2.v で記録に増えたもの(打球 bp・作戦の走塁)と球場の屋根を、v2 の 2.5D の層が読むように直す(rep)。
import sys, re, subprocess, tempfile, os, shutil
BASE, THEIRS, OURS, OUT = sys.argv[1:5]
tmp=tempfile.mkdtemp()
for n,src in (("o",OURS),("b",BASE),("t",THEIRS)): shutil.copy(src,os.path.join(tmp,n))
r=subprocess.run(["git","merge-file","-p","--diff3","-L","v2.0.j","-L","v1.2.k","-L","v1.2.v",os.path.join(tmp,"o"),os.path.join(tmp,"b"),os.path.join(tmp,"t")],capture_output=True)
s=r.stdout.decode("utf-8")
blocks=list(re.finditer(r"<<<<<<< v2\.0\.j\n(.*?)\|\|\|\|\|\|\| v1\.2\.k\n(.*?)=======\n(.*?)>>>>>>> v1\.2\.v\n",s,re.S))
assert len(blocks)==1, ("衝突の数が想定(1)と違う。中身を見て直すこと",len(blocks))
m=blocks[0]; assert 'APP_VERSION="v2.0.j"' in m.group(1) and 'APP_VERSION="v1.2.v"' in m.group(3)
s=s[:m.start()]+'const APP_VERSION="v2.0.k"; const BASE_V1="v1.2.v";   /* v2(3D版):BASE_V1 は「元にした v1 の版」。同期するたびに上げる */\n'+s[m.end():]
assert "<<<<<<<" not in s and ">>>>>>>" not in s
shutil.rmtree(tmp)

def rep(a,b):
    global s
    k=s.count(a)
    if k!=1: raise SystemExit(f"count {k}: {a[:80]}")
    s=s.replace(a,b)

# ① 球場の屋根:v1.2.v の球場の表(PARK_FIX)は屋根を t.park.dome に持つ。rainDome と同じく、あればそれを読む(前のセーブの球場は名前から)
rep("""  const dome= turf && ((forteHash(String(t.name)+"屋根")>>>3)%2)===0;   // v1.2.k の rainDome と同じ決め方(parkOf を通さない)""",
    """  const dome= turf && (typeof t.park.dome==="boolean"? t.park.dome : ((forteHash(String(t.name)+"屋根")>>>3)%2)===0);   // v1.2.v の rainDome と同じ決め方(parkOf を通さない)""")

# ② 観戦の打球:v1.2.v から場面の記録に打球 bp("G二"=二塁ゴロ・"F右"=ライトフライ。作戦と走塁ありのリーグ)がある。あればそれで描く
rep("""function hl3Grounder(ev,seed,bip){""","""// v2.0.k:場面の記録の打球(v1.2.v の ev.bp)を、采配の lastBIP と同じ形にする。ないときは null(これまでどおり hlRand)
function hl3Bip(ev){ const b=ev && ev.bp; if(typeof b!=="string" || b.length<2) return null; return {type: b[0]==="G"? "GB" : "FB", pos: b.slice(1)}; }
function hl3Grounder(ev,seed,bip){""")
rep("""    const trg= tr || hl3Grounder(ev,seed), cam=hl3CamFor(ev,trg), c=HL3_CAMS[cam];""",
    """    const trg= tr || hl3Grounder(ev,seed,hl3Bip(ev)), cam=hl3CamFor(ev,trg), c=HL3_CAMS[cam];""")

# ③ 凡打の守備:v1.2.v の作戦と走塁(ゴロの間の得点・本塁でアウト・二塁で封殺・飛び出して併殺・進塁)に合わせる。
#    記録に「誰がどこでアウトか」はないので、打つ前の塁 pn・動いた走者 mv・打った後の塁 af・増えたアウトから決める:
#      動いていない走者のうち、打った後にその塁が空いている人がアウト。ゴロなら次の塁で(一塁走者=二塁・三塁走者=本塁)、フライ・ライナーなら元の塁で(飛び出し)
#      打者は、どこかへ動いていなければ一塁でアウト(ゴロ)/捕られてアウト(フライ)
#    数が増えたアウトと合わないとき(記録が足りない)は、これまでどおり打者だけ一塁でアウト
rep("""function hl3Fielding(ev,tr){""","""function hl3Fielding(ev,tr,af){""")
rep("""  if(k==="OUT"){
    if(!gb){ F.marks.push({x:tr.ex,y:tr.ey,t:.92}); F.end=1.3; return F; }   // フライ:捕った所でアウト
    if(ev.dp) tgt.push([1,2],[0,1]); else tgt.push([0,1]); force=true;
  }""","""  if(k==="OUT"){
    const src=new Set(mv.map(([a])=>a)), dst=new Set(mv.map(([,b])=>b)), A=af||[false,false,false];
    const gone=[2,1,0].filter(i=> pn[i] && !src.has(i+1) && !(A[i] && !dst.has(i+1)));   // 動いておらず、打った後にその塁が空いた走者(先の走者から)
    const batOut=!src.has(0);
    if(!gb){   // フライ・ライナー:捕った所でアウト。飛び出した走者は元の塁へ投げてアウト
      F.marks.push({x:tr.ex,y:tr.ey,t:.92}); F.end=1.3;
      if(gone.length && gone.length+1===dOuts) gone.forEach(i=>tgt.push([i+1,i+1]));
      if(!tgt.length) return F;
    } else if(gone.length+(batOut? 1 : 0)===dOuts && dOuts>0){   // ゴロ:先の走者から次の塁(併殺は二塁→一塁、ゴロゴーで本塁へ、二塁で封殺)、最後に打者を一塁で
      gone.forEach(i=>tgt.push([i+1,i+2])); if(batOut) tgt.push([0,1]);
    } else { if(ev.dp) tgt.push([1,2],[0,1]); else tgt.push([0,1]); }   // 記録が足りないとき(これまでどおり)
    force=true;
  }""")
# 飛び出し(元の塁でアウト)の送球は、捕ってすぐ。走者は動かずに、アウトのあと消える
rep("""  let px=tr.ex, py=tr.ey, t=.9+(gb? .08 : .3);   // 捕ってから投げるまで(ゴロ・バントは素早く、外野は拾ってから)""",
    """  let px=tr.ex, py=tr.ey, t=.9+((gb || k==="OUT")? .08 : .3);   // 捕ってから投げるまで(ゴロ・バント・内野のフライは素早く、外野の安打は拾ってから)""")
rep("""    const ra=Math.max(arrive(a,b), ta+.05);   // 走者はボールの直後に着く(間一髪)""",
    """    const ra= a===b? ta : Math.max(arrive(a,b), ta+.05);   // 走者はボールの直後に着く(間一髪)。飛び出しは元の塁のまま""")
# 動かない走者(飛び出し)の札:速さの割り算と、走る動きを飛ばす
rep("""    + F.mvOut.map(([a,b,ra])=>one(a,b,(ra-st)/(b-a),ra)).join("");   // v2.0.j:アウトになる走者""",
    """    + F.mvOut.map(([a,b,ra])=>one(a,b,(ra-st)/((b-a)||1),ra)).join("");   // v2.0.j:アウトになる走者(v2.0.k:a===b は飛び出し)""")
rep("""    try{ el.animate(kf,{duration:n*per,delay:stt,fill:"forwards"}); if(b===4 && oT===null)""",
    """    try{ if(n>0) el.animate(kf,{duration:n*per,delay:stt,fill:"forwards"}); if(b===4 && oT===null)""")
# 呼ぶ側:打った後の塁(観戦は ev.rn/ev.bases、采配は d.rn)を渡す
rep("""    const fld= isPc? null : hl3Fielding(ev,tr3),""",
    """    const fld= isPc? null : hl3Fielding(ev,tr3,(ev.rn||(ev.bases||[]).map(b=>!!b)).map(Boolean)),""")
rep("""  const fld=hl3Fielding(ev,tr3), moved=""","""  const fld=hl3Fielding(ev,tr3,(d.rn||[null,null,null]).map(Boolean)), moved=""")
# ④ 札の重なりをほどく1回目に、走る前の走者(塁にいる走者の札)も入れる。三塁走者が三塁手の札の下に隠れたまま走り出す・飛び出しで動かない走者が隠れたままになるのを防ぐ
rep("""  setTimeout(()=>hl3Declutter(st,false), (to!==from)? 520 : 40);""","""  setTimeout(()=>hl3Declutter(st,true), (to!==from)? 520 : 40);   // v2.0.k:走る前の走者も入れる""")
# ⑤ 走者を消す動き(本塁に還った・アウトになった)は、消す時刻になってから作る。遅らせて先に作っておくと、待っている間の不透明度の動きで
#    3D の重なりが崩れ、その走者の札がまったく描かれない(v2.0.j のアウトになる走者・本塁に還る走者)
rep("""    try{ if(n>0) el.animate(kf,{duration:n*per,delay:stt,fill:"forwards"}); if(b===4 && oT===null) el.animate([{opacity:1},{opacity:0}],{duration:250,delay:stt+n*per,fill:"forwards"});
      if(oT!==null) el.animate([{opacity:1},{opacity:0}],{duration:300,delay:oT+450,fill:"forwards"}); }catch(e){}""",
"""    const fade=(ms,dur)=>setTimeout(()=>{ if(!el.isConnected) return; try{ el.animate([{opacity:1},{opacity:0}],{duration:dur,fill:"forwards"}); }catch(e){ el.style.opacity=0; } }, ms);
    try{ if(n>0) el.animate(kf,{duration:n*per,delay:stt,fill:"forwards"}); }catch(e){}
    if(b===4 && oT===null) fade(stt+n*per,250);
    if(oT!==null) fade(oT+450,300);""")
open(OUT,"w",encoding="utf-8").write(s)
print("ok")
